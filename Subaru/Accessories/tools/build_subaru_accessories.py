#!/usr/bin/env python3
"""Extract structured Subaru accessory records from Excel-exported HTML sheets."""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "Subaru" / "Accessories"
OUTPUT = SOURCE_ROOT / "data" / "accessories.json"

PART_RE = re.compile(r"^(?=.{5,24}$)(?=.*[A-Z])(?=.*\d)[A-Z0-9][A-Z0-9\- ]+$")
YEAR_RE = re.compile(r"MY\s*(\d{2})(?:\s*[-–]\s*(\d{2}|Current))?", re.I)
GENERATION_HINTS = {
    "SF": "SF", "SG": "SG", "SH": "SH", "SJ": "SJ", "SK": "SK",
    "BRZ": "BRZ", "WRX": "WRX", "LEVORG": "Levorg", "XV": "XV",
}


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data: str):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            value = " ".join("".join(self.cell).replace("\xa0", " ").split())
            self.row.append(html.unescape(value))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if any(self.row):
                self.rows.append(self.row)
            self.row = None


def clean_part(value: str) -> str | None:
    value = re.sub(r"\s+", "", value.upper().strip())
    if value in {"PARTNUMBER", "PARTNO", "P/N", "PN"}:
        return None
    return value if PART_RE.match(value) else None


def infer_context(path: Path, rows: list[list[str]]) -> dict:
    rel = path.relative_to(SOURCE_ROOT).as_posix()
    parts = path.relative_to(SOURCE_ROOT).parts
    model = parts[0] if parts else "Subaru"
    text = " ".join(" ".join(r) for r in rows[:15]) + " " + rel
    year_match = YEAR_RE.search(text)
    year_from = year_to = None
    if year_match:
        year_from = 2000 + int(year_match.group(1))
        if year_match.group(2) and year_match.group(2).lower() != "current":
            year_to = 2000 + int(year_match.group(2))
        elif year_match.group(2):
            year_to = "current"
    generation = next((v for k, v in GENERATION_HINTS.items() if re.search(rf"\b{k}\b", text, re.I)), None)
    return {"model": model, "yearFrom": year_from, "yearTo": year_to, "generation": generation, "source": f"Subaru/Accessories/{rel}"}


def find_header(rows: list[list[str]]) -> tuple[int, int, int, list[tuple[int, str]]] | None:
    for i, row in enumerate(rows):
        upper = [c.upper() for c in row]
        part_idx = next((j for j, c in enumerate(upper) if "PART" in c and ("NUMBER" in c or "NO" in c)), None)
        desc_idx = next((j for j, c in enumerate(upper) if "DESCRIPTION" in c or "ACCESSORY" in c), None)
        if part_idx is None or desc_idx is None:
            continue
        variants: list[tuple[int, str]] = []
        for j, cell in enumerate(row):
            name = cell.strip()
            if j not in {part_idx, desc_idx} and name and len(name) <= 30 and name.upper() not in {"PRICE", "RRP", "FRT", "NOTES", "QTY"}:
                variants.append((j, name))
        return i, part_idx, desc_idx, variants
    return None


def extract_sheet(path: Path) -> list[dict]:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    if "<table" not in raw.lower():
        return []
    parser = TableParser()
    parser.feed(raw)
    rows = parser.rows
    header = find_header(rows)
    if not header:
        return []
    header_row, part_idx, desc_idx, variant_cols = header
    context = infer_context(path, rows)
    category = "General"
    records: list[dict] = []
    for row in rows[header_row + 1:]:
        cells = row + [""] * max(0, max(part_idx, desc_idx, *(j for j, _ in variant_cols), default=0) + 1 - len(row))
        part = clean_part(cells[part_idx])
        desc = cells[desc_idx].strip() if desc_idx < len(cells) else ""
        if not part:
            possible_category = cells[part_idx].strip()
            if possible_category and len(possible_category) < 60 and not any(ch.isdigit() for ch in possible_category):
                category = possible_category
            continue
        if not desc:
            continue
        variants = []
        for col, name in variant_cols:
            if col < len(cells):
                mark = cells[col].strip().lower()
                if mark and mark not in {"-", "n/a", "no"}:
                    variants.append(name)
        record = {
            "brand": "Subaru",
            **context,
            "category": category,
            "partNumber": part,
            "description": desc,
            "variants": variants,
            "notes": "",
            "href": "../" + context["source"].replace("Subaru/", "Subaru/"),
            "recordType": "part",
        }
        records.append(record)
    return records


def main() -> None:
    records: list[dict] = []
    scanned = 0
    for path in SOURCE_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".htm", ".html"} and "_files" in path.as_posix():
            scanned += 1
            records.extend(extract_sheet(path))
    dedup: dict[tuple, dict] = {}
    for item in records:
        key = (item["model"], item.get("yearFrom"), item.get("yearTo"), item["partNumber"], item["description"])
        if key not in dedup:
            dedup[key] = item
        else:
            merged = sorted(set(dedup[key].get("variants", [])) | set(item.get("variants", [])))
            dedup[key]["variants"] = merged
    items = sorted(dedup.values(), key=lambda x: (x["model"], str(x.get("yearFrom") or ""), x["category"], x["partNumber"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "market": "Australia",
        "brand": "Subaru",
        "sourceFilesScanned": scanned,
        "recordCount": len(items),
        "items": items,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(items)} Subaru accessory records from {scanned} sheet files to {OUTPUT}")


if __name__ == "__main__":
    main()

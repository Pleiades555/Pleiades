#!/usr/bin/env python3
"""Build a website-hosted Honda accessory JSON database from Excel-exported HTML sheets."""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ACCESSORIES = ROOT / "Honda" / "Accessories"
OUTPUT = ACCESSORIES / "data" / "accessories.json"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(clean("".join(self.cell)))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value).replace("\xa0", " ")).strip()


def infer_vehicle(rows: list[list[str]], path: Path) -> tuple[int | None, str, str]:
    text = " ".join(" ".join(r) for r in rows[:20]) + " " + path.stem
    year_match = re.search(r"(?:MY|YM)?\s*(20\d{2})|\b(\d{2})YM\b", text, re.I)
    year = None
    if year_match:
        token = next((g for g in year_match.groups() if g), None)
        if token:
            year = int(token) if len(token) == 4 else 2000 + int(token)
    model = "Civic" if re.search(r"Civic", text, re.I) else "Unknown"
    body = "Hatch" if re.search(r"Hatch", text, re.I) else "Sedan" if re.search(r"Sedan|4D", text, re.I) else "Unknown"
    return year, model, body


def parse_sheet(path: Path) -> list[dict]:
    parser = TableParser()
    parser.feed(path.read_text(encoding="windows-1252", errors="ignore"))
    rows = parser.rows
    year, model, body = infer_vehicle(rows, path)
    header = None
    category = "General"
    output: list[dict] = []

    for cells in rows:
        lower = [c.lower() for c in cells]
        if header is None and "part number" in lower:
            header = cells
            continue
        if not header:
            continue

        h = [c.lower() for c in header]
        try:
            pn_i = h.index("part number")
            desc_i = h.index("description")
        except ValueError:
            continue

        part = re.sub(r"\s+", "", cells[pn_i] if pn_i < len(cells) else "").upper()
        desc = cells[desc_i] if desc_i < len(cells) else ""
        notes = cells[desc_i + 1] if desc_i + 1 < len(cells) else ""
        populated = [c for c in cells if c]

        if not part and desc and len(populated) <= 2:
            category = desc
            continue
        if not re.fullmatch(r"[A-Z0-9-]{8,}", part) or not desc:
            continue

        variants: list[str] = []
        for name in ("VTi", "VTi-S", "VTi-L", "VTi-LX", "RS", "Petrol", "Hybrid"):
            try:
                idx = next(i for i, value in enumerate(header) if re.sub(r"\s+", "", value).lower() == re.sub(r"\s+", "", name).lower())
            except StopIteration:
                continue
            mark = cells[idx] if idx < len(cells) else ""
            if mark and mark not in {"-", "N/A", "n/a"}:
                variants.append(name)

        def by_header(fragment: str) -> str:
            idx = next((i for i, value in enumerate(h) if fragment in value), -1)
            return cells[idx] if idx >= 0 and idx < len(cells) else ""

        output.append({
            "year": year,
            "model": model,
            "body": body,
            "category": category,
            "partNumber": part,
            "description": desc,
            "notes": notes,
            "variants": variants,
            "frt": by_header("frt"),
            "listPrice": by_header("list price"),
            "fittedPrice": by_header("recommended fitted"),
            "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        })
    return output


def main() -> None:
    items: list[dict] = []
    for path in sorted(ACCESSORIES.glob("**/sheet*.html")):
        items.extend(parse_sheet(path))
    deduped = {f"{i['year']}|{i['model']}|{i['body']}|{i['partNumber']}|{','.join(i['variants'])}": i for i in items}
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "market": "Australia",
        "brand": "Honda",
        "items": sorted(deduped.values(), key=lambda i: (i.get("year") or 0, i["model"], i["body"], i["category"], i["partNumber"])),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['items'])} accessory records to {OUTPUT}")


if __name__ == "__main__":
    main()

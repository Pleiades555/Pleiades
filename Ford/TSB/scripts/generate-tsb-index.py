#!/usr/bin/env python3
"""Generate Ford TSB search index for Pleiades GitHub Pages.

Scans Ford/TSB/pdf and Ford/TSB/archive/superseded for PDF files.
Extracts TSB numbers, likely model/symptom, and supersession relationships.
Manual fixes can be added in Ford/TSB/data/manual-overrides.json.
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIRS = [TSB_ROOT / "pdf", TSB_ROOT / "archive" / "superseded"]
OUT = TSB_ROOT / "data" / "tsb-index.json"
OVERRIDES = TSB_ROOT / "data" / "manual-overrides.json"

TSB_RE = re.compile(r"\b(\d{2}[- ]?\d{3,5}|\d{2}S\d{2,5}|\d{2}B\d{2,5}|[A-Z]{1,4}[- ]?\d{2}[- ]?\d{3,5})\b", re.I)
MODEL_HINTS = ["Ranger", "Everest", "F-150", "F150", "Mustang", "Transit", "Escape", "Kuga", "Focus", "Fiesta", "Puma", "Explorer", "Bronco", "Falcon", "Territory", "Mondeo", "Endura", "EcoSport", "Maverick", "Super Duty"]
GEN_HINTS = ["PX", "PX1", "PX2", "PX3", "RA", "Next Gen", "T6", "LZ", "LW", "SZ", "FG", "FGX", "BA", "BF", "AU", "MY"]
ENGINE_RE = re.compile(r"\b(P5AT|P5BT|P4AT|P4BT|YN2S|CYR5|EcoBoost|PowerStroke|Duratorq|Panther|Lion|Coyote|Barra|2\.0L|2\.2L|3\.2L|3\.0L|5\.0L|V6|V8)\b", re.I)
TRANS_RE = re.compile(r"\b(10R80|10R60|6R80|6R60|MT82|6F35|ZF6|ZF|automatic|manual|transmission)\b", re.I)
SUPERSEDES_PATTERNS = [
    re.compile(r"(?:supersedes|replaces|replaced\s+by\s+this\s+bulletin|this\s+bulletin\s+replaces|this\s+article\s+supersedes)\s*(?:tsb|bulletin|article|ssm)?\s*[:#-]?\s*(" + TSB_RE.pattern[2:-2] + r")", re.I),
]
SUPERSEDED_BY_PATTERNS = [
    re.compile(r"(?:superseded\s+by|replaced\s+by)\s*(?:tsb|bulletin|article|ssm)?\s*[:#-]?\s*(" + TSB_RE.pattern[2:-2] + r")", re.I),
]


def read_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        chunks = []
        for page in reader.pages[:6]:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(chunks)
    except Exception:
        return ""


def normalise_tsb(value: str) -> str:
    value = (value or "").upper().replace(" ", "-")
    value = re.sub(r"--+", "-", value)
    return value.strip("- ")


def first_match(patterns, text):
    for pat in patterns:
        m = pat.search(text)
        if m:
            return normalise_tsb(m.group(1))
    return ""


def guess_model(text: str, name: str) -> str:
    source = f"{name} {text[:2000]}"
    hits = []
    for model in MODEL_HINTS:
        if re.search(r"\b" + re.escape(model) + r"\b", source, re.I):
            hits.append(model)
    return ", ".join(dict.fromkeys(hits)) or "Unknown"


def guess_generation(text: str, name: str) -> str:
    source = f"{name} {text[:1200]}"
    hits = []
    for gen in GEN_HINTS:
        if re.search(r"\b" + re.escape(gen) + r"\b", source, re.I):
            hits.append(gen)
    return ", ".join(dict.fromkeys(hits))


def guess_symptom(text: str, name: str, tsb: str, model: str) -> str:
    # Prefer explicit symptom/issue/condition lines from PDF text.
    for line in re.split(r"[\r\n]+", text[:3500]):
        line = re.sub(r"\s+", " ", line).strip()
        if re.search(r"\b(symptom|issue|condition|concern|customer concern|description)\b", line, re.I) and 12 <= len(line) <= 180:
            return line
    clean = Path(name).stem
    for bit in [tsb, model, "superseded", "archive", "bulletin", "tsb"]:
        clean = re.sub(re.escape(bit), " ", clean, flags=re.I)
    clean = re.sub(r"[_-]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean or "Unknown"


def load_overrides() -> Dict[str, Any]:
    if OVERRIDES.exists():
        return json.loads(OVERRIDES.read_text(encoding="utf-8"))
    return {}


def apply_override(item: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    keys = [item.get("tsbNumber", ""), item.get("fileName", ""), Path(item.get("file", "")).name]
    for key in keys:
        if key and key in overrides:
            item.update(overrides[key])
    return item


def scan() -> List[Dict[str, Any]]:
    overrides = load_overrides()
    items: List[Dict[str, Any]] = []
    for folder in PDF_DIRS:
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        for path in sorted(folder.rglob("*.pdf")):
            rel = path.relative_to(TSB_ROOT).as_posix()
            site_rel = "Ford/TSB/" + rel
            name = path.name
            text = read_pdf_text(path)
            combined = f"{name}\n{text}"
            tsb_match = TSB_RE.search(combined)
            tsb = normalise_tsb(tsb_match.group(1)) if tsb_match else ""
            supersedes = first_match(SUPERSEDES_PATTERNS, combined)
            superseded_by = first_match(SUPERSEDED_BY_PATTERNS, combined)
            in_archive = "archive/superseded" in rel.lower()
            name_sup = bool(re.search(r"\b(superseded|obsolete|old|archive|replaced)\b", rel, re.I))
            status = "Superseded" if in_archive or name_sup or superseded_by else "Current"
            engine = ", ".join(dict.fromkeys(m.group(1) for m in ENGINE_RE.finditer(combined)))
            trans = ", ".join(dict.fromkeys(m.group(1) for m in TRANS_RE.finditer(combined)))
            model = guess_model(text, name)
            item = {
                "tsbNumber": tsb,
                "bulletinNumber": tsb,
                "model": model,
                "vehicleGeneration": guess_generation(text, name),
                "engine": engine,
                "transmission": trans,
                "symptom": guess_symptom(text, name, tsb, model),
                "description": re.sub(r"\s+", " ", Path(name).stem).strip(),
                "status": status,
                "supersedes": supersedes,
                "supersededBy": superseded_by,
                "file": rel,
                "fileName": name,
                "textPreview": re.sub(r"\s+", " ", text[:1200]).strip(),
            }
            items.append(apply_override(item, overrides))

    # Cross-link: if a current item says it supersedes X, mark X as superseded by current item.
    by_tsb = {i.get("tsbNumber"): i for i in items if i.get("tsbNumber")}
    for item in items:
        old = item.get("supersedes")
        if old and old in by_tsb:
            by_tsb[old]["status"] = "Superseded"
            by_tsb[old]["supersededBy"] = item.get("tsbNumber") or by_tsb[old].get("supersededBy", "")
    return items


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    items = scan()
    OUT.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Indexed {len(items)} PDFs -> {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

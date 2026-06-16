#!/usr/bin/env python3
"""
Ford TSB auto-indexer for Pleiades.

What it does:
- Scans Ford/TSB/pdf and Ford/TSB/archive/superseded for PDFs.
- Extracts text from PDFs when possible.
- Detects TSB/SSM/recall/bulletin numbers, models, years, engines and symptoms.
- Detects supersession wording such as "supersedes", "replaces", "superseded by".
- Applies manual overrides from Ford/TSB/data/manual-overrides.json.
- Optionally moves superseded PDFs from pdf/ to archive/superseded/.
- Writes Ford/TSB/data/tsb-index.json for the website.

Local use:
  python Ford/TSB/scripts/generate-tsb-index.py

No hard failure if PDF extraction libraries are unavailable; filenames are still indexed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
OVERRIDES_FILE = DATA_DIR / "manual-overrides.json"
MOVE_SUPERSEDED = os.environ.get("MOVE_SUPERSEDED", "true").lower() in {"1", "true", "yes"}

MODELS = [
    "Ranger", "Everest", "F-150", "F150", "Mustang", "Transit", "Transit Custom", "Puma",
    "Escape", "Focus", "Fiesta", "Mondeo", "Endura", "Explorer", "Bronco", "Maverick",
    "Raptor", "Territory", "Falcon", "Kuga", "EcoSport", "Courier", "Capri"
]
ENGINES = [
    "P5AT", "P5BT", "P4AT", "PUMA", "EcoBoost", "PowerStroke", "Power Stroke", "Duratorq",
    "Duratec", "Barra", "Coyote", "Godzilla", "Lion", "Ingenium", "2.0L", "2.2L", "2.3L",
    "2.7L", "3.0L", "3.2L", "3.5L", "5.0L", "6.7L"
]
SYMPTOM_HINTS = [
    "battery drain", "no start", "hard start", "crank", "vibration", "shudder", "rattle", "knock",
    "noise", "leak", "oil leak", "coolant leak", "warning lamp", "MIL", "DTC", "transmission",
    "harsh shift", "rough idle", "stall", "misfire", "brake", "suspension", "steering", "clutch",
    "DPF", "AdBlue", "SCR", "EGR", "turbo", "overheat", "water ingress", "corrosion", "software",
    "calibration", "infotainment", "SYNC", "air conditioning", "A/C", "heater"
]

TSB_PATTERNS = [
    r"\b\d{2}-\d{4,5}\b",       # 25-2205
    r"\b\d{2}S\d{2,5}\b",        # 25S39
    r"\bSSM\s*\d{4,6}\b",        # SSM 52344
    r"\bTSB\s*\d{2}-\d{4,5}\b",  # TSB 25-2205
    r"\b\d{2}B\d{2,5}\b"
]

SUPERSEDES_PATTERNS = [
    r"(?:supersedes|supercedes|replaces|revised from|this bulletin replaces|this article supersedes)\s*(?:TSB|SSM|bulletin|article)?\s*[:#-]?\s*([A-Z0-9\- ]{4,18})",
]
SUPERSEDED_BY_PATTERNS = [
    r"(?:superseded by|superceded by|replaced by)\s*(?:TSB|SSM|bulletin|article)?\s*[:#-]?\s*([A-Z0-9\- ]{4,18})",
]


def normalise_doc_number(value: str) -> str:
    v = re.sub(r"\s+", "", value.upper())
    v = v.replace("TSB", "").strip(" :-_.,")
    if v.startswith("SSM"):
        return "SSM" + re.sub(r"\D", "", v[3:])
    return v


def first_doc_number(text: str, filename: str) -> str:
    joined = f"{filename}\n{text[:3000]}"
    for pat in TSB_PATTERNS:
        m = re.search(pat, joined, re.I)
        if m:
            return normalise_doc_number(m.group(0))
    return ""


def extract_pdf_text(path: Path) -> str:
    # Try PyMuPDF first because it is fast and usually reliable.
    try:
        import fitz  # type: ignore
        parts = []
        with fitz.open(path) as doc:
            for page in doc[:8]:
                parts.append(page.get_text("text") or "")
        return "\n".join(parts)
    except Exception:
        pass
    # Fallback to pypdf/PyPDF2 if available.
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:8])
    except Exception:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:8])
    except Exception:
        return ""


def uniq(items: List[str]) -> List[str]:
    seen: Set[str] = set(); out: List[str] = []
    for item in items:
        clean = str(item).strip(" ,;:.\n\t")
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key); out.append(clean)
    return out


def find_known_terms(text: str, terms: List[str]) -> List[str]:
    found = []
    for t in terms:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", text, re.I):
            found.append(t)
    return uniq(found)


def find_years(text: str) -> List[str]:
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    # Keep automotive-relevant years and avoid massive lists.
    return uniq([y for y in years if 1990 <= int(y) <= 2035])[:12]


def extract_title(text: str, name: str) -> str:
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines()]
    lines = [x for x in lines if len(x) >= 8 and not re.fullmatch(r"[0-9 /:.-]+", x)]
    for line in lines[:30]:
        if any(k in line.lower() for k in ["issue", "concern", "may exhibit", "condition", "service", "bulletin", "summary"]):
            return line[:180]
    return re.sub(r"[_-]+", " ", name).strip()[:180]


def extract_supersession(text: str) -> Dict[str, List[str]]:
    out = {"supersedes": [], "supersededBy": []}
    sample = text[:12000]
    for pat in SUPERSEDES_PATTERNS:
        for m in re.finditer(pat, sample, re.I):
            num = first_doc_number(m.group(1), m.group(1)) or normalise_doc_number(m.group(1))
            if num:
                out["supersedes"].append(num)
    for pat in SUPERSEDED_BY_PATTERNS:
        for m in re.finditer(pat, sample, re.I):
            num = first_doc_number(m.group(1), m.group(1)) or normalise_doc_number(m.group(1))
            if num:
                out["supersededBy"].append(num)
    out["supersedes"] = uniq(out["supersedes"])
    out["supersededBy"] = uniq(out["supersededBy"])
    return out


def document_type(num: str, text: str, filename: str) -> str:
    hay = f"{num} {filename} {text[:1500]}".lower()
    if num.startswith("SSM") or "special service message" in hay:
        return "SSM"
    if re.match(r"\d{2}s\d+", num.lower()) or "safety recall" in hay or "recall" in hay:
        return "Recall / Field Service Action"
    return "TSB"


def filename_guess(path: Path, doc_num: str) -> Dict[str, List[str] | str]:
    name = path.stem
    clean = re.sub(re.escape(doc_num), " ", name, flags=re.I) if doc_num else name
    clean = re.sub(r"[_-]+", " ", clean)
    return {
        "title": clean.strip(),
        "symptom": uniq([clean.strip()] if clean.strip() else [])
    }


def load_overrides() -> Dict[str, Any]:
    if not OVERRIDES_FILE.exists():
        return {"supersessions": {}, "metadata": {}}
    try:
        return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"supersessions": {}, "metadata": {}}


def scan_one(path: Path) -> Dict[str, Any]:
    rel = path.relative_to(TSB_ROOT).as_posix()
    site_file = rel
    text = extract_pdf_text(path)
    num = first_doc_number(text, path.name)
    full_text = f"{path.stem}\n{text}"
    file_guess = filename_guess(path, num)
    supers = extract_supersession(full_text)
    in_archive = "archive/superseded" in rel.lower()
    name_flags_sup = any(x in path.as_posix().lower() for x in ["superseded", "superseeded", "archive", "obsolete", "replaced"])
    item = {
        "tsbNumber": num,
        "bulletinNumber": num,
        "documentType": document_type(num, text, path.name),
        "title": extract_title(text, path.stem),
        "model": find_known_terms(full_text, MODELS),
        "years": find_years(full_text),
        "engine": find_known_terms(full_text, ENGINES),
        "symptom": uniq(find_known_terms(full_text, SYMPTOM_HINTS) + list(file_guess.get("symptom", []))),
        "supersedes": supers["supersedes"],
        "supersededBy": supers["supersededBy"],
        "status": "Superseded" if in_archive or name_flags_sup else "Current",
        "file": site_file,
        "archivedFrom": "",
        "sourceQuality": "PDF text extracted" if text else "Filename only - PDF text not extracted",
        "needsReview": False if text and num else True,
        "textPreview": re.sub(r"\s+", " ", text[:700]).strip(),
        "searchText": re.sub(r"\s+", " ", full_text[:6000]).strip(),
    }
    return item


def apply_overrides(items: List[Dict[str, Any]], overrides: Dict[str, Any]) -> None:
    by_num = {x.get("tsbNumber"): x for x in items if x.get("tsbNumber")}
    for old, new in overrides.get("supersessions", {}).items():
        oldn = normalise_doc_number(old); newn = normalise_doc_number(new)
        if oldn in by_num:
            by_num[oldn]["status"] = "Superseded"
            by_num[oldn]["supersededBy"] = uniq(listify(by_num[oldn].get("supersededBy")) + [newn])
        if newn in by_num:
            by_num[newn]["supersedes"] = uniq(listify(by_num[newn].get("supersedes")) + [oldn])
    for num, meta in overrides.get("metadata", {}).items():
        n = normalise_doc_number(num)
        if n in by_num and isinstance(meta, dict):
            for key, value in meta.items():
                by_num[n][key] = value
                by_num[n]["needsReview"] = False


def listify(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x]
    return [str(value)]


def cross_link_supersessions(items: List[Dict[str, Any]]) -> None:
    by_num = {x.get("tsbNumber"): x for x in items if x.get("tsbNumber")}
    for item in items:
        for old in listify(item.get("supersedes")):
            oldn = normalise_doc_number(old)
            if oldn in by_num and item.get("tsbNumber"):
                by_num[oldn]["status"] = "Superseded"
                by_num[oldn]["supersededBy"] = uniq(listify(by_num[oldn].get("supersededBy")) + [item["tsbNumber"]])
        for new in listify(item.get("supersededBy")):
            newn = normalise_doc_number(new)
            item["status"] = "Superseded"
            if newn in by_num and item.get("tsbNumber"):
                by_num[newn]["supersedes"] = uniq(listify(by_num[newn].get("supersedes")) + [item["tsbNumber"]])


def maybe_move_superseded(items: List[Dict[str, Any]]) -> bool:
    if not MOVE_SUPERSEDED:
        return False
    changed = False
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        if item.get("status") != "Superseded":
            continue
        rel = item.get("file", "")
        if not rel.startswith("pdf/"):
            continue
        src = TSB_ROOT / rel
        if not src.exists():
            continue
        dest = ARCHIVE_DIR / src.name
        if dest.exists() and dest.resolve() != src.resolve():
            stem, suffix = dest.stem, dest.suffix
            i = 2
            while dest.exists():
                dest = ARCHIVE_DIR / f"{stem}-{i}{suffix}"
                i += 1
        shutil.move(str(src), str(dest))
        item["archivedFrom"] = rel
        item["file"] = dest.relative_to(TSB_ROOT).as_posix()
        changed = True
    return changed


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))
    items = [scan_one(p) for p in paths]
    apply_overrides(items, load_overrides())
    cross_link_supersessions(items)
    moved = maybe_move_superseded(items)
    if moved:
        # Rescan moved files so paths/status are definitely correct.
        paths = sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))
        items = [scan_one(p) for p in paths]
        apply_overrides(items, load_overrides())
        cross_link_supersessions(items)
    items.sort(key=lambda x: (x.get("status") == "Superseded", str(x.get("tsbNumber") or x.get("title") or "")), reverse=False)
    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Indexed {len(items)} PDF(s) into {INDEX_FILE.relative_to(ROOT)}")

if __name__ == "__main__":
    main()

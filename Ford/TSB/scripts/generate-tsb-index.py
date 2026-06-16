import json
import re
import shutil
from pathlib import Path

try:
    import fitz
except ImportError:
    fitz = None

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
OVERRIDES_FILE = DATA_DIR / "manual-overrides.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

NUMBER_PATTERNS = [
    r"\b(?:TSB|SSM|FSA|FIELD SERVICE ACTION|BULLETIN|PROGRAM|RECALL)\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM[0-9]{4,6})\b",
    r"\b([0-9]{2}[- ][0-9]{4})\b",
    r"\b([0-9]{2}P[0-9]{2,5})\b",
    r"\b([0-9]{2}S[0-9]{2,5})\b",
    r"\b([0-9]{2}B[0-9]{2,5})\b",
    r"\b(SSM[0-9]{4,6})\b",
]

PROGRAM_NUMBER_RE = re.compile(
    r"\b(\d{2}[- ]\d{4}|\d{2}[A-Z]{1,3}\d{2,5}|SSM\d{4,6})\b",
    re.IGNORECASE,
)
YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:[-–—]|to|TO)\s*(19\d{2}|20\d{2})\b")
SINGLE_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

MODEL_WORDS = [
    "RANGER", "EVEREST", "MUSTANG", "FOCUS", "FIESTA", "MONDEO", "TERRITORY", "FALCON",
    "ESCAPE", "TRANSIT", "COURIER", "F-150", "F150", "F-250", "F250", "F-350", "F350",
    "BRONCO", "EXPLORER", "EDGE", "KUGA", "PUMA", "MAVERICK", "EXPEDITION", "ECOSPORT"
]
GENERATION_WORDS = ["PX1", "PX2", "PX3", "NEXT GEN", "NEXT-GEN", "RA", "PJ", "PK", "BA", "BF", "FG", "FG X"]
STOP_HEADINGS = [
    "ACTION", "SERVICE PROCEDURE", "PARTS REQUIREMENT", "PARTS REQUIRED", "WARRANTY STATUS",
    "LABOR ALLOWANCE", "LABOUR ALLOWANCE", "ATTACHMENTS", "DEALER CODING", "OWNER NOTIFICATION",
    "REPAIR FLOW CHART", "GENERAL INFORMATION", "NOTE:", "CAUTION:", "WARNING:", "PART NUMBER"
]
BAD_TITLE_STARTS = (
    "FORD MOTOR COMPANY", "TECHNICAL SERVICE BULLETIN", "SERVICE BULLETIN", "FIELD SERVICE ACTION",
    "CUSTOMER SATISFACTION PROGRAM", "PAGE ", "ISSUE DATE", "DATE", "MODEL", "YEAR", "VEHICLE", "VIN"
)

def clean_text(value):
    if not value:
        return ""
    value = re.sub(r"\s+", " ", str(value))
    return value.replace(" ,", ",").replace(" .", ".").strip(" -–—:|\t")

def normalise_number(value):
    value = clean_text(value).upper().replace(" ", "-")
    if re.fullmatch(r"\d{2}-\d{4}", value):
        return value
    value = value.replace("--", "-")
    return value

def read_pdf_text(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        pages = [page.get_text("text") for page in doc[:5]]
        doc.close()
        return "\n".join(pages)
    except Exception:
        return ""

def load_overrides():
    if not OVERRIDES_FILE.exists():
        return {}
    try:
        with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception:
        return {}

def find_number(filename, text):
    stem = Path(filename).stem
    for source in (stem, text[:3000]):
        for pattern in NUMBER_PATTERNS:
            match = re.search(pattern, source, re.IGNORECASE)
            if match:
                return normalise_number(match.group(1))
    return ""

def detect_type(number, text, filename):
    combined = f"{number} {filename} {text[:1500]}".upper()
    if re.search(r"\bFSA\b|FIELD SERVICE ACTION|CUSTOMER SATISFACTION PROGRAM|\d{2}P\d{2,5}", combined):
        return "FSA"
    if re.search(r"\bSSM\d{4,6}\b|SPECIAL SERVICE MESSAGE", combined):
        return "SSM"
    if re.search(r"\bRECALL\b|\d{2}S\d{2,5}", combined):
        return "Recall"
    return "TSB"

def find_years(text, filename):
    combined = f"{filename}\n{text[:5000]}"
    ranges = [f"{a}-{b}" for a, b in YEAR_RANGE_RE.findall(combined)]
    if ranges:
        return sorted(set(ranges))
    years = [y for y in SINGLE_YEAR_RE.findall(combined) if 1980 <= int(y) <= 2035]
    return sorted(set(years))[:8]

def find_models(text, filename):
    combined = f"{filename}\n{text[:4000]}".upper()
    found = []
    for model in MODEL_WORDS:
        if re.search(rf"\b{re.escape(model)}\b", combined):
            fixed = model.replace("F150", "F-150").replace("F250", "F-250").replace("F350", "F-350")
            if fixed.title() not in found:
                found.append(fixed.title())
    for gen in GENERATION_WORDS:
        if re.search(rf"\b{re.escape(gen)}\b", combined):
            gen = gen.replace("-", " ")
            if gen not in found:
                found.append(gen)
    return ", ".join(found)

def extract_title_from_lines(text, filename):
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]
    candidates = []
    for line in lines[:90]:
        upper = line.upper()
        if len(line) < 8 or any(upper.startswith(x) for x in BAD_TITLE_STARTS):
            continue
        if PROGRAM_NUMBER_RE.fullmatch(line) or re.fullmatch(r"[0-9 /\-–—]+", line):
            continue
        candidates.append(line)
        if len(candidates) >= 2:
            break
    if candidates:
        return clean_text(" - ".join(candidates))[:220]
    fallback = re.sub(PROGRAM_NUMBER_RE, "", Path(filename).stem)
    return clean_text(fallback.replace("_", " ").replace("-", " ").title())[:220]

def paragraph_after_label(text, labels):
    lines = [clean_text(x) for x in text.splitlines()]
    lines = [x for x in lines if x]
    for i, line in enumerate(lines):
        upper = line.upper()
        captured = None
        for label in labels:
            if upper.startswith(label.upper()):
                captured = clean_text(line[len(label):]).lstrip(":-–— ")
                break
        if captured is None:
            continue
        parts = [captured] if captured else []
        for nxt in lines[i + 1:i + 8]:
            nu = nxt.upper().strip()
            if any(nu.startswith(stop) for stop in STOP_HEADINGS):
                break
            if re.fullmatch(r"[A-Z][A-Z /&-]{3,30}:?", nu):
                break
            parts.append(nxt)
            if len(" ".join(parts)) > 420:
                break
        result = clean_text(" ".join(parts))
        if len(result) > 8:
            return result[:500]
    return ""

def find_title(text, filename):
    labelled = paragraph_after_label(text, ["Title:", "Subject:"])
    if labelled:
        return labelled[:220]
    return extract_title_from_lines(text, filename)

def find_concern(text, filename, title):
    concern = paragraph_after_label(text, [
        "Issue:", "Concern:", "Condition:", "Symptom:", "Customer Concern:", "Customer Symptom:",
        "Reason For This Program:", "Reason:"
    ])
    return concern or title or clean_text(Path(filename).stem)

def find_supersession(text):
    supersedes, superseded_by = [], []
    pat_old = r"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM[0-9]{4,6})"
    pat_new = r"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM[0-9]{4,6})"
    for m in re.findall(pat_old, text, re.IGNORECASE):
        supersedes.append(normalise_number(m))
    for m in re.findall(pat_new, text, re.IGNORECASE):
        superseded_by.append(normalise_number(m))
    return sorted(set(supersedes)), sorted(set(superseded_by))

def apply_manual_overrides(item, overrides):
    number = item.get("number", "")
    if number in overrides and isinstance(overrides[number], dict):
        item.update(overrides[number])
        if "number" in overrides[number]:
            item["number"] = normalise_number(overrides[number]["number"])
    return item

def build_item(path, overrides):
    rel_path = path.relative_to(ROOT).as_posix()
    filename = path.name
    text = read_pdf_text(path)
    number = find_number(filename, text)
    title = find_title(text, filename)
    concern = find_concern(text, filename, title)
    years = find_years(text, filename)
    model = find_models(text, filename)
    supersedes, superseded_by = find_supersession(text)
    is_archived = "archive/superseded" in rel_path.lower()
    status = "Superseded" if is_archived or any(w in filename.lower() for w in ["superseded", "obsolete", "replaced"]) else "Current"

    item = {
        "number": number,
        "tsbNumber": number,
        "bulletinNumber": number,
        "type": detect_type(number, text, filename),
        "title": title,
        "model": model,
        "years": years,
        "yearRange": ", ".join(years),
        "symptom": concern,
        "concern": concern,
        "description": concern,
        "status": status,
        "supersedes": supersedes,
        "supersededBy": superseded_by,
        "file": rel_path,
        "filename": filename,
    }
    item = apply_manual_overrides(item, overrides)
    clean_number = normalise_number(item.get("number", ""))
    item["number"] = clean_number
    item["tsbNumber"] = clean_number
    item["bulletinNumber"] = clean_number
    item["displayNumber"] = clean_number or item.get("filename", "Unknown")
    item["searchText"] = clean_text(" ".join(str(item.get(k, "")) for k in [
        "number", "type", "title", "model", "yearRange", "symptom", "status", "filename"
    ])).lower()
    return item

def collect_pdfs():
    return sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))

def apply_supersession_links(items):
    by_number = {item.get("number"): item for item in items if item.get("number")}
    for item in items:
        current = item.get("number", "")
        for old in item.get("supersedes", []):
            old_item = by_number.get(old)
            if old_item:
                old_item["status"] = "Superseded"
                old_item["supersededBy"] = current
        if item.get("supersededBy"):
            item["status"] = "Superseded"
    return items

def move_superseded_files(items):
    moved = False
    for item in items:
        if item.get("status") != "Superseded":
            continue
        source = ROOT / item["file"]
        if not source.exists() or ARCHIVE_DIR in source.parents:
            continue
        destination = ARCHIVE_DIR / source.name
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved = True
    return moved

def main():
    overrides = load_overrides()
    items = [build_item(path, overrides) for path in collect_pdfs()]
    items = apply_supersession_links(items)
    move_superseded_files(items)
    items = [build_item(path, overrides) for path in collect_pdfs()]
    items = apply_supersession_links(items)
    items.sort(key=lambda x: (x.get("status") == "Superseded", x.get("type", ""), x.get("number", ""), x.get("title", "")))
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(items)} Ford TSB index entries at {INDEX_FILE}")

if __name__ == "__main__":
    main()

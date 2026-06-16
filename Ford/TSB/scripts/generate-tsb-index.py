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

PROGRAM_NUMBER_RE = re.compile(
    r"\b("
    r"\d{2}[- ]?\d{4}"
    r"|"
    r"\d{2}[A-Z]\d{2,5}"
    r"|"
    r"\d{2}[A-Z]{1,3}\d{2,5}"
    r"|"
    r"[A-Z]{2,4}\d{4,6}"
    r")\b",
    re.IGNORECASE,
)

YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:[-–—]|to|TO)\s*(19\d{2}|20\d{2})\b")
SINGLE_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

MODEL_WORDS = [
    "RANGER", "EVEREST", "MUSTANG", "FOCUS", "FIESTA", "MONDEO", "TERRITORY", "FALCON",
    "ESCAPE", "TRANSIT", "COURIER", "F-150", "F150", "F-250", "F250", "F-350", "F350",
    "BRONCO", "EXPLORER", "EDGE", "KUGA", "PUMA", "MAVERICK", "EXPEDITION", "ECOSPORT",
]

STOP_HEADINGS = [
    "ACTION", "SERVICE PROCEDURE", "PARTS REQUIREMENT", "PARTS REQUIRED", "WARRANTY STATUS",
    "LABOR ALLOWANCE", "LABOUR ALLOWANCE", "ATTACHMENTS", "DEALER CODING", "OWNER NOTIFICATION",
    "REPAIR FLOW CHART", "GENERAL INFORMATION", "NOTE:", "CAUTION:", "WARNING:",
]

BAD_TITLE_STARTS = (
    "FORD MOTOR COMPANY", "TECHNICAL SERVICE BULLETIN", "SERVICE BULLETIN", "FIELD SERVICE ACTION",
    "CUSTOMER SATISFACTION PROGRAM", "PAGE ", "ISSUE DATE", "DATE", "MODEL", "YEAR", "VEHICLE", "VIN",
)


def clean_text(value):
    if not value:
        return ""
    value = re.sub(r"\s+", " ", str(value))
    value = value.replace(" ,", ",").replace(" .", ".")
    return value.strip(" -–—:|")


def read_pdf_text(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        pages = [page.get_text("text") for page in doc[:6]]
        doc.close()
        return "\n".join(pages)
    except Exception:
        return ""


def load_overrides():
    if not OVERRIDES_FILE.exists():
        return {}
    try:
        with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def find_number(filename, text):
    combined = f"{filename}\n{text[:4000]}"
    preferred_patterns = [
        r"\b(?:TSB|SSM|FSA|FIELD SERVICE ACTION|BULLETIN|PROGRAM)\s*[:#-]?\s*([0-9]{2}[A-Z]{0,3}[0-9]{2,5}|[0-9]{2}[- ][0-9]{4}|[A-Z]{2,4}[0-9]{4,6})\b",
        r"\b([0-9]{2}P[0-9]{2,5})\b",
        r"\b([0-9]{2}S[0-9]{2,5})\b",
        r"\b([0-9]{2}B[0-9]{2,5})\b",
        r"\b([0-9]{2}[- ][0-9]{4})\b",
        r"\b(SSM[0-9]{4,6})\b",
    ]
    for pattern in preferred_patterns:
        match = re.search(pattern, combined, re.IGNORECASE)
        if match:
            return match.group(1).replace(" ", "-").upper()
    match = PROGRAM_NUMBER_RE.search(combined)
    return match.group(1).replace(" ", "-").upper() if match else ""


def find_years(text, filename):
    combined = f"{filename}\n{text[:6000]}"
    ranges = [f"{start}-{end}" for start, end in YEAR_RANGE_RE.findall(combined)]
    if ranges:
        return sorted(set(ranges))
    years = [y for y in SINGLE_YEAR_RE.findall(combined) if 1980 <= int(y) <= 2035]
    return sorted(set(years))[:10]


def find_models(text, filename):
    combined = f"{filename}\n{text[:5000]}".upper()
    found = []
    for model in MODEL_WORDS:
        if re.search(rf"\b{re.escape(model)}\b", combined):
            model_name = model.replace("F150", "F-150").replace("F250", "F-250").replace("F350", "F-350").title()
            if model_name not in found:
                found.append(model_name)
    for pattern in [r"\bPX1\b", r"\bPX2\b", r"\bPX3\b", r"\bNEXT[- ]GEN\b", r"\bRA\b", r"\bPJ\b", r"\bPK\b", r"\bFG X\b", r"\bFG\b", r"\bBA\b", r"\bBF\b"]:
        match = re.search(pattern, combined)
        if match:
            gen = match.group(0).replace("-", " ")
            if gen not in found:
                found.append(gen)
    return ", ".join(found)


def extract_title_from_lines(lines):
    useful = []
    for raw in lines[:90]:
        line = clean_text(raw)
        if len(line) < 8:
            continue
        upper = line.upper()
        if any(upper.startswith(x) for x in BAD_TITLE_STARTS):
            continue
        if PROGRAM_NUMBER_RE.fullmatch(line):
            continue
        if re.fullmatch(r"[0-9 /\-–—]+", line):
            continue
        useful.append(line)
        if len(useful) >= 2:
            break
    return clean_text(" - ".join(useful))


def find_title(text, filename):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    for pattern in [r"(?:TITLE|SUBJECT)\s*[:\-–]\s*(.+)", r"(?:ISSUE|CONCERN)\s*[:\-–]\s*(.+)"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = clean_text(match.group(1))
            if len(title) > 8:
                return title[:260]
    title = extract_title_from_lines(lines)
    if title:
        return title[:260]
    fallback = Path(filename).stem
    fallback = re.sub(PROGRAM_NUMBER_RE, "", fallback)
    return clean_text(fallback.replace("_", " ").replace("-", " ").title())


def paragraph_after_label(text, labels):
    lines = [clean_text(x) for x in text.splitlines()]
    lines = [x for x in lines if x]
    for i, line in enumerate(lines):
        upper = line.upper()
        matched = False
        captured = ""
        for label in labels:
            label_upper = label.upper()
            if upper.startswith(label_upper):
                matched = True
                captured = clean_text(line[len(label):]).lstrip(":-–— ")
                break
        if not matched:
            continue
        parts = []
        if captured:
            parts.append(captured)
        for next_line in lines[i + 1:i + 10]:
            next_upper = next_line.upper().strip()
            if any(next_upper.startswith(stop) for stop in STOP_HEADINGS):
                break
            if re.fullmatch(r"[A-Z][A-Z /&-]{3,35}:?", next_upper):
                break
            parts.append(next_line)
            if len(" ".join(parts)) > 600:
                break
        result = clean_text(" ".join(parts))
        if len(result) > 8:
            return result[:700]
    return ""


def find_concern(text, filename, title):
    concern = paragraph_after_label(text, [
        "Issue:", "Concern:", "Condition:", "Symptom:", "Customer Concern:", "Customer Symptom:",
        "Reason For This Program:", "Reason:", "Summary:", "Description:",
    ])
    if concern:
        return concern
    if title:
        return clean_text(title)[:700]
    fallback = Path(filename).stem
    fallback = re.sub(PROGRAM_NUMBER_RE, "", fallback)
    return clean_text(fallback.replace("_", " ").replace("-", " ").title())


def find_supersession(text):
    supersedes = []
    superseded_by = []
    number_pat = r"([0-9]{2}[A-Z]{0,3}[0-9]{2,5}|[0-9]{2}[- ][0-9]{4}|[A-Z]{2,4}[0-9]{4,6})"
    for match in re.findall(rf"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{number_pat}", text, re.IGNORECASE):
        supersedes.append(match.replace(" ", "-").upper())
    for match in re.findall(rf"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{number_pat}", text, re.IGNORECASE):
        superseded_by.append(match.replace(" ", "-").upper())
    return sorted(set(supersedes)), sorted(set(superseded_by))


def detect_type(number, text, filename):
    combined = f"{number} {filename} {text[:1800]}".upper()
    if re.search(r"\bFSA\b|FIELD SERVICE ACTION|CUSTOMER SATISFACTION PROGRAM|\d{2}P\d{2,5}", combined):
        return "FSA"
    if re.search(r"\bSSM\d{4,6}\b|SPECIAL SERVICE MESSAGE", combined):
        return "SSM"
    if re.search(r"\bRECALL\b|\d{2}S\d{2,5}", combined):
        return "Recall"
    return "TSB"


def apply_manual_overrides(item, overrides):
    number = item.get("number", "")
    for source in [overrides.get("_global", {}), overrides.get(number, {})]:
        for key, value in source.items():
            item[key] = value
    return item


def collect_pdfs():
    files = []
    for folder in [PDF_DIR, ARCHIVE_DIR]:
        files.extend(folder.rglob("*.pdf"))
    return sorted(files)


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
    filename_lower = filename.lower()
    status = "Superseded" if is_archived or "superseded" in filename_lower or "obsolete" in filename_lower else "Current"
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
        "searchText": "",
    }
    item = apply_manual_overrides(item, overrides)
    item["searchText"] = clean_text(" ".join([
        item.get("number", ""), item.get("type", ""), item.get("title", ""), item.get("model", ""),
        item.get("yearRange", ""), item.get("symptom", ""), item.get("status", ""), item.get("filename", ""),
    ])).lower()
    return item


def apply_supersession_links(items):
    by_number = {item.get("number"): item for item in items if item.get("number")}
    for item in items:
        current_number = item.get("number", "")
        for old_number in item.get("supersedes", []):
            old_item = by_number.get(old_number)
            if old_item:
                old_item["status"] = "Superseded"
                old_item["supersededBy"] = current_number
        if item.get("supersededBy"):
            item["status"] = "Superseded"
    return items


def move_superseded_files(items):
    for item in items:
        if item.get("status") != "Superseded":
            continue
        source = ROOT / item["file"]
        if not source.exists() or ARCHIVE_DIR in source.parents:
            continue
        destination = ARCHIVE_DIR / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            continue
        shutil.move(str(source), str(destination))
        item["file"] = destination.relative_to(ROOT).as_posix()


def generate_items(overrides):
    return apply_supersession_links([build_item(path, overrides) for path in collect_pdfs()])


def main():
    overrides = load_overrides()
    items = generate_items(overrides)
    move_superseded_files(items)
    items = generate_items(overrides)
    items.sort(key=lambda x: (x.get("status") == "Superseded", x.get("number", ""), x.get("title", "")))
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(items)} Ford TSB index entries at {INDEX_FILE}")


if __name__ == "__main__":
    main()

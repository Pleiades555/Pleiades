import json
import re
import shutil
from datetime import datetime
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
OVERRIDES_FILE = DATA_DIR / "manual-overrides.json"
PARTS_FILE = DATA_DIR / "manual-parts.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

for file_path, default in [(OVERRIDES_FILE, {}), (PARTS_FILE, {})]:
    if not file_path.exists():
        file_path.write_text(json.dumps(default, indent=2), encoding="utf-8")

NUMBER_PATTERNS = [
    r"\b(?:TSB|SSM|FSA|FIELD SERVICE ACTION|BULLETIN|PROGRAM|RECALL|FAB)\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,6}|FAB[0-9]{6,8}|SSM[0-9]{4,6})\b",
    r"\b(FAB[0-9]{6,8})\b",
    r"\b([0-9]{2}[- ][0-9]{4})\b",
    r"\b([0-9]{2}P[0-9]{2,6})\b",
    r"\b([0-9]{2}S[0-9]{2,6})\b",
    r"\b([0-9]{2}B[0-9]{2,6})\b",
    r"\b(SSM[0-9]{4,6})\b",
]
PROGRAM_NUMBER_RE = re.compile(r"\b(\d{2}[- ]\d{4}|\d{2}[A-Z]{1,3}\d{2,6}|FAB\d{6,8}|SSM\d{4,6})\b", re.IGNORECASE)
YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:[-–—]|to|TO)\s*(19\d{2}|20\d{2})\b")
SINGLE_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b")

MODEL_WORDS = [
    "RANGER", "EVEREST", "MUSTANG", "FOCUS", "FIESTA", "MONDEO", "TERRITORY", "FALCON",
    "ESCAPE", "TRANSIT", "TRANSIT VO", "COURIER", "F-150", "F150", "F-250", "F250",
    "F-350", "F350", "BRONCO", "EXPLORER", "EDGE", "KUGA", "PUMA", "MAVERICK",
    "EXPEDITION", "ECOSPORT"
]
GENERATION_WORDS = ["PX1", "PX2", "PX3", "NEXT GEN", "NEXT-GEN", "VO", "RA", "PJ", "PK", "BA", "BF", "FG", "FG X"]
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
    if value is None:
        return ""
    value = re.sub(r"\s+", " ", str(value))
    return value.replace(" ,", ",").replace(" .", ".").strip(" -–—:|\t")


def normalise_number(value):
    value = clean_text(value).upper()
    value = value.replace(" ", "-")
    value = value.replace("--", "-")
    return value


def read_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Could not read {path}: {exc}")
    return default


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_pdf_text(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        pages = [page.get_text("text") for page in doc[:5]]
        doc.close()
        return "\n".join(pages)
    except Exception as exc:
        print(f"Could not read PDF {path}: {exc}")
        return ""


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
    if "FAB" in number or re.search(r"\bFSA\b|FIELD SERVICE ACTION|CUSTOMER SATISFACTION PROGRAM|\d{2}P\d{2,6}", combined):
        return "FSA"
    if re.search(r"\bSSM\d{4,6}\b|SPECIAL SERVICE MESSAGE", combined):
        return "SSM"
    if re.search(r"\bRECALL\b|\d{2}S\d{2,6}", combined):
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
            display = fixed.title().replace("Vo", "VO")
            if display not in found:
                found.append(display)
    for gen in GENERATION_WORDS:
        if re.search(rf"\b{re.escape(gen)}\b", combined):
            display = gen.replace("-", " ")
            if display not in found:
                found.append(display)
    return ", ".join(found)


def paragraph_after_label(text, labels, max_lines=8, max_chars=500):
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
        for nxt in lines[i + 1:i + 1 + max_lines]:
            nu = nxt.upper().strip()
            if any(nu.startswith(stop) for stop in STOP_HEADINGS):
                break
            if re.fullmatch(r"[A-Z][A-Z /&-]{3,30}:?", nu):
                break
            parts.append(nxt)
            if len(" ".join(parts)) > max_chars:
                break
        result = clean_text(" ".join(parts))
        if len(result) > 8:
            return result[:max_chars]
    return ""


def find_title(text, filename):
    labelled = paragraph_after_label(text, ["Title:", "Subject:"], max_lines=3, max_chars=220)
    if labelled:
        return labelled
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


def find_concern(text, filename, title):
    concern = paragraph_after_label(
        text,
        ["Issue:", "Concern:", "Condition:", "Symptom:", "Customer Concern:", "Customer Symptom:", "Reason For This Program:", "Reason:"],
        max_lines=8,
        max_chars=500,
    )
    return concern or title or clean_text(Path(filename).stem)


def parse_date(value):
    if not value:
        return ""
    raw = clean_text(value)
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%y", "%d-%m-%y"]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return raw


def find_date_after_labels(text, labels):
    for label in labels:
        pattern = rf"{re.escape(label)}\s*[:\-–—]?\s*(\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}|\d{{4}}[/-]\d{{1,2}}[/-]\d{{1,2}})"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return parse_date(match.group(1))
    return ""


def find_supersession(text):
    supersedes, superseded_by = [], []
    old_pattern = r"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,6}|FAB[0-9]{6,8}|SSM[0-9]{4,6})"
    new_pattern = r"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}[- ][0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,6}|FAB[0-9]{6,8}|SSM[0-9]{4,6})"
    for match in re.findall(old_pattern, text, re.IGNORECASE):
        supersedes.append(normalise_number(match))
    for match in re.findall(new_pattern, text, re.IGNORECASE):
        superseded_by.append(normalise_number(match))
    return sorted(set(supersedes)), sorted(set(superseded_by))


def apply_manual_overrides(item, overrides):
    number = item.get("number", "")
    override = overrides.get(number, {})
    if isinstance(override, dict):
        item.update(override)
    clean_number = normalise_number(item.get("number") or number)
    item["number"] = clean_number
    item["tsbNumber"] = clean_number
    item["bulletinNumber"] = clean_number
    item["displayNumber"] = clean_number or item.get("filename", "Manual Entry")
    return item


def build_item_from_pdf(path, overrides):
    rel_path = path.relative_to(ROOT).as_posix()
    filename = path.name
    text = read_pdf_text(path)
    number = find_number(filename, text)
    title = find_title(text, filename)
    concern = find_concern(text, filename, title)
    years = find_years(text, filename)
    supersedes, superseded_by = find_supersession(text)
    issue_date = find_date_after_labels(text, ["Issue Date", "Date", "Publication Date", "Published Date"])
    ford_upload_date = find_date_after_labels(text, ["Date Uploaded by Ford", "Upload Date", "Release Date", "Publication Date", "Published Date"])
    status = "Superseded" if "archive/superseded" in rel_path.lower() or any(w in filename.lower() for w in ["superseded", "obsolete", "replaced"]) else "Current"
    item = {
        "number": number,
        "tsbNumber": number,
        "bulletinNumber": number,
        "displayNumber": number or filename,
        "type": detect_type(number, text, filename),
        "title": title,
        "model": find_models(text, filename),
        "years": years,
        "yearRange": ", ".join(years),
        "fordUploadDate": ford_upload_date,
        "issueDate": issue_date,
        "symptom": concern,
        "concern": concern,
        "description": concern,
        "status": status,
        "supersedes": supersedes,
        "supersededBy": superseded_by,
        "file": rel_path,
        "filename": filename,
        "manualOnly": False,
    }
    return finish_item(apply_manual_overrides(item, overrides))


def build_manual_only_item(number, override):
    clean_number = normalise_number(number)
    item = {
        "number": clean_number,
        "tsbNumber": clean_number,
        "bulletinNumber": clean_number,
        "displayNumber": clean_number,
        "type": override.get("type") or detect_type(clean_number, "", ""),
        "title": override.get("title", "Manual bulletin entry"),
        "model": override.get("model", ""),
        "years": override.get("years", []),
        "yearRange": override.get("yearRange", ""),
        "fordUploadDate": override.get("fordUploadDate", ""),
        "issueDate": override.get("issueDate", ""),
        "symptom": override.get("symptom") or override.get("concern", ""),
        "concern": override.get("concern") or override.get("symptom", ""),
        "description": override.get("description") or override.get("concern") or override.get("symptom", ""),
        "status": override.get("status", "Current"),
        "supersedes": override.get("supersedes", []),
        "supersededBy": override.get("supersededBy", ""),
        "file": override.get("file", ""),
        "filename": override.get("filename", "Manual override only"),
        "manualOnly": True,
    }
    item.update(override)
    item["number"] = clean_number
    item["tsbNumber"] = clean_number
    item["bulletinNumber"] = clean_number
    item["displayNumber"] = clean_number
    return finish_item(item)



def normalise_parts_payload(payload):
    if not isinstance(payload, dict):
        return {"staticParts": [], "variants": {}}
    static_parts = payload.get("staticParts") or payload.get("static") or payload.get("bulletinParts") or []
    variants = payload.get("variants") or payload.get("variantParts") or {}
    if not isinstance(static_parts, list):
        static_parts = []
    if not isinstance(variants, dict):
        variants = {}
    cleaned_static = [clean_part_row(x) for x in static_parts if isinstance(x, dict)]
    cleaned_variants = {}
    for variant, rows in variants.items():
        if not isinstance(rows, list):
            continue
        cleaned_rows = [clean_part_row(x) for x in rows if isinstance(x, dict)]
        if cleaned_rows:
            cleaned_variants[str(variant)] = cleaned_rows
    return {"staticParts": cleaned_static, "variants": cleaned_variants}


def clean_part_row(row):
    part_number = clean_text(row.get("partNumber") or row.get("part") or row.get("number") or "").upper()
    qty = clean_text(row.get("qty") or row.get("quantity") or "1")
    description = clean_text(row.get("description") or row.get("desc") or "")
    note = clean_text(row.get("note") or "")
    return {"partNumber": part_number, "qty": qty, "quantity": qty, "description": description, "note": note}


def get_manual_parts_for_number(number, parts):
    clean_number = normalise_number(number)
    if not clean_number:
        return {"staticParts": [], "variants": {}}
    for key, value in parts.items():
        if normalise_number(key) == clean_number:
            return normalise_parts_payload(value)
    return {"staticParts": [], "variants": {}}


def attach_manual_parts(item, parts):
    part_payload = get_manual_parts_for_number(item.get("number") or item.get("displayNumber"), parts)
    item["parts"] = part_payload
    item["hasManualParts"] = bool(part_payload.get("staticParts") or part_payload.get("variants"))
    return item

def finish_item(item):
    number = normalise_number(item.get("number", ""))
    item["number"] = number
    item["tsbNumber"] = number
    item["bulletinNumber"] = number
    item["displayNumber"] = number or item.get("filename", "Unknown")
    item["type"] = item.get("type") or detect_type(number, "", item.get("filename", ""))
    if isinstance(item.get("years"), str):
        item["years"] = [item["years"]] if item["years"] else []
    if not item.get("yearRange") and item.get("years"):
        item["yearRange"] = ", ".join(item.get("years", []))
    if item.get("fordUploadDate"):
        item["fordUploadDate"] = parse_date(item.get("fordUploadDate"))
    if item.get("issueDate"):
        item["issueDate"] = parse_date(item.get("issueDate"))
    item["searchText"] = clean_text(" ".join(str(item.get(k, "")) for k in [
        "number", "type", "title", "model", "yearRange", "fordUploadDate", "issueDate", "symptom", "status", "filename"
    ])).lower()
    return item


def collect_pdfs():
    return sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))


def apply_supersession_links(items):
    by_number = {item.get("number"): item for item in items if item.get("number")}
    for item in items:
        current = item.get("number", "")
        normalised_supersedes = []
        for old in item.get("supersedes", []) or []:
            old_clean = normalise_number(old)
            if old_clean and old_clean not in normalised_supersedes:
                normalised_supersedes.append(old_clean)
            old_item = by_number.get(old_clean)
            if old_item:
                old_item["status"] = "Superseded"
                old_item["supersededBy"] = current
        item["supersedes"] = normalised_supersedes
        sb = item.get("supersededBy")
        if isinstance(sb, list):
            item["supersededBy"] = [normalise_number(x) for x in sb if normalise_number(x)]
        elif sb:
            item["supersededBy"] = normalise_number(sb)
        else:
            item["supersededBy"] = ""
        if item.get("supersededBy"):
            item["status"] = "Superseded"
        item["supersessionLinks"] = {
            "supersedes": item.get("supersedes", []),
            "supersededBy": item.get("supersededBy", ""),
        }
    return items


def move_superseded_files(items):
    moved = False
    for item in items:
        if item.get("status") != "Superseded" or item.get("manualOnly"):
            continue
        source = ROOT / item.get("file", "")
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
    overrides = read_json(OVERRIDES_FILE, {})
    parts = read_json(PARTS_FILE, {})
    write_json(PARTS_FILE, parts)
    write_json(OVERRIDES_FILE, overrides)

    items = [attach_manual_parts(build_item_from_pdf(path, overrides), parts) for path in collect_pdfs()]
    existing_numbers = {item.get("number") for item in items if item.get("number")}

    for number, override in overrides.items():
        if str(number).startswith("_") or not isinstance(override, dict):
            continue
        clean_number = normalise_number(number)
        if clean_number not in existing_numbers:
            items.append(attach_manual_parts(build_manual_only_item(clean_number, override), parts))

    items = apply_supersession_links(items)
    move_superseded_files(items)

    items = [attach_manual_parts(build_item_from_pdf(path, overrides), parts) for path in collect_pdfs()]
    existing_numbers = {item.get("number") for item in items if item.get("number")}
    for number, override in overrides.items():
        if str(number).startswith("_") or not isinstance(override, dict):
            continue
        clean_number = normalise_number(number)
        if clean_number not in existing_numbers:
            items.append(attach_manual_parts(build_manual_only_item(clean_number, override), parts))

    items = apply_supersession_links(items)
    items.sort(key=lambda x: (
        x.get("status") == "Superseded",
        x.get("fordUploadDate", ""),
        x.get("type", ""),
        x.get("number", ""),
    ), reverse=True)

    write_json(INDEX_FILE, items)
    print(f"Generated {len(items)} Ford TSB index entries at {INDEX_FILE}")


if __name__ == "__main__":
    main()

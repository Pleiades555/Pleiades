import json
import re
import shutil
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
OVERRIDES_FILE = DATA_DIR / "manual-overrides.json"

for folder in (PDF_DIR, ARCHIVE_DIR, DATA_DIR):
    folder.mkdir(parents=True, exist_ok=True)

# Ford identifiers handled:
# 26-2159, 262159, 23P23, 25SD9, 25S39, S1406, 14M02, SSM52344, FSA 23P23
NUMBER_PATTERNS = [
    r"\b(\d{2}\s*-\s*\d{4})\b",
    r"\b(\d{6})\b",
    r"\b(\d{2}[A-Z]{1,3}\d{1,5})\b",
    r"\b([A-Z]\d{4,6})\b",
    r"\b(SSM\s*\d{4,6})\b",
    r"\b(FSA\s*\d{2}[A-Z]{1,3}\d{1,5})\b",
]
NUMBER_RE = re.compile("|".join(NUMBER_PATTERNS), re.IGNORECASE)

YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:[-–—]|to|TO)\s*(19\d{2}|20\d{2})\b")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

MODELS = [
    "Transit Custom", "Transit Courier", "Mustang Mach-E", "Mach-E",
    "Ranger", "Everest", "Mustang", "Focus", "Fiesta", "Mondeo", "Territory",
    "Falcon", "Escape", "Transit", "Courier", "F-150", "F150", "F-250", "F250",
    "F-350", "F350", "Bronco", "Explorer", "Edge", "Kuga", "Puma", "Maverick",
    "Expedition", "EcoSport",
]
GENS = ["PX1", "PX2", "PX3", "Next Gen", "Next-Gen", "RA", "PJ", "PK", "BA", "BF", "FG", "FG X", "SZ", "UA", "UB"]

STOP_HEADINGS = [
    "ACTION", "SERVICE PROCEDURE", "PARTS REQUIREMENT", "PARTS REQUIRED", "PARTS INFORMATION",
    "WARRANTY STATUS", "LABOR ALLOWANCE", "LABOUR ALLOWANCE", "ATTACHMENTS", "DEALER CODING",
    "OWNER NOTIFICATION", "REPAIR FLOW CHART", "GENERAL INFORMATION", "NOTE:", "CAUTION:",
    "WARNING:", "CLAIM CODING", "LABOUR TIMES", "LABOR TIMES", "TOOLS", "SPECIAL TOOL",
    "REPAIR/CLAIM CODING", "PARTS", "MATERIALS"
]

BAD_TITLE_STARTS = (
    "FORD MOTOR", "TECHNICAL SERVICE", "SERVICE BULLETIN", "FIELD SERVICE", "CUSTOMER SATISFACTION",
    "PAGE ", "ISSUE DATE", "DATE", "MODEL", "YEAR", "VEHICLE", "VIN", "PART NUMBER",
    "LABOR", "LABOUR", "WARRANTY", "DEALER", "OWNER", "PROGRAM TERMS"
)


def clean(value):
    value = "" if value is None else str(value)
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[\t\r]+", " ", value)
    value = re.sub(r" {2,}", " ", value)
    return value.strip(" -–—:|\n")


def normalise_number(value):
    n = clean(value).upper()
    n = re.sub(r"\s+", "", n)
    n = n.replace("FSA", "")
    n = n.replace("SSM", "SSM")

    if re.fullmatch(r"\d{6}", n):
        return f"{n[:2]}-{n[2:]}"

    m = re.fullmatch(r"(\d{2})-(\d{4})", n)
    if m:
        return f"{m.group(1)}-{m.group(2)}"

    return n


def read_pdf(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        text = []
        for page in doc[:8]:
            text.append(page.get_text("text"))
        doc.close()
        return "\n".join(text)
    except Exception:
        return ""


def split_lines(text):
    return [clean(line) for line in text.splitlines() if clean(line)]


def load_overrides():
    if not OVERRIDES_FILE.exists():
        return {}
    try:
        return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def extract_numbers(source):
    found = []
    for match in NUMBER_RE.finditer(source):
        value = next((group for group in match.groups() if group), "")
        value = normalise_number(value)
        if value and value not in found:
            found.append(value)
    return found


def find_number(filename, text):
    stem = Path(filename).stem

    # Filename is the strongest signal. This prevents internal part numbers like 12A343
    # replacing a real file/program number such as S1406.pdf.
    filename_numbers = extract_numbers(stem.replace("_", " ").replace(".", " "))
    if filename_numbers:
        return filename_numbers[0]

    labelled = re.search(
        r"\b(?:TSB|SSM|FSA|FIELD SERVICE ACTION|BULLETIN|PROGRAM|RECALL|CAMPAIGN)\s*(?:NO\.|NUMBER|#|:)?\s*"
        r"([0-9]{2}\s*-?\s*[0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{1,5}|[A-Z][0-9]{4,6}|SSM\s*[0-9]{4,6})\b",
        text[:5000],
        re.IGNORECASE,
    )
    if labelled:
        return normalise_number(labelled.group(1))

    text_numbers = extract_numbers(text[:3000])
    return text_numbers[0] if text_numbers else ""


def detect_type(number, text, filename):
    combined = f"{number} {filename} {text[:2500]}".upper()
    if re.search(r"\bSSM\d{4,6}\b|SPECIAL SERVICE MESSAGE", combined):
        return "SSM"
    if re.search(r"FIELD SERVICE ACTION|CUSTOMER SATISFACTION PROGRAM|\bFSA\b|\b\d{2}P\d{2,5}\b|\b[A-Z]\d{4,6}\b", combined):
        return "FSA"
    if re.search(r"\bRECALL\b|\b\d{2}S\d{1,5}\b", combined):
        return "Recall"
    return "TSB"


def find_years(filename, text):
    combined = f"{filename}\n{text[:7000]}"
    ranges = [f"{a}-{b}" for a, b in YEAR_RANGE_RE.findall(combined) if int(a) <= int(b)]
    if ranges:
        return sorted(set(ranges))[:10]

    years = [year for year in YEAR_RE.findall(combined) if 1980 <= int(year) <= 2035]
    return sorted(set(years))[:10]


def find_models(filename, text):
    combined = f"{filename}\n{text[:6000]}".upper()
    found = []

    for model in sorted(MODELS, key=len, reverse=True):
        pattern = re.escape(model.upper()).replace(r"\-", "[- ]?")
        if re.search(rf"\b{pattern}\b", combined):
            nice = model.replace("F150", "F-150").replace("F250", "F-250").replace("F350", "F-350")
            if nice not in found:
                found.append(nice)

    for gen in GENS:
        pattern = re.escape(gen.upper()).replace(r"\-", "[- ]?")
        if re.search(rf"\b{pattern}\b", combined):
            nice = gen.replace("-", " ")
            if nice not in found:
                found.append(nice)

    return ", ".join(found)


def find_title(text, filename):
    labelled = re.search(r"(?:TITLE|SUBJECT)\s*[:\-–]\s*(.{8,220})", text, re.IGNORECASE)
    if labelled:
        value = clean(labelled.group(1))
        if value:
            return value[:220]

    useful = []
    for line in split_lines(text)[:120]:
        upper = line.upper()
        if len(line) < 8:
            continue
        if any(upper.startswith(bad) for bad in BAD_TITLE_STARTS):
            continue
        if NUMBER_RE.fullmatch(line) or re.fullmatch(r"[0-9 /\-–—]+", line):
            continue
        if re.search(r"\b(PHONE|FAX|ABN|ACN|WWW\.|HTTP|@)\b", upper):
            continue
        useful.append(line)
        if len(useful) >= 2:
            break

    if useful:
        return clean(" - ".join(useful))[:220]

    stem = Path(filename).stem
    stem = re.sub(NUMBER_RE, "", stem).replace("_", " ").replace("-", " ")
    stem = re.sub(r"\b\d{6}\b", "", stem)
    return clean(stem).title()


def paragraph_after(labels, text, max_lines=12, max_chars=900):
    lines = split_lines(text)
    for i, line in enumerate(lines):
        upper = line.upper()
        for label in labels:
            label_upper = label.upper()
            if upper.startswith(label_upper):
                first = clean(line[len(label):]).lstrip(":-–— ")
                parts = []
                if first:
                    parts.append(first)

                for next_line in lines[i + 1:i + 1 + max_lines]:
                    next_upper = next_line.upper()
                    if any(next_upper.startswith(stop) for stop in STOP_HEADINGS):
                        break
                    if re.fullmatch(r"[A-Z][A-Z /&\-]{3,35}:?", next_upper):
                        break
                    parts.append(next_line)
                    if len(" ".join(parts)) >= max_chars:
                        break

                output = clean(" ".join(parts))
                if len(output) > 8:
                    return output[:max_chars]
    return ""


def find_concern(text, filename, title):
    concern = paragraph_after(
        [
            "Issue", "Concern", "Condition", "Symptom", "Customer Concern", "Customer Symptom",
            "Reason For This Program", "Reason", "Reason for this Safety Recall", "Reason for this Customer Satisfaction Program",
        ],
        text,
        12,
        900,
    )
    return concern or title or clean(Path(filename).stem)


def find_supersession(text):
    supersedes = []
    superseded_by = []
    id_pattern = r"([0-9]{2}\s*-?\s*[0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{1,5}|[A-Z][0-9]{4,6}|SSM\s*[0-9]{4,6})"

    for match in re.findall(rf"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{id_pattern}", text, re.IGNORECASE):
        supersedes.append(normalise_number(match))

    for match in re.findall(rf"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{id_pattern}", text, re.IGNORECASE):
        superseded_by.append(normalise_number(match))

    return sorted(set(supersedes)), sorted(set(superseded_by))


def apply_overrides(item, overrides):
    for source in (overrides.get("_global", {}), overrides.get(item.get("number", ""), {})):
        if isinstance(source, dict):
            item.update(source)

    # Keep duplicate legacy fields aligned with the single primary number.
    item["tsbNumber"] = item.get("number", "")
    item["bulletinNumber"] = item.get("number", "")
    item["concern"] = item.get("concern", item.get("symptom", ""))
    item["description"] = item.get("description", item.get("symptom", ""))
    return item


def build_item(path, overrides):
    rel_path = path.relative_to(ROOT).as_posix()
    text = read_pdf(path)
    number = find_number(path.name, text)
    title = find_title(text, path.name)
    concern = find_concern(text, path.name, title)
    years = find_years(path.name, text)
    supersedes, superseded_by = find_supersession(text)

    archived = "archive/superseded" in rel_path.lower()
    filename_lower = path.name.lower()
    status = "Superseded" if archived or any(word in filename_lower for word in ["superseded", "obsolete", "replaced"]) else "Current"

    item = {
        "number": number,
        "tsbNumber": number,
        "bulletinNumber": number,
        "type": detect_type(number, text, path.name),
        "title": title,
        "model": find_models(path.name, text),
        "years": years,
        "yearRange": ", ".join(years),
        "symptom": concern,
        "concern": concern,
        "description": concern,
        "status": status,
        "supersedes": supersedes,
        "supersededBy": superseded_by,
        "file": rel_path,
        "filename": path.name,
    }

    item = apply_overrides(item, overrides)
    item["searchText"] = clean(" ".join([
        item.get("number", ""), item.get("type", ""), item.get("title", ""), item.get("model", ""),
        item.get("yearRange", ""), item.get("symptom", ""), item.get("status", ""), item.get("filename", ""),
    ])).lower()

    return item


def collect_pdfs():
    return sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))


def apply_supersession_links(items):
    by_number = {item.get("number"): item for item in items if item.get("number")}

    for item in items:
        current_number = item.get("number", "")
        for old_number in item.get("supersedes", []) or []:
            old_item = by_number.get(old_number)
            if old_item:
                old_item["status"] = "Superseded"
                old_item["supersededBy"] = current_number
        if item.get("supersededBy"):
            item["status"] = "Superseded"

    return items


def move_superseded(items):
    changed = False
    for item in items:
        if item.get("status") != "Superseded":
            continue

        source = ROOT / item.get("file", "")
        if not source.exists() or ARCHIVE_DIR in source.parents:
            continue

        destination = ARCHIVE_DIR / source.name
        if destination.exists():
            continue

        shutil.move(str(source), str(destination))
        changed = True

    return changed


def main():
    overrides = load_overrides()
    items = [build_item(path, overrides) for path in collect_pdfs()]
    items = apply_supersession_links(items)

    if move_superseded(items):
        items = [build_item(path, overrides) for path in collect_pdfs()]
        items = apply_supersession_links(items)

    items.sort(key=lambda item: (
        item.get("status") == "Superseded",
        item.get("type", ""),
        item.get("number", ""),
        item.get("title", ""),
    ))

    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(items)} Ford TSB records -> {INDEX_FILE}")


if __name__ == "__main__":
    main()

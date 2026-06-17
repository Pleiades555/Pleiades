import json
import re
import shutil
from pathlib import Path

try:
    import fitz
except Exception:
    fitz = None

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
OVERRIDES_FILE = DATA_DIR / "manual-overrides.json"
PARTS_FILE = DATA_DIR / "manual-parts.json"

for folder in [PDF_DIR, ARCHIVE_DIR, DATA_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

NUMBER_PATTERNS = [
    re.compile(r"\b(\d{2}-\d{4})\b", re.I),
    re.compile(r"\b(\d{2}[A-Z]{1,3}\d{2,5})\b", re.I),
    re.compile(r"\b(SSM\d{4,6})\b", re.I),
]
YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(19\d{2}|20\d{2})\b", re.I)
SINGLE_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
MODEL_WORDS = "RANGER EVEREST MUSTANG FOCUS FIESTA MONDEO TERRITORY FALCON ESCAPE TRANSIT COURIER BRONCO EXPLORER EDGE KUGA PUMA MAVERICK F-150 F150 F-250 F250 F-350 F350".split()
STOP_HEADINGS = ["ACTION", "SERVICE PROCEDURE", "PARTS", "PARTS REQUIRED", "WARRANTY", "LABOR", "LABOUR", "ATTACHMENTS", "DEALER CODING", "OWNER NOTIFICATION", "NOTE:", "CAUTION:", "WARNING:"]

MONTHS = {
    "jan": "01", "january": "01", "feb": "02", "february": "02", "mar": "03", "march": "03",
    "apr": "04", "april": "04", "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09", "september": "09", "oct": "10", "october": "10",
    "nov": "11", "november": "11", "dec": "12", "december": "12"
}
DATE_DMY_RE = re.compile(r"\b(0?[1-9]|[12][0-9]|3[01])[/.-](0?[1-9]|1[0-2])[/.-]((?:19|20)\d{2})\b")
DATE_YMD_RE = re.compile(r"\b((?:19|20)\d{2})[/.-](0?[1-9]|1[0-2])[/.-](0?[1-9]|[12][0-9]|3[01])\b")
DATE_TEXT_RE = re.compile(r"\b(0?[1-9]|[12][0-9]|3[01])\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+((?:19|20)\d{2})\b", re.I)
DATE_TEXT_REVERSE = re.compile(r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(0?[1-9]|[12][0-9]|3[01]),?\s+((?:19|20)\d{2})\b", re.I)


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip(" -–—:|")


def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_pdf(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        text = "\n".join(page.get_text("text") for page in doc[:6])
        doc.close()
        return text
    except Exception:
        return ""


def norm_number(num):
    num = clean(num).upper().replace(" ", "-")
    m = re.fullmatch(r"(\d{2})-(\d{4})", num)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return num


def find_number(filename, text):
    combined = f"{filename}\n{text[:3500]}"
    labelled = re.search(r"\b(?:TSB|FSA|SSM|FIELD SERVICE ACTION|BULLETIN|PROGRAM)\s*[:#-]?\s*(\d{2}-\d{4}|\d{2}[A-Z]{1,3}\d{2,5}|SSM\d{4,6})\b", combined, re.I)
    if labelled:
        return norm_number(labelled.group(1))
    for pat in NUMBER_PATTERNS:
        m = pat.search(combined)
        if m:
            return norm_number(m.group(1))
    return ""


def detect_type(number, text, filename):
    combined = f"{number} {filename} {text[:1500]}".upper()
    if "FIELD SERVICE ACTION" in combined or re.search(r"\b\d{2}P\d{2,5}\b", combined):
        return "FSA"
    if "SPECIAL SERVICE MESSAGE" in combined or number.startswith("SSM"):
        return "SSM"
    if "RECALL" in combined or re.search(r"\b\d{2}S\d{2,5}\b", combined):
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
    combined = f"{filename}\n{text[:5000]}".upper()
    found = []
    for model in MODEL_WORDS:
        if re.search(rf"\b{re.escape(model)}\b", combined):
            model = model.replace("F150", "F-150").replace("F250", "F-250").replace("F350", "F-350")
            if model not in found:
                found.append(model)
    for gen in ["PX1", "PX2", "PX3", "NEXT GEN", "NEXT-GEN", "RA", "PJ", "PK", "BA", "BF", "FG", "FG X"]:
        if gen in combined and gen not in found:
            found.append(gen.replace("-", " "))
    return ", ".join(x.title() if not x.startswith("F-") else x for x in found)


def labelled_paragraph(text, labels):
    lines = [clean(x) for x in text.splitlines() if clean(x)]
    for i, line in enumerate(lines):
        upper = line.upper()
        for label in labels:
            if upper.startswith(label.upper()):
                first = clean(line[len(label):].lstrip(":-–— "))
                parts = [first] if first else []
                for nxt in lines[i+1:i+9]:
                    nu = nxt.upper()
                    if any(nu.startswith(stop) for stop in STOP_HEADINGS):
                        break
                    if re.fullmatch(r"[A-Z][A-Z /&-]{3,35}:?", nu):
                        break
                    parts.append(nxt)
                    if len(" ".join(parts)) > 520:
                        break
                out = clean(" ".join(parts))
                if len(out) > 6:
                    return out[:650]
    return ""


def find_title(text, filename):
    labelled = labelled_paragraph(text, ["Title", "Subject"])
    if labelled:
        return labelled[:220]
    lines = [clean(x) for x in text.splitlines() if clean(x)]
    bad = ("FORD MOTOR", "TECHNICAL SERVICE", "SERVICE BULLETIN", "FIELD SERVICE ACTION", "PAGE", "ISSUE DATE", "DATE", "MODEL", "YEAR")
    useful = []
    for line in lines[:70]:
        up = line.upper()
        if len(line) < 8 or any(up.startswith(b) for b in bad):
            continue
        if any(p.fullmatch(line) for p in NUMBER_PATTERNS):
            continue
        useful.append(line)
        if len(useful) >= 2:
            break
    if useful:
        return clean(" - ".join(useful))[:220]
    return clean(re.sub(r"\.(pdf)$", "", filename, flags=re.I).replace("_", " "))


def find_concern(text, title, filename):
    concern = labelled_paragraph(text, ["Issue", "Concern", "Condition", "Symptom", "Customer Concern", "Customer Symptom", "Reason For This Program", "Reason"])
    if concern:
        return concern
    return clean(title) or clean(Path(filename).stem.replace("_", " "))


def iso_date(year, month, day):
    try:
        y = int(year); m = int(month); d = int(day)
        if 1980 <= y <= 2035 and 1 <= m <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        pass
    return ""


def normalise_date(raw):
    raw = clean(raw)
    if not raw:
        return ""

    m = DATE_YMD_RE.search(raw)
    if m:
        return iso_date(m.group(1), m.group(2), m.group(3))

    m = DATE_DMY_RE.search(raw)
    if m:
        return iso_date(m.group(3), m.group(2), m.group(1))

    m = DATE_TEXT_RE.search(raw)
    if m:
        month = MONTHS.get(m.group(2).lower()[:3], "") or MONTHS.get(m.group(2).lower(), "")
        return iso_date(m.group(3), month, m.group(1))

    m = DATE_TEXT_REVERSE.search(raw)
    if m:
        month = MONTHS.get(m.group(1).lower()[:3], "") or MONTHS.get(m.group(1).lower(), "")
        return iso_date(m.group(3), month, m.group(1))

    return ""


def find_date_near_label(text, labels):
    lines = [clean(x) for x in text.splitlines() if clean(x)]
    for i, line in enumerate(lines[:120]):
        upper = line.upper()
        for label in labels:
            if label.upper() in upper:
                # Try same line, then the next two lines.
                candidates = [line] + lines[i + 1:i + 3]
                for candidate in candidates:
                    date = normalise_date(candidate)
                    if date:
                        return date
    return ""


def find_dates(text):
    first_pages = text[:6000]

    ford_upload_date = find_date_near_label(first_pages, [
        "Date Uploaded by Ford",
        "Ford Upload Date",
        "Upload Date",
        "Uploaded Date",
        "Published Date",
        "Publication Date",
        "Release Date",
        "Released Date",
        "Dealer Bulletin Date",
        "Bulletin Date",
        "OASIS Date",
    ])

    issue_date = find_date_near_label(first_pages, [
        "Issue Date",
        "Date Issued",
        "Date:",
        "Date ",
    ])

    # If Ford upload date is not explicitly found, leave it blank rather than guessing from the PDF file date.
    # The editor/manual-overrides.json can be used to set the true Ford portal upload date.
    return ford_upload_date, issue_date


def find_supersession(text):
    supersedes = []
    superseded_by = []
    number = r"(\d{2}-\d{4}|\d{2}[A-Z]{1,3}\d{2,5}|SSM\d{4,6})"
    for m in re.findall(rf"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{number}", text, re.I):
        supersedes.append(norm_number(m))
    for m in re.findall(rf"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*{number}", text, re.I):
        superseded_by.append(norm_number(m))
    return sorted(set(supersedes)), sorted(set(superseded_by))


def key_candidates(item):
    keys = []
    for k in [item.get("number"), item.get("tsbNumber"), item.get("bulletinNumber"), item.get("filename")]:
        if k:
            keys.append(str(k))
            keys.append(str(k).upper())
            keys.append(str(k).replace("-", ""))
    return list(dict.fromkeys(keys))


def apply_overrides(item, overrides):
    global_overrides = overrides.get("_global", {}) if isinstance(overrides, dict) else {}
    if isinstance(global_overrides, dict):
        item.update(global_overrides)
    if isinstance(overrides, dict):
        for key in key_candidates(item):
            val = overrides.get(key)
            if isinstance(val, dict):
                item.update(val)
                item["manualOverride"] = True
    return item


def attach_parts(item, parts_data):
    item["parts"] = {"staticParts": [], "variants": {}}
    if isinstance(parts_data, dict):
        for key in key_candidates(item):
            val = parts_data.get(key)
            if isinstance(val, dict):
                item["parts"] = {
                    "staticParts": val.get("staticParts", []),
                    "variants": val.get("variants", {}),
                }
                item["hasManualParts"] = True
                break
    return item


def build_item(path, overrides, parts_data):
    rel = path.relative_to(ROOT).as_posix()
    text = read_pdf(path)
    number = find_number(path.name, text)
    title = find_title(text, path.name)
    concern = find_concern(text, title, path.name)
    years = find_years(text, path.name)
    supersedes, superseded_by = find_supersession(text)
    ford_upload_date, issue_date = find_dates(text)
    status = "Superseded" if "archive/superseded" in rel.lower() or "superseded" in path.name.lower() else "Current"
    item = {
        "number": number,
        "tsbNumber": number,
        "bulletinNumber": number,
        "type": detect_type(number, text, path.name),
        "title": title,
        "model": find_models(text, path.name),
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
        "file": rel,
        "filename": path.name,
        "manualOverride": False,
        "hasManualParts": False,
    }
    item = apply_overrides(item, overrides)
    item = attach_parts(item, parts_data)
    item["displayNumber"] = item.get("number") or item.get("tsbNumber") or item.get("bulletinNumber") or Path(item.get("filename", "")).stem
    item["searchText"] = clean(" ".join([str(item.get(k, "")) for k in ["displayNumber", "type", "title", "model", "yearRange", "fordUploadDate", "issueDate", "symptom", "status", "filename"]])).lower()
    return item


def collect_pdfs():
    return sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))


def apply_supersession_links(items):
    by_num = {i.get("number"): i for i in items if i.get("number")}
    for item in items:
        for old in item.get("supersedes", []):
            if old in by_num:
                by_num[old]["status"] = "Superseded"
                by_num[old]["supersededBy"] = item.get("number", "")
        if item.get("supersededBy"):
            item["status"] = "Superseded"
    return items


def move_superseded(items):
    for item in items:
        if item.get("status") != "Superseded":
            continue
        src = ROOT / item["file"]
        if not src.exists() or ARCHIVE_DIR in src.parents:
            continue
        dst = ARCHIVE_DIR / src.name
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))


def main():
    overrides = load_json(OVERRIDES_FILE, {})
    parts_data = load_json(PARTS_FILE, {})
    items = [build_item(p, overrides, parts_data) for p in collect_pdfs()]
    items = apply_supersession_links(items)
    move_superseded(items)
    items = [build_item(p, overrides, parts_data) for p in collect_pdfs()]
    items = apply_supersession_links(items)
    items.sort(key=lambda x: (x.get("status") == "Superseded", x.get("displayNumber", ""), x.get("title", "")))
    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(items)} Ford TSB entries")

if __name__ == "__main__":
    main()

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

for d in (PDF_DIR, ARCHIVE_DIR, DATA_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Ford-ish identifiers: 26-2159, 23P23, 25S39, SSM52344, CSP/FSAs etc.
NUMBER_PATTERNS = [
    r"\b(\d{2}-\d{4})\b",
    r"\b(\d{2}\s*-\s*\d{4})\b",
    r"\b(\d{2}[A-Z]{1,3}\d{2,5})\b",
    r"\b(SSM\s*\d{4,6})\b",
    r"\b(FSA\s*\d{2}[A-Z]?\d{2,5})\b",
]
NUMBER_RE = re.compile("|".join(NUMBER_PATTERNS), re.I)
YEAR_RANGE_RE = re.compile(r"\b(19\d{2}|20\d{2})\s*(?:[-–—]|to|TO)\s*(19\d{2}|20\d{2})\b")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
PART_RE = re.compile(r"\b([A-Z0-9]{2,6}[- ][A-Z0-9]{3,8}[- ][A-Z0-9]{1,8}(?:[- ][A-Z0-9]{1,8})?)\b")

MODELS = [
    "Ranger", "Everest", "Mustang", "Focus", "Fiesta", "Mondeo", "Territory", "Falcon",
    "Escape", "Transit", "Transit Custom", "Transit Courier", "F-150", "F150", "F-250", "F250",
    "F-350", "F350", "Bronco", "Explorer", "Edge", "Kuga", "Puma", "Maverick",
    "Expedition", "EcoSport", "Courier", "Mustang Mach-E", "Mach-E"
]
GENS = ["PX1", "PX2", "PX3", "Next Gen", "Next-Gen", "RA", "PJ", "PK", "BA", "BF", "FG", "FG X", "SZ", "UA", "UB"]
STOP_HEADINGS = [
    "ACTION", "SERVICE PROCEDURE", "PARTS REQUIREMENT", "PARTS REQUIRED", "PARTS INFORMATION",
    "WARRANTY STATUS", "LABOR ALLOWANCE", "LABOUR ALLOWANCE", "ATTACHMENTS", "DEALER CODING",
    "OWNER NOTIFICATION", "REPAIR FLOW CHART", "GENERAL INFORMATION", "NOTE:", "CAUTION:", "WARNING:",
    "CLAIM CODING", "LABOUR TIMES", "LABOR TIMES", "TOOLS", "SPECIAL TOOL", "REPAIR/CLAIM CODING"
]
PARTS_HEADINGS = ["PARTS REQUIRED", "PARTS REQUIREMENT", "PARTS INFORMATION", "PARTS", "MATERIALS"]
CONDITION_WORDS = [
    "if ", "only if", "where ", "when ", "as required", "if damaged", "if corrosion", "if inspection",
    "if equipped", "if necessary", "if present", "if found", "if required", "if replacing"
]

def clean(s):
    s = "" if s is None else str(s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[\t\r]+", " ", s)
    s = re.sub(r" {2,}", " ", s)
    return s.strip(" -–—:|\n")

def norm_number(n):
    n = clean(n).upper().replace(" ", "")
    # Restore hyphen for TSB-style 6 digit numeric numbers if OCR/source lost it.
    if re.fullmatch(r"\d{6}", n):
        return n[:2] + "-" + n[2:]
    if re.fullmatch(r"\d{2}-\d{4}", n):
        return n
    return n

def read_pdf(path):
    if fitz is None:
        return ""
    try:
        doc = fitz.open(path)
        txt = []
        for p in doc[:8]:
            txt.append(p.get_text("text"))
        doc.close()
        return "\n".join(txt)
    except Exception as e:
        return ""

def lines(text):
    return [clean(x) for x in text.splitlines() if clean(x)]

def load_overrides():
    if not OVERRIDES_FILE.exists():
        return {}
    try:
        return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def find_number(filename, text):
    base = f"{filename}\n{text[:5000]}"
    labelled = re.search(r"\b(?:TSB|SSM|FSA|FIELD SERVICE ACTION|BULLETIN|PROGRAM|RECALL)\s*(?:NO\.|NUMBER|#|:)?\s*([0-9]{2}\s*-?\s*[0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM\s*[0-9]{4,6})\b", base, re.I)
    if labelled:
        return norm_number(labelled.group(1))
    m = NUMBER_RE.search(base)
    if m:
        val = next(g for g in m.groups() if g)
        return norm_number(val)
    # last chance for filenames like 262159.pdf
    stem = Path(filename).stem
    m2 = re.search(r"\b(\d{6})\b", stem)
    return norm_number(m2.group(1)) if m2 else ""

def detect_type(number, text, filename):
    c = f"{number} {filename} {text[:2000]}".upper()
    if re.search(r"\bSSM\d{4,6}\b|SPECIAL SERVICE MESSAGE", c): return "SSM"
    if re.search(r"FIELD SERVICE ACTION|CUSTOMER SATISFACTION PROGRAM|\bFSA\b|\b\d{2}P\d{2,5}\b", c): return "FSA"
    if re.search(r"\bRECALL\b|\b\d{2}S\d{2,5}\b", c): return "Recall"
    return "TSB"

def find_years(filename, text):
    c = f"{filename}\n{text[:7000]}"
    rs = [f"{a}-{b}" for a,b in YEAR_RANGE_RE.findall(c) if int(a) <= int(b)]
    if rs:
        return sorted(set(rs))[:10]
    ys = [y for y in YEAR_RE.findall(c) if 1980 <= int(y) <= 2035]
    return sorted(set(ys))[:10]

def find_models(filename, text):
    c = f"{filename}\n{text[:6000]}".upper()
    found = []
    for m in sorted(MODELS, key=len, reverse=True):
        pat = re.escape(m.upper()).replace("\\-", "[- ]?")
        if re.search(rf"\b{pat}\b", c):
            nice = m.replace("F150", "F-150").replace("F250", "F-250").replace("F350", "F-350")
            if nice not in found: found.append(nice)
    for g in GENS:
        if re.search(rf"\b{re.escape(g.upper()).replace('\\-', '[- ]?')}\b", c):
            if g.replace('-', ' ') not in found: found.append(g.replace('-', ' '))
    return ", ".join(found)

def first_good_title(text, filename):
    labelled = re.search(r"(?:TITLE|SUBJECT)\s*[:\-–]\s*(.{8,220})", text, re.I)
    if labelled:
        return clean(labelled.group(1))
    bad = ("FORD MOTOR", "TECHNICAL SERVICE", "SERVICE BULLETIN", "FIELD SERVICE", "CUSTOMER SATISFACTION", "PAGE ", "ISSUE DATE", "DATE", "MODEL", "YEAR", "VEHICLE", "VIN")
    useful=[]
    for ln in lines(text)[:100]:
        up=ln.upper()
        if len(ln)<8 or any(up.startswith(b) for b in bad): continue
        if NUMBER_RE.fullmatch(ln) or re.fullmatch(r"[0-9 /\-–—]+", ln): continue
        useful.append(ln)
        if len(useful)>=2: break
    if useful: return clean(" - ".join(useful))[:220]
    stem=Path(filename).stem
    stem=re.sub(NUMBER_RE,"",stem).replace("_"," ")
    stem=re.sub(r"\b\d{6}\b", "", stem)
    return clean(stem).title()

def paragraph_after(labels, text, max_lines=10, max_chars=700):
    ls = lines(text)
    for i, ln in enumerate(ls):
        up=ln.upper()
        for label in labels:
            lu=label.upper()
            if up.startswith(lu):
                first=clean(ln[len(label):]).lstrip(":-–— ")
                parts=[]
                if first: parts.append(first)
                for nxt in ls[i+1:i+1+max_lines]:
                    nu=nxt.upper()
                    if any(nu.startswith(s) for s in STOP_HEADINGS): break
                    if re.fullmatch(r"[A-Z][A-Z /&\-]{3,35}:?", nu): break
                    parts.append(nxt)
                    if len(" ".join(parts))>=max_chars: break
                out=clean(" ".join(parts))
                if len(out)>8: return out[:max_chars]
    return ""

def find_concern(text, filename, title):
    val = paragraph_after(["Issue", "Concern", "Condition", "Symptom", "Customer Concern", "Customer Symptom", "Reason For This Program", "Reason"], text, 12, 900)
    return val or title or clean(Path(filename).stem)

def extract_section(text, headings, max_lines=35):
    ls = lines(text)
    for i, ln in enumerate(ls):
        if any(ln.upper().startswith(h) for h in headings):
            out=[]
            for nxt in ls[i+1:i+1+max_lines]:
                nu=nxt.upper()
                if any(nu.startswith(s) for s in STOP_HEADINGS if s not in headings): break
                out.append(nxt)
            return out
    return []

def extract_parts(text):
    sec = extract_section(text, PARTS_HEADINGS, 45)
    part_numbers=[]; part_rows=[]; conditional=[]
    source_lines = sec if sec else lines(text)[:220]
    for ln in source_lines:
        for pn in PART_RE.findall(ln):
            pn = pn.upper().replace(" ", "-")
            # Avoid catching year ranges and generic bulletin numbers as parts
            if re.fullmatch(r"\d{4}-\d{4}", pn) or re.fullmatch(r"\d{2}-\d{4}", pn):
                continue
            if pn not in part_numbers:
                part_numbers.append(pn)
            if len(ln) > 5 and ln not in part_rows:
                part_rows.append(ln[:240])
    for ln in lines(text)[:320]:
        low = ln.lower()
        if any(w in low for w in CONDITION_WORDS) and ("order" in low or "replace" in low or "required" in low or "install" in low or PART_RE.search(ln)):
            if ln not in conditional:
                conditional.append(ln[:300])
        if len(conditional) >= 8:
            break
    return {"partNumbers": part_numbers[:40], "partsTable": part_rows[:30], "conditionalLogic": conditional[:10]}

def find_supersession(text):
    supersedes=[]; superseded_by=[]
    p1 = r"\b(?:supersedes|replaces|this bulletin supersedes|this article supersedes)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}\s*-?\s*[0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM\s*[0-9]{4,6})"
    p2 = r"\b(?:superseded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|program)?\s*[:#-]?\s*([0-9]{2}\s*-?\s*[0-9]{4}|[0-9]{2}[A-Z]{1,3}[0-9]{2,5}|SSM\s*[0-9]{4,6})"
    for m in re.findall(p1, text, re.I): supersedes.append(norm_number(m))
    for m in re.findall(p2, text, re.I): superseded_by.append(norm_number(m))
    return sorted(set(supersedes)), sorted(set(superseded_by))

def apply_overrides(item, overrides):
    for source in (overrides.get("_global", {}), overrides.get(item.get("number",""), {})):
        if isinstance(source, dict):
            item.update(source)
    # Keep legacy duplicate fields aligned unless deliberately overridden.
    item["tsbNumber"] = item.get("number", item.get("tsbNumber", ""))
    item["bulletinNumber"] = item.get("number", item.get("bulletinNumber", ""))
    item["concern"] = item.get("concern", item.get("symptom", ""))
    item["description"] = item.get("description", item.get("symptom", ""))
    return item

def build_item(path, overrides):
    rel = path.relative_to(ROOT).as_posix()  # Important: untouched link path, URL encoded by HTML.
    text = read_pdf(path)
    number = find_number(path.name, text)
    title = first_good_title(text, path.name)
    concern = find_concern(text, path.name, title)
    years = find_years(path.name, text)
    supersedes, superseded_by = find_supersession(text)
    parts = extract_parts(text)
    archived = "archive/superseded" in rel.lower()
    status = "Superseded" if archived or any(w in path.name.lower() for w in ["superseded","obsolete","replaced"]) else "Current"
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
        "parts": parts,
        "partNumbers": parts["partNumbers"],
        "partsTable": parts["partsTable"],
        "conditionalLogic": parts["conditionalLogic"],
        "status": status,
        "supersedes": supersedes,
        "supersededBy": superseded_by,
        "file": rel,
        "filename": path.name,
    }
    item = apply_overrides(item, overrides)
    item["searchText"] = clean(" ".join([
        item.get("number",""), item.get("type",""), item.get("title",""), item.get("model",""), item.get("yearRange",""),
        item.get("symptom",""), item.get("status",""), item.get("filename",""), " ".join(item.get("partNumbers",[])),
        " ".join(item.get("partsTable",[])), " ".join(item.get("conditionalLogic",[]))
    ])).lower()
    return item

def collect_pdfs():
    return sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))

def apply_supersession_links(items):
    bynum={i.get("number"):i for i in items if i.get("number")}
    for item in items:
        cur=item.get("number","")
        for old in item.get("supersedes",[]) or []:
            if old in bynum:
                bynum[old]["status"]="Superseded"
                bynum[old]["supersededBy"]=cur
        if item.get("supersededBy"):
            item["status"]="Superseded"
    return items

def move_superseded(items):
    changed=False
    for item in items:
        if item.get("status") != "Superseded": continue
        src=ROOT / item.get("file","")
        if not src.exists() or ARCHIVE_DIR in src.parents: continue
        dst=ARCHIVE_DIR / src.name
        if dst.exists(): continue
        shutil.move(str(src), str(dst))
        changed=True
    return changed

def main():
    overrides=load_overrides()
    items=[build_item(p, overrides) for p in collect_pdfs()]
    items=apply_supersession_links(items)
    if move_superseded(items):
        items=[build_item(p, overrides) for p in collect_pdfs()]
        items=apply_supersession_links(items)
    items.sort(key=lambda x: (x.get("status") == "Superseded", x.get("type",""), x.get("number",""), x.get("title","")))
    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(items)} Ford TSB records -> {INDEX_FILE}")

if __name__ == "__main__":
    main()

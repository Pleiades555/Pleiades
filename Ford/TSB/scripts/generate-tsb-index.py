#!/usr/bin/env python3
"""
Pleiades Ford TSB/FSA/SSM accuracy indexer v2.

Designed to fix common bad extraction issues:
- Incorrect bulletin numbers caused by random numbers inside PDF body text.
- Titles taken from disclaimers, tables, dates or page text.
- Symptoms copied from filenames instead of Ford Issue/Concern/Condition wording.
- Year ranges shown as random year lists.
- FSA/recall/SSM/bulletin numbers not separated properly.

Usage locally:
  python Ford/TSB/scripts/generate-tsb-index.py

GitHub Action runs this automatically on every PDF/indexer change.
"""
from __future__ import annotations

import json, os, re, shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
CORRECTIONS_FILE = DATA_DIR / "manual-corrections.json"
MOVE_SUPERSEDED = os.environ.get("MOVE_SUPERSEDED", "true").lower() in {"1","true","yes"}

MODEL_ALIASES = {
    "Ranger": ["ranger", "px", "px2", "px3", "next-gen ranger", "next gen ranger"],
    "Everest": ["everest", "ua everest", "next-gen everest", "next gen everest"],
    "F-150": ["f-150", "f150", "f 150"],
    "Mustang": ["mustang"],
    "Transit": ["transit", "transit custom", "tourneo"],
    "Escape": ["escape", "kuga"],
    "Focus": ["focus"],
    "Fiesta": ["fiesta"],
    "Puma": ["puma"],
    "Mondeo": ["mondeo"],
    "Endura": ["endura", "edge"],
    "Explorer": ["explorer"],
    "Bronco": ["bronco"],
    "Maverick": ["maverick"],
    "Falcon": ["falcon", "fg", "fgx", "ba", "bf"],
    "Territory": ["territory"],
    "Courier": ["courier"],
}
ENGINES = ["P5AT","P5BT","P4AT","PUMA","EcoBoost","Power Stroke","PowerStroke","Duratorq","Duratec","Barra","Coyote","Godzilla","Lion","2.0L","2.2L","2.3L","2.7L","3.0L","3.2L","3.5L","5.0L","6.7L"]

DOC_PATTERNS = [
    ("FSA", re.compile(r"\b(\d{2}[SBCM]\d{2,5})\b", re.I)),       # 25S39, 24B12, 25C02, 25M01
    ("SSM", re.compile(r"\b(?:SSM\s*)?(\d{5,6})\b", re.I)),          # SSM 52344 or 52344 when near SSM
    ("TSB", re.compile(r"\b(\d{2}-\d{4,5})\b", re.I)),               # 25-2205
]

BAD_TITLE_RE = re.compile(r"(ford motor company|copyright|page \d+|printed copies|technical service bulletin|customer satisfaction program|field service action|summary:|publication date|attachment|dealer bulletin|important safety recall)", re.I)
FIELD_LABEL_RE = re.compile(r"^(issue|condition|concern|customer concern|reason for this bulletin|summary|description|title|subject|vehicles affected|affected vehicles|model|model year|vehicle line)\s*[:\-–]?\s*(.*)$", re.I)


def clean_space(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip(" \t\r\n-|:;,.•")


def uniq(seq):
    out=[]; seen=set()
    for x in seq:
        x=clean_space(x)
        if not x: continue
        k=x.lower()
        if k not in seen:
            seen.add(k); out.append(x)
    return out


def read_text(path: Path) -> str:
    # First 10 pages is usually enough for Ford bulletin header, issue, vehicles and supersession.
    try:
        import fitz  # PyMuPDF
        parts=[]
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                if i >= 10: break
                parts.append(page.get_text("text") or "")
        return "\n".join(parts)
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        r=PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in r.pages[:10])
    except Exception:
        return ""


def normalise_doc_number(v: str) -> str:
    v=clean_space(v).upper().replace(" ", "")
    v=re.sub(r"^(TSB|ARTICLE|BULLETIN|FSA|RECALL|SSM)[:#-]*", "", v)
    if re.fullmatch(r"\d{5,6}", v): return "SSM" + v
    return v


def detect_number_and_type(text: str, filename: str) -> tuple[str,str]:
    # Priority: filename/stem first. This avoids grabbing unrelated body numbers.
    stem = Path(filename).stem
    candidates = []
    zones = [stem, text[:2500]]
    for zi, zone in enumerate(zones):
        # Explicit labels first
        for m in re.finditer(r"\b(?:TSB|Article|Bulletin)\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{2}-\d{4,5})\b", zone, re.I):
            candidates.append((zi, m.start(), "TSB", m.group(1)))
        for m in re.finditer(r"\b(?:Field Service Action|FSA|Recall|Safety Recall|Customer Satisfaction Program)\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{2}[SBCM]\d{2,5})\b", zone, re.I):
            candidates.append((zi, m.start(), "FSA", m.group(1)))
        for m in re.finditer(r"\bSSM\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{5,6})\b", zone, re.I):
            candidates.append((zi, m.start(), "SSM", "SSM"+m.group(1)))
        # Bare common formats
        for typ, pat in DOC_PATTERNS:
            for m in pat.finditer(zone):
                val=m.group(1)
                if typ == "SSM":
                    around=zone[max(0,m.start()-20):m.end()+20].lower()
                    if "ssm" not in around and zi != 0: continue
                    val="SSM"+val if not val.upper().startswith("SSM") else val
                candidates.append((zi+1, m.start()+50, typ, val))
    if not candidates:
        return "", "Bulletin"
    candidates.sort(key=lambda x:(x[0], x[1]))
    typ, num = candidates[0][2], normalise_doc_number(candidates[0][3])
    return num, ("Recall / Field Service Action" if typ=="FSA" else typ)


def lines(text: str):
    return [clean_space(x) for x in re.split(r"[\r\n]+", text) if clean_space(x)]


def field_value(text: str, labels: list[str], max_chars=280) -> str:
    ls=lines(text[:9000])
    label_re=re.compile(r"^("+"|".join(re.escape(x) for x in labels)+r")\s*[:\-–]?\s*(.*)$", re.I)
    for i,l in enumerate(ls):
        m=label_re.match(l)
        if not m: continue
        val=clean_space(m.group(2))
        # If the value is on the next line, use a short continuation.
        if len(val) < 8 and i+1 < len(ls):
            val=clean_space(ls[i+1])
        if val and not BAD_TITLE_RE.search(val):
            return val[:max_chars]
    return ""


def sentence_with(text: str, patterns: list[str], max_chars=300) -> str:
    flat=clean_space(text[:12000])
    # split to sentences/clauses but keep "may exhibit" style sentence.
    chunks=re.split(r"(?<=[.!?])\s+|\s{2,}|\n", flat)
    for c in chunks:
        if len(c) < 18 or len(c) > 420: continue
        if any(re.search(p, c, re.I) for p in patterns) and not BAD_TITLE_RE.search(c):
            return clean_space(c)[:max_chars]
    return ""


def extract_symptom(text: str, filename: str) -> str:
    # Ford TSBs often use Issue/Condition/Concern/Summary. Prefer those exact fields.
    v=field_value(text, ["Issue", "Condition", "Concern", "Customer Concern", "Reason For This Bulletin", "Reason for this Field Service Action", "Summary", "Description"], 360)
    if v:
        return v
    v=sentence_with(text, [r"may exhibit", r"may experience", r"customer.*concern", r"illumination", r"noise", r"rattle", r"leak", r"no start", r"vibration", r"shudder", r"DTC", r"warning lamp"], 360)
    if v:
        return v
    # Filename last, and remove bulletin number/model-like noise.
    stem=re.sub(r"\b\d{2}-\d{4,5}\b|\b\d{2}[SBCM]\d{2,5}\b|\bSSM\s*\d{5,6}\b", " ", Path(filename).stem, flags=re.I)
    stem=re.sub(r"[_-]+", " ", stem)
    return clean_space(stem)[:220]


def extract_title(text: str, filename: str, symptom: str) -> str:
    # Prefer Subject/Title if present; otherwise use concise symptom.
    v=field_value(text, ["Title", "Subject"], 180)
    if v:
        return v
    if symptom:
        s = symptom
        # Shorten common Ford prose into a readable title.
        s = re.sub(r"^(Some|Certain)\s+", "", s, flags=re.I)
        s = re.sub(r"\bmay exhibit\b", "-", s, flags=re.I)
        s = re.sub(r"\bmay experience\b", "-", s, flags=re.I)
        return clean_space(s)[:180]
    stem=re.sub(r"[_-]+", " ", Path(filename).stem)
    return clean_space(stem)[:180]


def extract_models(text: str, filename: str) -> list[str]:
    hay=(Path(filename).stem + "\n" + text[:7000]).lower()
    found=[]
    # Strong lines first.
    vehicle_line = field_value(text, ["Vehicle Line", "Model", "Affected Vehicles", "Vehicles Affected", "Vehicle", "Model Line"], 300)
    strong = vehicle_line.lower()
    for model, aliases in MODEL_ALIASES.items():
        if any(re.search(r"(?<![a-z0-9])"+re.escape(a)+r"(?![a-z0-9])", strong, re.I) for a in aliases):
            found.append(model)
    for model, aliases in MODEL_ALIASES.items():
        if any(re.search(r"(?<![a-z0-9])"+re.escape(a)+r"(?![a-z0-9])", hay, re.I) for a in aliases):
            found.append(model)
    return uniq(found)


def extract_year_range(text: str, filename: str) -> str:
    zone = Path(filename).stem + "\n" + text[:9000]
    candidates=[]
    # Common Ford year ranges: 2019-2023, 2019–2023, 2019 / 2020 Ranger, 2021MY.
    for m in re.finditer(r"\b((?:19|20)\d{2})\s*(?:-|–|—|to|through|thru|/)\s*((?:19|20)\d{2})\b", zone, re.I):
        a,b=int(m.group(1)),int(m.group(2))
        if 1990 <= a <= 2035 and 1990 <= b <= 2035:
            around=zone[max(0,m.start()-90):m.end()+90].lower()
            score=3 if any(w in around for w in ["model", "vehicle", "ranger", "everest", "mustang", "transit", "f-150", "built", "from", "through"]) else 1
            candidates.append((score,a,b))
    years=[]
    for m in re.finditer(r"\b((?:19|20)\d{2})\s*(?:MY|model year|model|vehicles?|ranger|everest|f-150|transit|mustang)?\b", zone, re.I):
        y=int(m.group(1))
        if not (1990 <= y <= 2035): continue
        around=zone[max(0,m.start()-80):m.end()+80].lower()
        # Avoid publication dates unless near vehicle/model language.
        if any(w in around for w in ["model", "vehicle", "built", "ranger", "everest", "mustang", "transit", "f-150", "focus", "escape", "my"]):
            years.append(y)
    if candidates:
        candidates.sort(key=lambda x:(-x[0], x[1], x[2]))
        a,b=candidates[0][1], candidates[0][2]
        return f"{min(a,b)}-{max(a,b)}" if a != b else str(a)
    years=sorted(set(years))
    if not years:
        return ""
    # Collapse consecutive year sets to ranges. If scattered, show explicit years.
    if len(years) >= 2 and years[-1]-years[0] <= len(years)+1:
        return f"{years[0]}-{years[-1]}" if years[0] != years[-1] else str(years[0])
    return ", ".join(map(str, years[:8]))


def extract_engines(text: str, filename: str) -> list[str]:
    hay=Path(filename).stem + "\n" + text[:7000]
    found=[]
    for e in ENGINES:
        if re.search(r"(?<![A-Za-z0-9])"+re.escape(e)+r"(?![A-Za-z0-9])", hay, re.I):
            found.append(e)
    return uniq(found)


def extract_supersession(text: str, filename: str) -> dict[str,list[str]]:
    sample = Path(filename).stem + "\n" + text[:16000]
    out={"supersedes":[], "supersededBy":[]}
    patterns_old=[r"(?:supersedes|supercedes|replaces|this bulletin replaces|this article supersedes|previously released as)\s+(?:TSB|SSM|FSA|bulletin|article|recall)?\s*[:#-]?\s*([A-Z0-9 -]{4,18})"]
    patterns_new=[r"(?:superseded by|superceded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|article|recall)?\s*[:#-]?\s*([A-Z0-9 -]{4,18})"]
    for p in patterns_old:
        for m in re.finditer(p, sample, re.I):
            n,_=detect_number_and_type(m.group(1), m.group(1))
            if n: out["supersedes"].append(n)
    for p in patterns_new:
        for m in re.finditer(p, sample, re.I):
            n,_=detect_number_and_type(m.group(1), m.group(1))
            if n: out["supersededBy"].append(n)
    out["supersedes"]=uniq(out["supersedes"]); out["supersededBy"]=uniq(out["supersededBy"])
    return out


def load_corrections() -> dict[str,Any]:
    if not CORRECTIONS_FILE.exists(): return {"supersessions":{}, "metadata":{}}
    try: return json.loads(CORRECTIONS_FILE.read_text(encoding='utf-8'))
    except Exception: return {"supersessions":{}, "metadata":{}}


def scan_one(path: Path) -> dict[str,Any]:
    rel=path.relative_to(TSB_ROOT).as_posix()
    text=read_text(path)
    num, typ=detect_number_and_type(text, path.name)
    symptom=extract_symptom(text, path.name)
    title=extract_title(text, path.name, symptom)
    supers=extract_supersession(text, path.name)
    archived = rel.lower().startswith("archive/superseded/")
    name_sup = any(x in rel.lower() for x in ["superseded", "superseeded", "obsolete", "replaced"])
    needs = False
    reasons=[]
    if not num: needs=True; reasons.append("number not detected")
    if not extract_models(text, path.name): reasons.append("model not confidently detected")
    if not extract_year_range(text, path.name): reasons.append("year range not confidently detected")
    if not symptom: reasons.append("symptom not confidently detected")
    if reasons: needs=True
    search_text = " ".join([path.stem, num, typ, title, symptom, text[:6000]])
    return {
        "tsbNumber": num,
        "bulletinNumber": num,
        "documentNumber": num,
        "documentType": typ,
        "title": title,
        "model": extract_models(text, path.name),
        "yearRange": extract_year_range(text, path.name),
        "engine": extract_engines(text, path.name),
        "symptom": symptom,
        "supersedes": supers["supersedes"],
        "supersededBy": supers["supersededBy"],
        "status": "Superseded" if archived or name_sup else "Current",
        "file": rel,
        "archivedFrom": "",
        "needsReview": needs,
        "reviewReason": "; ".join(reasons),
        "sourceQuality": "PDF text extracted" if text else "Filename only - PDF text not extracted",
        "textPreview": clean_space(text[:700]),
        "searchText": clean_space(search_text),
    }


def listify(v):
    if not v: return []
    if isinstance(v, list): return [str(x) for x in v if x]
    return [str(v)]


def apply_corrections(items: list[dict[str,Any]]) -> None:
    corr=load_corrections()
    by={normalise_doc_number(i.get('documentNumber','')):i for i in items if i.get('documentNumber')}
    for old,new in corr.get('supersessions',{}).items():
        oldn=normalise_doc_number(old); newn=normalise_doc_number(new)
        if oldn in by:
            by[oldn]['status']='Superseded'
            by[oldn]['supersededBy']=uniq(listify(by[oldn].get('supersededBy'))+[newn])
        if newn in by:
            by[newn]['supersedes']=uniq(listify(by[newn].get('supersedes'))+[oldn])
    for num,meta in corr.get('metadata',{}).items():
        n=normalise_doc_number(num)
        if n in by and isinstance(meta, dict):
            for k,v in meta.items(): by[n][k]=v
            by[n]['needsReview']=False
            by[n]['reviewReason']='manual correction applied'


def cross_link(items: list[dict[str,Any]]) -> None:
    by={normalise_doc_number(i.get('documentNumber','')):i for i in items if i.get('documentNumber')}
    for item in items:
        current=normalise_doc_number(item.get('documentNumber',''))
        for old in listify(item.get('supersedes')):
            oldn=normalise_doc_number(old)
            if oldn in by and current:
                by[oldn]['status']='Superseded'
                by[oldn]['supersededBy']=uniq(listify(by[oldn].get('supersededBy'))+[current])
        for new in listify(item.get('supersededBy')):
            newn=normalise_doc_number(new)
            item['status']='Superseded'
            if newn in by and current:
                by[newn]['supersedes']=uniq(listify(by[newn].get('supersedes'))+[current])


def move_superseded(items: list[dict[str,Any]]) -> bool:
    if not MOVE_SUPERSEDED: return False
    changed=False; ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        if item.get('status') != 'Superseded': continue
        rel=item.get('file','')
        if not rel.startswith('pdf/'): continue
        src=TSB_ROOT / rel
        if not src.exists(): continue
        dest=ARCHIVE_DIR / src.name
        if dest.exists():
            stem,suf=dest.stem,dest.suffix; n=2
            while dest.exists():
                dest=ARCHIVE_DIR / f"{stem}-{n}{suf}"; n+=1
        shutil.move(str(src), str(dest))
        item['archivedFrom']=rel
        item['file']=dest.relative_to(TSB_ROOT).as_posix()
        changed=True
    return changed


def sort_key(item):
    n=item.get('documentNumber') or ''
    # newest TSB 26-xxxx first, then current before superseded
    nums=[int(x) for x in re.findall(r"\d+", n)]
    return (item.get('status')=='Superseded', -nums[0] if nums else 999, -nums[1] if len(nums)>1 else 0, n)


def build() -> list[dict[str,Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True); PDF_DIR.mkdir(parents=True, exist_ok=True); ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    paths=sorted(list(PDF_DIR.rglob('*.pdf')) + list(ARCHIVE_DIR.rglob('*.pdf')))
    items=[scan_one(p) for p in paths]
    apply_corrections(items); cross_link(items)
    if move_superseded(items):
        paths=sorted(list(PDF_DIR.rglob('*.pdf')) + list(ARCHIVE_DIR.rglob('*.pdf')))
        items=[scan_one(p) for p in paths]
        apply_corrections(items); cross_link(items)
    items.sort(key=sort_key)
    return items


def main():
    items=build()
    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Indexed {len(items)} Ford bulletin PDF(s) into {INDEX_FILE.relative_to(ROOT)}")
    review=sum(1 for i in items if i.get('needsReview'))
    if review: print(f"{review} item(s) marked Needs review. Use Ford/TSB/data/manual-corrections.json for fixes.")

if __name__ == '__main__': main()

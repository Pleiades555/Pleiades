#!/usr/bin/env python3
"""
Pleiades Ford TSB/FSA/SSM indexer v4.

Fixes found from live testing, especially programme numbers like 23P23, plus multi-line concern extraction:
- Accepts Ford programme/campaign numbers: 23P23, 23N06, 23S33, 23Bxx, 25Cxx, 25Mxx, plus -S1/-S2 supplements.
- Gives highest priority to the filename and Ford header fields, not random body numbers.
- Better title selection from Program Title / Subject / header line immediately after the bulletin number.
- Better year extraction by looking for Model Year/Affected Vehicles context and avoiding publication dates.
- Better concern/symptom extraction from Issue / Condition / Reason For This Program / In some affected vehicles.
- Concern/symptom can now span multiple wrapped PDF lines and stops only at real Ford section boundaries.
- Writes a QA report to Ford/TSB/data/tsb-review-report.json for anything uncertain.

Run locally:
  python Ford/TSB/scripts/generate-tsb-index.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TSB_ROOT = ROOT / "Ford" / "TSB"
PDF_DIR = TSB_ROOT / "pdf"
ARCHIVE_DIR = TSB_ROOT / "archive" / "superseded"
DATA_DIR = TSB_ROOT / "data"
INDEX_FILE = DATA_DIR / "tsb-index.json"
REVIEW_FILE = DATA_DIR / "tsb-review-report.json"
CORRECTIONS_FILE = DATA_DIR / "manual-corrections.json"
MOVE_SUPERSEDED = os.environ.get("MOVE_SUPERSEDED", "true").lower() in {"1", "true", "yes"}

# Ford/Lincoln models likely to occur in AU/US bulletins. Add to this list over time.
MODEL_ALIASES = {
    "Ranger": ["ranger", "px ranger", "px2", "px3", "next-gen ranger", "next gen ranger"],
    "Everest": ["everest", "ua everest", "next-gen everest", "next gen everest"],
    "F-150": ["f-150", "f150", "f 150"],
    "Super Duty": ["super duty", "f-250", "f250", "f-350", "f350", "f-450", "f450", "f-550", "f550"],
    "Mustang": ["mustang"],
    "Mustang Mach-E": ["mustang mach-e", "mach-e", "mache"],
    "Transit": ["transit", "transit custom", "tourneo"],
    "E-Transit": ["e-transit", "etransit"],
    "Escape": ["escape", "kuga"],
    "Focus": ["focus"],
    "Fiesta": ["fiesta"],
    "Puma": ["puma"],
    "Mondeo": ["mondeo"],
    "Endura": ["endura", "edge"],
    "Explorer": ["explorer"],
    "Expedition": ["expedition"],
    "Bronco": ["bronco", "bronco sport"],
    "Maverick": ["maverick"],
    "Falcon": ["falcon", "fg", "fgx", "ba", "bf"],
    "Territory": ["territory"],
    "Courier": ["courier"],
    "Lincoln Navigator": ["navigator"],
    "Lincoln Aviator": ["aviator"],
    "Lincoln Corsair": ["corsair"],
}

ENGINES = [
    "P5AT", "P5BT", "P4AT", "PUMA", "EcoBoost", "Power Stroke", "PowerStroke", "Duratorq", "Duratec",
    "Barra", "Coyote", "Godzilla", "Lion", "Dragon", "Panther", "10R80", "10R60", "MT82",
    "1.0L", "1.5L", "1.6L", "2.0L", "2.2L", "2.3L", "2.7L", "3.0L", "3.2L", "3.5L", "5.0L", "6.2L", "6.7L", "7.3L"
]

# Key formats. PROGRAM_RE intentionally accepts 23P23, 23N06 and supplements like 23S33-S1.
TSB_RE = re.compile(r"\b(\d{2}-\d{3,5})(?:\b|(?=[^0-9]))", re.I)
PROGRAM_RE = re.compile(r"\b(\d{2}[A-Z]\d{2,5}(?:[- ]?S\d+)?)\b", re.I)
SSM_RE = re.compile(r"\bSSM\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{5,6})\b", re.I)

BAD_TITLE_RE = re.compile(
    r"(ford motor company|copyright|page \d+|printed copies|technical service bulletin|customer satisfaction program$|field service action$|summary:$|publication date|attachment|dealer bulletin|important safety recall|new!|issued|expiration date|program terms|labor allowance|parts requirements|owner notification|service procedure|mobile service)",
    re.I,
)
BAD_VALUE_RE = re.compile(r"^(yes|no|n/a|none|ford|lincoln|model|vehicle|page|date|time|dealer|service|parts|labor)$", re.I)

DOC_TYPE_BY_LETTER = {
    "S": "Safety Recall / FSA",
    "B": "Field Service Action",
    "C": "Compliance Recall / FSA",
    "M": "Customer Satisfaction Program",
    "N": "Customer Satisfaction Program",
    "P": "Customer Satisfaction Program",
}


def clean_space(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip(" \t\r\n-|:;,.•")


def clean_line(s: Any) -> str:
    s = str(s or "").replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s).strip(" \t\r\n|:;,.•")
    return s


def uniq(seq):
    out, seen = [], set()
    for x in seq:
        x = clean_space(x)
        if not x:
            continue
        k = x.lower()
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def read_text(path: Path) -> str:
    # First 12 pages catches Ford header, issue, vehicles and supersession without indexing huge bodies.
    try:
        import fitz  # PyMuPDF
        parts = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                if i >= 12:
                    break
                parts.append(page.get_text("text") or "")
        return "\n".join(parts)
    except Exception:
        pass
    try:
        from pypdf import PdfReader
        r = PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in r.pages[:12])
    except Exception:
        return ""


def all_lines(text: str, limit: int = 16000) -> list[str]:
    return [clean_line(x) for x in re.split(r"[\r\n]+", text[:limit]) if clean_line(x)]


def normalise_doc_number(v: str) -> str:
    v = clean_space(v).upper().replace(" ", "")
    v = re.sub(r"^(TSB|ARTICLE|BULLETIN|FSA|RECALL|SSM|PROGRAM|CAMPAIGN)[:#-]*", "", v)
    v = re.sub(r"(?<=\d{2}[A-Z]\d{2,5})-?S(\d+)$", r"-S\1", v)
    if re.fullmatch(r"\d{5,6}", v):
        return "SSM" + v
    return v


def classify_number(num: str, context: str = "") -> str:
    n = normalise_doc_number(num)
    if TSB_RE.fullmatch(n):
        return "TSB"
    if n.startswith("SSM"):
        return "SSM"
    m = re.fullmatch(r"\d{2}([A-Z])\d{2,5}(?:-S\d+)?", n)
    if m:
        letter = m.group(1).upper()
        ctx = context.lower()
        if "safety recall" in ctx or letter == "S":
            return "Safety Recall / FSA"
        return DOC_TYPE_BY_LETTER.get(letter, "Campaign / FSA")
    return "Bulletin"


def number_candidates(zone: str, zone_priority: int) -> list[tuple[int, int, str, str, str]]:
    """Return priority, position, type, number, context."""
    cands: list[tuple[int, int, str, str, str]] = []
    # Explicit labels are very strong.
    explicit = [
        (re.compile(r"\b(?:TSB|Technical Service Bulletin|Article|Bulletin)\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{2}-\d{3,5})\b", re.I), "TSB", 0),
        (re.compile(r"\b(?:Field Service Action|FSA|Recall|Safety Recall|Customer Satisfaction Program|Program|Campaign)\s*(?:No\.?|Number|#)?\s*[:#-]?\s*(\d{2}[A-Z]\d{2,5}(?:[- ]?S\d+)?)\b", re.I), "FSA", 0),
        (SSM_RE, "SSM", 0),
    ]
    for pat, typ, boost in explicit:
        for m in pat.finditer(zone):
            val = m.group(1)
            if typ == "SSM" and not str(val).upper().startswith("SSM"):
                val = "SSM" + val
            ctx = zone[max(0, m.start() - 120):m.end() + 120]
            cands.append((zone_priority + boost, m.start(), typ, normalise_doc_number(val), ctx))
    # Bare filename/header formats. Programme bare matches are safe in filename and first header only.
    for m in TSB_RE.finditer(zone):
        ctx = zone[max(0, m.start() - 120):m.end() + 120]
        cands.append((zone_priority + 6, m.start(), "TSB", normalise_doc_number(m.group(1)), ctx))
    for m in PROGRAM_RE.finditer(zone):
        val = normalise_doc_number(m.group(1))
        ctx = zone[max(0, m.start() - 120):m.end() + 120]
        # Avoid matching part/catalog numbers in the body; accept programme pattern only near Ford wording unless filename/header priority.
        if zone_priority <= 3 or re.search(r"program|campaign|recall|field service action|customer satisfaction|safety", ctx, re.I):
            cands.append((zone_priority + 7, m.start(), "FSA", val, ctx))
    for m in SSM_RE.finditer(zone):
        ctx = zone[max(0, m.start() - 120):m.end() + 120]
        cands.append((zone_priority + 4, m.start(), "SSM", "SSM" + m.group(1), ctx))
    return cands


def detect_number_and_type(text: str, filename: str) -> tuple[str, str]:
    stem = Path(filename).stem
    header = "\n".join(all_lines(text, 4500)[:80])
    zones = [(stem, 0), (header, 2), (text[:3500], 8)]
    cands: list[tuple[int, int, str, str, str]] = []
    for zone, pri in zones:
        cands.extend(number_candidates(zone, pri))
    if not cands:
        return "", "Bulletin"
    # Deduplicate, choose earliest/highest-quality.
    cands.sort(key=lambda x: (x[0], x[1]))
    num = cands[0][3]
    return num, classify_number(num, cands[0][4])


def is_stop_label(line: str) -> bool:
    """True when a PDF line is probably the next Ford bulletin section/header, not a continuation."""
    l = clean_space(line)
    if not l:
        return True
    stop_patterns = [
        r"^(model|model year|vehicle|vehicles affected|affected vehicles|vehicle line|engine|transmission|issue date|publication date|date|article|bulletin|tsb|fsa|ssm|program number|campaign number)\b\s*[:\-]?",
        r"^(action|service action|service procedure|repair procedure|parts requirements|parts required|labor allowance|warranty status|warranty|claim coding|causal part|dealer coding|owner notification|attachments?|summary|description)\b\s*[:\-]?",
        r"^(new!|important|note:|caution:|warning:|dealer bulletin|technical service bulletin|customer satisfaction program|field service action|safety recall)\b",
        r"^(page\s+\d+|copyright|ford motor company|printed copies)\b",
    ]
    return any(re.search(p, l, re.I) for p in stop_patterns)


def is_probable_table_or_noise(line: str) -> bool:
    l = clean_space(line)
    if not l:
        return True
    if BAD_TITLE_RE.search(l):
        return True
    # Keep normal long sentences, reject obvious table fragments.
    if re.fullmatch(r"[A-Z0-9 /._-]{1,18}", l) and len(l.split()) <= 3:
        return True
    if re.search(r"^(yes|no|n/a|none)$", l, re.I):
        return True
    return False


def labelled_multiline_value(text: str, labels: list[str], max_chars: int = 900, max_lines: int = 8) -> str:
    """Extract a label value that may wrap across multiple PDF text lines.

    Ford PDFs often split Issue/Reason For This Program into several visual lines.
    Earlier versions joined only one continuation line, which cut off concerns.
    This version keeps joining until a real section header/table/header/footer is reached.
    """
    ls = all_lines(text, 22000)
    label_re = re.compile(r"^(" + "|".join(re.escape(x) for x in labels) + r")\s*[:\-–]?\s*(.*)$", re.I)
    for i, line in enumerate(ls):
        m = label_re.match(line)
        if not m:
            continue
        parts = []
        first = clean_space(m.group(2))
        if first and not BAD_VALUE_RE.match(first) and not is_probable_table_or_noise(first):
            parts.append(first)
        for j in range(i + 1, min(len(ls), i + 1 + max_lines)):
            nxt = clean_space(ls[j])
            if not nxt:
                break
            if is_stop_label(nxt):
                break
            if is_probable_table_or_noise(nxt) and parts:
                break
            # Stop if the PDF has reached a new labelled field, but do not stop on normal sentence punctuation.
            if re.match(r"^[A-Za-z][A-Za-z /]{2,42}\s*[:\-]", nxt) and not re.search(r"\b(may|can|could|will|has|have|is|are|was|were|with|without|during|when|while)\b", nxt, re.I):
                break
            parts.append(nxt)
            joined = clean_space(" ".join(parts))
            # Enough text once a complete sentence is captured; keep joining if sentence ends with comma/and/or.
            if len(joined) >= max_chars:
                break
            if len(joined) > 120 and re.search(r"[.!?]$", joined) and j + 1 < len(ls) and is_stop_label(ls[j + 1]):
                break
        val = clean_space(" ".join(parts))
        val = re.sub(r"\s+([,.;:!?])", r"\1", val)
        if val and not BAD_TITLE_RE.search(val) and not BAD_VALUE_RE.match(val):
            return val[:max_chars]
    return ""


def labelled_value(text: str, labels: list[str], max_chars: int = 320) -> str:
    # Backwards-compatible wrapper. Uses the safer multiline extractor.
    return labelled_multiline_value(text, labels, max_chars=max_chars, max_lines=5)

def extract_header_title(text: str, filename: str, doc_number: str) -> str:
    ls = all_lines(text, 9000)
    # If line contains the doc number/program number, the next useful line is usually the title.
    n = re.escape(normalise_doc_number(doc_number)) if doc_number else ""
    if n:
        loose = re.compile(n.replace("\\-", "[- ]?"), re.I)
        for i, line in enumerate(ls[:100]):
            if not loose.search(line):
                continue
            for nxt in ls[i + 1:i + 8]:
                if is_good_title(nxt, doc_number):
                    return clean_title(nxt, doc_number)
    return ""


def is_good_title(line: str, doc_number: str = "") -> bool:
    line = clean_space(line)
    if len(line) < 8 or len(line) > 220:
        return False
    if BAD_TITLE_RE.search(line) or BAD_VALUE_RE.match(line):
        return False
    if doc_number and normalise_doc_number(doc_number) == normalise_doc_number(line):
        return False
    if re.fullmatch(r"[A-Z ]{3,35}", line) and any(x in line.lower() for x in ["program", "action", "bulletin"]):
        return False
    # Strong signs of a Ford title/concern.
    if re.search(r"\b(update|replace|replacement|inspect|inspection|repair|reprogram|software|dtc|illuminated|noise|rattle|leak|fracture|crack|battery|transmission|camera|brake|door|module|charging|fire|latch|axle|turbocharger|malfunction|indicator|concern)\b", line, re.I):
        return True
    # Otherwise accept sentence-case lines near top.
    return bool(re.search(r"[a-z]", line) and len(line.split()) >= 3)


def clean_title(title: str, doc_number: str = "") -> str:
    t = clean_space(title)
    if doc_number:
        t = re.sub(re.escape(doc_number), "", t, flags=re.I)
    t = re.sub(r"^(title|subject|program title|summary)\s*[:\-]\s*", "", t, flags=re.I)
    t = re.sub(r"\s+\|\s+.*$", "", t)
    return clean_space(t)[:190]


def extract_title(text: str, filename: str, symptom: str, doc_number: str) -> str:
    for labels in [
        ["Program Title", "Campaign Title", "Bulletin Title", "Title", "Subject"],
        ["Reason For This Program", "Reason For This Field Service Action", "Reason For This Bulletin"],
    ]:
        v = labelled_value(text, labels, 190)
        if v:
            return clean_title(v, doc_number)
    v = extract_header_title(text, filename, doc_number)
    if v:
        return v
    if symptom:
        s = re.sub(r"^(Some|Certain)\s+", "", symptom, flags=re.I)
        s = re.sub(r"\bmay (?:exhibit|experience)\b", "-", s, flags=re.I)
        return clean_title(s, doc_number)
    stem = re.sub(r"[_-]+", " ", Path(filename).stem)
    stem = re.sub(r"\b\d{2}-\d{3,5}\b|\b\d{2}[A-Z]\d{2,5}(?:[- ]?S\d+)?\b|\bSSM\s*\d{5,6}\b", " ", stem, flags=re.I)
    return clean_title(stem, doc_number)


def extract_symptom(text: str, filename: str) -> str:
    # TSBs use Issue/Condition; FSA/CSPs often use Reason for this Program and "In some affected vehicles...".
    # Use multiline extraction because Ford PDF text frequently wraps concerns over several short lines.
    v = labelled_multiline_value(text, [
        "Issue", "Condition", "Concern", "Customer Concern", "Customer Symptom", "Symptom",
        "Reason For This Bulletin", "Reason For This Program", "Reason For This Field Service Action",
        "Reason For This Safety Recall", "Summary", "Description"
    ], max_chars=900, max_lines=10)
    if v:
        return v

    flat = clean_space(text[:22000])
    sentence_patterns = [
        r"In some of the affected vehicles[^.]{20,900}\.",
        r"In the affected vehicles[^.]{20,900}\.",
        r"Some (?:\d{4}[-–]\d{4} )?[^.]{0,220}\bmay (?:exhibit|experience|have|show|display)[^.]{20,900}\.",
        r"Certain (?:\d{4}[-–]\d{4} )?[^.]{0,220}\bmay (?:exhibit|experience|have|show|display)[^.]{20,900}\.",
        r"[^.]{0,220}\bmay (?:exhibit|experience|have|show|display)[^.]{20,900}\.",
    ]
    for pat in sentence_patterns:
        m = re.search(pat, flat, re.I)
        if m:
            val = clean_space(m.group(0))
            if not BAD_TITLE_RE.search(val):
                return val[:900]

    # Last fallback from filename.
    stem = re.sub(r"\b\d{2}-\d{3,5}\b|\b\d{2}[A-Z]\d{2,5}(?:[- ]?S\d+)?\b|\bSSM\s*\d{5,6}\b", " ", Path(filename).stem, flags=re.I)
    stem = re.sub(r"[_-]+", " ", stem)
    return clean_space(stem)[:260]


def extract_vehicle_zone(text: str) -> str:
    ls = all_lines(text, 18000)
    heads = ["Affected Vehicles", "Vehicles Affected", "Vehicle Line", "Model", "Model Year", "Vehicle", "Ford", "Lincoln"]
    out = []
    for i, line in enumerate(ls):
        if any(re.fullmatch(h + r"\s*[:\-]?", line, re.I) or re.match(h + r"\s*[:\-]", line, re.I) for h in heads):
            out.extend(ls[i:i + 14])
    return "\n".join(out)


def extract_models(text: str, filename: str) -> list[str]:
    zones = [Path(filename).stem, extract_vehicle_zone(text), text[:9000]]
    found = []
    for zone in zones:
        hay = zone.lower()
        for model, aliases in MODEL_ALIASES.items():
            if any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", hay, re.I) for a in aliases):
                found.append(model)
        if found:
            break
    return uniq(found)


def extract_year_range(text: str, filename: str) -> str:
    zones = [Path(filename).stem, extract_vehicle_zone(text), text[:11000]]
    scored: list[tuple[int, int, int]] = []
    singles: list[tuple[int, int]] = []
    for zi, zone in enumerate(zones):
        zone = zone.replace("\u2013", "-").replace("\u2014", "-")
        for m in re.finditer(r"\b((?:19|20)\d{2})\s*(?:-|to|through|thru|/)\s*((?:19|20)\d{2})\b", zone, re.I):
            a, b = int(m.group(1)), int(m.group(2))
            if not (1990 <= a <= 2036 and 1990 <= b <= 2036):
                continue
            around = zone[max(0, m.start() - 100):m.end() + 100].lower()
            score = 20 - zi * 5
            if any(w in around for w in ["model year", "model", "vehicle", "vehicles", "affected", "built", "from", "through"]):
                score += 10
            if any(w in around for w in ["publication", "copyright", "date", "printed"]):
                score -= 8
            scored.append((score, min(a, b), max(a, b)))
        # 2021MY / 2021 Model Year / MY2021
        for m in re.finditer(r"\b(?:MY\s*)?((?:19|20)\d{2})\s*(?:MY|model year|model-year|model|vehicles?|ranger|everest|f-150|transit|mustang|escape|explorer|bronco|maverick)\b", zone, re.I):
            y = int(m.group(1))
            around = zone[max(0, m.start() - 90):m.end() + 90].lower()
            if any(w in around for w in ["publication", "copyright", "printed"]):
                continue
            score = 12 - zi * 4
            if any(w in around for w in ["model year", "affected", "vehicles", "built"]):
                score += 8
            singles.append((score, y))
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1], x[2]))
        a, b = scored[0][1], scored[0][2]
        return str(a) if a == b else f"{a}-{b}"
    if singles:
        # Keep only high-scoring model-year singles, collapse if consecutive.
        maxscore = max(s for s, _ in singles)
        years = sorted(set(y for s, y in singles if s >= maxscore - 3))
        if len(years) >= 2 and years[-1] - years[0] <= len(years) + 1:
            return f"{years[0]}-{years[-1]}"
        return ", ".join(map(str, years[:8]))
    return ""


def extract_engines(text: str, filename: str) -> list[str]:
    hay = Path(filename).stem + "\n" + text[:9000]
    found = []
    for e in ENGINES:
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(e) + r"(?![A-Za-z0-9])", hay, re.I):
            found.append(e)
    return uniq(found)


def extract_supersession(text: str, filename: str) -> dict[str, list[str]]:
    sample = Path(filename).stem + "\n" + text[:18000]
    out = {"supersedes": [], "supersededBy": []}
    old_patterns = [
        r"(?:supersedes|supercedes|replaces|this bulletin replaces|this article supersedes|this program supersedes|previously released as)\s+(?:TSB|SSM|FSA|bulletin|article|recall|program|campaign)?\s*[:#-]?\s*([A-Z0-9 -]{4,20})",
        r"(?:supersedes prior|supersedes previous)[^\n.]{0,80}?\b(\d{2}(?:-\d{3,5}|[A-Z]\d{2,5}(?:[- ]?S\d+)?))\b",
    ]
    new_patterns = [
        r"(?:superseded by|superceded by|replaced by)\s+(?:TSB|SSM|FSA|bulletin|article|recall|program|campaign)?\s*[:#-]?\s*([A-Z0-9 -]{4,20})",
    ]
    for p in old_patterns:
        for m in re.finditer(p, sample, re.I):
            n, _ = detect_number_and_type(m.group(1), m.group(1))
            if n:
                out["supersedes"].append(n)
    for p in new_patterns:
        for m in re.finditer(p, sample, re.I):
            n, _ = detect_number_and_type(m.group(1), m.group(1))
            if n:
                out["supersededBy"].append(n)
    out["supersedes"] = uniq(out["supersedes"])
    out["supersededBy"] = uniq(out["supersededBy"])
    return out


def load_corrections() -> dict[str, Any]:
    default = {"supersessions": {}, "metadata": {}, "files": {}}
    if not CORRECTIONS_FILE.exists():
        return default
    try:
        data = json.loads(CORRECTIONS_FILE.read_text(encoding="utf-8"))
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default


def listify(v):
    if not v:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if x]
    return [str(v)]


def apply_meta(item: dict[str, Any], meta: dict[str, Any], reason: str = "manual correction applied") -> None:
    for k, v in meta.items():
        item[k] = v
    item["needsReview"] = False
    item["reviewReason"] = reason


def scan_one(path: Path) -> dict[str, Any]:
    rel = path.relative_to(TSB_ROOT).as_posix()
    text = read_text(path)
    num, typ = detect_number_and_type(text, path.name)
    symptom = extract_symptom(text, path.name)
    title = extract_title(text, path.name, symptom, num)
    models = extract_models(text, path.name)
    year_range = extract_year_range(text, path.name)
    supers = extract_supersession(text, path.name)
    archived = rel.lower().startswith("archive/superseded/")
    name_sup = any(x in rel.lower() for x in ["superseded", "superseeded", "obsolete", "replaced"])
    reasons = []
    if not num:
        reasons.append("number not detected")
    if not models:
        reasons.append("model not confidently detected")
    if not year_range:
        reasons.append("year range not confidently detected")
    if not symptom:
        reasons.append("concern/symptom not confidently detected")
    if title and symptom and title == symptom and len(title) > 150:
        reasons.append("title may be too long")
    search_text = " ".join([path.stem, num, typ, title, symptom, year_range, " ".join(models), text[:7000]])
    return {
        "tsbNumber": num,
        "bulletinNumber": num,
        "documentNumber": num,
        "documentType": typ,
        "title": title,
        "model": models,
        "yearRange": year_range,
        "engine": extract_engines(text, path.name),
        "symptom": symptom,
        "supersedes": supers["supersedes"],
        "supersededBy": supers["supersededBy"],
        "status": "Superseded" if archived or name_sup else "Current",
        "file": rel,
        "archivedFrom": "",
        "needsReview": bool(reasons),
        "reviewReason": "; ".join(reasons),
        "sourceQuality": "PDF text extracted" if text else "Filename only - PDF text not extracted",
        "textPreview": clean_space(text[:900]),
        "searchText": clean_space(search_text),
    }


def apply_corrections(items: list[dict[str, Any]]) -> None:
    corr = load_corrections()
    by = {normalise_doc_number(i.get("documentNumber", "")): i for i in items if i.get("documentNumber")}
    by_file = {i.get("file", "").lower(): i for i in items if i.get("file")}
    by_basename = {Path(i.get("file", "")).name.lower(): i for i in items if i.get("file")}

    for old, new in corr.get("supersessions", {}).items():
        oldn = normalise_doc_number(old)
        newn = normalise_doc_number(new)
        if oldn in by:
            by[oldn]["status"] = "Superseded"
            by[oldn]["supersededBy"] = uniq(listify(by[oldn].get("supersededBy")) + [newn])
        if newn in by:
            by[newn]["supersedes"] = uniq(listify(by[newn].get("supersedes")) + [oldn])

    for num, meta in corr.get("metadata", {}).items():
        n = normalise_doc_number(num)
        if n in by and isinstance(meta, dict):
            apply_meta(by[n], meta)

    # New: correct by filename/path when the document number is not yet detected correctly.
    for file_key, meta in corr.get("files", {}).items():
        if not isinstance(meta, dict):
            continue
        k = file_key.lower().replace("\\", "/")
        item = by_file.get(k) or by_basename.get(Path(k).name.lower())
        if item:
            apply_meta(item, meta, "manual file correction applied")


def cross_link(items: list[dict[str, Any]]) -> None:
    by = {normalise_doc_number(i.get("documentNumber", "")): i for i in items if i.get("documentNumber")}
    for item in items:
        current = normalise_doc_number(item.get("documentNumber", ""))
        for old in listify(item.get("supersedes")):
            oldn = normalise_doc_number(old)
            if oldn in by and current:
                by[oldn]["status"] = "Superseded"
                by[oldn]["supersededBy"] = uniq(listify(by[oldn].get("supersededBy")) + [current])
        for new in listify(item.get("supersededBy")):
            newn = normalise_doc_number(new)
            item["status"] = "Superseded"
            if newn in by and current:
                by[newn]["supersedes"] = uniq(listify(by[newn].get("supersedes")) + [current])


def move_superseded(items: list[dict[str, Any]]) -> bool:
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
        if dest.exists():
            stem, suf = dest.stem, dest.suffix
            n = 2
            while dest.exists():
                dest = ARCHIVE_DIR / f"{stem}-{n}{suf}"
                n += 1
        shutil.move(str(src), str(dest))
        item["archivedFrom"] = rel
        item["file"] = dest.relative_to(TSB_ROOT).as_posix()
        changed = True
    return changed


def sort_key(item: dict[str, Any]):
    n = item.get("documentNumber") or ""
    nums = [int(x) for x in re.findall(r"\d+", n)]
    return (item.get("status") == "Superseded", -nums[0] if nums else 999, -nums[1] if len(nums) > 1 else 0, n)


def build() -> list[dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))
    items = [scan_one(p) for p in paths]
    apply_corrections(items)
    cross_link(items)
    if move_superseded(items):
        paths = sorted(list(PDF_DIR.rglob("*.pdf")) + list(ARCHIVE_DIR.rglob("*.pdf")))
        items = [scan_one(p) for p in paths]
        apply_corrections(items)
        cross_link(items)
    items.sort(key=sort_key)
    return items


def write_review(items: list[dict[str, Any]]) -> None:
    review = [
        {
            "file": i.get("file"),
            "documentNumber": i.get("documentNumber"),
            "documentType": i.get("documentType"),
            "title": i.get("title"),
            "model": i.get("model"),
            "yearRange": i.get("yearRange"),
            "symptom": i.get("symptom"),
            "reviewReason": i.get("reviewReason"),
        }
        for i in items if i.get("needsReview")
    ]
    REVIEW_FILE.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    items = build()
    INDEX_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    write_review(items)
    print(f"Indexed {len(items)} Ford bulletin PDF(s) into {INDEX_FILE.relative_to(ROOT)}")
    review = sum(1 for i in items if i.get("needsReview"))
    if review:
        print(f"{review} item(s) marked Needs review. Check {REVIEW_FILE.relative_to(ROOT)} and use Ford/TSB/data/manual-corrections.json for fixes.")


if __name__ == "__main__":
    main()

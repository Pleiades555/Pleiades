#!/usr/bin/env python3
from __future__ import annotations
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / 'fluids_master.json'
IMPORT = ROOT / 'nissan_fluids_import.csv'

MANUAL_SOURCES = {'aw', 'manually uploaded by ashton white', 'manual upload by ashton white'}

def norm(v):
    return str(v or '').strip().upper().replace(' ', '')

def key(row):
    return (norm(row.get('brand')), norm(row.get('part_number') or row.get('engineering_part_number') or row.get('description')), norm(row.get('volume')))

def is_manual(row):
    return str(row.get('source') or '').strip().lower() in MANUAL_SOURCES or str(row.get('market_status') or '').strip().lower() == 'local-supply'

master = json.loads(MASTER.read_text(encoding='utf-8'))
with IMPORT.open(encoding='utf-8-sig', newline='') as f:
    incoming = list(csv.DictReader(f))

index = {key(r): i for i, r in enumerate(master) if isinstance(r, dict)}
added = updated = preserved = 0

for new in incoming:
    k = key(new)
    if not k[0] or not k[1]:
        continue
    if k in index:
        old = master[index[k]]
        if is_manual(old) and not is_manual(new):
            # Keep local/manual values, only fill blanks and audit fields.
            merged = dict(new)
            merged.update({a:b for a,b in old.items() if b not in ('', None)})
            preserved += 1
        else:
            # Incoming Australian/local record wins, but preserve useful fields not supplied.
            merged = dict(old)
            merged.update({a:b for a,b in new.items() if b not in ('', None)})
            updated += 1
        master[index[k]] = merged
    else:
        master.append(new)
        index[k] = len(master)-1
        added += 1

MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Nissan merge complete: {added} added, {updated} updated, {preserved} manual/local records preserved; {len(master)} total records.')

import json,re,sys, pathlib
root=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((root/'data/canonical/pleiades-v4.json').read_text())
errors=[]
ids=set()
for coll,rows in data.items():
    if isinstance(rows,list):
        for r in rows:
            if isinstance(r,dict) and 'id' in r:
                if r['id'] in ids: errors.append(f'duplicate id {r["id"]}')
                ids.add(r['id'])
for v in data['vehicles']:
    for vin in v.get('exactVins',[]):
        if len(vin)!=17 or re.search('[IOQ]',vin): errors.append(f'invalid VIN {vin}')
    if v.get('engineRef') and v['engineRef'] not in ids: errors.append(f'missing engine ref {v["engineRef"]}')
    if v.get('transmissionRef') and v['transmissionRef'] not in ids: errors.append(f'missing transmission ref {v["transmissionRef"]}')
for p in pathlib.Path(root).rglob('*'):
    if p.is_file() and p.suffix in {'.html','.js','.json','.md'}:
        txt=p.read_text(errors='ignore')
        if re.search(r'\b[A-Z]:\\',txt): errors.append(f'unsafe local path {p}')
report={'ok':not errors,'errors':errors,'counts':{k:len(v) for k,v in data.items() if isinstance(v,list)}}
(root/'reports/validation-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2)); sys.exit(1 if errors else 0)

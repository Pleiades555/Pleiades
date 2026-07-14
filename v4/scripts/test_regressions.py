import json, pathlib, re, sys
root=pathlib.Path(__file__).resolve().parents[1]
vehicles=json.loads((root/'public/data/vehicles.json').read_text())
search=json.loads((root/'public/data/search-index.json').read_text())['items']
expect={'JF1BLEKN36G023480':'Liberty','JF2SH9KD39G009340':'Forester','SALFA23A87H021769':'Freelander 2','SALLSAA137A998181':'Range Rover Sport'}
def decode(vin):
    exact=[v for v in vehicles if vin in v.get('exactVins',[])]
    if exact: return exact[0]
    fps=[v for v in vehicles if any(vin.startswith(p) for p in v.get('vinPrefixes',[]))]
    fps.sort(key=lambda v:max([len(p) for p in v.get('vinPrefixes',[]) if vin.startswith(p)] or [0]), reverse=True)
    return fps[0] if fps else None
errors=[]
for vin,model in expect.items():
    got=decode(vin)
    if not got or got.get('model')!=model: errors.append(f'{vin} expected {model} got {got}')
for q in 'EZ30 EJ255 TY85 TY856WVCAA TY758VGZAA 276DT B6324S R160'.split():
    if not any(q.lower() in i['tokens'] for i in search): errors.append(f'search miss {q}')
# estimated visible
forester=decode('JF2SH9KD39G009340')
if 'differential:subaru-r160-rear-estimate' not in forester.get('differentialRefs',[]): errors.append('Forester R160 estimate not linked')
print('PASS' if not errors else '\n'.join(errors)); sys.exit(1 if errors else 0)

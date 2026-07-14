import pathlib,re,sys,json
root=pathlib.Path(__file__).resolve().parents[2]; errors=[]
for f in (root/'v4').rglob('*.html'):
    for href in re.findall(r'href="([^"]+)"', f.read_text(errors='ignore')):
        if href.startswith(('http','#','mailto:')) or href=='./': continue
        if not (f.parent/href).resolve().exists(): errors.append(f'{f.relative_to(root)} -> {href}')
(root/'v4/reports/broken-links-report.json').write_text(json.dumps({'items':errors},indent=2))
print('ok' if not errors else errors); sys.exit(1 if errors else 0)

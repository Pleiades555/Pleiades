import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[2]
finder_html = (root / 'v3/vin-intelligence.html').read_text()
main_html = (root / 'v3/index.html').read_text()
finder_js = (root / 'v3/assets/vin-intelligence.js').read_text()
references = json.loads((root / 'v4/public/data/vinReferences.json').read_text())

errors = []
for value in ('vinReferenceSearch', 'modelCodeBrowser', 'vinReferenceResults'):
    if f'id="{value}"' not in finder_html:
        errors.append(f'missing finder element {value}')

if './vin-intelligence.html' not in main_html:
    errors.append('main V3 navigation does not link the VIN reference finder')

if '../v4/public/data/vinReferences.json' not in finder_js:
    errors.append('finder does not load the canonical VIN reference dataset')

seen = set()
for row in references:
    vin = row.get('vin', '')
    if not re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', vin):
        errors.append(f'invalid VIN {vin}')
    if vin in seen:
        errors.append(f'duplicate VIN {vin}')
    seen.add(vin)
    if not row.get('modelCode'):
        errors.append(f'missing model code for {vin}')
    if not row.get('epcUsage'):
        errors.append(f'missing EPC warning for {vin}')

example = next((row for row in references if row.get('vin') == 'SALEA7AW8P2115516'), None)
if not example:
    errors.append('missing 2023 Defender D300 example VIN')
else:
    searchable = ' '.join(str(example.get(key, '')) for key in ('modelYear', 'model', 'powertrain', 'modelCode')).lower()
    for term in ('2023', 'defender', 'd300', 'l663'):
        if term not in searchable:
            errors.append(f'Defender D300 example missing searchable term {term}')

print('PASS' if not errors else '\n'.join(errors))
sys.exit(1 if errors else 0)

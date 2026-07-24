import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[2]
finder_html = (root / 'v3/vin-intelligence.html').read_text()
main_html = (root / 'v3/index.html').read_text()
finder_js = (root / 'v3/assets/vin-intelligence.js').read_text()
references = json.loads((root / 'v4/public/data/vinReferences.json').read_text())
vehicle_data = json.loads((root / 'v3/data/vehicles.json').read_text())
identifier_data = json.loads((root / 'v3/data/identifiers.json').read_text())

errors = []

for value in ('vinReferenceSearch', 'modelCodeBrowser', 'vinReferenceResults'):
    if f'id="{value}"' not in finder_html:
        errors.append(f'missing finder element {value}')

if './vin-intelligence.html' not in main_html:
    errors.append('main V3 navigation does not link the VIN reference finder')

if '../v4/public/data/vinReferences.json' not in finder_js:
    errors.append('finder does not load the canonical VIN reference dataset')

if './data/identifiers.json' not in finder_js:
    errors.append('finder does not load the V3 identifier register')

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

subaru_factory_vins = {
    'JF2SH9KD39G009340',
    'JF1BLEKN36G023480',
    'JF1GDFKH37G067898',
    'JF1GDFKH37G067421',
    'JF1GDFKH37G069458',
    'JF1GDFKH37G067528',
    'JF1GM8KDGYG002614',
    'JF1GM8KDGYG003262',
    'JF1GRFKH38G022767',
    'JF1GDBLH35G063168',
    'JF1GDBLH34G052121',
    'JF1GGGKD37G040581',
    'JF1GGGKD37G040569',
    'JF2AX7DR0BG302342',
}

stored_factory_vins = set()
for vehicle in vehicle_data.get('vehicles', []):
    stored_factory_vins.update(vehicle.get('exampleVins', []))
    stored_factory_vins.update(
        prefix for prefix in vehicle.get('vinPrefixes', [])
        if isinstance(prefix, str) and len(prefix) == 17
    )

for vin in sorted(subaru_factory_vins - stored_factory_vins):
    errors.append(f'missing previously supplied Subaru factory VIN {vin}')

required_identifiers = {
    '6ZZ00000GVB005008',
    '6ZZ00000GDB013732',
    '6ZZ50000GDB037137',
    '7AT0GFG9X22095221',
    '7AT06F69K22095221',
    'GVB005008',
    'GDB013732',
    'GDB037137',
    'BL5037631',
    'GDB014305',
    'GC8069605',
    'GDB037441',
    'GDB032120',
    'BES002239',
    'GC8070918',
    'GC8069576',
    'GC8069578',
    'GDB037768',
    'GDB031976',
    'GC8071357',
    'GC8069424',
    'GF8019830',
}

stored_identifiers = {
    row.get('identifier')
    for row in identifier_data.get('identifiers', [])
    if row.get('identifier')
}

for value in sorted(required_identifiers - stored_identifiers):
    errors.append(f'missing previously supplied Subaru identifier {value}')

for value in ('GC8069605', 'GDB037441', '6ZZ00000GVB005008'):
    row = next((item for item in identifier_data.get('identifiers', []) if item.get('identifier') == value), None)
    if not row or not row.get('variant'):
        errors.append(f'{value} missing edition/variant label')
    if not row or not row.get('modelCode'):
        errors.append(f'{value} missing model code')

print('PASS' if not errors else '\n'.join(errors))
sys.exit(1 if errors else 0)

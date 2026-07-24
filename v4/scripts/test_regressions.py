import json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[1]
vehicles = json.loads((root / 'public/data/vehicles.json').read_text())
vin_references = json.loads((root / 'public/data/vinReferences.json').read_text())
generation_rules = json.loads((root / 'public/data/vinGenerationRules.json').read_text())
search = json.loads((root / 'public/data/search-index.json').read_text())['items']

expect = {
    'JF1BLEKN36G023480': 'Liberty',
    'JF2SH9KD39G009340': 'Forester',
    'SALFA23A87H021769': 'Freelander 2',
    'SALLSAA137A998181': 'Range Rover Sport',
    'SALEA7AW8P2115516': 'Defender',
    'SALKA9A90RA235568': 'Range Rover',
}


def decode(vin):
    exact = [vehicle for vehicle in vehicles if vin in vehicle.get('exactVins', [])]
    if exact:
        return {'type': 'vehicle', 'record': exact[0], 'match': 'exact'}

    exact_reference = [record for record in vin_references if record.get('vin') == vin]
    if exact_reference:
        return {'type': 'vin-reference', 'record': exact_reference[0], 'match': 'exact'}

    fingerprints = [
        (vehicle, prefix)
        for vehicle in vehicles
        for prefix in vehicle.get('vinPrefixes', [])
        if vin.startswith(prefix)
    ]
    fingerprints.sort(key=lambda match: len(match[1]), reverse=True)
    if fingerprints:
        return {'type': 'vehicle', 'record': fingerprints[0][0], 'match': fingerprints[0][1]}

    generations = [rule for rule in generation_rules if vin.startswith(rule.get('prefix', ''))]
    generations.sort(key=lambda rule: len(rule['prefix']), reverse=True)
    if generations:
        return {'type': 'generation', 'record': generations[0], 'match': generations[0]['prefix']}

    return None


def normalise(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').lower()).strip()


def reference_text(reference):
    values = [
        reference.get('vin'),
        reference.get('market'),
        reference.get('brand'),
        reference.get('model'),
        reference.get('modelCode'),
        reference.get('body'),
        reference.get('modelYear'),
        reference.get('advertisedYear'),
        reference.get('powertrain'),
        reference.get('variant'),
        reference.get('engineFamily'),
        reference.get('transmission'),
        reference.get('drivetrain'),
        reference.get('stockNumber'),
        *(reference.get('aliases') or []),
    ]
    return normalise(' '.join(str(value) for value in values if value))


def reference_matches(reference, query):
    terms = normalise(query).split()
    tokens = reference_text(reference).split()
    return all(any(token == term or token.startswith(term) or term in token for token in tokens) for term in terms)


errors = []
for vin, model in expect.items():
    result = decode(vin)
    got = result['record'] if result else None
    if not got or got.get('model') != model:
        errors.append(f'{vin} expected {model} got {got}')

for prefix, generation in {
    'JF2SG': 'SG',
    'JF2SH': 'SH',
    'JF2SK': 'SK',
    'JF2SL': 'SL',
}.items():
    # Synthetic suffix is used only to exercise deterministic prefix matching.
    result = decode(prefix + '123456789012')
    if not result or result['type'] != 'generation' or result['record'].get('generation') != generation:
        errors.append(f'{prefix} expected Forester {generation} generation fallback got {result}')

# A longer verified vehicle fingerprint must beat the shorter generation rule.
forester = decode('JF2SH9KD39G009340')
if not forester or forester['type'] != 'vehicle' or forester['match'] != 'exact':
    errors.append('Exact SH9 Forester record did not outrank JF2SH generation rule')

for query in 'EZ30 EJ255 TY85 TY856WVCAA TY758VGZAA 276DT B6324S R160'.split():
    if not any(query.lower() in item['tokens'] for item in search):
        errors.append(f'search miss {query}')

if 'differential:subaru-r160-rear-estimate' not in forester['record'].get('differentialRefs', []):
    errors.append('Forester R160 estimate not linked')

vins = [record.get('vin') for record in vin_references]
if len(vins) != len(set(vins)):
    errors.append('vinReferences.json contains duplicate VINs')

for record in vin_references:
    vin = record.get('vin', '')
    if not re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', vin):
        errors.append(f'invalid stored VIN {vin!r}')
    if not record.get('modelCode'):
        errors.append(f'{vin} missing modelCode')
    if not record.get('source', {}).get('url'):
        errors.append(f'{vin} missing public source URL')
    if not record.get('epcUsage'):
        errors.append(f'{vin} missing EPC usage warning')

example_hits = [record for record in vin_references if reference_matches(record, '2023 Defender D300')]
if not any(record.get('vin') == 'SALEA7AW8P2115516' for record in example_hits):
    errors.append('2023 Defender D300 lookup did not return SALEA7AW8P2115516')

model_code_hits = [record for record in vin_references if reference_matches(record, 'L663')]
if not model_code_hits or not all(record.get('model') == 'Defender' for record in model_code_hits):
    errors.append('L663 model-code lookup did not return Defender references')

progressive_hits = [record for record in vin_references if reference_matches(record, '2023 def d3')]
if not any(record.get('vin') == 'SALEA7AW8P2115516' for record in progressive_hits):
    errors.append('Progressive lookup 2023 def d3 did not return the D300 VIN')

partial_vin_hits = [record for record in vin_references if reference_matches(record, 'SALEA7AW8P')]
if not any(record.get('vin') == 'SALEA7AW8P2115516' for record in partial_vin_hits):
    errors.append('Partial VIN lookup did not return the full VIN')

print('PASS' if not errors else '\n'.join(errors))
sys.exit(1 if errors else 0)

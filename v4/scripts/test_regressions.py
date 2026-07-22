import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parents[1]
vehicles = json.loads((root / 'public/data/vehicles.json').read_text())
generation_rules = json.loads((root / 'public/data/vinGenerationRules.json').read_text())
search = json.loads((root / 'public/data/search-index.json').read_text())['items']

expect = {
    'JF1BLEKN36G023480': 'Liberty',
    'JF2SH9KD39G009340': 'Forester',
    'SALFA23A87H021769': 'Freelander 2',
    'SALLSAA137A998181': 'Range Rover Sport',
}


def decode(vin):
    exact = [vehicle for vehicle in vehicles if vin in vehicle.get('exactVins', [])]
    if exact:
        return {'type': 'vehicle', 'record': exact[0], 'match': 'exact'}

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

print('PASS' if not errors else '\n'.join(errors))
sys.exit(1 if errors else 0)

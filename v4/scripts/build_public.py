import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
json.loads((root/'data/canonical/pleiades-v4.json').read_text())
print('V4 static assets are committed under v4/public and v4/public/data')

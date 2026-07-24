# Pleiades V4 Preview

Static GitHub Pages-compatible preview at `/v4/index.html`. V4 keeps the legacy site intact and links back to `../Pleiades Version 3.html`.

The V4 landing page includes a progressive VIN / EPC reference finder. Queries can use a full or partial VIN, model year, model, powertrain, dealer stock number or model code such as `L663`. Exact publicly listed Australian VINs are stored in `public/data/vinReferences.json`; existing confirmed `vehicles.json` exact VINs are merged into the finder at runtime.

Reference VINs are examples for legitimate EPC lookup and do not guarantee part compatibility. See `docs/vin-reference-data.md` for the evidence and privacy policy.

Run `python3 v4/scripts/validate.py`, `python3 v4/scripts/test_regressions.py`, and `python3 v4/scripts/check_links.py` before changes are completed.

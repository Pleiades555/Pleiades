# Pleiades Version 3.8

Version 3 is a shared Australian-market vehicle knowledge application. It does not merge Inventory into the vehicle portal.

## VIN intelligence access

- Main application: `v3/index.html`
- VIN decoder: open **Decode a VIN** in the V3 sidebar
- VIN / EPC Reference Finder: `v3/vin-intelligence.html`
- Direct repository entry point: `VIN Intelligence.html`
- Canonical saved public VIN records: `v4/public/data/vinReferences.json`

The VIN / EPC Reference Finder searches progressively by year, model, body, powertrain, model code, stock number, partial VIN or full VIN. A result can be copied or sent directly to the main VIN decoder.

## Live V3 components

- Shared responsive application shell and navigation
- Clearly separated **Decode a VIN** and **Find an EPC VIN** workflows
- Progressive VIN / EPC reference search with model-code compatibility such as `L663`, `L405`, `L460`, `L461` and `L551`
- VIN fingerprint matching with manual no-guess fallback
- Exact lookup for reviewed factory VINs, Australian `6ZZ` surrogate VINs and hosted Japanese chassis numbers
- Progressive VIN prefix trail, WMI candidates, region, repeating model-year code, plant, serial and check-digit analysis
- Searchable Australian make directory covering 90 current, legacy and major commercial marques
- Shared-manufacturer warnings where one WMI cannot safely distinguish a marque
- Opt-in in-page official vPIC decoding, Australian Vehicle Recalls and exact Australian web research links
- Browser-private local analysis until an external research link is deliberately opened
- Vehicle profile and specification cards
- Power, torque, kerb weight, calculated kW/tonne and 0–100 fields
- Global search across V3 vehicle profiles, hosted Honda accessories and connected modules
- Hosted accessory browser
- Admin-side JSON validation workspace
- Automated repository data validation
- Links to existing fluids, TSB, FSM and specialist brand resources

## Data rules

1. Australian-market records and confirmed vehicles present in Australian import/register research workflows only; original Australian delivery must not be inferred.
2. A VIN fingerprint must be confirmed before it can automatically identify a vehicle.
3. Kerb weight must match the exact year, body and variant before power-to-weight is calculated.
4. Manufacturer-rated and independently tested performance figures must be labelled separately.
5. Unknown values remain `null` and display as **Not yet verified**.
6. Inventory remains a separate permission-controlled module.
7. Engine identity is stored separately as `code`, `family` and `marketingName`; cross-brand aliases belong in `alternateCodes`.
8. Conflicting source fields are retained as a `sourceWarning` and are not allowed to override a confirmed VIN/configuration record.
9. A WMI is manufacturer-routing evidence only. It cannot by itself confirm Australian delivery, model, trim, engine, transmission or parts fitment.
10. Shared group WMIs return multiple candidate marques rather than silently selecting the first match.
11. VINs are not sent to external services automatically. External research is user initiated.
12. Australian surrogate VINs and Japanese chassis numbers are stored as identifier mappings; they do not inherit model, engine, transmission or DCCD detail without separate evidence.
13. EPC reference VINs are examples only. Final part applicability must be checked against the target vehicle, build date and fitted options.

## Core data packs

- `data/vehicles.json` — VIN fingerprints, vehicle identity and specifications
- `../v4/public/data/vinReferences.json` — full public Australian VIN examples for EPC/reference lookup
- `data/identifiers.json` — confirmed administrative surrogate VIN and Japanese chassis-number mappings
- `data/modules.json` — connected TSB, FSM, fluids and specialist modules
- `data/source-queue.json` — public auction/dealer URLs awaiting extraction
- `data/source-review.json` — generated evidence requiring human/specification review
- `data/wmi.json` — Australian make directory, selected WMI routes, aliases, portals and source policy
- `../Honda/Accessories/data/accessories.json` — hosted Honda accessory records

## Grays acquisition

Run `python v3/tools/harvest_grays.py` after installing Playwright and Chromium. The script renders each queued public Grays lot, extracts visible and JSON-LD evidence, validates 17-character VIN candidates and writes `data/source-review.json`.

The GitHub Actions workflow **Harvest Grays VIN candidates** performs the same pass from the repository Actions tab and uploads the review JSON as an artifact. A found VIN still requires Australian-market, variant, engine and transmission verification before its fingerprint is added to `vehicles.json` or `vin-prefixes.json`.

## Migration approach

Existing brand portals remain available while their content is converted into structured V3 records. A module is not labelled fully migrated until its primary records are searchable from V3 and its importer/validator is committed.

## Validation

Run these checks before publishing VIN changes:

```text
python v3/tools/validate_v3_data.py
node v3/tools/test_vin_workbench.js
python v3/scripts/test_vin_intelligence.py
```

The regression tests protect the confirmed Honda, Subaru and Land Rover examples, Subaru surrogate/chassis mappings, shared-WMI handling, VIN cleaning, check-digit calculation, broad Australian make coverage and the progressive VIN / EPC reference finder.

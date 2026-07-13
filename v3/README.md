# Pleiades Version 3

Version 3 is a shared Australian-market vehicle knowledge application. It does not merge Inventory into the vehicle portal.

## Live V3 components

- Shared responsive application shell and navigation
- VIN fingerprint matching with manual no-guess fallback
- Vehicle profile and specification cards
- Power, torque, kerb weight, calculated kW/tonne and 0–100 fields
- Global search across V3 vehicle profiles, hosted Honda accessories and connected modules
- Hosted accessory browser
- Admin-side JSON validation workspace
- Automated repository data validation
- Links to existing fluids, TSB, FSM and specialist brand resources

## Data rules

1. Australian-market records only.
2. A VIN fingerprint must be confirmed before it can automatically identify a vehicle.
3. Kerb weight must match the exact year, body and variant before power-to-weight is calculated.
4. Manufacturer-rated and independently tested performance figures must be labelled separately.
5. Unknown values remain `null` and display as **Not yet verified**.
6. Inventory remains a separate permission-controlled module.
7. Engine identity is stored separately as `code`, `family` and `marketingName`; cross-brand aliases belong in `alternateCodes`.
8. Conflicting source fields are retained as a `sourceWarning` and are not allowed to override a confirmed VIN/configuration record.
9. Harvested auction data is written to a review file and never promoted directly into `vehicles.json`.

## Core data packs

- `data/vehicles.json` — VIN fingerprints, vehicle identity and specifications
- `data/modules.json` — connected TSB, FSM, fluids and specialist modules
- `data/source-queue.json` — public auction/dealer URLs awaiting extraction
- `data/source-review.json` — generated evidence requiring human/specification review
- `../Honda/Accessories/data/accessories.json` — hosted Honda accessory records

## Grays acquisition

Run `python v3/tools/harvest_grays.py` after installing Playwright and Chromium. The script renders each queued public Grays lot, extracts visible and JSON-LD evidence, validates 17-character VIN candidates and writes `data/source-review.json`.

The GitHub Actions workflow **Harvest Grays VIN candidates** performs the same pass from the repository Actions tab and uploads the review JSON as an artifact. A found VIN still requires Australian-market, variant, engine and transmission verification before its fingerprint is added to `vehicles.json` or `vin-prefixes.json`.

## Migration approach

Existing brand portals remain available while their content is converted into structured V3 records. A module is not labelled fully migrated until its primary records are searchable from V3 and its importer/validator is committed.

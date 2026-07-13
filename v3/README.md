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

## Core data packs

- `data/vehicles.json` — VIN fingerprints, vehicle identity and specifications
- `data/modules.json` — connected TSB, FSM, fluids and specialist modules
- `../Honda/Accessories/data/accessories.json` — hosted Honda accessory records

## Migration approach

Existing brand portals remain available while their content is converted into structured V3 records. A module is not labelled fully migrated until its primary records are searchable from V3 and its importer/validator is committed.

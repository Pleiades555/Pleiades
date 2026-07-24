# Pleiades Version 3.9

Version 3 is a shared Australian-market vehicle knowledge application. Inventory remains separate.

## VIN intelligence access

- Main application: `v3/index.html`
- VIN decoder: open **Decode a VIN** in the V3 sidebar
- VIN / chassis / EPC finder: `v3/vin-intelligence.html`
- Direct repository entry point: `VIN Intelligence.html`
- Canonical public Australian VIN records: `v4/public/data/vinReferences.json`
- Confirmed factory VIN profiles: `v3/data/vehicles.json`
- Surrogate VIN and chassis register: `v3/data/identifiers.json`

The reference finder searches progressively by year, model, body, edition, production number, powertrain, model code, stock number, partial identifier or complete identifier. A result can be copied or sent directly to the main decoder.

## Restored Subaru coverage

Version 3.9 restores all Subaru references previously supplied in the research conversation:

- 14 full factory VINs covering Forester SH9, Liberty Blitzen, RB320, P1, Cosworth CS400, Peter Solberg Edition, GB270 and Vortex XT
- 22 Australian/New Zealand surrogate VIN and Japanese chassis identifiers covering S201-S206, S401, 22B, Blitzen and Tommy Kaira research records
- production numbers and edition labels where supplied
- conservative manual-review notes where year, transcription, production-total convention, powertrain, transmission, DCCD or Australian delivery remains unresolved

These records are searchable from the dedicated VIN / EPC finder by terms such as `RB320`, `P1`, `S204`, `22B`, `GDB`, `GC8`, `SH9`, `BL` or a partial VIN/chassis number.

## Live components

- Clearly separated **Decode a VIN** and **Find VIN / EPC Reference** workflows
- Progressive VIN, surrogate VIN and chassis-number search
- VIN fingerprint matching with a manual no-guess fallback
- Exact lookup for reviewed factory VINs, Australian `6ZZ` surrogate VINs, New Zealand `7AT` candidates and Japanese chassis numbers
- Progressive VIN prefix trail, WMI candidates, region, repeating model-year code, plant, serial and check-digit analysis
- Searchable Australian make directory covering 90 current, legacy and major commercial marques
- Shared-manufacturer warnings where one WMI cannot safely distinguish a marque
- Opt-in official vPIC decoding, Australian Vehicle Recalls and exact web-research links
- Vehicle profile and specification cards
- Global search across vehicle profiles, identifiers, engines, transmissions, accessories and connected modules
- Automated repository validation

## Data rules

1. Australian-market records and confirmed vehicles present in Australian import/register research workflows are kept separate; original Australian delivery must not be inferred.
2. A VIN fingerprint must be confirmed before it can automatically identify a vehicle family.
3. Full factory VIN records can preserve a user-confirmed identity without creating a broader reusable prefix rule.
4. Kerb weight must match the exact year, body and variant before power-to-weight is calculated.
5. Manufacturer-rated and independently tested performance figures must be labelled separately.
6. Unknown values remain `null` and display as **Not yet verified**.
7. Engine identity is stored separately as code, family and marketing name.
8. Conflicting source fields remain visible and cannot silently override a confirmed record.
9. A WMI is manufacturer-routing evidence only. It cannot by itself confirm delivery, model, trim, engine, transmission or parts fitment.
10. VINs are not sent to external services automatically.
11. Surrogate VINs and Japanese chassis numbers do not inherit engine, transmission, DCCD or parts-fitment claims without separate evidence.
12. EPC reference identifiers are examples only. Final applicability must be checked against the target vehicle, build date and fitted options.

## Validation

Run these checks before publishing VIN changes:

```text
python v3/tools/validate_v3_data.py
node v3/tools/test_vin_workbench.js
python v3/scripts/test_vin_intelligence.py
```

The regression checks now protect every restored Subaru factory VIN and identifier so they cannot silently disappear from a later rebuild.

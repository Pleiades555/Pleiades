# Nissan Australia fluids data

This folder now contains `nissan_fluids_import.csv`, prepared from the Nissan records already present in the live Fluids Compatibility Hub.

## Quantity and part-number rule

A fluid part number must stay attached to its documented pack quantity. A 1 L, 4 L, 5 L, 20 L or drum record is a separate stock item unless an OEM source explicitly confirms that the same ordering number covers multiple quantities.

The import therefore follows these rules:

1. Never create a new quantity by copying an existing part number.
2. Leave quantity blank when the source does not identify it.
3. Keep punctuation-normalised duplicates as previous/search numbers rather than separate products when they represent the same known pack. Example: `KE90899933` is retained under the normalised 5 L record `KE908-99933`.
4. Keep local workshop/distributor products (`AI...` numbers) separate from Nissan genuine-branded products.
5. Do not promote specification matches to guaranteed substitutes. Vehicle, transmission and VIN applicability must still be checked.

## Validation

Run:

```bash
python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/nissan_fluids_import.csv
python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/fluids_master.json
```

The validator reports exact brand/part-number combinations associated with more than one non-empty pack size and exact duplicate rows.

## Importing into the hub

Use the Fluids Admin CSV import control and select `nissan_fluids_import.csv`. Review the Nissan filter, export the merged JSON, then push it through the existing GitHub control only after checking the live preview.

The `verification_status` and `source` columns are research/audit fields. The current hub safely ignores additional CSV columns, so they remain available in exported data without affecting search.

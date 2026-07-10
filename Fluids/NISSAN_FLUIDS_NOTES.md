# Nissan fluids data — Australia first

This folder contains `nissan_fluids_import.csv`, prepared as an Australia-first Nissan fluids dataset.

## Market policy

Every record must have both `market` and `market_status`.

- `Australia` / `Australian-market`: preferred and shown as the primary catalogue.
- A named overseas market such as `Japan`, `Europe`, `United States` or `New Zealand`: kept only when useful and clearly labelled.
- `Unconfirmed` / `market-unconfirmed`: retained for research but must not be presented as an Australian ordering number.
- `Australia` / `local-supply`: Australian distributor or workshop supply number, not necessarily a Nissan genuine-branded ordering number.

No overseas number is to be silently blended into the Australian catalogue.

## Confirmed Australian Nissan Matic numbering rule

The following prefix and pack-size structure is recorded for the Australian catalogue:

| Part number | Product | Pack |
|---|---|---:|
| `KLE22-00004` | AT-Matic D | 4 L |
| `KLE23-00004` | AT-Matic J | 4 L |
| `KLE24-00004` | AT-Matic S | 4 L |

Rules:

- `KLE22` identifies Matic D.
- `KLE23` identifies Matic J.
- `KLE24` identifies Matic S.
- `-00004` identifies the 4-litre container in these records.
- Do not assign another pack size to these exact numbers.
- `KE908-99933` is a separate 5 L AT-Matic S ordering number and must not be merged with `KLE24-00004`.

## Quantity and part-number rule

A fluid part number must stay attached to its documented pack quantity. A 1 L, 4 L, 5 L, 20 L or drum record is a separate stock item unless an OEM source explicitly confirms otherwise.

1. Never create a new quantity by copying an existing part number.
2. Leave quantity blank when the source does not identify it.
3. Keep punctuation-normalised duplicates as previous/search numbers only when they represent the same documented pack.
4. Keep local workshop/distributor products (`AI...` numbers) separate from Nissan genuine-branded products.
5. Do not promote specification matches to guaranteed substitutes. Vehicle, transmission and VIN applicability must still be checked.
6. Never infer an Australian market assignment from a foreign catalogue without Australian evidence.

## Validation

Run:

```bash
python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/nissan_fluids_import.csv
python Fluids/tools/validate_fluid_pack_part_numbers.py Fluids/fluids_master.json
```

The validator reports:

- exact part numbers associated with multiple pack sizes;
- duplicate rows;
- missing market labels;
- Nissan KLE Matic prefix/description mismatches;
- `-00004` Nissan Matic records that are not recorded as 4 L.

## Importing into the hub

Use the Fluids Admin CSV import control and select `nissan_fluids_import.csv`. Review the Nissan filter, export the merged JSON, then push it through the existing GitHub control only after checking the preview.

The additional audit fields are:

- `market`
- `market_status`
- `source`
- `verification_status`

The current hub safely ignores fields it does not yet display, but they remain in exported data for audit and future UI support.
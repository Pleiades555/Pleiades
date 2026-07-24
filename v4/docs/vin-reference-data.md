# VIN / EPC reference data

`public/data/vinReferences.json` stores exact VINs that were publicly displayed in Australian vehicle listings and matched to a confirmed vehicle identity.

## Purpose

The records provide known full VINs for legitimate EPC and parts-catalogue reference searches. They are not universal fitment guarantees. Every result displays the warning:

> Reference VIN for EPC lookup only; confirm part applicability against the target vehicle.

## Search behaviour

The V4 finder searches progressively while the user types. Records are searchable by:

- full or partial VIN
- model year or advertised year
- manufacturer and model
- model code, such as `L663`, `L405`, `L460`, `L461` or `L551`
- body designation, such as Defender `110`
- marketing powertrain, such as `D300`, `D350`, `P400e`, `P530` or `P635`
- variant, engine family and dealer stock number
- curated aliases

An exact full-VIN match receives the highest priority. Partial terms such as `2023 def d3` are accepted, but every supplied term must match the same record.

## Data policy

- Store only VINs already made public by an Australian dealer or Australian vehicle-listing source.
- Record the public source URL and how the VIN was captured.
- Keep model year separate from the listing's advertised or compliance year.
- Do not infer a grade from a broader VIN fingerprint.
- Mark unresolved fields explicitly rather than guessing.
- Do not store owner names, registration-holder details or other personal information.
- Preserve exact VINs even when a listing is later removed, so the evidence trail and EPC reference remain reproducible.

Existing exact VINs in `vehicles.json` are merged into the finder at runtime, while newly collected EPC-oriented examples live in `vinReferences.json`.

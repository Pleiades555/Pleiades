# Ford TSB v18.4 - ERA Multi-Part Builder

Upload this package into the root of your Pleiades repository and overwrite existing files.

## What changed

- Manual Parts for ERA now supports adding multiple part numbers before saving.
- `Add Part Row` now stages the part in a visible list instead of immediately replacing/saving one row.
- `Save Parts to GitHub` saves the full staged list to `Ford/TSB/data/manual-parts.json`.
- Existing parts can be loaded, amended, deleted, and reordered.
- Supports multiple whole-bulletin parts and multiple variant-specific parts.
- Keeps the ERA copy format: part number on one line, quantity below it.
- Keeps PDF directory fix, variant dropdown display, scenery mode, mobile layout, true save, and persistence.

## How to use

1. Unlock Advanced Mode.
2. Enter the bulletin/FSA/SSM number.
3. In Manual Parts for ERA, enter the same bulletin number or let it auto-fill.
4. Press **Load Existing Parts**.
5. Enter Part Number, Quantity, Description, Comments and optional Variant.
6. Press **Add Part Row** for each part required.
7. Press **Save Parts to GitHub** when the staged list is complete.

Leaving Variant blank stores the part under **Applies to all variants**.
Entering a Variant stores it under the variant dropdown.

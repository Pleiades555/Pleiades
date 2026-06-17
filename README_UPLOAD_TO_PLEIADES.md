# Ford TSB v16 - Parts Display + Supersession Links

Upload the contents of this ZIP to the root of the Pleiades repository and overwrite existing files.

## Important before uploading

If your live repo already contains edited files, do **not** overwrite them blindly:

- `Ford/TSB/data/manual-overrides.json`
- `Ford/TSB/data/manual-parts.json`

If GitHub asks whether to replace those two files, keep your existing live versions unless you know they are empty. They contain your manual corrections and parts rows.

## What this fixes

- Restores the Parts list display on each bulletin card.
- Shows static whole-bulletin parts plus variant-specific parts.
- Adds a variant dropdown on cards that have variant parts.
- Each part row has its own EraLink copy button.
- Copy format is vertical:

  PART NUMBER
  QTY

- Adds clickable supersession links:
  - Supersedes old bulletin
  - Superseded by replacement bulletin

## After upload

Run:

GitHub → Actions → Update Ford TSB Index → Run workflow

Then refresh:

https://pleiades555.github.io/Pleiades/Ford/TSB/index.html

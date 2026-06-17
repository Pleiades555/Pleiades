# Ford TSB v13 - EraLink Part Copy Update

Upload the contents of this ZIP into the root of your Pleiades GitHub repository and overwrite existing files.

This package keeps the existing advanced editor functions and adds the EraLink-safe part copy behaviour.

## What changed

- Keeps the advanced editor, GitHub token tools, PDF upload, field override tools and workflow trigger.
- Keeps the bulletin-level/static parts editor.
- Keeps the variant-specific parts editor.
- Adds a **Copy** button to every displayed part row.
- Each Copy button copies **only that part row**.
- Clipboard format is vertical for Excel/Pentana EraLink:

```text
PART NUMBER
QTY
```

Example:

```text
AB39-7A543-AC
2
```

When pasted into Excel:

```text
A1 = AB39-7A543-AC
A2 = 2
```

No bulk copy button has been added, because bulk copy can break the EraLink stock/order-in process.

## Files included

```text
.github/workflows/update-ford-tsb-index.yml
Ford/TSB/index.html
Ford/TSB/scripts/generate-tsb-index.py
Ford/TSB/data/manual-overrides.json
Ford/TSB/data/variant-parts.json
Ford/TSB/data/tsb-index.json
```

## After upload

1. Upload the ZIP contents to the repo root.
2. Commit changes.
3. Go to **Actions → Update Ford TSB Index → Run workflow**.
4. Refresh the TSB page after GitHub Pages updates.

## Parts editor format

Use this format per line:

```text
part number | qty | description | notes
```

Example:

```text
AB39-7A543-AC | 2 | Clutch pedal switch | Required for manual variants
```

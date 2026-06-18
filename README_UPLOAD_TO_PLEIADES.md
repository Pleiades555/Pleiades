# Ford TSB v18.5 – PDF Extension + Duplicate Number Fix

Upload the contents of this ZIP to the root of the Pleiades repository and overwrite existing files.

## Fixes

- Stops `.pdf` being saved/displayed as part of the bulletin number.
  - Example: `25SE6.pdf` now normalises to `25SE6`.
- Recognises short Ford FSA numbers such as `25SE6` and `25SD9`.
- De-duplicates entries where both `25SE6` and `25SE6.pdf` exist in manual overrides or the generated index.
- Keeps the PDF-backed entry and merges the manual fields/ERA parts into it.
- Keeps existing mobile/background/ERA multi-part builder updates.

## After Upload

1. Upload and overwrite these files.
2. Go to GitHub Actions.
3. Run `Update Ford TSB Index` manually.
4. Wait for GitHub Pages to refresh.

## Existing manual data

Do not overwrite your live:

- `Ford/TSB/data/manual-overrides.json`
- `Ford/TSB/data/manual-parts.json`

if GitHub asks. This update does not need to replace your saved manual data.

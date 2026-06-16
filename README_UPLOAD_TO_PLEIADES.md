# Ford TSB auto-index fix package

Upload the contents of this folder into the root of your Pleiades GitHub repository.

This package contains:

- `.github/workflows/update-ford-tsb-index.yml`
- `Ford/TSB/scripts/generate-tsb-index.py`
- `Ford/TSB/data/manual-overrides.json`
- `Ford/TSB/data/tsb-index.json`
- empty PDF folders so the structure is preserved

After upload:

1. Go to GitHub Actions.
2. Open `Update Ford TSB Index`.
3. Click `Run workflow`.
4. Wait for it to finish.
5. Confirm `Ford/TSB/data/tsb-index.json` is no longer empty.

Important: upload the actual files, not copied/pasted text, so line breaks are preserved.

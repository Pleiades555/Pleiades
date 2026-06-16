# Ford TSB v8 JSON Update Fix

Upload this ZIP's contents to the root of the Pleiades repository and overwrite existing files.

This package fixes:

- GitHub workflow formatting with proper line breaks.
- Python script formatting with proper line breaks.
- Removes parts table and conditional logic fields from the generated JSON.
- Stops part numbers inside PDFs being selected as the main bulletin number.
- Preserves hyphenated TSB numbers such as 26-2159.
- Recognises program numbers such as 23P23, 25SD9, 25S39, S1406 and 14M02.
- Keeps PDF links untouched by preserving the real repository file path.

After uploading:

1. Go to GitHub Actions.
2. Open `Update Ford TSB Index`.
3. Click `Run workflow`.
4. Confirm `Ford/TSB/data/tsb-index.json` updates with records.

# Ford TSB v5 Full Integration

Upload the contents of this ZIP into the root of your Pleiades GitHub repository and overwrite existing Ford/TSB files.

Included fixes:
- Preserves hyphenated bulletin numbers such as `26-2159`.
- Recognises FSA/program numbers such as `23P23` and recall numbers such as `25S39`.
- Keeps PDF links based on the real file path and URL-encodes spaces/special characters in the webpage.
- Improves year range, model, title, symptom and concern extraction.
- Adds parts/part number extraction from the PDF.
- Adds conditional ordering/if-clause extraction such as `if damaged, order...`.
- Search now includes part numbers and conditional logic.
- Superseded files can still be archived automatically when supersession wording is detected.

After upload:
1. Go to GitHub > Actions.
2. Open `Update Ford TSB Index`.
3. Click `Run workflow`.
4. Wait for it to complete.
5. Check `Ford/TSB/data/tsb-index.json` contains records, not just `[]`.
6. Refresh `https://pleiades555.github.io/Pleiades/Ford/TSB/index.html`.

Optional manual corrections go in:
`Ford/TSB/data/manual-overrides.json`

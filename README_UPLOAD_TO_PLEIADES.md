# Ford TSB v7 Professional Page Update

Upload the contents of this ZIP to the root of the Pleiades repository and overwrite existing files.

## What changed

- Cleaner, more professional `Ford/TSB/index.html`.
- Advanced instructions are hidden by default.
- Enter passcode `11290` in the top-right field to unlock the advanced/admin notes.
- Parts table and if-clause sections are removed.
- Primary number display is cleaned so the page does not deliberately duplicate TSB/FSA/SSM numbers.
- PDF links preserve the generated file path.
- Parser keeps Ford-style hyphen numbers such as `26-2159`.

## After upload

1. Go to GitHub Actions.
2. Run `Update Ford TSB Index` manually once.
3. Wait for it to commit `Ford/TSB/data/tsb-index.json`.
4. Refresh the live page with Ctrl+F5.

## Manual corrections

Use:

`Ford/TSB/data/manual-overrides.json`

Example:

```json
{
  "23P23": {
    "number": "23P23",
    "type": "FSA",
    "title": "Correct title",
    "model": "Correct model",
    "yearRange": "2020-2023",
    "symptom": "Correct concern"
  }
}
```

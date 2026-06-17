# Ford TSB v14.1 — Persistence + Date Uploaded by Ford

Upload the contents of this ZIP to the root of your Pleiades GitHub repository and overwrite existing files.

## What this update adds

- Keeps v14 persistence behaviour:
  - manual field edits save to `Ford/TSB/data/manual-overrides.json`
  - manual parts save to `Ford/TSB/data/manual-parts.json`
  - regenerated `tsb-index.json` should not wipe manual edits
- Adds a new field: `Date uploaded by Ford`
- Adds optional `Issue date`
- Shows both dates on each bulletin card
- Adds both date fields to Advanced Mode
- Sort dropdown now includes `Sort by Ford upload date`

## Important

This package does **not** include blank `manual-overrides.json` or `manual-parts.json`, so it should not overwrite your existing manual edits.

## Manual override example

In `Ford/TSB/data/manual-overrides.json`:

```json
{
  "23P23": {
    "fordUploadDate": "2023-11-15",
    "issueDate": "2023-11-13",
    "title": "Corrected FSA title"
  }
}
```

Use ISO format for dates:

```text
YYYY-MM-DD
```

The page displays them as:

```text
DD/MM/YYYY
```

## After upload

Run:

GitHub → Actions → Update Ford TSB Index → Run workflow

Then refresh:

https://pleiades555.github.io/Pleiades/Ford/TSB/index.html

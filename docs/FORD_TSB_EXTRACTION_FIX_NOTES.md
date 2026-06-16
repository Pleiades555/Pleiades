# Pleiades Ford TSB accuracy fix

Upload these files into the root of your Pleiades repository and overwrite existing files when asked.

## What this fixes

- Better TSB/FSA/SSM number detection.
- Year ranges now use vehicle/model context instead of random publication dates.
- Titles now favour `Title`, `Subject`, or Issue/Concern wording instead of disclaimers/page text.
- Symptoms now favour Ford fields such as `Issue`, `Condition`, `Concern`, `Reason For This Bulletin`, and `Summary`.
- Supersession filter now correctly checks for non-empty supersession arrays.
- Manual correction file added for PDFs that are badly formatted or image-only.

## Upload paths

```text
.github/workflows/update-ford-tsb-index.yml
Ford/TSB/index.html
Ford/TSB/scripts/generate-tsb-index.py
Ford/TSB/data/manual-corrections.json
Ford/TSB/data/tsb-index.json
```

## After upload

Go to GitHub Actions and run **Update Ford TSB Index** manually once.

The action will scan:

```text
Ford/TSB/pdf/
Ford/TSB/archive/superseded/
```

and rewrite:

```text
Ford/TSB/data/tsb-index.json
```

## Manual correction example

Use `Ford/TSB/data/manual-corrections.json` like this when a PDF is ugly or image-only:

```json
{
  "supersessions": {
    "25-2205": "26-2159"
  },
  "metadata": {
    "26-2159": {
      "title": "Battery drain / no start condition",
      "model": ["Ranger", "Everest"],
      "yearRange": "2022-2025",
      "symptom": "Battery drain or intermittent no start condition.",
      "documentType": "TSB"
    }
  }
}
```

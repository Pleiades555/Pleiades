# Ford TSB Auto Library

This folder is designed for the Pleiades GitHub Pages repository.

## How to use

1. Upload current/unknown Ford TSB PDFs into:

   `Ford/TSB/pdf/`

2. Upload known superseded PDFs into:

   `Ford/TSB/archive/superseded/`

3. Commit and push to GitHub.

4. GitHub Actions runs automatically and updates:

   `Ford/TSB/data/tsb-index.json`

5. Open:

   `Ford/TSB/index.html`

## What happens automatically

The action scans PDFs and attempts to extract:

- TSB number
- SSM number
- recall / field service action number
- model
- year
- engine
- symptom / concern
- title
- supersedes
- superseded by
- current or superseded status

If a PDF is identified as superseded, it is automatically moved from:

`Ford/TSB/pdf/`

to:

`Ford/TSB/archive/superseded/`

## Manual overrides

If Ford's PDF text does not clearly mention supersession details, edit:

`Ford/TSB/data/manual-overrides.json`

Example:

```json
{
  "supersessions": {
    "25-2205": "26-2159"
  },
  "metadata": {
    "26-2159": {
      "model": ["Ranger", "Everest"],
      "symptom": ["Battery drain", "No start"],
      "engine": ["P5AT"]
    }
  }
}
```

## Important notes

PDF text extraction depends on the PDF containing readable text. Scanned image-only PDFs may be indexed by filename only unless OCR is added later.

The website still indexes those files, but they may show as `Needs review`.

# Ford TSB v4 Concern / Symptom Cut-Off Fix

Upload the contents of this ZIP to the root of your Pleiades GitHub repository and overwrite existing files.

Then run:

GitHub > Actions > Update Ford TSB Index > Run workflow

## What this fixes

This v4 update improves the Ford PDF parser where concerns/symptoms were being cut off.

Previous behaviour:
- grabbed only the first line or one continuation line after `Issue`, `Condition`, or `Reason For This Program`
- stopped too early at punctuation or PDF line breaks
- could miss the rest of the Ford concern statement

New behaviour:
- allows multi-line Issue / Condition / Concern / Reason fields
- stops only when it reaches real Ford section headers such as Service Procedure, Parts Requirements, Labor Allowance, Warranty Status, Affected Vehicles, etc.
- expands fallback sentence extraction from 390 characters to 900 characters
- keeps 23P23 / FSA / CSP / SSM / TSB number detection from v3

## Files changed

- `Ford/TSB/scripts/generate-tsb-index.py`
- existing `index.html`, workflow, data folders and correction files are included so this can be uploaded as a complete patch

## Manual corrections still supported

For ugly PDFs, use:

`Ford/TSB/data/manual-corrections.json`

Example:

```json
{
  "metadata": {
    "23P23": {
      "documentNumber": "23P23",
      "documentType": "Customer Satisfaction Program",
      "title": "Your corrected title",
      "model": ["Ranger"],
      "yearRange": "2022-2023",
      "symptom": "Full corrected concern text goes here.",
      "needsReview": false,
      "reviewReason": "manual correction applied"
    }
  },
  "files": {},
  "supersessions": {}
}
```

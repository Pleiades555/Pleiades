# Ford TSB Automatic Library Upload Guide

## Where to put files

Current bulletins:

```text
Ford/TSB/pdf/
```

Known superseded/old bulletins:

```text
Ford/TSB/archive/superseded/
```

The page is:

```text
Ford/TSB/index.html
```

## Recommended PDF naming

Use descriptive names. The automatic scanner uses both the filename and PDF text.

```text
25-2205 Ranger PX3 vibration at idle.pdf
26-2159 Everest battery drain no start.pdf
25S39 F-150 brake hose recall bulletin.pdf
```

## Supersession detection

Detected automatically from:

- folder path: `archive/superseded`
- filename words: `superseded`, `replaced`, `obsolete`, `archive`, `old`
- PDF text containing phrases like:
  - `supersedes 25-2205`
  - `this bulletin replaces 25-2205`
  - `superseded by 26-1010`

If the PDF does not contain clear wording, add a manual correction in:

```text
Ford/TSB/data/manual-overrides.json
```

Example:

```json
{
  "25-2205": {
    "model": "Ranger PX3",
    "symptom": "Vibration at idle",
    "status": "Superseded",
    "supersededBy": "26-1010"
  },
  "26-1010": {
    "model": "Ranger PX3",
    "symptom": "Vibration at idle",
    "status": "Current",
    "supersedes": "25-2205"
  }
}
```

## How automatic updates work

When you upload PDFs or edit `manual-overrides.json`, GitHub Actions runs:

```text
.github/workflows/update-ford-tsb-index.yml
```

It regenerates:

```text
Ford/TSB/data/tsb-index.json
```

The website loads that JSON file and updates the search results automatically.

## Link from your Ford home page

Add this link wherever your Ford navigation sits:

```html
<a href="Ford/TSB/index.html">Ford TSB Library</a>
```

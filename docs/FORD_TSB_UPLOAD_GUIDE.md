# Ford TSB Upload Guide

## Recommended upload process

1. Put all new or unknown PDFs into:

   `Ford/TSB/pdf/`

2. Put PDFs you already know are superseded into:

   `Ford/TSB/archive/superseded/`

3. Push to GitHub.

4. Wait for the GitHub Action named `Update Ford TSB Index` to finish.

5. The site will update automatically.

## Filename recommendation

The scanner can read PDF text, but good filenames improve results.

Best format:

```text
26-2159 Ranger Everest Battery Drain No Start.pdf
25-2205 Ranger PX3 Vibration At Idle.pdf
SSM52344 F-150 Sync Screen Blank.pdf
25S39 Ranger Brake Hose Recall.pdf
```

## Supersession detection

The scanner looks for wording such as:

```text
supersedes TSB 25-2205
this bulletin replaces 25-2205
superseded by 26-2159
replaced by 26-2159
```

If it finds that a bulletin is superseded, it updates the index and moves the old PDF to:

`Ford/TSB/archive/superseded/`

## Manual override example

Open:

`Ford/TSB/data/manual-overrides.json`

Add:

```json
{
  "supersessions": {
    "25-2205": "26-2159"
  },
  "metadata": {
    "25-2205": {
      "model": ["Ranger"],
      "symptom": ["Vibration at idle"]
    }
  }
}
```

Then commit and push again.

# Ford TSB extraction fix notes v3

## Main change

`23P23` style programme numbers are now treated as first-class Ford bulletin/campaign numbers.

## Extraction priority

The indexer now prioritises fields in this order:

1. PDF filename
2. Ford header fields
3. first-page/header text
4. early PDF body text
5. filename fallback

This prevents random body text, page numbers, publication dates and disclaimer text from becoming the title or bulletin number.

## Ford number formats recognised

- TSB: `23-2353`
- SSM: `SSM52344`, `SSM 52344`
- Safety/FSA: `23S33`, `23S33-S1`
- Customer programmes: `23P23`, `23N06`, `25M01`
- Other campaigns: `23B12`, `25C02`

## Still not perfect

Some PDFs are scanned images or have poor text extraction. These will appear in:

```text
Ford/TSB/data/tsb-review-report.json
```

Correct those in:

```text
Ford/TSB/data/manual-corrections.json
```

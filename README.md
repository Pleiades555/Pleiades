# Pleiades Ford TSB Auto Library Package

Upload the contents of this folder into the root of your GitHub repository.

It adds:

- `Ford/TSB/index.html` searchable TSB page
- `Ford/TSB/pdf/` current PDF storage
- `Ford/TSB/archive/superseded/` superseded PDF storage
- `Ford/TSB/scripts/generate-tsb-index.py` automatic scanner
- `Ford/TSB/data/manual-overrides.json` manual fixes when needed
- `.github/workflows/update-ford-tsb-index.yml` automatic GitHub Action

After upload, add this to your Ford homepage/navigation:

```html
<a href="Ford/TSB/index.html">Ford TSB Library</a>
```

Then upload PDFs into `Ford/TSB/pdf/`. The index updates automatically on push.

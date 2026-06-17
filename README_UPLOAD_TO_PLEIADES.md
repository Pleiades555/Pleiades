# Ford TSB v17.2 - ERA Comments + UI Cleanup

Upload these files/folders into the **root** of your `Pleiades` repository and overwrite existing files.

This update keeps the v17 True Save behaviour and adds:

- `Comments` field to **Manual Parts for ERA**
- Comments saved into `Ford/TSB/data/manual-parts.json`
- Comments displayed underneath each ERA part row
- Cleaner ERA parts layout:
  - `Applies to all variants`
  - separate variant sections
  - variant dropdown no longer mixes static and variant parts awkwardly
- Cleaner card footer so `Open PDF` no longer gets pushed/cut off
- Keeps individual ERA-safe copy buttons only:

```text
PART NUMBER
QTY
```

## Important

This ZIP deliberately does **not** include your live:

- `Ford/TSB/data/manual-overrides.json`
- `Ford/TSB/data/manual-parts.json`

Do not overwrite those files if GitHub asks, because they contain your saved manual work.

After upload, run:

```text
GitHub → Actions → Update Ford TSB Index → Run workflow
```

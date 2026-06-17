# Ford TSB v17 - True Save Update

Upload these folders/files into the root of your `Pleiades` repository and overwrite existing files.

This update keeps the v16 parts + supersession behaviour and changes the Advanced Editor save flow:

- **Save Field Overrides to GitHub** writes to `Ford/TSB/data/manual-overrides.json`.
- **Save Part Row to GitHub** writes to `Ford/TSB/data/manual-parts.json`.
- After either save, the page automatically triggers the `Update Ford TSB Index` workflow.
- The generated `tsb-index.json` is still not edited directly.
- ERA copy remains one part at a time: part number on the first line, quantity on the second line.

## Important

Do **not** overwrite your live `manual-overrides.json` or `manual-parts.json` if they already contain manual data. This package includes blank starter files only for fresh installs.

## How to use

1. Open Ford TSB page.
2. Click **Advanced**.
3. Enter passcode `11290`.
4. Enter GitHub token, repo, and branch.
5. Enter bulletin number.
6. Save fields or part row.
7. Wait around 30-90 seconds for GitHub Actions/GitHub Pages to refresh.

## Token permissions

Your GitHub token needs repository content write permission and workflow dispatch permission.


## v17.1 update

- Renames EraLink wording to ERA.
- Re-adds Manual Parts for ERA comments/instructions.
- Keeps true-save GitHub behaviour from v17.
- Keeps per-part vertical copy format only: part number on one line, quantity beneath.

Do not overwrite live `manual-overrides.json` or `manual-parts.json` if they already contain saved edits.

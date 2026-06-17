# Ford TSB v15 Manual Persistence Fix

Upload the contents of this ZIP to the root of the Pleiades GitHub repository and overwrite existing files.

This fixes the issue where manual entries such as FAB2026033 save to manual-overrides.json but do not appear on the live site because tsb-index.json is regenerated from PDFs only.

## What changed

- The GitHub workflow now includes real line breaks and tracks manual-parts.json.
- The generator now creates index entries from manual-overrides.json even when there is no matching PDF.
- manual-parts.json is created automatically if missing.
- Manual fields such as title, model, yearRange, fordUploadDate, issueDate, concern, status and supersededBy persist through regeneration.

## After upload

1. Go to GitHub Actions.
2. Run `Update Ford TSB Index` manually.
3. Wait for it to commit the regenerated `Ford/TSB/data/tsb-index.json`.
4. Refresh the live TSB page.

For FAB2026033, the manual override should now appear even if there is no matching PDF.

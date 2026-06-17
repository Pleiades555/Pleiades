# Pleiades Ford TSB v18.3 PDF directory fix

Upload these files to the root of your Pleiades repository and overwrite existing files.

## What this fixes

- Corrects Open PDF links from the Ford TSB page.
- Converts generated JSON paths like `Ford/TSB/pdf/23P23.pdf` into page-relative links like `pdf/23P23.pdf`.
- Converts superseded archive paths like `Ford/TSB/archive/superseded/25-2205.pdf` into `archive/superseded/25-2205.pdf`.
- Keeps PDF upload target as `Ford/TSB/pdf/`, which is the correct GitHub repository folder.
- Keeps v18.2 variant dropdown, ERA copy, mobile layout and GT40 background work intact.

## Important

Do not overwrite your live `manual-overrides.json` or `manual-parts.json` if they contain real edits. This package does not include those data files.

After upload, refresh GitHub Pages. If old links persist, force refresh the page with Ctrl+F5.

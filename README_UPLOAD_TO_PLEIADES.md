# Pleiades Ford TSB v10 - Advanced editor package

Upload the contents of this ZIP to the root of the Pleiades GitHub repository and overwrite existing files.

## What changed

- Keeps the v9 working PDF index generator.
- Keeps clean bulletin number display and removes the parts table / if-clause sections.
- Adds an Advanced panel behind passcode `11290`.
- Advanced panel can:
  - edit TSB/FSA/SSM/Recall fields by writing to `Ford/TSB/data/manual-overrides.json`
  - upload PDFs to `Ford/TSB/pdf/` or `Ford/TSB/archive/superseded/`
  - request the `Update Ford TSB Index` GitHub Action to regenerate JSON

## Token safety

Do not hard-code a GitHub token in the HTML. The page asks for a token at runtime.
Use a fine-grained GitHub token restricted to this repo with contents read/write and actions workflow permission.

## After upload

1. Go to the live page.
2. Enter passcode `11290`.
3. Open `GitHub connection`.
4. Paste the token.
5. Save connection.
6. Edit fields or upload a PDF.
7. The page will request the workflow to regenerate the JSON.

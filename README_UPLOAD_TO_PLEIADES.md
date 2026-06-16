# Pleiades Ford TSB v11 - Variant Parts Selector

Upload the contents of this ZIP to the root of your Pleiades repository.

## Added

- A professional Variant Parts Selector section on `Ford/TSB/index.html`.
- `Ford/TSB/data/variant-parts.json` for parts lists.
- Supports:
  - variant-specific parts, for example PX2, PX3, Next Gen
  - static whole-model lists for TSBs that apply across all variants
  - related TSB numbers per list
  - advanced editor hidden behind passcode `11290`

## Important

This does not hard-code any GitHub token into the page. The included advanced editor lets you edit and download `variant-parts.json`. You can then upload/commit the JSON safely.

The safer next step is adding a GitHub API push button that asks for the token at runtime only.

# Pleiades Ford TSB v12 - merged editor + parts section

Upload the contents of this ZIP to the root of your Pleiades repository and overwrite existing files.

This version restores/preserves the advanced editor functions from v10 and adds a parts section inside the same advanced editor.

## Kept from existing editor

- Passcode advanced mode: `11290`
- GitHub token field at runtime only
- Edit bulletin field overrides
- Upload PDF to GitHub
- Run GitHub indexing workflow
- Clean bulletin display

## New parts editor

Advanced mode now includes a **Parts lists** tab. It saves to:

```text
Ford/TSB/data/variant-parts.json
```

Each bulletin can have:

1. **Whole-bulletin/static parts** - parts that apply to the entire bulletin regardless of vehicle variant.
2. **Variant-specific parts** - parts shown through a variant dropdown on the bulletin card.

Use this line format in the editor:

```text
part number | qty | description | notes
```

Example:

```text
AB39-12345-A | 1 | Harness kit | Use when connector is damaged
```

## Important

Do not put your token directly in the HTML. Paste it into the advanced page only when needed, or save it in your own browser.

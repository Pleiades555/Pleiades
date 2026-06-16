# Direct upload package for Pleiades

Copy the contents of this ZIP into the root of your GitHub repository.

It adds:

```text
Ford/TSB/index.html
Ford/TSB/pdf/
Ford/TSB/archive/superseded/
Ford/TSB/scripts/generate-tsb-index.py
Ford/TSB/data/tsb-index.json
Ford/TSB/data/manual-overrides.json
.github/workflows/update-ford-tsb-index.yml
docs/FORD_TSB_UPLOAD_GUIDE.md
```

After upload, dump Ford TSB PDFs into:

```text
Ford/TSB/pdf/
```

Then commit/push. GitHub Actions will generate the searchable index and move detected superseded bulletins into the archive folder.

Your public page will be:

```text
/Ford/TSB/index.html
```

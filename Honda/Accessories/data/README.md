# Honda accessory data

`accessories.json` is the live, website-hosted accessory database used by `Honda/Accessories.html`.

The source Excel-exported HTML sheets remain in this folder tree for auditing. Run:

```bash
python Honda/Accessories/tools/build_accessory_data.py
```

to rebuild the JSON data from those source sheets. The GitHub Actions workflow also rebuilds it automatically when Honda accessory source files change on `main`.

Records are intended for Australian-market vehicles only. Unknown or ambiguous applicability must not be added as confirmed.

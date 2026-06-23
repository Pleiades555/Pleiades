FLUIDS HUB CSV OPTION B UPDATE

Input CSV:
- fluids_master_export(in).csv

Processed:
- CSV rows imported: 87
- Final fluid records: 102
- Auto/reverse/spec-created records: 15
- Brands in data/filter list: 60

Option B enabled:
- Exact compatible_substitutes entries are parsed.
- Reverse entries are created for compatible brands/part numbers listed in compatible_substitutes.
- Spec-based cross references are created when different brand entries share matching:
  - brand_spec
  - general_spec
  - industry_standard

Important:
Spec-based matches are marked in notes as needing verification. They are useful for searching/cross-reference but should not be treated as guaranteed application approval without checking the relevant spec/PDS.

Upload:
Replace/add these files:
- Fluids/Fluids Compatibility Hub.html
- Fluids/fluids_master.json
- Fluids/fluids_changelog.json
- Fluids/fluid_brands.json
- Fluids/fluids_import_template.csv

No Ford parts JSON is touched.

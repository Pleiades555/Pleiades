FORD PARTS KNOWLEDGE BASE - FRESH MANUAL-PROTECTED VERSION

Purpose:
- Starts fresh with no part entries.
- Manual entries are stored separately from future package/core updates.
- Future package updates should NOT replace ford_parts_kb_manual.json, ford_parts_kb_deleted.json, or ford_parts_kb_changelog.json.

Files:
- Ford/Ford Parts Knowledge Base.html
- Ford/ford_parts_kb_core.json       Empty core database for future package/static data
- Ford/ford_parts_kb_manual.json     Protected manual entry database
- Ford/ford_parts_kb_deleted.json    Deleted/hidden entry history
- Ford/ford_parts_kb_changelog.json  Steam-style changelog
- Ford/backups/                      Automatic GitHub backups before commit
- Ford/ford_parts_kb_manual_template.csv

Admin:
- Password: 11290
- Add/update/delete/import/GitHub controls hidden until unlocked.

Delete function:
- Kept as requested.
- Delete/hide moves the entry into deleted history rather than simply vanishing.
- Deleted history is backed up and committed separately.

GitHub commit:
- Creates backups in Ford/backups/
- Then updates:
  - Ford/ford_parts_kb_manual.json
  - Ford/ford_parts_kb_deleted.json
  - Ford/ford_parts_kb_changelog.json

Safety rule for future updates:
- Replace HTML and core JSON only.
- Do not replace manual/deleted/changelog JSON unless intentionally restoring from backup.

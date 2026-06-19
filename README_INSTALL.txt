FORD GITHUB LIVE UPDATE PACKAGE

Copy this package into the root of your GitHub repo.

Files:
- Ford Web.html
- Ford/Ford Parts Knowledge Base.html
- Ford/ford_parts_kb_data.json
- Ford/ford_prefix_codes.json
- Ford/ford_parts_kb_template.csv

Starter data:
- 674 rows extracted from preview.html

How updates work:
1. Open Ford Parts Knowledge Base from your site.
2. Enter password: 11290
3. Open "GitHub live update settings".
4. Add:
   - owner: Pleiades555
   - repo: Pleiades
   - branch: main
   - GitHub token
5. Add/update entries.
6. Click "Commit Parts JSON to GitHub".

Required token:
- Fine-grained GitHub token
- Repository access: Pleiades only
- Permissions: Contents Read and Write

Security warning:
Putting a token into a public HTML/browser storage is not secure.
Anyone with access to your browser or source could obtain it.
Use a fine-grained token limited to this repo only.

Recovery:
If abused, revoke the token and restore previous JSON from GitHub commit history.


CHANGELOG UPDATE:
- Visible Change Log button added near search bar.
- Opens as overlay/modal.
- Save/update/delete actions automatically create changelog entries.
- Commit Parts JSON to GitHub also commits Ford/ford_parts_kb_changelog.json.
- Existing part data is preserved: site JSON and local additions are merged by basic number.
- This package includes Ford/ford_parts_kb_changelog.json.


ADMIN VISIBILITY UPDATE:
- GitHub live update settings are now completely hidden until password 11290 is entered.
- Manual add/update section is now completely hidden until password 11290 is entered.
- Prefix code manager is now completely hidden until password 11290 is entered.
- Advanced/import/export section is now completely hidden until password 11290 is entered.
- Public users still see search and Change Log only.

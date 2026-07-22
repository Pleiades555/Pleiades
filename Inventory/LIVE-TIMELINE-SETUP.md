# Daily timeline live sharing setup

The timeline now has two storage modes:

1. **Per-user local mode** works immediately. Preferences, order numbers and check-offs are stored under the signed-in Pleiades username in that browser.
2. **Firebase live mode** shares the daily checklist, order numbers, user display name and timestamps between all open browsers.

## Enable Firebase live mode

1. Create a Firebase project and add a Web app.
2. Enable **Realtime Database**.
3. Enable **Authentication → Anonymous** sign-in.
4. Add the site's deployed domain to Firebase Authentication's authorised domains.
5. Copy the Web app configuration into `Inventory/timeline-sync-config.js` and set `enabled: true`.
6. Apply Realtime Database rules similar to the following:

```json
{
  "rules": {
    "inventoryTimeline": {
      "$date": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

## Data written by the timeline

Each daily code record stores:

- checked state
- order number
- Pleiades username and display name that made the latest change
- server-generated update timestamp
- completing username, display name and server-generated completion timestamp

The checklist automatically starts a new shared path for each local calendar date.

## Important identity limitation

The current Pleiades login is a browser-side username selector backed by the public `accounts/users.json` file. Firebase can provide reliable server timestamps, but the displayed Pleiades username is not cryptographically verified. For tamper-resistant auditing, the next step is to replace the username-only login with server-validated accounts or Firebase custom authentication.

## Safe fallback

If Firebase is disabled, unreachable or misconfigured, the page remains operational in per-user local mode and shows **Offline fallback** or **Per-user local** in the status pill.

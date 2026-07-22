/*
  Firebase live-sync configuration for the Pleiades Inventory timeline.
  Realtime Database and Anonymous Authentication must remain enabled in Firebase.
*/
window.PleiadesTimelineSyncConfig = {
  enabled: true,
  provider: 'firebase',
  firebase: {
    apiKey: 'AIzaSyAR4KlnQtZ8lcKsP99BuuzTkJv1xOnQJsY',
    authDomain: 'pleiades-inventory.firebaseapp.com',
    databaseURL: 'https://pleiades-inventory-default-rtdb.firebaseio.com',
    projectId: 'pleiades-inventory',
    appId: '1:127811575372:web:92827c992f8a5d80615ee9'
  }
};
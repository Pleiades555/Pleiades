/*
  Optional Firebase live-sync configuration.
  Firebase web app details have been added for the Pleiades Inventory project.
  Live sync remains disabled until the exact Realtime Database URL is added.
  Find it in Firebase Console > Realtime Database > Data.
*/
window.PleiadesTimelineSyncConfig = {
  enabled: false,
  provider: 'firebase',
  firebase: {
    apiKey: 'AIzaSyAR4KlnQtZ8lcKsP99BuuzTkJv1xOnQJsY',
    authDomain: 'pleiades-inventory.firebaseapp.com',
    databaseURL: '',
    projectId: 'pleiades-inventory',
    appId: '1:127811575372:web:92827c992f8a5d80615ee9'
  }
};

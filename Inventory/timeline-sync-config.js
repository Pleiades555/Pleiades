/*
  Optional Firebase live-sync configuration.
  Leave enabled:false for per-user browser storage only.
  See LIVE-TIMELINE-SETUP.md before enabling this file.
*/
window.PleiadesTimelineSyncConfig = {
  enabled: false,
  provider: 'firebase',
  firebase: {
    apiKey: '',
    authDomain: '',
    databaseURL: '',
    projectId: '',
    appId: ''
  }
};

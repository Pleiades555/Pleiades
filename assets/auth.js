/* Pleiades shared authentication framework
   Branch: site-wide-login-v1
   Provides site-wide username login, permissions, admin account editing and optional GitHub users.json push.
*/
(function () {
  'use strict';

  const CONFIG = {
    usersPath: '/Pleiades/accounts/users.json',
    permissionsPath: '/Pleiades/accounts/permissions.json',
    brandCssPath: '/Pleiades/assets/brand-portal.css',
    currentUserKey: 'pleiades.currentUser',
    sessionTokenKey: 'pleiades.githubToken',
    adminPassword: 'Pleiades',
    githubOwner: 'Pleiades555',
    githubRepo: 'Pleiades',
    githubBranch: 'site-wide-login-v1',
    githubUsersPath: 'accounts/users.json'
  };

  const ROLE_DEFAULTS = {
    unrestricted: ['*'],
    externalDealer: ['site-basic', 'ford-basic', 'ford-tsb', 'ford-parts', 'ford-fluids'],
    fordParts: ['site-basic', 'ford-basic', 'ford-tsb', 'ford-parts', 'ford-fluids'],
    fordWorkshop: ['site-basic', 'ford-basic', 'ford-tsb', 'ford-fsm'],
    readOnly: ['site-basic']
  };

  const BRAND_META = {
    ford: { label: 'Ford', accent: '#3b82f6', video: '/Pleiades/assets/video/ford.mp4', chips: ['Dealer systems', 'TSBs', 'FSMs', 'Parts KB'] },
    subaru: { label: 'Subaru', accent: '#2b6cb0', video: '/Pleiades/assets/video/subaru.mp4', chips: ['Catalogue', 'Accessories', 'Learning', 'FSMs'] },
    jlr: { label: 'Jaguar Land Rover', accent: '#2f855a', video: '/Pleiades/assets/video/jlr.mp4', chips: ['JLR systems', 'Accessories', 'FSMs', 'Processes'] },
    honda: { label: 'Honda', accent: '#dc2626', video: '/Pleiades/assets/video/honda.mp4', chips: ['Extranet', 'Catalogue', 'TSBs', 'Common items'] },
    nissan: { label: 'Nissan', accent: '#ef4444', video: '/Pleiades/assets/video/nissan.mp4', chips: ['Catalogue', 'Accessories', 'FSMs', 'Ordering'] },
    toyota: { label: 'Toyota', accent: '#f43f5e', video: '/Pleiades/assets/video/toyota.mp4', chips: ['Portal', 'References'] },
    mazda: { label: 'Mazda', accent: '#9ca3af', video: '/Pleiades/assets/video/mazda.mp4', chips: ['Portal', 'References'] },
    bmw: { label: 'BMW', accent: '#0ea5e9', video: '/Pleiades/assets/video/bmw.mp4', chips: ['Portal', 'References'] },
    porsche: { label: 'Porsche', accent: '#f59e0b', video: '/Pleiades/assets/video/porsche.mp4', chips: ['Portal', 'References'] },
    audi: { label: 'Audi', accent: '#e5e7eb', video: '/Pleiades/assets/video/audi.mp4', chips: ['Portal', 'References'] },
    volvo: { label: 'Volvo', accent: '#22d3ee', video: '/Pleiades/assets/video/volvo.mp4', chips: ['Portal', 'References'] },
    kia: { label: 'Kia', accent: '#a855f7', video: '/Pleiades/assets/video/kia.mp4', chips: ['Portal', 'References'] },
    hyundai: { label: 'Hyundai', accent: '#38bdf8', video: '/Pleiades/assets/video/hyundai.mp4', chips: ['Portal', 'References'] }
  };

  const state = { users: [], permissions: {}, loaded: false };

  function normaliseUsername(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, '');
  }

  async function fetchJson(path, fallback) {
    try {
      const response = await fetch(path + '?v=' + Date.now(), { cache: 'no-store' });
      if (!response.ok) throw new Error(path + ' returned HTTP ' + response.status);
      return await response.json();
    } catch (error) {
      console.warn('[Pleiades Auth] ' + error.message);
      return fallback;
    }
  }

  async function loadData() {
    const users = await fetchJson(CONFIG.usersPath, []);
    const permissions = await fetchJson(CONFIG.permissionsPath, {});
    state.users = Array.isArray(users) ? cleanUsers(users) : [];
    state.permissions = permissions || {};
    state.loaded = true;
  }

  function cleanUsers(users) {
    const seen = new Set();
    return (users || []).map(user => {
      const username = normaliseUsername(user.username);
      return {
        username,
        name: user.name || username,
        title: user.title || 'Not specified',
        dealer: user.dealer || 'Not specified',
        department: user.department || '',
        fordStartDate: user.fordStartDate || '',
        role: user.role || 'custom',
        enabled: user.enabled !== false,
        permissions: Array.isArray(user.permissions) ? user.permissions : null,
        createdAt: user.createdAt || new Date().toISOString(),
        updatedAt: user.updatedAt || new Date().toISOString()
      };
    }).filter(user => {
      if (!user.username || seen.has(user.username)) return false;
      seen.add(user.username);
      return true;
    }).sort((a, b) => a.username.localeCompare(b.username));
  }

  function getCurrentUsername() { return normaliseUsername(localStorage.getItem(CONFIG.currentUserKey)); }
  function setCurrentUsername(username) { localStorage.setItem(CONFIG.currentUserKey, normaliseUsername(username)); }
  function clearCurrentUsername() { localStorage.removeItem(CONFIG.currentUserKey); }

  function getCurrentUser() {
    const username = getCurrentUsername();
    if (!username) return null;
    return state.users.find(user => user.enabled && normaliseUsername(user.username) === username) || null;
  }

  function getUserPermissions(user) {
    if (!user) return [];
    if (Array.isArray(user.permissions)) return user.permissions;
    return ROLE_DEFAULTS[user.role] || [];
  }

  function hasAccess(requiredAccess, user) {
    if (!requiredAccess) return true;
    const permissions = getUserPermissions(user);
    return permissions.includes('*') || permissions.includes(requiredAccess);
  }

  function applyAccess() {
    const user = getCurrentUser();
    document.documentElement.classList.toggle('pleiades-logged-in', !!user);
    document.documentElement.classList.toggle('pleiades-logged-out', !user);

    document.querySelectorAll('[data-access]').forEach(element => {
      const required = element.getAttribute('data-access');
      element.classList.toggle('pleiades-hidden', !hasAccess(required, user));
    });

    const pageRequired = document.body ? document.body.getAttribute('data-requires-access') : '';
    const pageAllowed = !pageRequired || hasAccess(pageRequired, user);

    document.querySelectorAll('[data-auth-content]').forEach(element => {
      element.classList.toggle('pleiades-hidden', !(user && pageAllowed));
    });

    const denied = document.getElementById('pleiadesAccessDenied');
    if (denied) denied.classList.toggle('pleiades-hidden', !!(user && pageAllowed));

    updateUserCard(user);
    updatePortalCards(user);
  }

  function updatePortalCards(user) {
    document.querySelectorAll('[data-portal-card]').forEach(card => {
      const required = card.getAttribute('data-access');
      card.classList.toggle('pleiades-hidden', !hasAccess(required, user));
    });
  }

  function login(username) {
    const clean = normaliseUsername(username);
    const user = state.users.find(item => item.enabled && normaliseUsername(item.username) === clean);
    if (!user) return { ok: false, message: 'No approved account found for that username.' };
    setCurrentUsername(user.username);
    applyAccess();
    return { ok: true, message: 'Access loaded for ' + user.username + '.' };
  }

  function logout() { clearCurrentUsername(); applyAccess(); }

  function calculateFordDays(startDate) {
    if (!startDate) return '0';
    const start = new Date(startDate + 'T00:00:00');
    const today = new Date();
    start.setHours(0, 0, 0, 0);
    today.setHours(0, 0, 0, 0);
    if (isNaN(start.getTime())) return '0';
    const diff = today.getTime() - start.getTime();
    if (diff < 0) return '0';
    return Math.floor(diff / 86400000).toLocaleString();
  }

  function ensureShell() {
    if (document.getElementById('pleiadesAuthShell')) return;
    const shell = document.createElement('div');
    shell.id = 'pleiadesAuthShell';
    shell.innerHTML = `
      <div id="pleiadesAccessDenied" class="pleiades-access-denied pleiades-hidden"><strong>Access required.</strong><br>Sign in with an approved Pleiades username to view this page.</div>
      <button id="pleiadesLoginButton" class="pleiades-floating-button" type="button">Login</button>
      <section id="pleiadesLoginPanel" class="pleiades-login-panel pleiades-hidden" aria-label="Pleiades login">
        <h2>Pleiades Access</h2><p>Enter your approved username.</p>
        <label for="pleiadesUsernameInput">Username</label><input id="pleiadesUsernameInput" type="text" autocomplete="username" placeholder="gurneywhite">
        <div class="pleiades-button-row"><button id="pleiadesDoLogin" type="button">Load Access</button><button id="pleiadesCloseLogin" class="secondary" type="button">Close</button></div>
        <div id="pleiadesLoginStatus" class="pleiades-status"></div>
      </section>
      <aside id="pleiadesUserCard" class="pleiades-user-card pleiades-hidden" aria-label="Current user">
        <h3 id="pleiadesCardName">User</h3><div id="pleiadesCardRole" class="role-line">Role</div>
        <div class="detail"><span>Username</span><strong id="pleiadesCardUsername">-</strong></div>
        <div class="detail"><span>Title</span><strong id="pleiadesCardTitle">-</strong></div>
        <div class="detail"><span>Dealership</span><strong id="pleiadesCardDealer">-</strong></div>
        <div class="suffer-counter"><strong id="pleiadesCardDays">0</strong><span>Days suffered dealing with Ford</span></div>
        <div class="pleiades-button-row"><button id="pleiadesSwitchUser" class="secondary" type="button">Switch</button><button id="pleiadesLogout" class="danger" type="button">Logout</button><button id="pleiadesAdminOpen" data-access="site-admin" type="button">Admin</button></div>
      </aside>
      <section id="pleiadesAdminPanel" class="pleiades-admin-panel pleiades-hidden" aria-label="Pleiades admin">
        <h2>Account Administration</h2><p>Create or update users, then optionally push <code>accounts/users.json</code> to GitHub using a fine-grained token.</p>
        <div class="pleiades-admin-grid">
          <label>Username<input id="adminUsername" type="text" placeholder="dealer123"></label><label>Name<input id="adminName" type="text" placeholder="John Smith"></label>
          <label>Title<input id="adminTitle" type="text" placeholder="Parts Interpreter"></label><label>Dealership<input id="adminDealer" type="text" placeholder="11290 - Metro Ford"></label>
          <label>Department<input id="adminDepartment" type="text" placeholder="Parts"></label><label>Ford start date<input id="adminFordStart" type="date"></label>
        </div>
        <div id="pleiadesPermissionEditor" class="pleiades-permission-editor"></div>
        <div class="pleiades-button-row"><button id="adminSaveLocal" type="button">Save Locally</button><button id="adminPushGithub" type="button">Push Users to GitHub</button><button id="adminClose" class="secondary" type="button">Close</button></div>
        <label>Fine-grained GitHub token<input id="adminGithubToken" type="password" placeholder="Paste token for this session only"></label>
        <div id="pleiadesAdminStatus" class="pleiades-status"></div><div id="pleiadesUserList" class="pleiades-user-list"></div>
      </section>`;
    document.body.appendChild(shell);
    document.getElementById('pleiadesLoginButton').addEventListener('click', showLoginPanel);
    document.getElementById('pleiadesCloseLogin').addEventListener('click', hideLoginPanel);
    document.getElementById('pleiadesDoLogin').addEventListener('click', handleLogin);
    document.getElementById('pleiadesUsernameInput').addEventListener('keydown', event => { if (event.key === 'Enter') handleLogin(); });
    document.getElementById('pleiadesSwitchUser').addEventListener('click', showLoginPanel);
    document.getElementById('pleiadesLogout').addEventListener('click', logout);
    document.getElementById('pleiadesAdminOpen').addEventListener('click', openAdminPanel);
    document.getElementById('adminClose').addEventListener('click', () => document.getElementById('pleiadesAdminPanel').classList.add('pleiades-hidden'));
    document.getElementById('adminSaveLocal').addEventListener('click', saveAdminUserLocal);
    document.getElementById('adminPushGithub').addEventListener('click', pushUsersToGitHub);
  }

  function ensureBrandCinematic() {
    if (!document.body || document.getElementById('pleiadesBrandCinematic')) return;
    const required = document.body.getAttribute('data-requires-access') || '';
    const brandKey = required.replace(/-.*/, '');
    const meta = BRAND_META[brandKey];
    if (!meta) return;

    document.body.classList.add('brand-cinematic');
    document.documentElement.style.setProperty('--brand', meta.accent);
    document.documentElement.style.setProperty('--brand-bg', hexToRgba(meta.accent, .18));

    if (!document.querySelector('link[href="' + CONFIG.brandCssPath + '"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = CONFIG.brandCssPath;
      document.head.appendChild(link);
    }

    const layer = document.createElement('div');
    layer.id = 'pleiadesBrandCinematic';
    layer.innerHTML = `<video class="brand-video-bg" autoplay muted loop playsinline preload="metadata"><source src="${meta.video}" type="video/mp4"></video><div class="brand-video-overlay"></div>`;
    document.body.prepend(layer);
    const video = layer.querySelector('video');
    video.addEventListener('error', () => { video.style.display = 'none'; });

    const hero = document.querySelector('.hero');
    if (hero && !hero.querySelector('.brand-portal-meta')) {
      const chips = document.createElement('div');
      chips.className = 'brand-portal-meta';
      chips.innerHTML = meta.chips.map(chip => `<span class="brand-chip">${escapeHtml(chip)}</span>`).join('');
      hero.appendChild(chips);
    }
  }

  function hexToRgba(hex, alpha) {
    const clean = String(hex || '#a3c5c6').replace('#', '');
    const bigint = parseInt(clean.length === 3 ? clean.split('').map(ch => ch + ch).join('') : clean, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r},${g},${b},${alpha})`;
  }

  function showLoginPanel() { document.getElementById('pleiadesLoginPanel').classList.remove('pleiades-hidden'); setTimeout(() => document.getElementById('pleiadesUsernameInput').focus(), 0); }
  function hideLoginPanel() { document.getElementById('pleiadesLoginPanel').classList.add('pleiades-hidden'); }
  function handleLogin() { const result = login(document.getElementById('pleiadesUsernameInput').value); setLoginStatus(result.message, result.ok); if (result.ok) hideLoginPanel(); }
  function setLoginStatus(message, ok) { const status = document.getElementById('pleiadesLoginStatus'); if (status) { status.textContent = message; status.className = 'pleiades-status ' + (ok ? 'good' : 'bad'); } }
  function setAdminStatus(message, ok) { const status = document.getElementById('pleiadesAdminStatus'); if (status) { status.textContent = message; status.className = 'pleiades-status ' + (ok ? 'good' : 'bad'); } }

  function updateUserCard(user) {
    const card = document.getElementById('pleiadesUserCard');
    const loginButton = document.getElementById('pleiadesLoginButton');
    if (!card || !loginButton) return;
    if (!user) { card.classList.add('pleiades-hidden'); loginButton.classList.remove('pleiades-hidden'); return; }
    card.classList.remove('pleiades-hidden'); loginButton.classList.add('pleiades-hidden');
    document.getElementById('pleiadesCardName').textContent = user.name || user.username;
    document.getElementById('pleiadesCardRole').textContent = user.role || 'custom';
    document.getElementById('pleiadesCardUsername').textContent = user.username;
    document.getElementById('pleiadesCardTitle').textContent = user.title || 'Not specified';
    document.getElementById('pleiadesCardDealer').textContent = user.dealer || 'Not specified';
    document.getElementById('pleiadesCardDays').textContent = calculateFordDays(user.fordStartDate);
  }

  function openAdminPanel() {
    const user = getCurrentUser();
    if (!hasAccess('site-admin', user)) { setLoginStatus('Admin permission required.', false); return; }
    const entered = prompt('Enter admin password:');
    if (entered !== CONFIG.adminPassword) return;
    buildPermissionEditor(); renderUserList();
    document.getElementById('pleiadesAdminPanel').classList.remove('pleiades-hidden');
  }

  function getPermissionGroups() {
    if (Array.isArray(state.permissions.permissionGroups)) return state.permissions.permissionGroups;
    return Object.keys(state.permissions || {}).map(key => ({ id: key, label: key, permissions: state.permissions[key] }));
  }

  function buildPermissionEditor(selected) {
    const host = document.getElementById('pleiadesPermissionEditor');
    if (!host) return;
    const selectedSet = new Set(selected || []);
    const groups = getPermissionGroups();
    host.innerHTML = groups.map(group => {
      const items = group.permissions || [];
      return `<fieldset><legend>${escapeHtml(group.label || group.id)}</legend>${items.map(item => {
        const key = item.key || item.id;
        return `<label class="permission-check"><input type="checkbox" value="${escapeHtml(key)}" ${selectedSet.has(key) ? 'checked' : ''}> ${escapeHtml(item.label || key)}</label>`;
      }).join('')}</fieldset>`;
    }).join('') + '<label class="permission-check"><input type="checkbox" value="*" ' + (selectedSet.has('*') ? 'checked' : '') + '> Unrestricted (*)</label>';
  }

  function getAdminFormUser() {
    const permissions = Array.from(document.querySelectorAll('#pleiadesPermissionEditor input[type="checkbox"]:checked')).map(input => input.value);
    const username = normaliseUsername(document.getElementById('adminUsername').value);
    if (!username) throw new Error('Username is required.');
    return { username, name: document.getElementById('adminName').value.trim() || username, title: document.getElementById('adminTitle').value.trim() || 'Not specified', dealer: document.getElementById('adminDealer').value.trim() || 'Not specified', department: document.getElementById('adminDepartment').value.trim() || '', fordStartDate: document.getElementById('adminFordStart').value || '', role: permissions.includes('*') ? 'unrestricted' : 'custom', enabled: true, permissions, updatedAt: new Date().toISOString() };
  }

  function saveAdminUserLocal() {
    try {
      const formUser = getAdminFormUser();
      const index = state.users.findIndex(user => user.username === formUser.username);
      if (index >= 0) state.users[index] = { ...state.users[index], ...formUser, createdAt: state.users[index].createdAt || new Date().toISOString() };
      else state.users.push({ ...formUser, createdAt: new Date().toISOString() });
      state.users = cleanUsers(state.users);
      renderUserList(); setAdminStatus('Saved locally. Push to GitHub to update users.json.', true);
    } catch (error) { setAdminStatus(error.message, false); }
  }

  function renderUserList() {
    const host = document.getElementById('pleiadesUserList');
    if (!host) return;
    host.innerHTML = state.users.map(user => `<div class="admin-user-row"><strong>${escapeHtml(user.username)}</strong><span>${escapeHtml(user.name || '')}</span><button type="button" data-edit-user="${escapeHtml(user.username)}">Edit</button></div>`).join('');
    host.querySelectorAll('[data-edit-user]').forEach(button => button.addEventListener('click', () => loadUserIntoAdmin(button.getAttribute('data-edit-user'))));
  }

  function loadUserIntoAdmin(username) {
    const user = state.users.find(item => item.username === username);
    if (!user) return;
    document.getElementById('adminUsername').value = user.username || '';
    document.getElementById('adminName').value = user.name || '';
    document.getElementById('adminTitle').value = user.title || '';
    document.getElementById('adminDealer').value = user.dealer || '';
    document.getElementById('adminDepartment').value = user.department || '';
    document.getElementById('adminFordStart').value = user.fordStartDate || '';
    buildPermissionEditor(getUserPermissions(user));
  }

  async function pushUsersToGitHub() {
    const tokenInput = document.getElementById('adminGithubToken');
    const token = (tokenInput.value || sessionStorage.getItem(CONFIG.sessionTokenKey) || '').trim();
    if (!token) { setAdminStatus('Paste a fine-grained GitHub token first.', false); return; }
    sessionStorage.setItem(CONFIG.sessionTokenKey, token); tokenInput.value = '';
    const apiUrl = `https://api.github.com/repos/${CONFIG.githubOwner}/${CONFIG.githubRepo}/contents/${CONFIG.githubUsersPath}`;
    try {
      setAdminStatus('Checking current users.json...', true);
      const getResponse = await fetch(`${apiUrl}?ref=${encodeURIComponent(CONFIG.githubBranch)}`, { headers: githubHeaders(token) });
      if (!getResponse.ok) throw new Error('GitHub read failed: HTTP ' + getResponse.status);
      const current = await getResponse.json();
      const content = JSON.stringify(cleanUsers(state.users), null, 2) + '\n';
      const putResponse = await fetch(apiUrl, { method: 'PUT', headers: { ...githubHeaders(token), 'Content-Type': 'application/json' }, body: JSON.stringify({ message: 'Update Pleiades user accounts', content: base64EncodeUnicode(content), branch: CONFIG.githubBranch, sha: current.sha }) });
      if (!putResponse.ok) throw new Error('GitHub push failed: HTTP ' + putResponse.status);
      setAdminStatus('users.json pushed to GitHub.', true);
    } catch (error) { setAdminStatus(error.message, false); }
  }

  function githubHeaders(token) { return { Accept: 'application/vnd.github+json', Authorization: 'Bearer ' + token, 'X-GitHub-Api-Version': '2022-11-28' }; }
  function base64EncodeUnicode(value) { const bytes = new TextEncoder().encode(value); let binary = ''; bytes.forEach(byte => { binary += String.fromCharCode(byte); }); return btoa(binary); }
  function escapeHtml(value) { return String(value || '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;'); }

  async function init() {
    ensureBrandCinematic();
    await loadData();
    ensureShell();
    applyAccess();
    window.PleiadesAuth = { login, logout, applyAccess, getCurrentUser, hasAccess, state };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

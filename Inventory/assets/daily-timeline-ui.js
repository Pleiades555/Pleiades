(function (TL) {
  'use strict';

  const accentOptions = [
    ['#14b8a6', 'Neon teal'],
    ['#39ff14', 'Neon green'],
    ['#00b7ff', 'Electric blue'],
    ['#2563eb', 'Royal blue'],
    ['#22d3ee', 'Cyan'],
    ['#ff2bd6', 'Hot pink'],
    ['#f43f5e', 'Rose'],
    ['#fb7185', 'Coral'],
    ['#f97316', 'Neon orange'],
    ['#facc15', 'Neon yellow'],
    ['#84cc16', 'Lime'],
    ['#a855f7', 'Electric purple'],
    ['#8b5cf6', 'Violet'],
    ['#e879f9', 'Magenta']
  ];
  const textColourOptions = [
    ['auto', 'Automatic contrast'],
    ['#f8fafc', 'Snow white'],
    ['#d8fcff', 'Ice cyan'],
    ['#bbf7d0', 'Mint green'],
    ['#fde68a', 'Soft yellow'],
    ['#172033', 'Deep navy'],
    ['#334155', 'Slate'],
    ['#111827', 'Charcoal'],
    ['#000000', 'Black']
  ];
  const fontStacks = {
    avenir: 'Avenir, "Segoe UI", Arial, sans-serif',
    segoe: '"Segoe UI", Arial, sans-serif',
    arial: 'Arial, Helvetica, sans-serif',
    verdana: 'Verdana, Geneva, sans-serif',
    trebuchet: '"Trebuchet MS", Arial, sans-serif',
    tahoma: 'Tahoma, Verdana, sans-serif',
    georgia: 'Georgia, "Times New Roman", serif',
    courier: '"Courier New", Courier, monospace'
  };
  const pageBackgrounds = {
    auto: {
      dark: 'radial-gradient(circle at top left,var(--accent-soft),transparent 34%),linear-gradient(135deg,#071019,#111827 48%,#05070b)',
      light: 'radial-gradient(circle at top left,var(--accent-soft),transparent 34%),linear-gradient(135deg,#f8fafc,#e2e8f0 52%,#f8fafc)'
    },
    midnight: { dark: 'linear-gradient(135deg,#020617,#0f172a 52%,#020617)', light: 'linear-gradient(135deg,#e8eef8,#f8fafc 52%,#e2e8f0)' },
    slate: { dark: 'linear-gradient(135deg,#111827,#334155 52%,#0f172a)', light: 'linear-gradient(135deg,#e2e8f0,#f8fafc 52%,#cbd5e1)' },
    ocean: { dark: 'linear-gradient(135deg,#032238,#0c4a6e 52%,#06141f)', light: 'linear-gradient(135deg,#e0f2fe,#f0f9ff 52%,#bae6fd)' },
    purple: { dark: 'linear-gradient(135deg,#24103a,#4c1d95 52%,#13071f)', light: 'linear-gradient(135deg,#f3e8ff,#faf5ff 52%,#e9d5ff)' },
    black: { dark: 'linear-gradient(135deg,#000,#111 52%,#000)', light: 'linear-gradient(135deg,#e5e7eb,#fff 52%,#d1d5db)' },
    warm: { dark: 'linear-gradient(135deg,#241810,#3f2a1d 52%,#17100b)', light: 'linear-gradient(135deg,#fff7ed,#fffbeb 52%,#fed7aa)' },
    ice: { dark: 'linear-gradient(135deg,#082f49,#164e63 52%,#071b26)', light: 'linear-gradient(135deg,#ecfeff,#f0fdfa 52%,#cffafe)' }
  };

  Object.assign(TL.defaults, {
    theme: 'dark',
    font: 'avenir',
    textColor: 'auto',
    background: 'auto',
    surface: 'glass'
  });
  TL.state.prefs = { ...TL.defaults, ...TL.state.prefs };

  const customizationCss = `
    body{background:var(--page-background)!important;font-family:var(--timeline-font)!important;transition:background .2s,color .2s}
    body.timeline-light{color:var(--text)}
    body.timeline-light .btn:not(.primary),body.timeline-light .expand-btn{color:#17324d;background:rgba(255,255,255,.74)}
    body.timeline-light .export-sort{color:#17324d;background:rgba(255,255,255,.74)}
    body.timeline-light .assignment-control>span,body.timeline-light .assignment-badge{color:#0f3b4f!important}
    body.timeline-light .activity{color:#0f6b78!important}
    body.timeline-light .note{color:#8a4b00}
    body.timeline-light .custom-backdrop{background:rgba(15,23,42,.42)}
    body[data-surface="solid"] .hero,body[data-surface="solid"] .slot,body[data-surface="solid"] .summary,body[data-surface="solid"] .custom-panel,body[data-surface="solid"] .day-health{backdrop-filter:none}
    body[data-surface="contrast"] .hero,body[data-surface="contrast"] .slot,body[data-surface="contrast"] .summary,body[data-surface="contrast"] .custom-panel,body[data-surface="contrast"] .day-health{backdrop-filter:none;box-shadow:0 18px 48px rgba(0,0,0,.32)}
    .custom-grid label>span{width:100%}
    .custom-grid input[type="color"]{width:100%;height:40px;margin-top:6px;border:1px solid var(--border);border-radius:10px;background:var(--panel);cursor:pointer}
    .custom-grid .colour-pair{display:grid;grid-template-columns:minmax(0,1fr) 70px;gap:8px;align-items:end}
    .custom-grid .colour-pair select{margin-top:6px}
    @media(max-width:620px){.custom-grid .colour-pair{grid-template-columns:1fr}}
  `;

  TL.installCustomizationUi = () => {
    if (!document.getElementById('timelineCustomizationCss')) {
      const style = document.createElement('style');
      style.id = 'timelineCustomizationCss';
      style.textContent = customizationCss;
      document.head.appendChild(style);
    }

    const accent = document.getElementById('prefAccent');
    const density = document.getElementById('prefDensity');
    if (!accent || !density) return;

    const accentLabel = accent.closest('label');
    if (accentLabel && !document.getElementById('prefAccentCustom')) {
      accentLabel.innerHTML = `<span>Accent colour<div class="colour-pair"><select id="prefAccent">${accentOptions.map(([value,label])=>`<option value="${value}">${label}</option>`).join('')}<option value="custom">Custom colour</option></select><input id="prefAccentCustom" type="color" value="#14b8a6" aria-label="Custom accent colour"></div></span>`;
    }

    if (!document.getElementById('prefTheme')) {
      const densityLabel = density.closest('label');
      densityLabel.insertAdjacentHTML('afterend', `
        <label><span>Appearance<select id="prefTheme"><option value="dark">Dark mode</option><option value="light">Light mode</option><option value="system">Match device</option></select></span></label>
        <label><span>Font<select id="prefFont"><option value="avenir">Avenir / system</option><option value="segoe">Segoe UI</option><option value="arial">Arial</option><option value="verdana">Verdana</option><option value="trebuchet">Trebuchet</option><option value="tahoma">Tahoma</option><option value="georgia">Georgia</option><option value="courier">Courier New</option></select></span></label>
        <label><span>Main text colour<div class="colour-pair"><select id="prefTextColor">${textColourOptions.map(([value,label])=>`<option value="${value}">${label}</option>`).join('')}<option value="custom">Custom colour</option></select><input id="prefTextColorCustom" type="color" value="#f8fafc" aria-label="Custom text colour"></div></span></label>
        <label><span>Page background<select id="prefBackground"><option value="auto">Automatic</option><option value="midnight">Midnight</option><option value="slate">Slate</option><option value="ocean">Ocean</option><option value="purple">Purple</option><option value="black">Black / monochrome</option><option value="warm">Warm</option><option value="ice">Ice blue</option></select></span></label>
        <label><span>Panel style<select id="prefSurface"><option value="glass">Glass</option><option value="solid">Solid</option><option value="contrast">High contrast</option></select></span></label>
      `);
    }
  };

  const baseApplyPreferences = TL.applyPreferences;
  TL.applyPreferences = () => {
    TL.state.prefs = { ...TL.defaults, ...TL.state.prefs };
    baseApplyPreferences();

    const prefs = TL.state.prefs;
    const systemLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
    const light = prefs.theme === 'light' || (prefs.theme === 'system' && systemLight);
    const root = document.documentElement;
    const surface = ['glass','solid','contrast'].includes(prefs.surface) ? prefs.surface : 'glass';
    const backgroundSet = pageBackgrounds[prefs.background] || pageBackgrounds.auto;
    const text = prefs.textColor && prefs.textColor !== 'auto' ? prefs.textColor : (light ? '#172033' : '#f5f5f5');
    const panel = light
      ? (surface === 'glass' ? 'rgba(255,255,255,.82)' : surface === 'solid' ? '#ffffff' : '#ffffff')
      : (surface === 'glass' ? 'rgba(10,12,16,.76)' : surface === 'solid' ? '#111827' : '#030712');
    const border = light
      ? (surface === 'contrast' ? 'rgba(15,23,42,.34)' : 'rgba(15,23,42,.16)')
      : (surface === 'contrast' ? 'rgba(255,255,255,.34)' : 'rgba(255,255,255,.14)');

    root.style.setProperty('--timeline-font', fontStacks[prefs.font] || fontStacks.avenir);
    root.style.setProperty('--page-background', light ? backgroundSet.light : backgroundSet.dark);
    root.style.setProperty('--text', text);
    root.style.setProperty('--muted', light ? '#526173' : '#cbd5e1');
    root.style.setProperty('--panel', panel);
    root.style.setProperty('--border', border);
    document.body.classList.toggle('timeline-light', light);
    document.body.dataset.surface = surface;
  };

  const optionValues = options => new Set(options.map(([value]) => value));
  const accentValues = optionValues(accentOptions);
  const textValues = optionValues(textColourOptions);
  TL.setColourControl = (selectId, customId, value, knownValues, fallback) => {
    const select = document.getElementById(selectId);
    const custom = document.getElementById(customId);
    if (!select || !custom) return;
    if (knownValues.has(value)) {
      select.value = value;
      if (value !== 'auto') custom.value = value;
    } else {
      select.value = 'custom';
      custom.value = /^#[0-9a-f]{6}$/i.test(value || '') ? value : fallback;
    }
  };
  TL.readColourControl = (selectId, customId, fallback) => {
    const select = document.getElementById(selectId);
    const custom = document.getElementById(customId);
    if (!select) return fallback;
    return select.value === 'custom' ? (custom?.value || fallback) : select.value;
  };

  TL.activityText = id => {
    const record = TL.state.activity[id];
    if (!record || !record.updatedAt) return '';
    return `${record.checked ? 'Completed' : 'Updated'} by ${record.updatedName || record.updatedBy || 'Unknown user'} · ${TL.formatDateTime(record.updatedAt)}`;
  };
  TL.assignmentText = id => {
    const assignment = TL.state.assignments[id];
    if (!assignment || !assignment.assignedTo) return 'Unassigned';
    const by = assignment.assignedByName || assignment.assignedBy;
    return `Assigned to ${assignment.assignedName || assignment.assignedTo}${by ? ` by ${by}` : ''}${assignment.assignedAt ? ` · ${TL.formatDateTime(assignment.assignedAt)}` : ''}`;
  };
  TL.assigneeOptions = selected => `<option value="">Unassigned</option>${TL.eligibleAssignees().map(user => {
    const username = TL.normaliseUsername(user.username);
    const label = `${user.name || user.username} (${username})`;
    return `<option value="${TL.escapeHtml(username)}" ${username === TL.normaliseUsername(selected) ? 'selected' : ''}>${TL.escapeHtml(label)}</option>`;
  }).join('')}`;

  TL.dayHealthEntries = () => {
    const entries = [];
    const slots = typeof TL.rawAssignedSlots === 'function' ? TL.rawAssignedSlots() : [];
    slots.forEach(slot => slot.items.forEach(item => {
      const rowId = TL.idFor(slot.time, item.brand);
      const cutoffAt = TL.parseTime(slot.time).getTime();
      item.codes.forEach(code => {
        const id = TL.codeId(rowId, code);
        const record = TL.state.activity[id] || {};
        const assignment = TL.state.assignments[id] || {};
        const completed = TL.state.done.has(id);
        const seconds = TL.secondsUntil(slot.time);
        const completedAt = completed ? (Number(record.completedAt) || Number(record.updatedAt) || 0) : 0;
        let status = 'green';
        if (!completed && seconds <= 0) status = 'red';
        else if (!completed && seconds <= 300) status = 'yellow';
        else if (completed && completedAt > cutoffAt) status = 'orange';
        entries.push({ status, slot, item, code, id, seconds, completedAt, cutoffAt, assignment });
      });
    }));
    return entries;
  };
  TL.healthDetail = entry => {
    const rawName = String(entry.assignment.assignedName || '').trim();
    const rawUsername = TL.normaliseUsername(entry.assignment.assignedTo);
    const assignee = rawName && TL.normaliseUsername(rawName) !== rawUsername ? rawName : entry.assignment.assignedTo ? 'Assigned user' : 'Unassigned';
    const identity = `${entry.item.brand} ${entry.code[0]}`;
    const cutoff = TL.displayTime(entry.slot.time);
    if (entry.status === 'red') return `${identity} · ${cutoff} · ${assignee} · ${TL.durationText(entry.seconds)} overdue`;
    if (entry.status === 'yellow') return `${identity} · ${cutoff} · ${assignee} · ${TL.durationText(entry.seconds)} remaining`;
    if (entry.status === 'orange') return `${identity} · ${cutoff} · ${assignee} · submitted ${TL.durationText(Math.ceil((entry.completedAt - entry.cutoffAt) / 1000))} late`;
    return `${identity} · ${cutoff} · ${assignee}`;
  };
  TL.updateDayHealth = () => {
    const panel = document.getElementById('dayHealth');
    if (!panel) return;
    const setText = (id, value) => { const element = document.getElementById(id); if (element) element.textContent = value; };
    try {
      const entries = TL.dayHealthEntries();
      const counts = { green: 0, yellow: 0, orange: 0, red: 0 };
      entries.forEach(entry => counts[entry.status]++);
      const status = counts.red ? 'red' : counts.yellow ? 'yellow' : counts.orange ? 'orange' : 'green';
      const titles = {
        green: 'All orders are on track',
        yellow: 'Orders are nearing cut-off',
        orange: 'Orders were submitted late',
        red: 'Order missed — intervention required'
      };
      const messages = {
        green: 'No missed, late or five-minute warnings in this view.',
        yellow: `${counts.yellow} outstanding order${counts.yellow === 1 ? ' is' : 's are'} within five minutes of cut-off. Confirm submission is underway.`,
        orange: `${counts.orange} order${counts.orange === 1 ? ' was' : 's were'} submitted after cut-off. There are no currently missed outstanding orders.`,
        red: `${counts.red} outstanding order${counts.red === 1 ? ' has' : 's have'} passed cut-off. Contact the assigned user and intervene now.`
      };

      panel.classList.remove('green', 'yellow', 'orange', 'red');
      panel.classList.add(status);
      panel.dataset.healthReady = 'true';
      panel.querySelectorAll('[data-health-light]').forEach(light => light.classList.toggle('active', light.dataset.healthLight === status));
      setText('dayHealthScope', TL.isAssignmentManager() || TL.isReadOnlyOverseer() ? 'Full-day ordering status' : 'My assigned ordering status');
      setText('dayHealthTitle', entries.length ? titles[status] : 'No orders in this view');
      setText('dayHealthMessage', entries.length ? messages[status] : 'No order codes are currently assigned or visible.');
      setText('healthGreenCount', counts.green);
      setText('healthYellowCount', counts.yellow);
      setText('healthOrangeCount', counts.orange);
      setText('healthRedCount', counts.red);

      const intervention = document.getElementById('dayHealthInterventions');
      if (!intervention) return;
      const priority = { red: 0, yellow: 1, orange: 2 };
      const attention = entries.filter(entry => entry.status !== 'green').sort((a, b) => priority[a.status] - priority[b.status] || a.cutoffAt - b.cutoffAt);
      intervention.innerHTML = attention.length
        ? `<strong>Attention</strong><div class="health-alert-list">${attention.slice(0, 6).map(entry => `<span class="health-alert ${entry.status}">${TL.escapeHtml(TL.healthDetail(entry))}</span>`).join('')}</div>${attention.length > 6 ? `<small>+ ${attention.length - 6} more warning${attention.length - 6 === 1 ? '' : 's'} in the timeline</small>` : ''}`
        : '<strong>No intervention needed</strong><span>All visible orders are currently on track.</span>';
    } catch (error) {
      console.error('[Daily Timeline health status]', error);
      panel.classList.remove('green', 'yellow', 'orange');
      panel.classList.add('red');
      setText('dayHealthTitle', 'Status temporarily unavailable');
      setText('dayHealthMessage', 'The timeline is still available. Refresh the page if this warning remains.');
      const intervention = document.getElementById('dayHealthInterventions');
      if (intervention) intervention.innerHTML = '<strong>Status error</strong><span>The warning panel could not calculate the current order state.</span>';
    }
  };

  TL.updateSummary = slots => {
    const ids = [];
    slots.forEach(slot => slot.items.forEach(item => item.codes.forEach(code => ids.push(TL.codeId(TL.idFor(slot.time, item.brand), code)))));
    const complete = ids.filter(id => TL.state.done.has(id)).length;
    document.getElementById('sumDone').textContent = `${complete} of ${ids.length}`;
    document.getElementById('sumLeft').textContent = String(ids.length - complete);
    const next = slots.find(slot => TL.secondsUntil(slot.time) >= 0 && !slot.items.every(item => TL.itemComplete(TL.idFor(slot.time, item.brand), item)));
    document.getElementById('sumNext').textContent = next ? `${TL.displayTime(next.time)} (${TL.countdownLabel(next.time)})` : 'None';
    document.getElementById('sumNow').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    document.getElementById('sumChanged').textContent = TL.state.lastChanged ? TL.formatDateTime(TL.state.lastChanged) : '-';
    document.getElementById('sumView').textContent = TL.isAssignmentManager() ? 'Full-day manager view' : TL.isReadOnlyOverseer() ? 'Full-day view only' : `${TL.state.displayName}'s assignments`;
    document.getElementById('doneToggle').textContent = TL.state.showDone ? 'Hide completed' : 'Show completed';
  };
  TL.updateLiveCountdowns = () => {
    try {
      document.querySelectorAll('[data-live-countdown]').forEach(element => {
        const closed = element.dataset.closed === 'true';
        const closedLabel = element.dataset.closedLabel || 'Done';
        element.classList.remove('late', 'soon', 'done');
        if (closed) {
          element.classList.add('done');
          element.textContent = closedLabel;
          return;
        }
        const status = TL.countdownStatus(element.dataset.time);
        if (status) element.classList.add(status);
        element.textContent = TL.countdownLabel(element.dataset.time);
      });
      TL.updateSummary(TL.activeSlots());
    } catch (error) {
      console.error('[Daily Timeline live display]', error);
    } finally {
      TL.updateDayHealth();
    }
  };

  TL.render = () => {
    const timeline = document.getElementById('timeline');
    if (!timeline) { TL.updateDayHealth(); return; }
    if (!TL.authReady() || !TL.user()) {
      timeline.innerHTML = '<div class="empty">Loading assigned transaction codes…</div>';
      TL.updateDayHealth();
      return;
    }
    const slots = TL.activeSlots();
    if (!slots.length) {
      const message = !TL.isAssignmentManager() && !TL.isReadOnlyOverseer() && TL.liveConfigured() && !TL.state.assignmentLoaded
        ? 'Loading today’s live assignments…'
        : !TL.isAssignmentManager() && !TL.isReadOnlyOverseer() && TL.state.assignmentLoaded
          ? 'No order codes have been assigned to you today.'
          : 'No visible transaction codes. Open Customize my view to restore hidden codes.';
      timeline.innerHTML = `<div class="empty">${message}</div>`;
      TL.updateSummary([]);
      TL.updateDayHealth();
      return;
    }

    const manager = TL.isAssignmentManager();
    const readOnly = TL.isReadOnlyOverseer();
    const editable = TL.canEditTimeline();
    let html = '';
    for (const slot of slots) {
      const allDone = slot.items.every(item => TL.itemComplete(TL.idFor(slot.time, item.brand), item));
      const status = allDone ? 'done' : TL.countdownStatus(slot.time);
      const label = allDone ? 'Done' : TL.countdownLabel(slot.time);
      html += `<section class="slot"><div class="slot-head"><div class="slot-time">${TL.displayTime(slot.time)}</div><div class="slot-status ${status}" data-live-countdown data-time="${TL.escapeHtml(slot.time)}" data-closed="${allDone}" data-closed-label="Done">${label}</div></div>`;
      slot.items.forEach(item => {
        const rowId = TL.idFor(slot.time, item.brand);
        const closed = TL.itemComplete(rowId, item);
        const open = TL.state.expanded.has(rowId) || !closed || TL.state.prefs.autoCollapse === false;
        const hidden = closed && !TL.state.showDone && !TL.state.expanded.has(rowId);
        const rowStatus = closed ? 'done' : TL.countdownStatus(slot.time);
        const rowLabel = closed ? 'Closed for today' : TL.countdownLabel(slot.time);
        html += `<article class="brand-row ${closed ? 'done' : ''} ${hidden ? 'hidden' : ''}"><div><div class="brand-head"><div><div class="brand-name">${TL.escapeHtml(item.brand)}</div><div class="vendor">Vendor ${TL.escapeHtml(item.vendor)}</div>${closed ? '<div class="brand-complete">✓ Closed for today</div>' : ''}</div><button class="expand-btn" type="button" data-expand="${TL.escapeHtml(rowId)}">${open ? 'Collapse' : 'Expand'}</button></div><div class="codes ${open ? '' : 'hidden'}">${item.codes.map(code => {
          const id = TL.codeId(rowId, code);
          const checked = TL.state.done.has(id);
          const activity = TL.activityText(id);
          const assignment = TL.state.assignments[id] || {};
          const assignmentControl = manager
            ? `<div class="assignment-control"><span>Assign code</span><select data-assignment="${TL.escapeHtml(id)}" ${TL.state.liveReady ? '' : 'disabled'}>${TL.assigneeOptions(assignment.assignedTo)}</select></div>`
            : `<span class="assignment-badge">${TL.escapeHtml(TL.assignmentText(id))}</span>`;
          return `<div class="code ${checked ? 'done' : ''}"><input type="checkbox" data-code-toggle="${TL.escapeHtml(id)}" data-row="${TL.escapeHtml(rowId)}" ${checked ? 'checked' : ''} ${editable ? '' : 'disabled'}><span><strong>${TL.escapeHtml(code[0])}</strong><span>${TL.escapeHtml(code[1])}</span><em>${TL.escapeHtml(code[3])}</em>${code[4] ? `<span class="warning">⚠ ${TL.escapeHtml(code[4])}</span>` : ''}${assignmentControl}<span class="code-order"><input data-order="${TL.escapeHtml(id)}" value="${TL.escapeHtml(TL.state.orders[id] || '')}" placeholder="Order number for ${TL.escapeHtml(code[0])}" ${editable ? '' : 'readonly'}><button class="copy-order" type="button" data-copy="${TL.escapeHtml(id)}">Copy</button></span>${readOnly ? '<span class="activity">View-only access — live changes cannot be edited.</span>' : ''}${activity ? `<span class="activity">${TL.escapeHtml(activity)}</span>` : ''}</span></div>`;
        }).join('')}</div>${item.note && open ? `<div class="note">${TL.escapeHtml(item.note)}</div>` : ''}${item.procedure && open ? `<div class="row-actions"><a class="procedure-link" href="${TL.escapeHtml(item.procedure)}">Open ${TL.escapeHtml(item.brand)} procedure</a></div>` : ''}</div><div class="minute ${rowStatus}" data-live-countdown data-time="${TL.escapeHtml(slot.time)}" data-closed="${closed}" data-closed-label="Closed for today">${rowLabel}</div></article>`;
      });
      html += '</section>';
    }
    timeline.innerHTML = html;
    TL.bindTimelineEvents();
    TL.updateLiveCountdowns();
  };

  TL.bindTimelineEvents = () => {
    document.querySelectorAll('[data-code-toggle]').forEach(input => input.addEventListener('change', () => TL.toggleCode(input.dataset.codeToggle, input.dataset.row, input.checked)));
    document.querySelectorAll('[data-expand]').forEach(button => button.addEventListener('click', () => TL.toggleExpand(button.dataset.expand)));
    document.querySelectorAll('[data-assignment]').forEach(select => {
      select.addEventListener('click', event => event.stopPropagation());
      select.addEventListener('change', () => TL.assignCode(select.dataset.assignment, select.value));
    });
    document.querySelectorAll('[data-order]').forEach(input => {
      input.addEventListener('click', event => event.stopPropagation());
      input.addEventListener('input', () => TL.saveOrder(input.dataset.order, input.value));
    });
    document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      TL.copyOrder(button.dataset.copy, button);
    }));
  };

  TL.openCustomizer = () => {
    TL.installCustomizationUi();
    const list = document.getElementById('customCodeList');
    const hidden = new Set(TL.state.prefs.hiddenCodes);
    const rows = [];
    TL.rawAssignedSlots().forEach(slot => slot.items.forEach(item => item.codes.forEach(code => rows.push(`<label class="custom-code"><input type="checkbox" data-code="${TL.escapeHtml(TL.permissionKey(code))}" ${hidden.has(TL.permissionKey(code)) ? '' : 'checked'}><span><strong>${TL.escapeHtml(item.brand)} ${TL.escapeHtml(code[0])}</strong><small>${TL.escapeHtml(code[1])}</small></span></label>`))));
    list.innerHTML = rows.join('');

    TL.setColourControl('prefAccent', 'prefAccentCustom', TL.state.prefs.accent, accentValues, '#14b8a6');
    TL.setColourControl('prefTextColor', 'prefTextColorCustom', TL.state.prefs.textColor, textValues, '#f8fafc');
    document.getElementById('prefDensity').value = TL.state.prefs.density;
    document.getElementById('prefTheme').value = TL.state.prefs.theme;
    document.getElementById('prefFont').value = TL.state.prefs.font;
    document.getElementById('prefBackground').value = TL.state.prefs.background;
    document.getElementById('prefSurface').value = TL.state.prefs.surface;
    document.getElementById('prefShowDone').checked = TL.state.prefs.showDone;
    document.getElementById('prefAutoCollapse').checked = TL.state.prefs.autoCollapse;
    document.getElementById('customBackdrop').classList.remove('hidden');
  };
  TL.closeCustomizer = () => document.getElementById('customBackdrop').classList.add('hidden');
  TL.savePreferences = () => {
    TL.state.prefs = {
      ...TL.state.prefs,
      accent: TL.readColourControl('prefAccent', 'prefAccentCustom', '#14b8a6'),
      textColor: TL.readColourControl('prefTextColor', 'prefTextColorCustom', 'auto'),
      density: document.getElementById('prefDensity').value,
      theme: document.getElementById('prefTheme').value,
      font: document.getElementById('prefFont').value,
      background: document.getElementById('prefBackground').value,
      surface: document.getElementById('prefSurface').value,
      showDone: document.getElementById('prefShowDone').checked,
      autoCollapse: document.getElementById('prefAutoCollapse').checked,
      hiddenCodes: [...document.querySelectorAll('#customCodeList input[data-code]:not(:checked)')].map(input => input.dataset.code)
    };
    TL.state.showDone = TL.state.prefs.showDone;
    localStorage.setItem(TL.preferenceKey(), JSON.stringify(TL.state.prefs));
    TL.applyPreferences();
    TL.closeCustomizer();
    TL.render();
  };

  TL.setSyncStatus = (mode, text) => {
    const pill = document.getElementById('syncPill');
    pill.classList.remove('live', 'error');
    if (mode) pill.classList.add(mode);
    document.getElementById('syncStatus').textContent = text;
    document.getElementById('storageNote').textContent = TL.state.liveReady
      ? (TL.isAssignmentManager()
        ? 'Shared assignments and checklist changes update live. You can allocate every code and export the full day.'
        : TL.isReadOnlyOverseer()
          ? 'Full-day view-only access. You can monitor assignments, order numbers, completion and timestamps but cannot make changes.'
          : 'Only codes allocated to your username are shown. Changes and timestamps update live.')
      : 'Live assignment data is unavailable. Cached local data may be shown until Firebase reconnects.';
  };

  TL.installCustomizationUi();
  if (window.matchMedia) {
    const media = window.matchMedia('(prefers-color-scheme: light)');
    const refreshSystemTheme = () => { if (TL.state?.prefs?.theme === 'system') TL.applyPreferences(); };
    if (media.addEventListener) media.addEventListener('change', refreshSystemTheme);
    else if (media.addListener) media.addListener(refreshSystemTheme);
  }
})(window.PleiadesTimeline = window.PleiadesTimeline || {});

const DATA = [
  'vehicles',
  'vinGenerationRules',
  'engines',
  'transmissions',
  'transmissionFamilies',
  'differentials',
  'fluids',
  'parts',
  'accessories',
  'tsbs',
  'sources',
  'reviewItems',
  'brands'
];

const state = {};
const $ = selector => document.querySelector(selector);

async function load(name) {
  if (!state[name]) {
    const response = await fetch(`data/${name}.json`);
    if (!response.ok) throw new Error(`Unable to load ${name}.json (${response.status})`);
    state[name] = await response.json();
  }
  return state[name];
}

function badge(status) {
  const css = String(status || 'unknown').replace(/[^a-z-]/g, '');
  return `<span class="badge ${css}">${status || 'unknown'}</span>`;
}

function title(value) {
  return [value.year, value.brand || value.manufacturer, value.model, value.variant]
    .filter(Boolean)
    .join(' ') || value.title || value.code || value.exactCode || value.family || value.id;
}

function longestMatchingPrefix(values, vin, field = 'vinPrefixes') {
  return values
    .flatMap(value => (value[field] || []).map(prefix => ({ value, prefix })))
    .filter(match => vin.startsWith(match.prefix))
    .sort((a, b) => b.prefix.length - a.prefix.length)[0] || null;
}

function generationMatch(rules, vin) {
  return rules
    .filter(rule => rule.prefix && vin.startsWith(rule.prefix))
    .sort((a, b) => b.prefix.length - a.prefix.length)[0] || null;
}

async function decodeVin(raw) {
  const vin = (raw || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  const out = $('#vinResult');

  if (!vin) {
    out.innerHTML = '<p class="empty">Enter a VIN to decode.</p>';
    return;
  }

  if (vin.length !== 17 || /[IOQ]/.test(vin)) {
    out.innerHTML = '<p class="error">Invalid VIN: use 17 characters and exclude I, O and Q.</p>';
    return;
  }

  try {
    const [vehicles, generationRules] = await Promise.all([
      load('vehicles'),
      load('vinGenerationRules')
    ]);

    const exact = vehicles.find(vehicle => (vehicle.exactVins || []).includes(vin));
    const vehicleFingerprint = longestMatchingPrefix(vehicles, vin);
    const generation = generationMatch(generationRules, vin);
    const vehicle = exact || vehicleFingerprint?.value;

    if (!vehicle && !generation) {
      out.innerHTML = '<p class="empty">No exact VIN, vehicle fingerprint or generation rule matched. Unknown remains unknown.</p>';
      return;
    }

    if (vehicle) {
      const matchLabel = exact ? 'exact VIN match' : 'vehicle fingerprint match';
      const inheritedGeneration = generation
        ? `<p><strong>Generation rule:</strong> ${generation.manufacturer} ${generation.model} ${generation.generation} (${generation.prefix})</p>`
        : '';

      out.innerHTML = vehicleCard(vehicle, matchLabel) +
        `<details><summary>How this VIN was decoded</summary>
          <p>Normalised to ${vin}. Exact match: ${exact ? 'yes' : 'no'}.</p>
          <p>Longest vehicle fingerprint: ${vehicleFingerprint?.prefix || 'none'}.</p>
          ${inheritedGeneration}
          <p>Only the most specific matched vehicle is displayed. Parent generation rules provide context but do not add unverified trim or powertrain claims.</p>
        </details>`;
      return;
    }

    out.innerHTML = generationCard(generation) +
      `<details><summary>How this VIN was decoded</summary>
        <p>Normalised to ${vin}. No exact or longer vehicle fingerprint matched.</p>
        <p>Generation prefix ${generation.prefix} matched.</p>
        <p>Engine, transmission, variant, model year and Australian delivery remain unresolved.</p>
      </details>`;
  } catch (error) {
    console.error(error);
    out.innerHTML = '<p class="error">VIN data could not be loaded. Please try again after the data files are available.</p>';
  }
}

function generationCard(rule) {
  return `<article class="card">
    <h3>${rule.manufacturer} ${rule.model} ${rule.generation}</h3>
    <p>${badge(rule.confidence)} generation fingerprint match</p>
    <dl>
      <dt>VIN prefix</dt><dd>${rule.prefix}</dd>
      <dt>Body family</dt><dd>${rule.bodyFamily || 'unknown'}</dd>
      <dt>Engine</dt><dd>unresolved</dd>
      <dt>Transmission</dt><dd>unresolved</dd>
      <dt>Variant</dt><dd>unresolved</dd>
    </dl>
    <p class="warning">${rule.reviewNote}</p>
  </article>`;
}

function vehicleCard(vehicle, match = 'record') {
  return `<article class="card">
    <h3>${title(vehicle)}</h3>
    <p>${badge(vehicle.claims?.identity?.status || vehicle.confidence)} ${match}</p>
    <dl>
      <dt>Engine</dt><dd>${vehicle.legacyEngineSnapshot?.code || vehicle.engineRef || 'unknown'} ${vehicle.legacyEngineSnapshot?.family || ''}</dd>
      <dt>Transmission</dt><dd>${vehicle.transmissionRef || vehicle.transmission || 'unknown'}</dd>
      <dt>Driveline</dt><dd>${vehicle.drive || 'unknown'}</dd>
      <dt>Chassis</dt><dd>${vehicle.chassis || 'unknown'}</dd>
    </dl>
    ${vehicle.sourceWarning ? `<p class="warning">${vehicle.sourceWarning}</p>` : ''}
    ${(vehicle.differentialRefs || []).map(diff => `<p>${badge('estimated')} ${diff}</p>`).join('')}
  </article>`;
}

async function search(query) {
  const index = await fetch('data/search-index.json').then(response => response.json());
  const terms = (query || '').toLowerCase().split(/\s+/).filter(Boolean);
  const expanded = [...terms, ...terms.flatMap(term => index.synonyms[term] || [])];
  const hits = index.items.filter(item => expanded.every(term => item.tokens.includes(term))).slice(0, 50);
  const groups = {};
  hits.forEach(hit => (groups[hit.type] ??= []).push(hit));
  $('#searchResults').innerHTML = Object.entries(groups)
    .map(([type, items]) => `<section><h3>${type}</h3>${items.map(item => `<button class="result" data-id="${item.id}" data-type="${item.type}">${item.title}<small>${item.id}</small></button>`).join('')}</section>`)
    .join('') || '<p class="empty">No results.</p>';
}

async function renderSection(name) {
  const rows = await load(name);
  $('#panel').innerHTML = `<h2>${name}</h2><div class="grid">${rows.slice(0, 200).map(row => `<article class="card"><h3>${title(row)}</h3><p>${row.id}</p>${badge(row.status || row.confidence || row.reviewStatus)}</article>`).join('')}</div>`;
}

async function dashboard() {
  const counts = await Promise.all(DATA.map(async name => [name, (await load(name)).length]));
  $('#panel').innerHTML = '<h2>Dashboard</h2><div class="grid">' +
    counts.map(([name, count]) => `<button class="card" onclick="renderSection('${name}')"><strong>${count}</strong><span>${name}</span></button>`).join('') +
    '</div><p><a href="../Pleiades Version 3.html">Back to legacy V3 site</a></p>';
}

addEventListener('DOMContentLoaded', () => {
  dashboard();
  $('#vinForm').onsubmit = event => {
    event.preventDefault();
    decodeVin($('#vin').value);
  };
  $('#search').oninput = event => search(event.target.value);
  document.querySelectorAll('[data-section]').forEach(anchor => {
    anchor.onclick = event => {
      event.preventDefault();
      renderSection(anchor.dataset.section);
    };
  });
});

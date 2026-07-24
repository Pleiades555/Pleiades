const DATA = [
  'vehicles',
  'vinReferences',
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
    const response = await fetch(`public/data/${name}.json`).catch(() => null);
    const fallback = response && response.ok ? response : await fetch(`data/${name}.json`);
    if (!fallback.ok) throw new Error(`Unable to load ${name}.json (${fallback.status})`);
    state[name] = await fallback.json();
  }
  return state[name];
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function badge(status) {
  const value = String(status || 'unknown');
  const css = value.replace(/[^a-z-]/gi, '').toLowerCase();
  return `<span class="badge ${css}">${escapeHtml(value)}</span>`;
}

function title(value) {
  return [
    value.year || value.modelYear,
    value.brand || value.manufacturer,
    value.model,
    value.body,
    value.powertrain,
    value.variant === 'unresolved' ? null : value.variant
  ].filter(Boolean).join(' ') ||
    value.title || value.code || value.exactCode || value.family || value.id;
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

function normaliseLookup(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function referenceSearchText(reference) {
  return normaliseLookup([
    reference.vin,
    reference.market,
    reference.brand,
    reference.model,
    reference.modelCode,
    reference.chassis,
    reference.body,
    reference.modelYear,
    reference.advertisedYear,
    reference.powertrain,
    reference.variant,
    reference.engineFamily,
    reference.transmission,
    reference.drivetrain,
    reference.stockNumber,
    ...(reference.aliases || [])
  ].filter(Boolean).join(' '));
}

function referenceFromVehicle(vehicle, vin) {
  return {
    id: `vinref:${vin.toLowerCase()}`,
    vin,
    market: vehicle.market || 'Australia',
    brand: vehicle.brand,
    model: vehicle.model,
    modelCode: vehicle.modelCode || vehicle.chassis,
    body: vehicle.body,
    modelYear: vehicle.year,
    powertrain: vehicle.legacyEngineSnapshot?.marketingName ||
      vehicle.legacyEngineSnapshot?.code ||
      vehicle.variant,
    variant: vehicle.variant,
    engineFamily: vehicle.legacyEngineSnapshot?.family ||
      vehicle.legacyEngineSnapshot?.description ||
      vehicle.engineRef,
    transmission: vehicle.transmission || vehicle.transmissionRef,
    drivetrain: vehicle.drive,
    confidence: vehicle.confidence,
    epcUsage: 'Reference VIN for EPC lookup only; confirm part applicability against the target vehicle.',
    source: { type: 'Pleiades confirmed vehicle record' }
  };
}

function mergeVinReferences(references, vehicles) {
  const merged = new Map();
  vehicles.forEach(vehicle => {
    [...new Set(vehicle.exactVins || [])].forEach(vin => {
      merged.set(vin, referenceFromVehicle(vehicle, vin));
    });
  });
  references.forEach(reference => merged.set(reference.vin, reference));
  return [...merged.values()];
}

function scoreReference(reference, query) {
  const normalised = normaliseLookup(query);
  if (!normalised) return -1;

  const compactQuery = normalised.replaceAll(' ', '');
  const compactVin = String(reference.vin || '').toLowerCase();
  if (compactQuery === compactVin) return 100000;

  const terms = normalised.split(/\s+/).filter(Boolean);
  const tokens = referenceSearchText(reference).split(/\s+/).filter(Boolean);
  let score = 0;

  for (const term of terms) {
    const exact = tokens.some(token => token === term);
    const prefix = tokens.some(token => token.startsWith(term));
    const contains = tokens.some(token => token.includes(term));

    if (!exact && !prefix && !contains) return -1;
    score += exact ? 100 : prefix ? 60 : 20;

    if (term === String(reference.modelYear)) score += 80;
    if (term === normaliseLookup(reference.modelCode)) score += 80;
    if (term === normaliseLookup(reference.powertrain)) score += 80;
    if (compactVin.startsWith(term)) score += 120;
  }

  return score;
}

function findVinReferences(references, query, limit = 20) {
  return references
    .map(reference => ({ reference, score: scoreReference(reference, query) }))
    .filter(result => result.score >= 0)
    .sort((a, b) =>
      b.score - a.score ||
      Number(b.reference.modelYear || 0) - Number(a.reference.modelYear || 0) ||
      String(a.reference.vin).localeCompare(String(b.reference.vin))
    )
    .slice(0, limit)
    .map(result => result.reference);
}

function vinReferenceCard(reference, match = 'EPC reference') {
  const sourceLink = reference.source?.url
    ? `<a class="source-link" href="${escapeHtml(reference.source.url)}" target="_blank" rel="noopener">Open Australian source</a>`
    : '';
  const advertised = reference.advertisedYear &&
    Number(reference.advertisedYear) !== Number(reference.modelYear)
    ? `<dt>Advertised year</dt><dd>${escapeHtml(reference.advertisedYear)}</dd>`
    : '';
  const review = reference.review
    ? `<p class="warning">${escapeHtml(reference.review)}</p>`
    : '';

  return `<article class="card vin-reference">
    <h3>${escapeHtml(title(reference))}</h3>
    <p>${badge(reference.confidence)} ${escapeHtml(match)}</p>
    <div class="vin-line">
      <code>${escapeHtml(reference.vin)}</code>
      <button type="button" class="copy-vin" data-vin="${escapeHtml(reference.vin)}">Copy VIN</button>
    </div>
    <dl>
      <dt>Model code</dt><dd>${escapeHtml(reference.modelCode || 'unknown')}</dd>
      <dt>Model year</dt><dd>${escapeHtml(reference.modelYear || 'unknown')}</dd>
      ${advertised}
      <dt>Powertrain</dt><dd>${escapeHtml(reference.powertrain || 'unresolved')}</dd>
      <dt>Engine family</dt><dd>${escapeHtml(reference.engineFamily || 'unresolved')}</dd>
      <dt>Transmission</dt><dd>${escapeHtml(reference.transmission || 'unresolved')}</dd>
      <dt>Drivetrain</dt><dd>${escapeHtml(reference.drivetrain || 'unresolved')}</dd>
      <dt>Stock</dt><dd>${escapeHtml(reference.stockNumber || 'not recorded')}</dd>
    </dl>
    <p class="epc-note">${escapeHtml(reference.epcUsage || 'Reference VIN only. Confirm applicability before ordering parts.')}</p>
    ${review}
    ${sourceLink}
  </article>`;
}

async function allVinReferences() {
  const [references, vehicles] = await Promise.all([
    load('vinReferences'),
    load('vehicles')
  ]);
  return mergeVinReferences(references, vehicles);
}

async function renderVinLookup(query) {
  const output = $('#vehicleLookupResults');
  if (!output) return;

  if (!normaliseLookup(query)) {
    output.innerHTML = '<p class="empty">Start typing a year, model, powertrain, model code or VIN.</p>';
    return;
  }

  try {
    const references = await allVinReferences();
    const hits = findVinReferences(references, query);
    output.innerHTML = hits.length
      ? `<div class="result-grid">${hits.map(reference => vinReferenceCard(reference)).join('')}</div>`
      : '<p class="empty">No matching reference VIN. Unknown remains unknown.</p>';
  } catch (error) {
    console.error(error);
    output.innerHTML = '<p class="error">VIN reference data could not be loaded.</p>';
  }
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
    const [vehicles, generationRules, references] = await Promise.all([
      load('vehicles'),
      load('vinGenerationRules'),
      allVinReferences()
    ]);

    const exact = vehicles.find(vehicle => (vehicle.exactVins || []).includes(vin));
    const exactReference = references.find(reference => reference.vin === vin);
    const vehicleFingerprint = longestMatchingPrefix(vehicles, vin);
    const generation = generationMatch(generationRules, vin);
    const vehicle = exact || vehicleFingerprint?.value;

    if (exactReference && !exact) {
      out.innerHTML = vinReferenceCard(exactReference, 'exact saved VIN match') +
        `<details><summary>How this VIN was decoded</summary>
          <p>Normalised to ${escapeHtml(vin)} and matched an exact Australian EPC reference VIN.</p>
          <p>The saved full-VIN identity outranks broader fingerprint and generation rules.</p>
        </details>`;
      return;
    }

    if (!vehicle && !generation) {
      out.innerHTML = '<p class="empty">No exact VIN, saved EPC reference, vehicle fingerprint or generation rule matched. Unknown remains unknown.</p>';
      return;
    }

    if (vehicle) {
      const matchLabel = exact ? 'exact VIN match' : 'vehicle fingerprint match';
      const inheritedGeneration = generation
        ? `<p><strong>Generation rule:</strong> ${escapeHtml(generation.manufacturer)} ${escapeHtml(generation.model)} ${escapeHtml(generation.generation)} (${escapeHtml(generation.prefix)})</p>`
        : '';

      out.innerHTML = vehicleCard(vehicle, matchLabel) +
        `<details><summary>How this VIN was decoded</summary>
          <p>Normalised to ${escapeHtml(vin)}. Exact match: ${exact ? 'yes' : 'no'}.</p>
          <p>Longest vehicle fingerprint: ${escapeHtml(vehicleFingerprint?.prefix || 'none')}.</p>
          ${inheritedGeneration}
          <p>Only the most specific matched vehicle is displayed. Parent generation rules provide context but do not add unverified trim or powertrain claims.</p>
        </details>`;
      return;
    }

    out.innerHTML = generationCard(generation) +
      `<details><summary>How this VIN was decoded</summary>
        <p>Normalised to ${escapeHtml(vin)}. No exact or longer vehicle fingerprint matched.</p>
        <p>Generation prefix ${escapeHtml(generation.prefix)} matched.</p>
        <p>Engine, transmission, variant, model year and Australian delivery remain unresolved.</p>
      </details>`;
  } catch (error) {
    console.error(error);
    out.innerHTML = '<p class="error">VIN data could not be loaded. Please try again after the data files are available.</p>';
  }
}

function generationCard(rule) {
  return `<article class="card">
    <h3>${escapeHtml(rule.manufacturer)} ${escapeHtml(rule.model)} ${escapeHtml(rule.generation)}</h3>
    <p>${badge(rule.confidence)} generation fingerprint match</p>
    <dl>
      <dt>VIN prefix</dt><dd>${escapeHtml(rule.prefix)}</dd>
      <dt>Body family</dt><dd>${escapeHtml(rule.bodyFamily || 'unknown')}</dd>
      <dt>Engine</dt><dd>unresolved</dd>
      <dt>Transmission</dt><dd>unresolved</dd>
      <dt>Variant</dt><dd>unresolved</dd>
    </dl>
    <p class="warning">${escapeHtml(rule.reviewNote)}</p>
  </article>`;
}

function vehicleCard(vehicle, match = 'record') {
  return `<article class="card">
    <h3>${escapeHtml(title(vehicle))}</h3>
    <p>${badge(vehicle.claims?.identity?.status || vehicle.confidence)} ${escapeHtml(match)}</p>
    <dl>
      <dt>Engine</dt><dd>${escapeHtml(vehicle.legacyEngineSnapshot?.code || vehicle.engineRef || 'unknown')} ${escapeHtml(vehicle.legacyEngineSnapshot?.family || '')}</dd>
      <dt>Transmission</dt><dd>${escapeHtml(vehicle.transmissionRef || vehicle.transmission || 'unknown')}</dd>
      <dt>Driveline</dt><dd>${escapeHtml(vehicle.drive || 'unknown')}</dd>
      <dt>Chassis</dt><dd>${escapeHtml(vehicle.chassis || vehicle.modelCode || 'unknown')}</dd>
    </dl>
    ${vehicle.sourceWarning ? `<p class="warning">${escapeHtml(vehicle.sourceWarning)}</p>` : ''}
    ${(vehicle.differentialRefs || []).map(diff => `<p>${badge('estimated')} ${escapeHtml(diff)}</p>`).join('')}
  </article>`;
}

async function search(query) {
  const [index, references] = await Promise.all([
    fetch('public/data/search-index.json')
      .then(response => response.ok ? response : fetch('data/search-index.json'))
      .then(response => response.json()),
    allVinReferences()
  ]);
  const terms = normaliseLookup(query).split(/\s+/).filter(Boolean);
  const expanded = [...terms, ...terms.flatMap(term => index.synonyms[term] || [])];
  const hits = terms.length
    ? index.items.filter(item => expanded.every(term => item.tokens.includes(term))).slice(0, 50)
    : [];
  const vinHits = findVinReferences(references, query, 12);
  const groups = {};
  hits.forEach(hit => (groups[hit.type] ??= []).push(hit));

  const vinSection = vinHits.length
    ? `<section><h3>VIN / EPC references</h3><div class="result-grid">${vinHits.map(reference => vinReferenceCard(reference)).join('')}</div></section>`
    : '';
  const normalSections = Object.entries(groups)
    .map(([type, items]) => `<section><h3>${escapeHtml(type)}</h3>${items.map(item => `<button class="result" data-id="${escapeHtml(item.id)}" data-type="${escapeHtml(item.type)}">${escapeHtml(item.title)}<small>${escapeHtml(item.id)}</small></button>`).join('')}</section>`)
    .join('');

  $('#searchResults').innerHTML = vinSection + normalSections ||
    (terms.length ? '<p class="empty">No results.</p>' : '');
}

async function renderSection(name) {
  const rows = await load(name);
  $('#panel').innerHTML = `<h2>${escapeHtml(name)}</h2><div class="grid">${rows.slice(0, 200).map(row => {
    if (name === 'vinReferences') return vinReferenceCard(row);
    return `<article class="card"><h3>${escapeHtml(title(row))}</h3><p>${escapeHtml(row.id)}</p>${badge(row.status || row.confidence || row.reviewStatus)}</article>`;
  }).join('')}</div>`;
}

async function dashboard() {
  const counts = await Promise.all(DATA.map(async name => [name, (await load(name)).length]));
  $('#panel').innerHTML = '<h2>Dashboard</h2><div class="grid">' +
    counts.map(([name, count]) => `<button class="card" onclick="renderSection('${escapeHtml(name)}')"><strong>${count}</strong><span>${escapeHtml(name)}</span></button>`).join('') +
    '</div><p><a href="../Pleiades Version 3.html">Back to legacy V3 site</a></p>';
}

async function copyVin(vin, button) {
  try {
    await navigator.clipboard.writeText(vin);
  } catch {
    const input = document.createElement('textarea');
    input.value = vin;
    input.setAttribute('readonly', '');
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    input.remove();
  }
  const previous = button.textContent;
  button.textContent = 'Copied';
  setTimeout(() => { button.textContent = previous; }, 1200);
}

addEventListener('DOMContentLoaded', () => {
  dashboard();

  $('#vinForm').onsubmit = event => {
    event.preventDefault();
    decodeVin($('#vin').value);
  };

  $('#search').oninput = event => search(event.target.value);

  const vehicleLookup = $('#vehicleLookup');
  if (vehicleLookup) {
    vehicleLookup.oninput = event => renderVinLookup(event.target.value);
    renderVinLookup('');
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('.copy-vin');
    if (button) copyVin(button.dataset.vin, button);
  });

  document.querySelectorAll('[data-section]').forEach(anchor => {
    anchor.onclick = event => {
      event.preventDefault();
      renderSection(anchor.dataset.section);
    };
  });
});

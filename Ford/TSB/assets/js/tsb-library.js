let allItems = [];
let activeFilter = 'all';
const search = document.getElementById('tsbSearch');
const results = document.getElementById('results');
const summary = document.getElementById('summary');
const template = document.getElementById('resultTemplate');

function clean(value){ return value === undefined || value === null || value === '' ? 'Unknown' : String(value); }
function norm(value){ return clean(value).toLowerCase(); }
function linkForNumber(num){ return allItems.find(x => norm(x.tsbNumber) === norm(num) || norm(x.bulletinNumber) === norm(num)); }

async function load(){
  try{
    const res = await fetch('data/tsb-index.json?v=' + Date.now());
    if(!res.ok) throw new Error('Index not found');
    allItems = await res.json();
    allItems.sort((a,b)=> norm(b.date || b.tsbNumber).localeCompare(norm(a.date || a.tsbNumber)));
    render();
  }catch(err){
    summary.textContent = 'Could not load data/tsb-index.json. Run the generator or push PDFs to trigger GitHub Actions.';
    results.innerHTML = '<div class="empty">No index loaded yet.</div>';
  }
}

function matchesFilter(item){
  const status = norm(item.status);
  if(activeFilter === 'current') return status !== 'superseded';
  if(activeFilter === 'superseded') return status === 'superseded';
  if(activeFilter === 'missing-meta') return !item.model || !item.symptom || item.model === 'Unknown' || item.symptom === 'Unknown';
  return true;
}

function matchesSearch(item, q){
  if(!q) return true;
  const haystack = [item.tsbNumber,item.bulletinNumber,item.model,item.vehicleGeneration,item.engine,item.transmission,item.symptom,item.description,item.status,item.supersedes,item.supersededBy,item.file,item.textPreview].join(' ').toLowerCase();
  return q.split(/\s+/).every(part => haystack.includes(part));
}

function render(){
  const q = search.value.trim().toLowerCase();
  const filtered = allItems.filter(item => matchesFilter(item) && matchesSearch(item,q));
  summary.textContent = `${filtered.length} result${filtered.length===1?'':'s'} shown from ${allItems.length} indexed PDF${allItems.length===1?'':'s'}.`;
  if(!filtered.length){ results.innerHTML = '<div class="empty">No matching TSBs found.</div>'; return; }
  results.innerHTML = '';
  for(const item of filtered){
    const node = template.content.cloneNode(true);
    const card = node.querySelector('.card');
    const statusText = clean(item.status || 'Current');
    const isSup = statusText.toLowerCase() === 'superseded';
    card.classList.add(isSup ? 'superseded' : 'current');
    node.querySelector('.title').textContent = `${clean(item.tsbNumber || item.bulletinNumber || 'Unknown Bulletin')} — ${clean(item.model)}`;
    node.querySelector('.meta').textContent = [item.vehicleGeneration, item.engine, item.transmission, item.date].filter(Boolean).join(' · ') || clean(item.fileName);
    const badge = node.querySelector('.status'); badge.textContent = statusText; badge.classList.add(isSup ? 'superseded' : 'current');
    node.querySelector('.symptom').textContent = item.symptom || item.description || 'No symptom listed.';
    const sup = node.querySelector('.supersession');
    let supHtml = '';
    if(item.supersededBy){ const target = linkForNumber(item.supersededBy); supHtml += `<div class="notice">⚠️ Superseded by ${target ? `<a href="${target.file}">${item.supersededBy}</a>` : item.supersededBy}</div>`; }
    if(item.supersedes){ const target = linkForNumber(item.supersedes); supHtml += `<div class="notice">↳ Supersedes ${target ? `<a href="${target.file}">${item.supersedes}</a>` : item.supersedes}</div>`; }
    sup.innerHTML = supHtml;
    const details = node.querySelector('.details');
    ['tsbNumber','bulletinNumber','model','vehicleGeneration','engine','transmission'].forEach(k => { if(item[k]) details.insertAdjacentHTML('beforeend', `<span class="chip">${k}: ${item[k]}</span>`); });
    const a = node.querySelector('.open'); a.href = item.file; a.textContent = `Open ${clean(item.fileName || 'PDF')}`;
    results.appendChild(node);
  }
}

document.querySelectorAll('.filter').forEach(btn => btn.addEventListener('click', () => { document.querySelectorAll('.filter').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); activeFilter = btn.dataset.filter; render(); }));
search.addEventListener('input', render);
load();

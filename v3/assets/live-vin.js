(()=>{'use strict';
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
let rules=[];
function clean(v){return String(v||'').toUpperCase().replace(/[^A-HJ-NPR-Z0-9]/g,'').slice(0,17)}
function render(value){const box=document.getElementById('vinLiveResult');if(!box)return;if(!value){box.innerHTML='';return}
const matched=rules.filter(r=>value.startsWith(r.prefix)).sort((a,b)=>a.prefix.length-b.prefix.length);
const next=rules.filter(r=>r.prefix.startsWith(value)&&r.prefix.length>value.length).sort((a,b)=>a.prefix.length-b.prefix.length);
let html='';
if(matched.length){html+=`<div class="notice ok"><strong>Decoded so far</strong><div class="results">${matched.map(r=>`<article class="result-card"><span class="badge">${esc(r.prefix)} · ${esc(r.level)}</span><h3>${esc(r.label)}</h3><p class="muted">${esc(r.description||'')}</p></article>`).join('')}</div></div>`}
else html+=`<div class="notice">No confirmed progressive rule yet for <strong>${esc(value)}</strong>.</div>`;
if(next.length){const seen=new Set();const immediate=[];for(const r of next){const key=r.prefix.slice(0,Math.min(r.prefix.length,value.length+3));if(!seen.has(key)){seen.add(key);immediate.push(r)}if(immediate.length>=8)break}html+=`<div class="panel"><h3>Possible continuations</h3><div class="results">${immediate.map(r=>`<article class="result-card"><span class="badge">${esc(r.prefix)}</span><h3>${esc(r.label)}</h3><p class="muted">${esc(r.description||'')}</p></article>`).join('')}</div></div>`}
box.innerHTML=html}
async function init(){try{const res=await fetch('./data/vin-prefixes.json');const data=await res.json();rules=data.rules||[]}catch(e){console.warn('Progressive VIN rules unavailable',e)}
const input=document.getElementById('vinInput');if(!input)return;input.addEventListener('input',()=>{const v=clean(input.value);input.value=v;render(v)});render(clean(input.value))}
document.addEventListener('DOMContentLoaded',init);
})();

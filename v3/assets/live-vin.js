(()=>{
'use strict';
const VIN_LENGTH=17;
const POSITION_HINTS=['Region','Manufacturer','Vehicle type','Descriptor 1','Descriptor 2','Descriptor 3','Descriptor 4','Descriptor 5','Check digit / descriptor','Model year','Plant','Serial 1','Serial 2','Serial 3','Serial 4','Serial 5','Serial 6'];
const YEAR_CODES='ABCDEFGHJKLMNPRSTVWXY123456789';
const YEAR_STARTS=[1980,2010];
const TRANSLITERATION={A:1,B:2,C:3,D:4,E:5,F:6,G:7,H:8,J:1,K:2,L:3,M:4,N:5,P:7,R:9,S:2,T:3,U:4,V:5,W:6,X:7,Y:8,Z:9};
const WEIGHTS=[8,7,6,5,4,3,2,10,0,9,8,7,6,5,4,3,2];
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
let rules=[],brands=[],vehicles=[];

function clean(value){return String(value||'').toUpperCase().replace(/[^A-HJ-NPR-Z0-9]/g,'').slice(0,VIN_LENGTH)}
function labelForRule(rule){return [rule.year,rule.brand,rule.model,rule.variant].filter(Boolean).join(' ')||rule.label||rule.brand||rule.prefix}
function confidenceClass(value=''){if(/exact|confirmed|user/.test(value))return'ok';if(/standard|platform|manufacturer/.test(value))return'partial';return'research'}
function regionFor(first){if(/[1-5]/.test(first))return'North America';if(/[6-7]/.test(first))return'Oceania';if(/[8-9]/.test(first))return'South America';if(/[A-H]/.test(first))return'Africa';if(/[J-R]/.test(first))return'Asia';if(/[S-Z]/.test(first))return'Europe';return null}
function yearCandidates(code){const index=YEAR_CODES.indexOf(String(code||''));return index<0?[]:YEAR_STARTS.map(start=>start+index)}
function checkDigitFor(vin){
  if(vin.length!==VIN_LENGTH)return null;
  let sum=0;
  for(let i=0;i<VIN_LENGTH;i++){
    const ch=vin[i];
    const value=/\d/.test(ch)?Number(ch):TRANSLITERATION[ch];
    if(value===undefined)return null;
    sum+=value*WEIGHTS[i];
  }
  const remainder=sum%11;
  return remainder===10?'X':String(remainder);
}
function structure(value){
  const vin=clean(value);
  const computed=checkDigitFor(vin);
  const supplied=vin.length>=9?vin[8]:null;
  const northAmerican=/^[1-5]/.test(vin);
  return {
    vin,
    validLength:vin.length===VIN_LENGTH,
    region:regionFor(vin[0]),
    wmi:vin.length>=3?vin.slice(0,3):vin,
    descriptor:vin.length>=9?vin.slice(3,9):vin.slice(3),
    yearCode:vin.length>=10?vin[9]:null,
    yearCandidates:vin.length>=10?yearCandidates(vin[9]):[],
    plant:vin.length>=11?vin[10]:null,
    serial:vin.length>=17?vin.slice(11):vin.slice(11),
    checkDigit:{supplied,computed,match:computed!==null&&supplied===computed,applicability:northAmerican?'expected-for-region':'informational-outside-north-america'}
  };
}
function brandMatches(value,allBrands=brands){
  const vin=clean(value);
  if(!vin)return[];
  const probe=vin.slice(0,Math.min(3,vin.length));
  return allBrands.filter(brand=>(brand.wmis||[]).some(wmi=>vin.length<3?wmi.startsWith(probe):wmi===vin.slice(0,3)));
}
function vehicleRules(rows){
  return rows.flatMap(vehicle=>(vehicle.vinPrefixes||[]).map(prefix=>({
    prefix,level:'confirmed-vehicle-profile',brand:vehicle.brand,year:vehicle.year,model:vehicle.model,variant:vehicle.variant,
    generation:vehicle.generation,chassis:vehicle.chassis,engineCode:vehicle.engine?.code,
    transmission:typeof vehicle.transmission==='string'?vehicle.transmission:vehicle.transmission?.family,
    label:[vehicle.year,vehicle.brand,vehicle.model,vehicle.variant].filter(Boolean).join(' '),
    description:'Reviewed Australian-market vehicle profile. Open the complete decode to view its evidence and confidence.',
    confidence:vehicle.confidence||'confirmed vehicle profile',derivedFrom:'vehicles.json'
  })));
}
function dedupeRules(rows){const seen=new Map();for(const row of rows){const key=`${row.prefix}|${row.label||''}`;if(!seen.has(key))seen.set(key,row)}return[...seen.values()]}
function renderRuler(value){return `<div class="vin-ruler" aria-label="VIN progress">${Array.from({length:VIN_LENGTH},(_,i)=>`<div class="vin-cell ${value[i]?'filled':''}"><strong>${esc(value[i]||'·')}</strong><small>${i+1}</small><span>${esc(POSITION_HINTS[i])}</span></div>`).join('')}</div>`}
function renderProgress(value,matched,next){const pct=Math.round((value.length/VIN_LENGTH)*100);const best=matched[0];const status=best?`${best.level} match`:next.length?'narrowing evidence paths':'no hosted model rule';return `<div class="vin-preview-head"><div><strong>${esc(value.length)} / ${VIN_LENGTH} characters</strong><p class="muted">${esc(status)}. Results remain evidence-only; unknown Australian model, trim and specifications are not inferred.</p></div><div class="vin-meter" aria-label="${pct}% complete"><span style="width:${pct}%"></span></div></div>`}
function renderTrail(value,matched){const points=[...new Set([...matched.map(rule=>rule.prefix),value.length>=3?value.slice(0,3):null].filter(Boolean))].sort((a,b)=>a.length-b.length);if(!points.length)return'';return `<div class="vin-trail"><strong>Confirmed prefix trail</strong><div>${points.map((point,index)=>`${index?' <span aria-hidden="true">→</span> ':''}<span class="badge">${esc(point)}</span>`).join('')}</div></div>`}
function renderNextChars(value,next){const counts=new Map();const paths=[...next.map(rule=>rule.prefix),...brands.flatMap(brand=>brand.wmis||[])];paths.filter(prefix=>prefix.startsWith(value)&&prefix.length>value.length).forEach(prefix=>{const ch=prefix[value.length];if(ch)counts.set(ch,(counts.get(ch)||0)+1)});const chips=[...counts.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,18);return chips.length?`<div class="vin-next"><strong>Observed next characters</strong><div>${chips.map(([ch,n])=>`<span class="badge">${esc(ch)} · ${n}</span>`).join('')}</div></div>`:''}
function renderStats(matched,next,candidates){const levels=new Map();[...matched,...next].forEach(rule=>levels.set(rule.level,(levels.get(rule.level)||0)+1));if(candidates.length)levels.set('candidate-makes',candidates.length);return levels.size?`<div class="vin-stats">${[...levels.entries()].map(([level,n])=>`<div class="fact"><small>${esc(level)}</small><strong>${n}</strong></div>`).join('')}</div>`:''}
function renderBest(best,value){if(!best)return `<div class="notice">No confirmed model/configuration rule yet for <strong>${esc(value)}</strong>. Manufacturer routing and manual make research remain available.</div>`;const cls=confidenceClass(best.confidence);const facts=[['Prefix',best.prefix],['Level',best.level],['Brand',best.brand],['Model',best.model],['Generation',best.generation],['Chassis',best.chassis],['Variant',best.variant],['Engine',best.engineCode],['Transmission',best.transmission||best.transmissionCode],['Confidence',best.confidence]].filter(([,v])=>v);return `<div class="notice ${cls==='ok'?'ok':''}"><strong>Most specific hosted evidence</strong><div class="results"><article class="result-card"><span class="badge">${esc(best.prefix)} · ${esc(best.level)}</span><h3>${esc(labelForRule(best))}</h3><p class="muted">${esc(best.description||'')}</p><div class="vin-stats">${facts.map(([key,item])=>`<div class="fact"><small>${esc(key)}</small><strong>${esc(item)}</strong></div>`).join('')}</div></article></div></div>`}
function renderWmi(value,candidates){
  if(!candidates.length)return value.length>=3?`<div class="notice"><strong>WMI not hosted:</strong> ${esc(value.slice(0,3))}. Use the Australian make directory or official WMI research link after entering all 17 characters.</div>`:'';
  const exact=value.length>=3;
  const labels=candidates.map(brand=>brand.brand).sort();
  const shared=labels.length>1;
  return `<div class="notice ${exact&&!shared?'ok':''}"><strong>${exact?'WMI route':'Possible Australian makes'}:</strong> ${esc(labels.join(', '))}${shared?' · shared manufacturer family; exact marque is not inferred.':''}<div class="filters">${candidates.slice(0,14).map(brand=>brand.portal?`<a class="mini-action" href="${esc(brand.portal)}">${esc(brand.brand)} portal</a>`:`<span class="badge">${esc(brand.brand)}</span>`).join('')}</div></div>`;
}
function renderStructure(value){const data=structure(value);if(value.length<10)return'';const years=data.yearCandidates.length?data.yearCandidates.join(' / '):'Not encoded by hosted table';const check=data.validLength?(data.checkDigit.match?'Matches calculation':`Calculated ${data.checkDigit.computed||'unavailable'}; supplied ${data.checkDigit.supplied||'unavailable'}`):'Complete all 17 characters';return `<div class="panel vin-structure"><h3>VIN structure</h3><div class="vin-stats"><div class="fact"><small>Region</small><strong>${esc(data.region||'Unknown')}</strong></div><div class="fact"><small>WMI</small><strong>${esc(data.wmi)}</strong></div><div class="fact"><small>Year-code candidates</small><strong>${esc(years)}</strong></div><div class="fact"><small>Plant character</small><strong>${esc(data.plant||'Pending')}</strong></div><div class="fact"><small>Serial</small><strong>${esc(data.serial||'Pending')}</strong></div><div class="fact"><small>Check digit</small><strong>${esc(check)}</strong></div></div><p class="muted">The model-year character repeats on a 30-year cycle. Check-digit calculation is mandatory for many North American VINs but is informational for many Australian-market imports.</p></div>`}
function render(value){
  const box=document.getElementById('vinLiveResult');if(!box)return;if(!value){box.innerHTML='';return}
  const matched=rules.filter(rule=>value.startsWith(rule.prefix)).sort((a,b)=>b.prefix.length-a.prefix.length);
  const best=matched[0]||null;
  const next=rules.filter(rule=>rule.prefix.startsWith(value)&&rule.prefix.length>value.length).sort((a,b)=>a.prefix.length-b.prefix.length||String(a.label).localeCompare(String(b.label)));
  const candidates=brandMatches(value);
  let html=`<section class="vin-preview">${renderProgress(value,matched,next)}${renderRuler(value)}${renderTrail(value,matched)}${renderWmi(value,candidates)}${renderBest(best,value)}${renderNextChars(value,next)}${renderStats(matched,next,candidates)}${renderStructure(value)}`;
  if(next.length){const seen=new Set(),immediate=[];for(const rule of next){const key=rule.prefix.slice(0,Math.min(rule.prefix.length,value.length+3));if(!seen.has(key)){seen.add(key);immediate.push(rule)}if(immediate.length>=10)break}html+=`<div class="panel vin-continuations"><h3>Nearest hosted continuations</h3><p class="muted">Evidence paths are grouped to avoid duplicate serial-number examples.</p><div class="results">${immediate.map(rule=>`<article class="result-card"><span class="badge">${esc(rule.prefix)}</span><h3>${esc(rule.label)}</h3><p class="muted">${esc(rule.description||'')}</p></article>`).join('')}</div></div>`}
  box.innerHTML=html+'</section>';
}
async function init(){
  try{
    const [prefixResponse,wmiResponse,vehicleResponse]=await Promise.all([
      fetch('./data/vin-prefixes.json',{cache:'no-store'}),fetch('./data/wmi.json',{cache:'no-store'}),fetch('./data/vehicles.json',{cache:'no-store'})
    ]);
    const prefixData=await prefixResponse.json(),wmiData=await wmiResponse.json(),vehicleData=await vehicleResponse.json();
    brands=wmiData.brands||[];vehicles=vehicleData.vehicles||[];rules=dedupeRules([...(prefixData.rules||[]),...vehicleRules(vehicles)]);
  }catch(error){console.warn('Progressive VIN data unavailable',error)}
  const input=document.getElementById('vinInput');if(!input)return;
  input.addEventListener('input',()=>{const value=clean(input.value);input.value=value;render(value);document.dispatchEvent(new CustomEvent('pleiades:vinchange',{detail:{vin:value}}))});
  render(clean(input.value));
}
window.PleiadesVin={clean,structure,yearCandidates,checkDigitFor,regionFor,brandMatches:(value,brandRows)=>brandMatches(value,brandRows||brands)};
document.addEventListener('DOMContentLoaded',init);
})();

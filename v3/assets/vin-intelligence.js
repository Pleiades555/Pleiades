(()=>{
'use strict';

const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const normal=value=>String(value??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
const state={references:[]};
const examples=[
  '2023 Defender D300',
  'L663',
  '2007 Subaru RB320',
  'Subaru P1',
  'S204',
  '22B',
  'GDB',
  'L551 P250'
];

async function json(url,fallback){
  try{
    const response=await fetch(url,{cache:'no-store'});
    if(!response.ok)throw Error(response.status);
    return await response.json();
  }catch(error){
    console.warn('VIN intelligence data unavailable',url,error);
    return fallback;
  }
}

function vehicleReferences(vehicleData){
  const rows=vehicleData?.vehicles||[];
  return rows.flatMap(vehicle=>{
    const vins=[...(vehicle.exampleVins||[]),...(vehicle.vinPrefixes||[]).filter(value=>String(value).length===17)];
    return [...new Set(vins)].map(vin=>({
      id:`vinref:${vin.toLowerCase()}`,
      vin,
      referenceType:'factory-vin',
      market:vehicle.marketStatus||vehicleData.market||'Australia',
      brand:vehicle.brand,
      model:vehicle.model,
      modelCode:vehicle.chassis||null,
      body:vehicle.body||null,
      modelYear:vehicle.year||null,
      advertisedYear:vehicle.advertisedYear||vehicle.year||null,
      powertrain:vehicle.engine?.marketingName||vehicle.engine?.code||null,
      variant:vehicle.variant||'unresolved',
      productionNumber:vehicle.productionNumber||null,
      editionDetail:vehicle.editionDetail||null,
      engineFamily:vehicle.engine?.family||vehicle.engine?.description||vehicle.engine?.code||null,
      transmission:typeof vehicle.transmission==='string'
        ?vehicle.transmission
        :[vehicle.transmission?.family,vehicle.transmission?.exactCode,vehicle.transmission?.type].filter(Boolean).join(' · '),
      drivetrain:vehicle.drive||null,
      aliases:[
        `${vehicle.year||''} ${vehicle.model||''} ${vehicle.variant||''}`.trim(),
        `${vehicle.chassis||''} ${vehicle.variant||''}`.trim(),
        vehicle.productionNumber||''
      ].filter(Boolean),
      confidence:vehicle.confidence||'confirmed Pleiades record',
      review:vehicle.sourceWarning||null,
      epcUsage:'Reference VIN for EPC lookup only; confirm build date, body, powertrain, fitted options and final part applicability against the target vehicle.',
      source:{type:'Pleiades confirmed vehicle record'}
    }));
  });
}

function identifierMarket(row){
  if(row.type==='australian-surrogate-vin')return 'Australia';
  if(row.type==='new-zealand-surrogate-vin')return 'New Zealand';
  if(row.type==='japanese-chassis-number')return 'Japan / import research';
  return 'Identifier research';
}

function identifierReferences(identifierData){
  return (identifierData?.identifiers||[]).map(row=>({
    id:`idref:${String(row.identifier).toLowerCase()}`,
    vin:row.identifier,
    referenceType:row.type,
    market:identifierMarket(row),
    brand:row.brand,
    model:row.model||null,
    modelCode:row.modelCode||null,
    body:row.body||null,
    modelYear:row.year||null,
    advertisedYear:row.year||null,
    powertrain:null,
    variant:row.variant||'unresolved',
    productionNumber:row.productionNumber||null,
    editionDetail:row.editionDetail||null,
    engineFamily:null,
    transmission:null,
    drivetrain:null,
    aliases:[row.linkedIdentifier,...(row.aliases||[]),row.variant,row.productionNumber,row.editionDetail].filter(Boolean),
    confidence:row.confidence||'identifier record',
    review:row.notes||null,
    epcUsage:'Reference identifier for EPC or chassis lookup only. Confirm the original chassis, build date, powertrain and fitted options before ordering parts.',
    source:{type:'Pleiades confirmed identifier register'}
  }));
}

function mergeReferences(publicReferences,vehicleData,identifierData){
  const merged=new Map();
  vehicleReferences(vehicleData).forEach(reference=>merged.set(reference.vin,reference));
  identifierReferences(identifierData).forEach(reference=>merged.set(reference.vin,reference));
  (Array.isArray(publicReferences)?publicReferences:[]).forEach(reference=>merged.set(reference.vin,{referenceType:'public-factory-vin',...reference}));
  return [...merged.values()].filter(reference=>/^[A-HJ-NPR-Z0-9]{8,17}$/.test(reference.vin||''));
}

function referenceText(reference){
  return normal([
    reference.vin,reference.referenceType,reference.market,reference.brand,reference.model,reference.modelCode,reference.chassis,
    reference.body,reference.modelYear,reference.advertisedYear,reference.powertrain,reference.variant,
    reference.productionNumber,reference.editionDetail,reference.engineFamily,reference.transmission,
    reference.drivetrain,reference.stockNumber,...(reference.aliases||[])
  ].filter(Boolean).join(' '));
}

function score(reference,query){
  const cleaned=normal(query);
  if(!cleaned)return 1;
  const compactQuery=cleaned.replaceAll(' ','');
  const compactValue=String(reference.vin||'').toLowerCase();
  if(compactQuery===compactValue)return 100000;
  const terms=cleaned.split(/\s+/).filter(Boolean);
  const tokens=referenceText(reference).split(/\s+/).filter(Boolean);
  let total=0;
  for(const term of terms){
    const exact=tokens.some(token=>token===term);
    const prefix=tokens.some(token=>token.startsWith(term));
    const contains=tokens.some(token=>token.includes(term));
    const valuePrefix=compactValue.startsWith(term);
    if(!exact&&!prefix&&!contains&&!valuePrefix)return -1;
    total+=valuePrefix?140:exact?100:prefix?60:20;
    if(term===String(reference.modelYear||''))total+=80;
    if(term===normal(reference.modelCode))total+=80;
    if(term===normal(reference.powertrain))total+=80;
    if(term===normal(reference.variant))total+=80;
  }
  return total;
}

function findReferences(query){
  return state.references
    .map(reference=>({reference,score:score(reference,query)}))
    .filter(item=>item.score>=0)
    .sort((a,b)=>
      b.score-a.score||
      Number(b.reference.modelYear||0)-Number(a.reference.modelYear||0)||
      String(a.reference.model||'').localeCompare(String(b.reference.model||''))||
      String(a.reference.vin).localeCompare(String(b.reference.vin))
    )
    .map(item=>item.reference);
}

function title(reference){
  return [
    reference.modelYear,
    reference.brand,
    reference.model,
    reference.body,
    reference.powertrain,
    reference.variant&&reference.variant!=='unresolved'?reference.variant:null,
    reference.productionNumber?`No. ${reference.productionNumber}`:null
  ].filter(Boolean).join(' ')||`${reference.brand||''} ${reference.vin}`.trim();
}

function fact(label,value){return `<div class="fact"><small>${esc(label)}</small><strong>${esc(value||'Not yet verified')}</strong></div>`}

function typeLabel(reference){
  return String(reference.referenceType||'reference').replaceAll('-',' ');
}

function referenceCard(reference){
  const advertised=reference.advertisedYear&&Number(reference.advertisedYear)!==Number(reference.modelYear)?fact('Advertised year',reference.advertisedYear):'';
  const source=reference.source?.url?`<a class="secondary-link" href="${esc(reference.source.url)}" target="_blank" rel="noopener">Open Australian source</a>`:'';
  const review=reference.review?`<p class="review-note">${esc(reference.review)}</p>`:'';
  const decoderUrl=`./index.html?vin=${encodeURIComponent(reference.vin)}#vin`;
  const valueLabel=reference.referenceType==='japanese-chassis-number'?'Chassis number':'VIN / identifier';
  return `<article class="vin-card">
    <div class="tags">
      <span class="tag">${esc(typeLabel(reference))}</span>
      <span class="tag">${esc(reference.market||'market pending')}</span>
      <span class="tag">${esc(reference.modelCode||'model code pending')}</span>
      <span class="tag confidence">${esc(reference.confidence||'confirmed')}</span>
    </div>
    <h3>${esc(title(reference))}</h3>
    <div class="vin-row"><div><small>${esc(valueLabel)}</small><code>${esc(reference.vin)}</code></div><button type="button" data-copy-vin="${esc(reference.vin)}">Copy</button></div>
    <div class="facts">
      ${fact('Model code',reference.modelCode)}
      ${fact('Model year',reference.modelYear)}
      ${advertised}
      ${fact('Body',reference.body)}
      ${fact('Variant / edition',reference.variant)}
      ${fact('Production number',reference.productionNumber)}
      ${fact('Edition detail',reference.editionDetail)}
      ${fact('Engine family',reference.engineFamily)}
      ${fact('Transmission',reference.transmission)}
      ${fact('Drivetrain',reference.drivetrain)}
      ${fact('Dealer stock',reference.stockNumber)}
    </div>
    <p class="epc-note">${esc(reference.epcUsage||'Reference only. Confirm applicability before ordering parts.')}</p>
    ${review}
    <div class="card-actions"><a class="primary-link" href="${decoderUrl}">Use in VIN decoder</a>${source}</div>
  </article>`;
}

function renderExamples(){
  $('exampleQueries').innerHTML=examples.map(query=>`<button type="button" data-example-query="${esc(query)}">${esc(query)}</button>`).join('');
}

function renderModelCodes(){
  const counts=new Map();
  state.references.forEach(reference=>{
    const code=reference.modelCode||'Code pending';
    counts.set(code,(counts.get(code)||0)+1);
  });
  $('modelCodeBrowser').innerHTML=[...counts.entries()]
    .sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))
    .map(([code,count])=>`<button type="button" data-model-code="${esc(code)}"><strong>${esc(code)}</strong> · ${count} reference${count===1?'':'s'}</button>`)
    .join('');
}

function renderSummary(){
  $('referenceCount').textContent=state.references.length;
  $('modelCount').textContent=new Set(state.references.map(reference=>`${reference.brand}|${reference.model}|${reference.body||''}`)).size;
  $('codeCount').textContent=new Set(state.references.map(reference=>reference.modelCode).filter(Boolean)).size;
}

function renderResults(){
  const query=$('vinReferenceSearch').value;
  const results=findReferences(query);
  $('searchStatus').textContent=query.trim()
    ?`${results.length} matching VIN or identifier reference${results.length===1?'':'s'} for “${query.trim()}”.`
    :`${results.length} saved VIN and identifier reference${results.length===1?'':'s'} available. Start typing to narrow the list.`;
  $('vinReferenceResults').innerHTML=results.length
    ?results.map(referenceCard).join('')
    :`<div class="empty"><strong>No saved VIN or identifier matched.</strong><p>Try a broader year, model, edition, production number or model code. Unknown remains unknown rather than being guessed.</p></div>`;
}

async function copyVin(vin,button){
  try{await navigator.clipboard.writeText(vin)}catch{
    const input=document.createElement('textarea');
    input.value=vin;
    input.setAttribute('readonly','');
    input.style.position='fixed';
    input.style.opacity='0';
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    input.remove();
  }
  const previous=button.textContent;
  button.textContent='Copied';
  button.classList.add('copy-feedback');
  setTimeout(()=>{button.textContent=previous;button.classList.remove('copy-feedback')},1300);
}

function wire(){
  $('vinReferenceSearch').addEventListener('input',renderResults);
  $('clearSearch').onclick=()=>{$('vinReferenceSearch').value='';renderResults();$('vinReferenceSearch').focus()};
  document.addEventListener('click',event=>{
    const example=event.target.closest('[data-example-query]');
    if(example){
      $('vinReferenceSearch').value=example.dataset.exampleQuery;
      renderResults();
      $('vinReferenceResults').scrollIntoView({behavior:'smooth',block:'start'});
      return;
    }
    const code=event.target.closest('[data-model-code]');
    if(code){
      $('vinReferenceSearch').value=code.dataset.modelCode;
      renderResults();
      $('vinReferenceResults').scrollIntoView({behavior:'smooth',block:'start'});
      return;
    }
    const copy=event.target.closest('[data-copy-vin]');
    if(copy)copyVin(copy.dataset.copyVin,copy);
  });
}

async function init(){
  const [publicReferences,vehicleData,identifierData]=await Promise.all([
    json('../v4/public/data/vinReferences.json',[]),
    json('./data/vehicles.json',{market:'Australia',vehicles:[]}),
    json('./data/identifiers.json',{market:'Australia',identifiers:[]})
  ]);
  state.references=mergeReferences(publicReferences,vehicleData,identifierData);
  renderExamples();
  renderModelCodes();
  renderSummary();
  renderResults();
  wire();
  const query=new URLSearchParams(location.search).get('q');
  if(query){$('vinReferenceSearch').value=query;renderResults()}
}

document.addEventListener('DOMContentLoaded',init);
})();

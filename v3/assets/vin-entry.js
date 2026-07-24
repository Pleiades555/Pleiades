(()=>{
'use strict';
const requested=new URLSearchParams(location.search).get('vin');
if(!requested)return;
const vin=String(requested).toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,17);
if(!vin)return;
function openRequestedVin(attempt=0){
  const input=document.getElementById('vinInput');
  const go=document.getElementById('vinGo');
  const route=document.querySelector('[data-view="vin"]');
  if(!input||!go||typeof go.onclick!=='function'){
    if(attempt<40)setTimeout(()=>openRequestedVin(attempt+1),100);
    return;
  }
  route?.click();
  input.value=vin;
  input.dispatchEvent(new Event('input',{bubbles:true}));
  go.click();
  history.replaceState(null,'',`${location.pathname}#vin`);
}
document.addEventListener('DOMContentLoaded',()=>openRequestedVin());
})();

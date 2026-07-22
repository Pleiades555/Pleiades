#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const root=path.resolve(__dirname,'..');
const wmi=JSON.parse(fs.readFileSync(path.join(root,'data','wmi.json'),'utf8'));
const vehicles=JSON.parse(fs.readFileSync(path.join(root,'data','vehicles.json'),'utf8')).vehicles;
const source=fs.readFileSync(path.join(root,'assets','live-vin.js'),'utf8');
const sandbox={
  window:{},
  document:{addEventListener() {},getElementById(){return null}},
  console,
  CustomEvent:function CustomEvent(){}
};
vm.createContext(sandbox);
vm.runInContext(source,sandbox,{filename:'live-vin.js'});
const vin=sandbox.window.PleiadesVin;

assert.ok(vin,'VIN helper API must be exported');
assert.equal(vin.clean('jhm fl1860n x200901'),'JHMFL1860NX200901');
assert.equal(vin.clean('IOQ'),'','I, O and Q are not valid VIN characters');
assert.equal(vin.checkDigitFor('1M8GDM9AXKP042788'),'X');

const honda=vin.structure('JHMFL1860NX200901');
assert.equal(honda.validLength,true);
assert.equal(honda.wmi,'JHM');
assert.equal(honda.region,'Asia');
assert.deepEqual(Array.from(honda.yearCandidates),[1992,2022]);

const subaru=vin.brandMatches('JF2SH9KD39G009340',wmi.brands).map(row=>row.brand);
assert.deepEqual(Array.from(subaru),['Subaru']);
const greatWall=vin.brandMatches('LGWAAAAAA00000000',wmi.brands).map(row=>row.brand).sort();
assert.deepEqual(Array.from(greatWall),['GWM','Great Wall','Haval']);
const cheryFamily=vin.brandMatches('LVVAAAAAA00000000',wmi.brands).map(row=>row.brand).sort();
assert.deepEqual(Array.from(cheryFamily),['Chery','Jaecoo','Omoda']);

assert.ok(wmi.brands.length>=70,'Australian make directory must retain broad coverage');
assert.ok(wmi.brands.some(row=>row.brand==='Holden'));
assert.ok(wmi.brands.some(row=>row.brand==='KGM'&&row.aliases.includes('SsangYong')));
assert.ok(wmi.brands.some(row=>row.brand==='XPeng'),'Makes without hosted WMI evidence must still be searchable');
assert.ok(vehicles.some(row=>row.vinPrefixes.includes('JHMFL1860NX')),'Confirmed Honda VIN profile must remain');
assert.ok(vehicles.some(row=>row.vinPrefixes.includes('JF2SH9KD39')),'Confirmed Subaru VIN profile must remain');
assert.ok(vehicles.some(row=>row.vinPrefixes.includes('SALFA23A87H')),'Confirmed Land Rover VIN profile must remain');

console.log(`VIN workbench regression passed: ${wmi.brands.length} Australian makes, ${vehicles.length} confirmed profiles.`);

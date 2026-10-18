import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {controlledInput} from './input.mjs';
import {loadInput} from '../player-impact-v30/input.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {sourceFlow} from '../player-impact-v37/model.mjs';
const root='reports/player-impact-v38',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
assert.ok(!fs.existsSync(root+'/input-verification.json'));
const reference=loadInput('2025-26'),canonical=new Map(reference.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])),a=await controlledInput('v30'),b=await controlledInput('v37');
for(const key of ['profiles','options','roleMap'])assert.deepEqual(b[key],a[key]);let checked=0;
for(const [aa,bb]of [[a.players,b.players],...a.opponents.map((t,i)=>[t.roster,b.opponents[i].roster])]){
 assert.equal(aa.length,bb.length);
 for(let i=0;i<aa.length;i++){
  const p=aa[i],q=structuredClone(bb[i]);assert.equal(q.playerId,p.playerId);
  for(const key of ['opportunityMeasurement','creationSuccessMeasurement'])assert.deepEqual(p[key],canonical.get(p.playerId)[key]);
  q.shootingMeasurement=p.shootingMeasurement;assert.deepEqual(q,p);checked++;
 }
}
const versions=[],rows=[],hashes={};
for(const v of ['v24','v29','v30','v34','v35','v36','v37']){
 const path=`reports/player-impact-${v}/ovr-input.mjs`,{ovrInput}=await import(`../player-impact-${v}/ovr-input.mjs`),x=await ovrInput('2025-26');let changed=0,lower=0,higher=0,maxRelative=0;
 for(const p of x.players){
  const c=canonical.get(p.playerId),before=p.opportunityMeasurement.passOpportunityRate,after=c.opportunityMeasurement.passOpportunityRate,delta=before-after;
  if(Math.abs(delta)>1e-12){changed++;if(delta<0)lower++;else higher++;}maxRelative=Math.max(maxRelative,Math.abs(delta/after));
  rows.push({version:v,playerId:p.playerId,name:p.name,archivedPassRate:before,canonicalPassRate:after,correctionRatio:after/before,otherRoleKeysIdentical:Object.keys(c.opportunityMeasurement).filter(k=>k!=='passOpportunityRate').every(k=>JSON.stringify(p.opportunityMeasurement[k])===JSON.stringify(c.opportunityMeasurement[k]))});
 }
 versions.push({version:v,players:x.players.length,changedPassRates:changed,archivedLower:lower,archivedHigher:higher,maxRelativeDifference:maxRelative});hashes[path]=sha(path);
}
const branches={};
for(const p of b.players){const slot=b.roleMap.get(p.playerId).slot,f=sourceFlow(elasticLineup(b.profiles.map((q,i)=>i===slot?p:q),'elastic-creation'));branches[f.branch]=(branches[f.branch]??0)+1;}
for(const p of ['src/source_creation_roles.js','test/source_creation_roles.js',root+'/input.mjs',root+'/audit-inputs.mjs','reports/player-impact-v6/2025-26-cards.json','reports/player-impact-v17/2025-26-creation-audit.json','reports/player-impact-v37/2025-26-contexts.json','reports/player-impact-v30/validation-protocol.json'])hashes[p]=sha(p);
fs.writeFileSync(root+'/input-assembly-audit.json',JSON.stringify({scope:'Retrospective audit of actual imported OVR card constructors against once-corrected canonical season roles. Prior numerical simulation ledgers are preserved; affected workload/ranking interpretations require rerun. No claim every historical mechanism is invalid. Shared synthetic profile styles held unchanged.',versions,rows,hashes},null,2));
fs.writeFileSync(root+'/input-verification.json',JSON.stringify({passed:true,actualCardsAndOpponentPrimaries:checked,players:582,allCanonicalRolesExactlySeasonInput:true,allOtherCardFieldsIdenticalAcrossControlledVariants:true,onlyShootingCenteringDiffers:true,profilesExactlyArchivedV30:true,mean70Branches:branches,hashes},null,2));
console.log(JSON.stringify({passed:true,checked,versions,mean70Branches:branches}));

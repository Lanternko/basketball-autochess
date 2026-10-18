import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {buildCards,aged,calibrate,attrs} from './cards.mjs';
const d='reports/defense-tenth/step3-a2',p=read(d+'/protocol.json'),lock=read(d+'/curve-lock.json'),curves=read(d+'/curves.json').curves;
if(hash(d+'/curves.json')!==lock.curveHash)throw Error('Curve changed');for(const[f,h]of Object.entries(lock.files))if(hash(f)!==h)throw Error('Locked input changed '+f);
fs.mkdirSync(d+'/bundles',{recursive:true});fs.mkdirSync(d+'/personal-cards',{recursive:true});
const cached=new Map();function data(s){if(!cached.has(s)){console.log('PERSONAL DATA',s);cached.set(s,buildCards(s));}return cached.get(s);}
const copyKeys=[...attrs,'stamina','physique','pos','courtPosition','heightInches','bodyWeight','offBall','screen','handle','breakDbl','shotProfile','defenseMeasurement','offenseMeasurement'];
let exact=0;const issues=[],inventory=[];
for(const[prior,target]of p.pairs){const prev=data(prior),next=data(target),curve=curves[target],own=[...next.cards.values()].map(q=>calibrate(q,prior));fs.writeFileSync(`${d}/personal-cards/${target}.json`,JSON.stringify({diagnostic:'Target personal answer-side cards; same origin league constants',cards:own})+'\n');
 const counts={prior,target,replacedNewcomerIds:[],updatedPriorIds:[],unavailableNewcomerIds:[]};
 for(const layer of ['L2','L3','P3'])for(const seed of p.seeds){const mode=layer==='P3'?'preseason':'oracle',file=`${p.base}/bundles/${target}-${mode}-${seed}.json`,b=read(file),old=read(file);let replacements=0,ageUpdates=0;
  for(const t of b.league.teams)for(const q of t.roster){if(!q.measurementPriorOnly){const src=prev.cards.get(q.playerId);if(!src)throw Error('No prior card '+q.playerId);const equivalent=calibrate(src,prior);for(const k of copyKeys)if(JSON.stringify(equivalent[k])!==JSON.stringify(q[k]))issues.push({target,layer,seed,id:q.playerId,field:k,type:'A card rebuild mismatch'});exact++;}
   const isNew=!!q.measurementPriorOnly;let replacement=null;
   if(isNew&&layer!=='P3'){const c=next.cards.get(q.playerId);if(c){replacement=calibrate(c,prior);replacements++;counts.replacedNewcomerIds.push(q.playerId);q.measurementPriorOnly=false;q.a2CardSource='target-personal-newcomer';}else counts.unavailableNewcomerIds.push(q.playerId);}
   else if(!isNew&&layer!=='L2'){replacement=calibrate(aged(prev,q,curve),prior);ageUpdates++;counts.updatedPriorIds.push(q.playerId);q.a2CardSource='prior-plus-age';}
   else q.a2CardSource=isNew?'A-role-prior':'A-prior-card';
   if(replacement){for(const k of copyKeys)q[k]=structuredClone(replacement[k]);q.abilitySource=replacement.abilitySource;q.a2Label=layer==='P3'?'前季輸入半盲預測':'答案側診斷';}
  }
  if(JSON.stringify(b.exposure)!==JSON.stringify(old.exposure)||JSON.stringify(b.league.schedule)!==JSON.stringify(old.league.schedule)||JSON.stringify(b.options)!==JSON.stringify(old.options))throw Error('Exposure/schedule/options changed');
  for(let i=0;i<b.league.teams.length;i++)for(let j=0;j<b.league.teams[i].roster.length;j++){const x=b.league.teams[i].roster[j],y=old.league.teams[i].roster[j];for(const k of ['seasonMinutesPerGame','preseasonAvailability','preseasonAvailableAfter','twoWay','observed'])if(JSON.stringify(x[k])!==JSON.stringify(y[k]))throw Error('Minute-related input changed '+k);}
  b.provenance={...b.provenance,layer,protocolHash:hash(d+'/protocol.json'),curveLockHash:hash(d+'/curve-lock.json'),baseBundleHash:hash(file),replacements,ageUpdates};fs.writeFileSync(`${d}/bundles/${target}-${layer}-${seed}.json`,JSON.stringify(b)+'\n');if(seed===p.seeds[0])console.log('BUNDLE',target,layer,{replacements,ageUpdates});
 }
 for(const k of ['replacedNewcomerIds','updatedPriorIds','unavailableNewcomerIds'])counts[k]=[...new Set(counts[k])];inventory.push(counts);
}
for(const[f,h]of Object.entries(p.fingerprints))if(hash(f)!==h)throw Error('Source changed '+f);for(const[f,h]of Object.entries(p.preservedAHashes))if(hash(p.base+'/'+f)!==h)throw Error('A output changed '+f);
const out={finishedAt:new Date().toISOString(),protocolHash:hash(d+'/protocol.json'),curveLockHash:hash(d+'/curve-lock.json'),exactRebuiltPriorInstances:exact,issues,inventory};fs.writeFileSync(d+'/preparation-audit.json',JSON.stringify(out,null,2)+'\n');console.log('PREPARED',exact,'issues',issues.length);if(issues.length)throw Error('A card equivalence failed');

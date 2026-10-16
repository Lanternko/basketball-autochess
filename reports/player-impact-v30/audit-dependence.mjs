import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v28/input.mjs';
import {attachCreationDependence,creationDependence} from '../../src/source_creation_dependence.js';
const root='reports/player-impact-v30',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=[];
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),players=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])).values()];
 const rows=players.map(p=>{
  const before=structuredClone(p),oldDependence=creationDependence(p),q=structuredClone(p);attachCreationDependence([q]);
  if(JSON.stringify(before)!==JSON.stringify(p))throw Error('Source player mutation');
  return {playerId:p.playerId,name:p.name,drive:p.drive,pass:p.pass,oldDependence,sourceDependence:creationDependence(q),
   sourceTerminal:p.opportunityMeasurement.terminalOpportunityRate,sourceReceived:p.opportunityMeasurement.receiveOpportunityRate,
   sourceSelf:p.opportunityMeasurement.selfOpportunityRate,sourceAnchor:q.creationDependenceMeasurement.sourceSelfCreation};
 });
 const old=JSON.parse(fs.readFileSync(`reports/player-impact-v28/${season}-contexts.json`)),current=JSON.parse(fs.readFileSync(`${root}/${season}-contexts.json`));
 for(const f of ['states','stints','strictMinutes','contextReference'])if(JSON.stringify(old[f])!==JSON.stringify(current[f]))throw Error('Source context scope changed '+f);
 for(const[id,p]of Object.entries(old.cards))for(const f of ['strictSeconds','sourceZoneAttempts','meanSourceShootingMultiplier'])if(JSON.stringify(p[f])!==JSON.stringify(current.cards[id][f]))throw Error('Source context exposure changed');
 seasons.push({season,rows,states:current.states,stints:current.stints,
  contextChange:Object.fromEntries(['long','mid','short'].map(z=>{const values=Object.keys(old.cards).map(id=>current.cards[id].contexts['rotation-space'][z]-old.cards[id].contexts['rotation-space'][z]);return[z,{min:Math.min(...values),max:Math.max(...values)}];}))});
}
const files=['src/source_creation_dependence.js',`${root}/audit-dependence.mjs`,`${root}/model.mjs`,`${root}/prepare-contexts.mjs`,...seasons.flatMap(s=>[`${root}/${s.season}-contexts.json`,`reports/player-impact-v28/${s.season}-contexts.json`])];
fs.writeFileSync(`${root}/dependence-audit.json`,JSON.stringify({design:'Source role ratio vs previous FTR-derived drive/pass dependence; no role or attribute edits. Context state, minutes, attempts, energy and reference pools exactly retained. Only source predicted-context probability changes.',seasons,hashes:Object.fromEntries(files.map(f=>[f,hash(f)]))},null,2));
console.log(JSON.stringify({cards:seasons.reduce((s,x)=>s+x.rows.length,0),states:seasons.reduce((s,x)=>s+x.states,0),unchangedExposure:true}));

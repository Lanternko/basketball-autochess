import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
const parent='reports/defense-tenth/step3-a',root=process.argv[2]??parent+'/preseason-schedule';
const p=read(root+'/protocol.json'),manifest=read(root+'/run-manifest.json'),issues=[];
let games=0,cardPairs=0;
for(const [file,expected] of Object.entries(p.fingerprints))if(hash(file)!==expected)issues.push('Frozen/source changed: '+file);
for(const entry of manifest.files){
 if(hash(entry.file)!==entry.sha256)issues.push('Run hash: '+entry.file);
 const bf=`${root}/bundles/${entry.target}-${entry.mode}-${entry.seed}.json`;
 if(hash(bf)!==entry.bundleHash)issues.push('Bundle hash: '+bf);
 const b=read(bf),r=read(entry.file);
 if(r.matches.length!==1230||r.teams.length!==30||r.teams.some(t=>t.games!==82)||r.teams.reduce((s,t)=>s+t.wins,0)!==1230)issues.push('Season size: '+entry.file);
 const by=new Map(r.teams.map(t=>[t.id,{games:0,wins:0,pts:0,allowed:0}]));
 for(const g of r.matches){
  if(!Number.isFinite(g.scoreA+g.scoreB)||g.scoreA===g.scoreB)issues.push('Invalid score: '+entry.file+'/'+g.id);
  for(const [id,pts,allowed] of [[g.homeId,g.scoreA,g.scoreB],[g.awayId,g.scoreB,g.scoreA]]){const t=by.get(id);t.games++;t.wins+=Number(pts>allowed);t.pts+=pts;t.allowed+=allowed;}
 }
 for(const t of r.teams){const z=by.get(t.id),s=t.stats,o=t.opponent;
  if(z.games!==t.games||z.wins!==t.wins||z.pts!==s.pts||z.allowed!==o.pts)issues.push('Score aggregation: '+entry.file+'/'+t.id);
  if(s.pts!==2*s.fgm+s.fg3m+s.ftm||s.fga!==s.rima+s.mida+s.fg3a||s.tov!==s.liveTov+s.deadTov||s.liveTov!==o.stl)issues.push('Event accounting: '+entry.file+'/'+t.id);
  if(t.simulatedPlayerMinutes.some(q=>!Number.isFinite(q.minutes)))issues.push('Player minutes: '+entry.file+'/'+t.id);
 }
 if(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].some(k=>b.options[k]!==false)||b.options.defenseSignals||b.options.sixthSignals||b.options.seventhSignals)issues.push('Signal flags/maps: '+bf);
 if(root!==parent){const old=read(`${parent}/bundles/${entry.target}-${entry.mode}-${entry.seed}.json`);
  if(JSON.stringify(b.options)!==JSON.stringify(old.options)||JSON.stringify(b.league.teams)!==JSON.stringify(old.league.teams))issues.push('Main/parent abilities changed: '+bf);
 }
 games+=r.matches.length;
}
for(const [,season] of p.pairs){
 const a=read(`${root}/bundles/${season}-preseason-${p.seeds[0]}.json`),b=read(`${root}/bundles/${season}-oracle-${p.seeds[0]}.json`);
 for(const t of a.league.teams){const ot=b.league.teams.find(z=>z.id===t.id);
  for(const q of t.roster){const z=ot.roster.find(v=>v.playerId===q.playerId);if(!z)continue;cardPairs++;
   for(const k of ['pos','heightInches','bodyWeight','long','mid','short','ft','drive','tovSkill','pass','rebound','stamina','physique','onBall','help','offBall','screen','handle','breakDbl','shotProfile','defenseMeasurement','offenseMeasurement'])if(JSON.stringify(q[k])!==JSON.stringify(z[k]))issues.push('Exposure arm card differs: '+season+'/'+q.playerId+'/'+k);
  }
 }
}
const adapterNames=['prepare.mjs','prepare-opening.mjs','run.mjs','analyze.mjs','report.mjs','rosters.py','schedules.py','completion-audit.mjs'];
const result={checkedAt:new Date().toISOString(),protocolHash:hash(root+'/protocol.json'),runCount:manifest.files.length,games,allTeams82:true,commonCardPairs:cardPairs,checks:['Frozen/source fingerprints','120 run and bundle hashes','Same main/parent cards and engine options','Score aggregation and event-count identities','Five segment signals/maps absent','Common cards between exposure arms'],adapterHashes:Object.fromEntries(adapterNames.map(n=>[n,hash(parent+'/'+n)])),priorInputAuditHash:hash(root+'/input-audit.json'),issues};
fs.writeFileSync(root+'/completion-audit.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));if(issues.length)process.exitCode=1;

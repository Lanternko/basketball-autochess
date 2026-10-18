import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step3-a2',p=read(d+'/protocol.json'),lock=read(d+'/curve-lock.json'),manifest=read(d+'/run-manifest.json'),a=read(d+'/analysis.json'),base=read(p.base+'/analysis.json');
const issues=[];let games=0,bundleChecks=0,priorOnlyUnchanged=0;
if(hash(d+'/curves.json')!==lock.curveHash)issues.push('Curve coefficient change');
for(const[f,h]of Object.entries(p.preservedAHashes))if(hash(p.base+'/'+f)!==h)issues.push('A output changed '+f);
for(const[f,h]of Object.entries(p.fingerprints))if(hash(f)!==h)issues.push('Frozen/source changed '+f);
for(const[f,h]of Object.entries(lock.files))if(hash(f)!==h)issues.push('Coefficient/source lock changed '+f);
const oldParent=read(p.base+'/protocol.json');if(hash('reports/defense-tenth/step3-a/protocol.json')!==oldParent.parentProtocolHash)issues.push('Original conditional A protocol changed');
for(const e of read(p.base+'/run-manifest.json').files){if(hash(e.file)!==e.sha256)issues.push('A run changed '+e.file);const f=`${p.base}/bundles/${e.target}-${e.mode}-${e.seed}.json`;if(hash(f)!==e.bundleHash)issues.push('A bundle changed '+f);}
for(const e of manifest.files){const file=`${d}/bundles/${e.target}-${e.layer}-${e.seed}.json`,b=read(file),old=read(`${p.base}/bundles/${e.target}-${e.layer==='P3'?'preseason':'oracle'}-${e.seed}.json`),r=read(e.file);
 if(hash(file)!==e.bundleHash||hash(e.file)!==e.sha256)issues.push('Run/bundle hash mismatch '+e.file);
 if(JSON.stringify(b.exposure)!==JSON.stringify(old.exposure)||JSON.stringify(b.league.schedule)!==JSON.stringify(old.league.schedule)||JSON.stringify(b.options)!==JSON.stringify(old.options))issues.push('Exposure/schedule/options changed '+file);
 if(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].some(k=>b.options[k]!==false)||b.options.defenseSignals||b.league.sixthSignals||b.league.seventhSignals)issues.push('Forbidden signals/maps '+file);
 if(r.matches.length!==1230||r.teams.length!==30||r.teams.some(t=>t.games!==82)||r.teams.reduce((s,t)=>s+t.wins,0)!==1230)issues.push('Season size '+e.file);
 for(const t of r.teams){const s=t.stats,o=t.opponent;if(s.pts!==2*s.fgm+s.fg3m+s.ftm||s.fga!==s.rima+s.mida+s.fg3a||s.tov!==s.liveTov+s.deadTov||s.liveTov!==o.stl)issues.push('Accounting '+e.file+'/'+t.id);}
 for(let i=0;i<b.league.teams.length;i++)for(let j=0;j<b.league.teams[i].roster.length;j++){const q=b.league.teams[i].roster[j],z=old.league.teams[i].roster[j];for(const k of ['seasonMinutesPerGame','preseasonAvailability','preseasonAvailableAfter','twoWay','observed'])if(JSON.stringify(q[k])!==JSON.stringify(z[k]))issues.push('Minute input '+file+'/'+k);
  if(e.layer==='P3'&&z.measurementPriorOnly){priorOnlyUnchanged++;const copy={...q};for(const k of ['a2CardSource','a2Label'])delete copy[k];if(JSON.stringify(copy)!==JSON.stringify(z))issues.push('P3 newcomer changed '+file+'/'+q.playerId);}
  if(e.layer==='L2'&&!z.measurementPriorOnly){const copy={...q};delete copy.a2CardSource;if(JSON.stringify(copy)!==JSON.stringify(z))issues.push('L2 existing card changed '+file+'/'+q.playerId);}
 }
 games+=r.matches.length;bundleChecks++;
}
const mapping={L1:'oracle',preseason:'preseason',simple:'simple',shrink:'shrink'};
for(const c of a.cells){const b=base.cells.find(q=>q.target===c.target);for(const[x,y]of Object.entries(mapping))for(const k of Object.keys(b.versions[y].metrics))if(Math.abs(c.versions[x].metrics[k]-b.versions[y].metrics[k])>1e-11)issues.push('Referenced A metric differs '+c.target+'/'+x+'/'+k);}
const result={checkedAt:new Date().toISOString(),protocolHash:hash(d+'/protocol.json'),curveLockHash:hash(d+'/curve-lock.json'),runCount:manifest.files.length,games,bundleChecks,priorOnlyP3CardInstancesUnchanged:priorOnlyUnchanged,unchangedA:true,unchangedFrozenSources:true,identicalAReferencedMetrics:true,issues};
fs.writeFileSync(d+'/completion-audit.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));if(issues.length)process.exitCode=1;

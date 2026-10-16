import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step4-t0',issues=[],a=read(d+'/completion-audit.json');
for(const f of ['validation-supplement','validation-supplement-v2','validation-supplement-v3','zero-minute-supplement'])if(hash(d+'/'+f+'.json')!==fs.readFileSync(d+'/'+f+'.sha256','utf8').trim())issues.push('supplement changed '+f);
for(const f of ['validation-supplement-v3.json','zero-minute-code-registration.json']){const j=read(d+'/'+f),c=j.code??j;if(hash(c.file)!==c.sha256)issues.push('adapter changed '+c.file);}
const fit=read(d+'/fit-audit.json');for(const f of fit)if(hash(f.source)!==f.sha256||!f.finite||f.strictGames!==f.fittedGames)issues.push('factor source '+f.season);
for(const season of ['2022-23','2023-24','2024-25']){
 const b=read(d+'/'+season+'/bundle.json');if(b.options.seasonMinuteTargets!==true)issues.push('raw bundle minutes unexpected; worker must override false');
 if(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].some(k=>!b.options[k]))issues.push('v3 groups '+season);
 if(b.league.teams.flatMap(t=>t.roster).some(p=>p.offenseMeasurement.minutes<=0||p.defenseMeasurement.minutes<=0))issues.push('zero denominator '+season);
 const c=read(d+'/'+season+'/calibration-v3.json');if(c.history.length>5||c.seeds.join(',')!=='20260101,20260102,20260103')issues.push('calibration rules '+season);
}
const supplement={finishedAt:new Date().toISOString(),parentAuditSHA:hash(d+'/completion-audit.json'),issues,analysisUnchangedSHA:hash(d+'/analysis.json'),bootstrapUnchangedSHA:hash(d+'/joint-intervals.json'),fitAuditSHA:hash(d+'/fit-audit.json')};fs.writeFileSync(d+'/completion-audit-supplement.json',JSON.stringify(supplement,null,2)+'\n');
const hashes=read(d+'/deliverable-hashes.json');for(const f of ['report.md','failures.md','fit-audit.json','completion-audit-supplement.json',...['validation-supplement','validation-supplement-v2','validation-supplement-v3','zero-minute-supplement'].map(f=>f+'.json')])hashes[f]=hash(d+'/'+f);fs.writeFileSync(d+'/deliverable-hashes.json',JSON.stringify(hashes,null,2)+'\n');console.log(JSON.stringify(supplement));if(issues.length||a.issues.length)process.exitCode=1;

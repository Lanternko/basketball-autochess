import fs from 'node:fs';
import {TEAMS} from '../src/teams.js';
import {buildPer36Report} from '../src/per36_report.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const refs=read('../data/reference-seasons.json'),league=read('../data/league-context.json');
const keys=['CLE','LAL','OKC','NYK'];
const run=(key,options)=>buildPer36Report(TEAMS[key],refs.teams[key],{leagueReboundShare:league.contexts.find(c=>c.season===TEAMS[key].season&&c.type==='Regular Season').orebShare,...options});
function errors(rows) {
 const ps=rows.flatMap(r=>r.players);
 return Object.fromEntries(['pts','reb','tov','usage'].map(k=>[k,ps.reduce((s,p)=>s+Math.abs(k==='usage'?p.error.usageProxyPercentagePoints:p.simulated[k]-p.real[k]),0)/ps.length]));
}
const score=e=>e.pts/3+e.usage/2+e.reb+e.tov;
const candidates=[];
const n=Number(process.env.CALIBRATION_N??2000);
const trainingN=300,trainingSeed=83001;
const trainingBaseline=errors(keys.map(k=>run(k,{n:trainingN,seed:trainingSeed})));
for (const contextScale of [.85,1]) for (const rollAccess of [.5,.75,1]) for (const turnoverFloor of [.015,.03,.045]) {
 const config={possessionModel:'stable',contextScale,rollAccess,turnoverFloor};
 const metrics=errors(keys.map(k=>run(k,{...config,n:trainingN,seed:trainingSeed})));
 candidates.push({config,metrics,score:score(metrics),eligible:['pts','usage','reb','tov'].every(k=>metrics[k]<=trainingBaseline[k])});
}
candidates.sort((a,b)=>Number(b.eligible)-Number(a.eligible)||a.score-b.score);
const best=candidates[0];console.log('Selected on four development teams',best);
const validation=[];
for (const seed of [20261219,20270119]) {
 const baseline=keys.map(k=>run(k,{n,seed}));
 const candidate=keys.map(k=>run(k,{...best.config,n,seed}));
 const groups={};
 for (const [group,indices] of Object.entries({all:[0,1,2,3],historical:[0,1],modern:[2,3]})) {
   const old=errors(indices.map(i=>baseline[i])),now=errors(indices.map(i=>candidate[i]));
   groups[group]={baseline:old,candidate:now,passed:['pts','usage','reb','tov'].every(k=>now[k]<=old[k])};
 }
 validation.push({seed,n,groups,baseline,candidate});
 console.log(seed,JSON.stringify(groups));
}
const passed=best.eligible&&validation.every(v=>v.groups.all.passed);
const report={schemaVersion:2,trainingN,trainingSeed,trainingBaseline,developmentTeams:keys,selectionDisclosure:'All four teams were used in iterative model development. Fresh validation seeds test Monte Carlo generalization only; no claim of held-out teams or independent NBA prediction.',candidates,best,passed,validation,decision:passed?'Eligible for explicit fixed-game calibration preset; season USG is only a proxy, not tracking validation.':'Not promoted: at least one no-regression gate failed.'};
fs.writeFileSync(new URL('../reports/possession-calibration.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
await import('./render_calibration.js');

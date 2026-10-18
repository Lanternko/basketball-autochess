import assert from 'node:assert/strict';
import fs from 'node:fs';
import {decomposition,pairedEighth,measureEighth} from '../src/defense_eighth_analysis.js';
import {read,hash} from '../scripts/defense_io.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
import {seventhInputs} from '../src/defense_seventh_jobs.js';
import {thirdLineup} from '../src/defense_third_minutes.js';
import {simulateDefenseGame} from '../src/defense_game.js';
import {simulateDefenseFifthGame} from '../src/defense_fifth_game.js';
const a=[-4,-2,0,1,3,6],b=a.map(x=>2*x+5),d=decomposition(a,b);assert(Math.abs(d.identityError)<1e-12);assert(d.rankingMSE<1e-12);assert(Math.abs(d.oracleMultiplier-.5)<1e-12);
const rows=Array.from({length:30},(_,i)=>({id:i,net:i-15,wins:20+i,observed:{net:(i-15)*.8+Math.sin(i),wins:21+i,defensiveRatingProxy:100+i},defensiveRatingProxy:101+i})),rs=Array.from({length:20},()=>rows);
const same=pairedEighth([{a:rs,b:rs}],{B:200});for(const [k,x]of Object.entries(same))if(x.estimate!==null){assert.equal(x.estimate,0,k);for(const mode of ['team','seed','joint'])assert.deepEqual(x[mode].ci95,[0,0]);}
if(process.argv.includes('--artifacts')){
 const root='reports/defense-eighth/a',r=read(root+'/analysis.json'),coverage=read(root+'/coverage/rules.json');assert.equal(r.B,5000);assert.equal(r.seeds.length,20);
 for(const[file,h]of Object.entries(r.sources))assert.equal(hash(file),h);
 for(const season of ['2024-25','2025-26'])for(const k of [25,41,55]){
  const x=r.seasons[season][k],c=read(`reports/defense-seventh/${season}/calendar-${k}/config.json`),truth=calendarTruth(c);assert(x.shrinkRule.split<c.date);assert(x.shrinkRule.multiplier>=0&&x.shrinkRule.multiplier<=1);
  for(const v of ['v3','v4','simple','shrink']){const m=x.models[v];assert(Math.abs(m.decomposition.identityError)<1e-8);assert(Math.abs(m.decomposition.standardIdentityError)<1e-8);assert(m.decomposition.oracleShrunkRMSE<=m.metrics.netRMSE+1e-8);assert.equal(m.teams.length,30);}
  const old=read(`reports/defense-seventh/${season}-calendar-assessment.json`).cutoffs[k];for(const v of ['v3','v4','simple'])for(const key of ['netRMSE','netCorrelation','netSDRatio','calibrationSlope','winMAE','winRMSE'])assert(Math.abs(x.models[v].metrics[key]-old[v].metrics[key])<1e-9,season+k+v+key);
  assert.equal(truth.teams.length,30);for(const pair of Object.values(x.pairs))for(const ci of Object.values(pair))for(const mode of ['seed','team','joint'])assert(ci[mode].ci95.every(x=>x===null||Number.isFinite(x)));
 }
 for(const seed of coverage.maskSeeds){const mask=read(`${root}/coverage/mask-${seed}.json`);assert.equal(mask.kept.length,1091);assert.equal(new Set(mask.kept).size,1091);assert.equal(mask.excluded.length,97);for(const k of [25,41,55]){const dir=`${root}/coverage/mask-${seed}/calendar-${k}`,c=read(dir+'/config.json'),m=read(dir+'/ability-model-forward.json'),f=read(dir+'/factors/engine-signals.json');assert.deepEqual([...m.trainGames].sort(),[...c.trainGames].sort());assert.deepEqual([...f.trainGames].sort(),[...c.trainGames].sort());assert(c.trainGames.every(g=>mask.kept.includes(g)));for(const model of Object.values(m.models))for(const fold of model.CV.folds)assert(fold.lastTrainingDate<fold.firstValidationDate);}}
 for(const k of [25,41,55]){const z=read(`${root}/coverage/diagnosis-${k}.json`);assert.equal(Object.keys(z.models).length,4);for(const v of ['v1','v3-signals-off']){const dir=`${root}/2024-25/calendar-${k}-${v}`,mf=read(`reports/defense-seventh/2024-25-eighth-a-calendar-${k}-${v}-seeds.json`),c=read(dir+'/config.json'),cal=read(dir+`/calibration-${v}.json`),b=read(dir+'/bundle.json');assert.equal(mf.files.length,20);assert(cal.history.length<=5);assert(cal.trainGames.every(id=>c.trainGames.includes(id)));for(const f of mf.files)assert.equal(hash(f.file),f.sha256);for(const flag of ['reboundSignal','rimSignal','liveSignal','zoneSignal','foulSignal'])assert(!b.options[flag]);}}
 const bundle=seventhInputs({bundle:root+'/2024-25/calendar-25-v1/bundle.json',cutoff:25,neutralContests:false});
 for(const index of [550,900]){const g=bundle.league.schedule[index],e=bundle.exposure.games.find(e=>e.id===g.id),pair=[g.homeId,g.awayId].map((id,j)=>thirdLineup(bundle.league.teams.find(t=>t.id===id),g[j?'awayPlayerIds':'homePlayerIds'],e.teams.find(t=>t.teamId===id),true)),a=simulateDefenseGame(...pair,{...bundle.options,seed:20261012}),b=simulateDefenseFifthGame(...pair,{...bundle.options,seed:20261012});assert.deepEqual([a.scoreA,a.scoreB],[b.scoreA,b.scoreB]);for(const side of ['A','B'])for(const key of ['pts','fga','fgm','fg3a','fg3m','fta','ftm','oreb','dreb','tov','stl','ast','pf'])assert.equal(a['stat'+side][key],b['stat'+side][key]);}
}
console.log('eighth A: decomposition identity, paired resampling, prior-only comparator, coverage and control artifacts passed');

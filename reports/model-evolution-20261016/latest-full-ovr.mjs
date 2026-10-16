// Full-league diagnostic; healthy contribution and availability remain separate.
// Uses frozen v41 machinery. This does not adopt v41 or change production OVR.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
import {ovrInput} from '../player-impact-v41/ovr-input.mjs';
const root='reports/model-evolution-20261016/latest-full-ovr';
const read=f=>JSON.parse(fs.readFileSync(f));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
const original=read('reports/player-impact-v41/probe-protocol.json');
const x=await ovrInput();
fs.mkdirSync(root,{recursive:true});
const hashes={...original.hashes,'reports/model-evolution-20261016/latest-full-ovr.mjs':sha('reports/model-evolution-20261016/latest-full-ovr.mjs')};
const verify=()=>{for(const[f,h]of Object.entries(hashes))if(sha(f)!==h)throw Error('Frozen input drift: '+f);};verify();
const protocol={season:'2025-26',engine:'v41',samples:original.samples,seed:original.seed,ids:x.players.map(p=>p.playerId).sort((a,b)=>a-b),hashes,
 design:'All 582 players; frozen v41 healthy-load and full-cap paired protocols, natural position and four distinct mean-70 positional teammates, 30 opponents, two seats, four seed/rotation pairs. Rank by mean supportedHealthy (team margin minus same-minute mean70 baseline margin). FullCap is a separate diagnostic. No availability deduction; no name/position offsets or low-minute exclusion. Conditional Monte Carlo intervals only; source/opponent/role uncertainty remains. Historical short-game ranks use a different protocol. Experimental, not adopted; v41 failed team win gates.'};
const fingerprint=sha('reports/model-evolution-20261016/latest-full-ovr.mjs')+'-'+crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex');
const pf=root+'/protocol.json',cf=root+'/checkpoint.jsonl';
if(fs.existsSync(pf)){if(read(pf).fingerprint!==fingerprint)throw Error('Protocol drift');}else fs.writeFileSync(pf,JSON.stringify({...protocol,fingerprint},null,2));
function summarizeArm(arm){
 const strata=new Map(),stats={},margins=[],baseMargins=[],deltaWins=[],minutes=[];
 for(const g of arm.games){
  const delta=mean(g.pair.map(p=>p.margin-p.baselineMargin));
  if(!strata.has(g.opponent))strata.set(g.opponent,[]);strata.get(g.opponent).push(delta);
  margins.push(mean(g.pair.map(p=>p.margin)));baseMargins.push(mean(g.pair.map(p=>p.baselineMargin)));
  deltaWins.push(mean(g.pair.map(p=>p.win-p.baselineWin)));
  for(const p of g.pair){minutes.push(p.playerMinutes);for(const[k,v]of Object.entries(p.playerStats)){if(!stats[k])stats[k]=[];stats[k].push(v);}}
 }
 const values=[...strata.values()],contribution=mean(values.map(mean));
 const variance=values.reduce((s,a)=>{const m=mean(a);return s+a.reduce((t,v)=>t+(v-m)**2,0)/(a.length-1)/a.length;},0)/values.length**2;
 const se=Math.sqrt(variance);
 return{minutes:mean(minutes),meanContribution:contribution,standardError:se,ci95:[contribution-1.96*se,contribution+1.96*se],meanMargin:mean(margins),baselineMargin:mean(baseMargins),deltaWinProbability:mean(deltaWins),statsPerGame:Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,mean(v)])),independentPairs:arm.games.length,
   strata:[...strata].map(([opponent,values])=>({opponent,values}))};
}
function summarize(m,reused=false){
 if(m.job.variant!=='v41'||m.job.seed!==protocol.seed||m.job.samples!==protocol.samples)throw Error('Probe mismatch');
 const p=x.players.find(p=>p.playerId===m.result.playerId);if(!p)throw Error('Unknown player');
 return{playerId:p.playerId,name:p.name,position:m.result.position,healthy:summarizeArm(m.result.arms.find(a=>a.arm==='supportedHealthy')),fullCap:summarizeArm(m.result.arms.find(a=>a.arm==='fullCapCounterfactual')),simulatedGames:m.result.simulatedGames,reusedVerifiedProbe:reused};
}
const rows=fs.existsSync(cf)?fs.readFileSync(cf,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse):[];
if(new Set(rows.map(r=>r.playerId)).size!==rows.length)throw Error('Duplicate checkpoint player');
if(!rows.length){
 const previous=read('reports/player-impact-v41/probe-checkpoint.json');
 for(const m of previous.rows.filter(r=>r.job.variant==='v41')){const row=summarize(m,true);rows.push(row);fs.appendFileSync(cf,JSON.stringify(row)+'\n');}
}
const jobs=protocol.ids.filter(id=>!rows.some(r=>r.playerId===id)).map(id=>({id,variant:'v41',samples:protocol.samples,seed:protocol.seed}));
let next=0,done=0;const workers=[],started=Date.now();
function status(complete=false){fs.writeFileSync(root+'/status.json',JSON.stringify({state:complete?'complete':'running',playersCompleted:rows.length,totalPlayers:protocol.ids.length,reused:rows.filter(r=>r.reusedVerifiedProbe).length,elapsedSeconds:(Date.now()-started)/1000,updatedAt:new Date().toISOString(),fingerprint},null,2));}
status();console.log(JSON.stringify({start:true,total:protocol.ids.length,reused:rows.length,remaining:jobs.length,workers:4}));
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('../player-impact-v41/probe-worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);
  w.on('message',m=>{if(m.error)return reject(Error(m.error));try{
   const row=summarize(m);rows.push(row);fs.appendFileSync(cf,JSON.stringify(row)+'\n');done++;status();
   if(done%4===0||done===jobs.length)console.log(JSON.stringify({completed:rows.length,total:protocol.ids.length,elapsedSeconds:(Date.now()-started)/1000}));
   if(done===jobs.length)resolve();else dispatch(w);
  }catch(e){reject(e);}});dispatch(w);
 }
});}catch(e){fs.writeFileSync(root+'/failure.txt',e.stack);throw e;}finally{await Promise.all(workers.map(w=>w.terminate()));}
verify();if(rows.length!==protocol.ids.length)throw Error('Incomplete full-league result');
const players=rows.sort((a,b)=>b.healthy.meanContribution-a.healthy.meanContribution||a.playerId-b.playerId).map((r,i)=>({...r,rank:i+1}));
fs.writeFileSync(root+'/ranking.json',JSON.stringify({season:protocol.season,protocolFingerprint:fingerprint,rankingMetric:'supportedHealthy paired incremental team margin (points per 48-minute game)',experimental:true,adopted:false,availabilityPenalty:0,players},null,2));
const csv=[['rank','playerId','name','position','supportedMinutes','meanContribution','standardError','ci95Low','ci95High'],...players.map(p=>[p.rank,p.playerId,p.name,p.position,p.healthy.minutes,p.healthy.meanContribution,p.healthy.standardError,...p.healthy.ci95])].map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n');fs.writeFileSync(root+'/ranking.csv',csv);
fs.writeFileSync(root+'/verification.json',JSON.stringify({passed:true,players:players.length,healthyArmComplete:true,availabilityDeduction:false,allFrozenSourceHashesPassed:true,checkpointSHA256:sha(cf),rankingSHA256:sha(root+'/ranking.json'),fingerprint},null,2));
status(true);console.log(JSON.stringify({complete:true,players:players.length,elapsedSeconds:(Date.now()-started)/1000}));

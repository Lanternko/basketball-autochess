import {contextReference,attachCreationContext,measuredContext} from '../../src/measured_creation_context.js';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {defenseProbabilities,pressureSignal} from '../../src/defense_probability.js';
import {loadInput} from '../player-impact-v9/input.mjs';
import {opportunityPlan as terminalPlan} from '../player-impact-v6/model.mjs';
import {opportunityPlan as supplyPlan} from '../player-impact-v11/model.mjs';
const root='reports/player-impact-v14',zones=['long','mid','short'],versions=['rotation-space'];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-contexts.json`;if(fs.existsSync(output))throw Error('Keep original context artifact; use a new version to change it');
 const b=loadInput(season),reference=contextReference(b.league.teams.flatMap(t=>t.roster));attachCreationContext(b.league.teams.flatMap(t=>t.roster),reference);const teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,valid=new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${season}-on-court-truth.json`)).gameIds);
 const states=new Map(),games=new Map();let stints=0;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<=0)continue;stints++;
  const rows=games.get(s.id)??[];rows.push(s);games.set(s.id,rows);
 }
 for(const[id,rows]of games){
  rows.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  const energies=new Map();let lastPeriod=1;
  for(const s of rows){
   if(s.period>lastPeriod){for(const[k,e]of energies)energies.set(k,periodEnergyRecovery(e,s.period-lastPeriod));lastPeriod=s.period;}
   const active=new Map();
   for(const t of s.teams){
    const ids=new Set(t.players),lineup=new Map();
    for(const[pid,p]of teams.get(t.teamId)){
     const key=t.teamId+':'+pid,e=energies.get(key)??1,step=rotationEnergyStep(e,s.seconds,ids.has(pid),p.stamina);energies.set(key,step.end);
     if(ids.has(pid))lineup.set(pid,M.applyStamina(p,1-step.mean));
    }
    active.set(t.teamId,lineup);
   }
   for(let side=0;side<2;side++){
    const a=s.teams[side],d=s.teams[1-side],own=[...a.players].sort((x,y)=>x-y),def=[...d.players].sort((x,y)=>x-y);
    states.set(id+':'+s.period+':'+s.startClock+':'+s.endClock+':'+side,{own:own.map(pid=>active.get(a.teamId).get(pid)),def:def.map(pid=>active.get(d.teamId).get(pid)),seconds:s.seconds});
   }
  }
 }
 const sums=new Map(),exposures=new Map(),energySums=new Map();let done=0;
 for(const state of states.values()){
  const os=state.own,ds=state.def,help=M.helpDefense(ds),phys=M.teamPhysique(ds),onBall=ds.reduce((s,p)=>s+p.onBall,0)/5,pressure=pressureSignal(ds,b.options.stealPriorRate).attribute;
  const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound),oreb=tr(os),dreb=tr(ds);
  const plans=[terminalPlan(os,undefined,1),supplyPlan(os,undefined,1,'supply-creation')],contexts=os.map((_,i)=>measuredContext(os,i));
  for(let v=0;v<versions.length;v++){
   const plan=plans[1],longScale=1;
   for(let i=0;i<5;i++){
    const p=os[i],weights=os.map((_,j)=>j===i?plan.rows[i].weight*plan.rows[i].shoot:plan.rows[j].receivers[i]),den=weights.reduce((s,x)=>s+x,0),delta=Object.fromEntries(zones.map(z=>[z,0]));
    for(let j=0;j<5;j++)if(weights[j]>0){
     const q=defenseProbabilities(p,contexts[i],{onBall},help,oreb,dreb,phys,{assist:j===i?null:os[j].pass,contextScale:b.options.contextScale,contextLongScale:longScale,contextShortScale:b.options.contextShortScale,turnoverScale:b.options.turnoverScale,turnoverMode:b.options.turnoverMode,pressureAttribute:pressure});
     for(const z of zones)delta[z]+=weights[j]/den*(q.make[z]-p.shootingMeasurement.sourceBase[z]);
    }
    const key=p.playerId+':'+versions[v],sum=sums.get(key)??{seconds:0,long:0,mid:0,short:0};sum.seconds+=state.seconds;for(const z of zones)sum[z]+=state.seconds*delta[z];sums.set(key,sum);exposures.set(p.playerId,(exposures.get(p.playerId)??0)+(v===0?state.seconds:0));
    if(v===0)energySums.set(p.playerId,(energySums.get(p.playerId)??0)+state.seconds*p._eff);
   }
  }
  if(++done%10000===0)console.log(JSON.stringify({season,states:done,total:states.size}));
 }
 const players=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])),priors={};
 for(const version of versions)priors[version]=Object.fromEntries(zones.map(z=>{
  let num=0,den=0;for(const[id,p]of players){const c=sums.get(id+':'+version);if(!c)continue;const a=p.opportunityMeasurement.freshShotCounts?.[z+'A']??0;num+=a*c[z]/c.seconds;den+=a;}return[z,num/den];
 }));
 const cards=Object.fromEntries([...players].map(([id,p])=>[id,{strictSeconds:exposures.get(id)??0,meanSourceShootingMultiplier:exposures.get(id)?energySums.get(id)/exposures.get(id):null,contexts:Object.fromEntries(versions.map(v=>{const s=sums.get(id+':'+v),sec=s?.seconds??0;return[v,Object.fromEntries(zones.map(z=>[z,((s?.[z]??0)+3600*priors[v][z])/(sec+3600)]))];}))}]));
 const out={season,design:'Frozen source-context predicted make MINUS frozen unfatigued source attribute curve. Actual strict rotation order reconstructs model energy (linear drain/recovery, +.12 each period), probabilities use mean energy within each stint. Includes source mean fatigue rather than deleting every future fatigue effect. Strict own/opponent lineups, time exposure weights, model-implied self/received shot mix, mean on-ball defender proxy. 60-minute context-delta prior and 100-attempt empirical FG prior. No simulation residual, individual name offset, on/off outcome or ranking fit. Same-season reconstruction; model energy is not measured physiology.',stints,states:states.size,priors,cards,contextReference:reference,sources:{stints:file,stintsSHA256:hash(file),codeSHA256:hash(root+'/prepare.mjs'),inputSHA256:hash('reports/player-impact-v9/input.mjs'),contextModelSHA256:hash('src/measured_creation_context.js'),energyModelSHA256:hash('src/source_rotation_energy.js'),roleModelSHA256:hash('reports/player-impact-v11/model.mjs')}};
 fs.writeFileSync(output,JSON.stringify(out,null,2));console.log(JSON.stringify({season,players:players.size,stints,states:states.size,priors}));
}

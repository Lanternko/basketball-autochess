import {centeredMake} from '../player-impact-v14/model.mjs';
import {contextReference,attachCreationContext,measuredContext} from '../../src/measured_creation_context.js';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {observedFoulInputs} from '../player-impact-v5/model.mjs';
import {pressureSignal,attemptMakeProbability} from '../../src/defense_probability.js';
import {exposureDefenseProbabilities as defenseProbabilities} from './model.mjs';
import {loadInput} from './input.mjs';
import {opportunityPlan as terminalPlan} from '../player-impact-v6/model.mjs';
import {opportunityPlan as supplyPlan} from '../player-impact-v11/model.mjs';
const root='reports/player-impact-v20',zones=['long','mid','short'],versions=['rotation-space'];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-creation-audit.json`;if(fs.existsSync(output))throw Error('Preserve creation audit');
 const b=loadInput(season),reference=contextReference(b.league.teams.flatMap(t=>t.roster));attachCreationContext(b.league.teams.flatMap(t=>t.roster),reference);const teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,valid=new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${season}-on-court-truth.json`)).gameIds);
 const shotExposures=JSON.parse(fs.readFileSync(`reports/player-impact-v17/${season}-shot-exposures.json`));
 if(b.options.liveSignal)throw Error('Source FGA conditioner needs explicit live-signal support');
 const states=new Map(),games=new Map();let stints=0;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;s.shots=shotExposures.games[s.id]?.[s.startIndex+':'+s.endIndex];if(!s.shots)throw Error('Missing source shot exposure');stints++;
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
    states.set(id+':'+s.startIndex+':'+s.endIndex+':'+side,{own:own.map(pid=>active.get(a.teamId).get(pid)),def:def.map(pid=>active.get(d.teamId).get(pid)),seconds:s.seconds,shots:s.shots});
   }
  }
 }

 const sums=new Map();let done=0;
 for(const state of states.values()){
  const os=state.own,ds=state.def,help=M.helpDefense(ds),phys=M.teamPhysique(ds),onBall=ds.reduce((s,p)=>s+p.onBall,0)/5,pressure=pressureSignal(ds,b.options.stealPriorRate).attribute;
  const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound),oreb=tr(os),dreb=tr(ds),plan=supplyPlan(os,undefined,1,'supply-creation'),contexts=os.map((_,i)=>measuredContext(os,i));
  for(let j=0;j<5;j++){
   const key=os[j].playerId,sum=sums.get(key)??{seconds:0,delivered:0,assists:0};sum.seconds+=state.seconds;
   for(let i=0;i<5;i++)if(i!==j&&plan.rows[j].receivers[i]>0){
    const p=os[i],q=defenseProbabilities(p,contexts[i],{onBall},help,oreb,dreb,phys,{assist:os[j].pass,contextScale:b.options.contextScale,contextLongScale:1,contextShortScale:b.options.contextShortScale,turnoverScale:b.options.turnoverScale,turnoverMode:b.options.turnoverMode,pressureAttribute:pressure},ds);
    const fresh={...q,make:centeredMake(q,p,'rotation-space'),zone:p.opportunityMeasurement.freshZone},fouls=observedFoulInputs(fresh,p,b.options,attemptMakeProbability);
    const hazard=Math.min(.95,q.pTovTouch*(b.options.turnoverCategories?b.options.touchTurnoverScale:1));
    const survival=(1-hazard)/zones.reduce((s,z)=>s+fresh.zone[z]/fouls[z].recorded,0);
    const success=survival*zones.reduce((s,z)=>s+fresh.zone[z]*fresh.make[z],0),delivered=plan.rows[j].receivers[i]*state.seconds/60;
    sum.delivered+=delivered;sum.assists+=delivered*success;
   }
   sums.set(key,sum);
  }
  if(++done%20000===0)console.log(JSON.stringify({season,states:done,total:states.size}));
 }
 const actual=new Map(),manifest=JSON.parse(fs.readFileSync((season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json'));
 for(const spec of manifest.sources)if(valid.has(spec.id))for(const e of JSON.parse(fs.readFileSync(spec.file)).data.game.actions){if(e.isFieldGoal&&e.shotResult==='Made'&&e.assistPersonId)actual.set(e.assistPersonId,(actual.get(e.assistPersonId)??0)+1);}
 const old=JSON.parse(fs.readFileSync(`reports/player-impact-v4/${season}-cards.json`)),oldSuccess=old.leagueFG*old.leagueFgaSurvival,players=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])).values()];
 const rows=players.map(p=>{const s=sums.get(p.playerId)??{seconds:0,delivered:0,assists:0};return {playerId:p.playerId,name:p.name,minutes:s.seconds/60,actualAssists:actual.get(p.playerId)??0,...s,conditionalSuccess:s.delivered?s.assists/s.delivered:null,oldGlobalSuccess:oldSuccess,impliedRateCorrection:s.assists?oldSuccess*s.delivered/s.assists:null};});
 const totals=rows.reduce((s,p)=>({actual:s.actual+p.actualAssists,predicted:s.predicted+p.assists,delivered:s.delivered+p.delivered}),{actual:0,predicted:0,delivered:0});
 fs.writeFileSync(output,JSON.stringify({season,design:'Deterministic source-lineup audit only; no input changes. Delivered creator flow per minute times model probability of a made receiver FG, including touch turnover and unrecorded foul-miss survival. Uses centered source rates and mean stint energy/mean on-ball proxy. Flow rate per minute assumes approximate terminal clock, so count discrepancy is diagnostic, not a calibrated estimate. Actual AST from strict PBP; no ranks or on/off fit.',totals,oldGlobalSuccess:oldSuccess,conditionalSuccess:totals.predicted/totals.delivered,rows,sources:{codeSHA256:hash(root+'/source-creation-audit.mjs'),contextsSHA256:hash(root+'/'+season+'-contexts.json')}},null,2));
 console.log(JSON.stringify({season,totals,oldSuccess,conditionalSuccess:totals.predicted/totals.delivered}));
}

import {contextReference,attachCreationContext,measuredContext} from '../../src/measured_creation_context.js';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {observedFoulInputs} from '../player-impact-v5/model.mjs';
import {pressureSignal,attemptMakeProbability} from '../../src/defense_probability.js';
import {exposureDefenseProbabilities as defenseProbabilities} from './model.mjs';
import {loadSourceInput as loadInput} from './input.mjs';
import {attachDefenseAnchors} from '../player-impact-v28/defense-input.mjs';
import {attachCreationDependence} from '../../src/source_creation_dependence.js';
import {opportunityPlan as terminalPlan} from '../player-impact-v6/model.mjs';
import {opportunityPlan as supplyPlan} from '../player-impact-v11/model.mjs';
const root='reports/player-impact-v42',zones=['long','mid','short'],versions=['rotation-space'];
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-contexts.json`;if(fs.existsSync(output))throw Error('Keep original context artifact; use a new version to change it');
 const b=loadInput(season);const reference=contextReference(b.league.teams.flatMap(t=>t.roster));attachCreationContext(b.league.teams.flatMap(t=>t.roster),reference);const teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
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
 const sums=new Map(),exposures=new Map(),energySums=new Map();let done=0;
 for(const state of states.values()){
  const os=state.own,ds=state.def,help=M.helpDefense(ds),phys=M.teamPhysique(ds),onBall=ds.reduce((s,p)=>s+p.onBall,0)/5,pressure=pressureSignal(ds,b.options.stealPriorRate).attribute;
  const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound),oreb=tr(os),dreb=tr(ds);
  const plans=[terminalPlan(os,undefined,1),supplyPlan(os,undefined,1,'supply-creation')],contexts=os.map((_,i)=>measuredContext(os,i));
  for(let v=0;v<versions.length;v++){
   const plan=plans[1],longScale=1;
   for(let i=0;i<5;i++){
    const p=os[i],weights=os.map((_,j)=>j===i?plan.rows[i].weight*plan.rows[i].shoot:plan.rows[j].receivers[i]),delta=Object.fromEntries(zones.map(z=>[z,0]));
    let conditionalFgaWeight=0;
    for(let j=0;j<5;j++)if(weights[j]>0){
     const q=defenseProbabilities(p,contexts[i],{onBall},help,oreb,dreb,phys,{assist:j===i?null:os[j].pass,contextScale:b.options.contextScale,contextLongScale:longScale,contextShortScale:b.options.contextShortScale,turnoverScale:b.options.turnoverScale,turnoverMode:b.options.turnoverMode,pressureAttribute:pressure},ds);
     const fresh=q,fouls=observedFoulInputs(fresh,p,b.options,attemptMakeProbability);
     const hazard=Math.min(.95,q.pTovTouch*(b.options.turnoverCategories?b.options.touchTurnoverScale:1));
     const survival=(1-hazard)/zones.reduce((s,z)=>s+fresh.zone[z]/fouls[z].recorded,0),weight=weights[j]*survival;
     conditionalFgaWeight+=weight;
     for(const z of zones)delta[z]+=weight*(q.make[z]-p.shootingMeasurement.sourceBase[z]);
    }
    if(!(conditionalFgaWeight>0))throw Error('No source recorded-FGA support');
    for(const z of zones)delta[z]/=conditionalFgaWeight;
    const key=p.playerId+':'+versions[v],sum=sums.get(key)??{seconds:0,attempts:{long:0,mid:0,short:0},long:0,mid:0,short:0};
    sum.seconds+=state.seconds;
    for(const z of zones){const n=state.shots[p.playerId]?.[z]??0;sum[z]+=n*delta[z];sum.attempts[z]+=n;}
    sums.set(key,sum);exposures.set(p.playerId,(exposures.get(p.playerId)??0)+(v===0?state.seconds:0));
    if(v===0)energySums.set(p.playerId,(energySums.get(p.playerId)??0)+state.seconds*p._eff);
   }
  }
  if(++done%10000===0)console.log(JSON.stringify({season,states:done,total:states.size}));
 }
 const players=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])),priors={},priorAttempts={};
 const strictMinutes=[...exposures.values()].reduce((s,x)=>s+x,0)/60;
 for(const version of versions){
  priors[version]={};priorAttempts[version]={};
  for(const z of zones){let num=0,den=0;for(const[id,p]of players){const c=sums.get(id+':'+version);if(c){num+=c[z];den+=c.attempts[z];}}
   priors[version][z]=num/den;priorAttempts[version][z]=60*den/strictMinutes;
   if(den!==shotExposures.totals[z])throw Error('Source zone FGA coverage mismatch: '+z+' '+den);
  }
 }
 const cards=Object.fromEntries([...players].map(([id,p])=>[id,{strictSeconds:exposures.get(id)??0,meanSourceShootingMultiplier:exposures.get(id)?energySums.get(id)/exposures.get(id):null,
  sourceZoneAttempts:sums.get(id+':'+versions[0])?.attempts??{long:0,mid:0,short:0},
  contexts:Object.fromEntries(versions.map(v=>{const s=sums.get(id+':'+v);return[v,Object.fromEntries(zones.map(z=>{const prior=priorAttempts[v][z],n=s?.attempts[z]??0;return[z,((s?.[z]??0)+prior*priors[v][z])/(n+prior)];}))];}))}]));
 const out={season,design:'v41 make-defense plus v42 shooter/five-defender zone choice; source FGA conditional survival recentered. Source defense physique baseline neutralized; current-minus-source counterfactual slopes preserved. Same raw attributes, canonical once-corrected roles, actual source rotation energy, fresh FGA weights and recorded-FGA survival. New defense descriptors themselves were fitted to same-season outcomes; this centering step only weights recorded FGA counts and never fits simulation/win/onoff residuals. Frozen60minute source attempt prior, not causal defense or physiology.',stints,states:states.size,strictMinutes,priors,priorAttempts,cards,contextReference:reference,
 sources:{freshDefenseFitSHA256:hash('reports/player-impact-v41/fit.json'),freshDefenseSelectionSHA256:hash('reports/player-impact-v41/selection.json'),choiceFitSHA256:hash(root+'/choice-fit.json'),sourceInputSHA256:hash(root+'/input.mjs'),stints:file,stintsSHA256:hash(file),shotExposureSHA256:hash(`reports/player-impact-v17/${season}-shot-exposures.json`),codeSHA256:hash(root+'/prepare-contexts.mjs'),defenseAnchorSHA256:hash('reports/player-impact-v28/defense-input.mjs'),inputSHA256:hash('reports/player-impact-v20/role-input.mjs'),shootingFTRPriorSHA256:hash('reports/player-impact-v19/ftr-prior.json'),foulContactSHA256:hash('reports/player-impact-v19/'+season+'-foul-contact-audit.json'),creationReferenceSHA256:hash('reports/player-impact-v18/creation-reference.mjs'),creationAuditSHA256:hash('reports/player-impact-v17/'+season+'-creation-audit.json'),contextModelSHA256:hash('src/measured_creation_context.js'),energyModelSHA256:hash('src/source_rotation_energy.js'),roleModelSHA256:hash('reports/player-impact-v11/model.mjs'),exposureDefenseModelSHA256:hash(root+'/model.mjs'),creationDependenceSHA256:hash('src/source_creation_dependence.js'),defenseExposureSHA256:hash('reports/player-impact-v20/'+season+'-defense-exposure.json')}};
 fs.writeFileSync(output,JSON.stringify(out,null,2));console.log(JSON.stringify({season,players:players.size,stints,states:states.size,priors}));
}

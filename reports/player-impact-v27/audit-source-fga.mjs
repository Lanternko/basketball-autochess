// Conditional source reconstruction: fix real five-player lineups and the
// observed number of fresh recorded FGAs, then inspect model recipient shares.
// This does not test team opportunity volume or causal player ability.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../player-impact-v26/input.mjs';
import {opportunityPlan} from '../player-impact-v14/model.mjs';
import {terminalDefenseProbabilities} from '../player-impact-v21/model.mjs';
import {spaceProbability} from '../player-impact-v22/model.mjs';
import {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
import {attemptMakeProbability,pressureSignal} from '../../src/defense_probability.js';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
const root='reports/player-impact-v27',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
fs.mkdirSync(root,{recursive:true});
const seconds=c=>{const m=c.match(/^PT(?:(\d+)M)?([\d.]+)S$/);assert.ok(m);return Number(m[1]??0)*60+Number(m[2]);};
const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2025-26']){
 const output=`${root}/${season}-source-fga-audit.json`;assert.ok(!fs.existsSync(output),'Preserve source audit');
 const b=loadInput(season),opt={...b.options,creationPolicy:'rotation-space',contextLongScale:1};
 const truth=read(`reports/player-impact-v1/${season}-on-court-truth.json`),valid=new Set(truth.gameIds);
 const teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),names=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p.name]));
 const src=read(`reports/player-impact-v22/${season}-putback-events.json`),pbs=new Map(src.games.map(g=>[g.id,new Set(g.events.map(e=>e.index))]));
 const sf=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,games=new Map();
 for(const line of fs.readFileSync(sf,'utf8').trim().split('\n')){const s=JSON.parse(line);if(valid.has(s.id)&&s.seconds>=0){if(!games.has(s.id))games.set(s.id,[]);games.get(s.id).push(s);}}
 const mf=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',paths=new Map(read(mf).sources.map(s=>[s.id,s.file]));
 const sums=new Map([...names].map(([id,name])=>[id,{playerId:id,name,actual:0,expectedRaw:0,expectedSurvival:0,teamFreshFgaOpportunities:0,sourceWeightedSurvival:0,sourceSurvivalWeight:0}]));
 const totals={fga:0,putback:0,excludedLateOrEndgame:0,eligibleFresh:0,states:0,games:0},outGames=[];
 for(const[id,stints]of games){
  const actions=read(paths.get(id)).data.game.actions,putbacks=pbs.get(id),energies=new Map(),joined=new Set(),gameRows=[];let lastPeriod=1;
  const eligible=new Map();
  for(let k=0;k<actions.length;k++){
   const e=actions[k];if(!e.isFieldGoal||!['2pt','3pt'].includes(e.actionType))continue;totals.fga++;
   if(putbacks.has(k)){totals.putback++;continue;}
   const sec=seconds(e.clock);if(sec<=1.5||(e.period>=4&&sec<=27)){totals.excludedLateOrEndgame++;continue;}
   eligible.set(k,e);totals.eligibleFresh++;
  }
  stints.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  for(const s of stints){
   if(s.period>lastPeriod){for(const[k,e]of energies)energies.set(k,periodEnergyRecovery(e,s.period-lastPeriod));lastPeriod=s.period;}
   const active=s.teams.map(t=>{
    const ids=new Set(t.players),ps=new Map();
    for(const[pid,p]of teams.get(t.teamId)){
     const key=t.teamId+':'+pid,step=rotationEnergyStep(energies.get(key)??1,s.seconds,ids.has(pid),p.stamina);energies.set(key,step.end);
     if(ids.has(pid))ps.set(pid,M.applyStamina(p,1-step.mean));
    }
    return t.players.map(pid=>ps.get(pid));
   });
   const observed=s.teams.map(()=>new Map());
   for(let k=s.startIndex;k<s.endIndex;k++)if(eligible.has(k)){
    assert.ok(!joined.has(k),'Overlapping source event stints');joined.add(k);const e=eligible.get(k),side=s.teams.findIndex(t=>t.teamId===e.teamId);assert.ok(side>=0);assert.ok(s.teams[side].players.includes(e.personId));observed[side].set(e.personId,(observed[side].get(e.personId)??0)+1);
   }
   for(let side=0;side<2;side++){
    const N=[...observed[side].values()].reduce((a,b)=>a+b,0);if(!N)continue;
    const os=active[side],ds=active[1-side],pressure=pressureSignal(ds,opt.stealPriorRate),plan=opportunityPlan(os,null,pressure.relative,'rotation-space'),contexts=os.map((_,i)=>measuredContext(os,i));
    const help=M.helpDefense(ds),oreb=tr(os),dreb=tr(ds),phys=M.teamPhysique(ds),qs=os.map(()=>new Map());
    const probability=(i,assist)=>{
     if(qs[i].has(assist))return qs[i].get(assist);
     const q=spaceProbability(terminalDefenseProbabilities(os[i],contexts[i],ds[i],help,oreb,dreb,phys,{assist,forced:false,putback:false,contextScale:opt.contextScale,turnoverScale:opt.turnoverScale,turnoverMode:opt.turnoverMode,pressureAttribute:pressure.attribute,contextLongScale:1,contextShortScale:opt.contextShortScale},ds,opt),os[i],false,opt);
     qs[i].set(assist,q);return q;
    };
    const survival=q=>{
     const i=os.findIndex(p=>qs[os.indexOf(p)].get(null)===q||[...qs[os.indexOf(p)].values()].includes(q));assert.ok(i>=0);
     const f=observedFoulInputs(q,os[i],opt,attemptMakeProbability);
     // Recorded-zone sampling expands foul misses BEFORE sampling a zone.
     return (1-q.pTovTouch)/(['long','mid','short'].reduce((n,z)=>n+q.zone[z]/f[z].recorded,0));
    };
    const raw=os.map(()=>0),effective=os.map(()=>0),selfSurvival=os.map((_,i)=>survival(probability(i,null)));
    for(let i=0;i<5;i++){
     const row=plan.rows[i],self=plan.weights[i]*row.shoot;raw[i]+=self;effective[i]+=self*selfSurvival[i];
     const pass=plan.weights[i]*(1-row.shoot)*(1-row.intercept),den=row.receivers.reduce((a,b)=>a+b,0);assert.ok(pass===0||den>0);
     for(let j=0;j<5;j++)if(row.receivers[j]>0){
      const weight=pass*row.receivers[j]/den,own=probability(j,null),caught=probability(j,os[i].pass),q=caught.ev>=own.ev?caught:own;
      raw[j]+=weight;effective[j]+=weight*survival(q);
     }
    }
    const denRaw=raw.reduce((a,b)=>a+b,0),den=effective.reduce((a,b)=>a+b,0);assert.ok(den>0&&denRaw>0);
    const row={own:os.map(p=>p.playerId),opponent:ds.map(p=>p.playerId),observed:os.map(p=>observed[side].get(p.playerId)??0),expectedRaw:raw.map(x=>N*x/denRaw),expectedSurvival:effective.map(x=>N*x/den)};
    for(let i=0;i<5;i++){
     const sum=sums.get(os[i].playerId);sum.actual+=row.observed[i];sum.expectedRaw+=row.expectedRaw[i];sum.expectedSurvival+=row.expectedSurvival[i];sum.teamFreshFgaOpportunities+=N;sum.sourceWeightedSurvival+=N*effective[i];sum.sourceSurvivalWeight+=N*raw[i];
    }
    gameRows.push(row);totals.states++;
   }
  }
  assert.equal(joined.size,eligible.size,'Every eligible FGA must have one source lineup');outGames.push({id,rows:gameRows});totals.games++;
  if(totals.games%200===0)console.log(JSON.stringify({season,...totals}));
 }
 assert.equal(totals.games,truth.strictGames);assert.equal(totals.fga,read(`reports/player-impact-v21/${season}-terminal-events.json`).totals.fga);assert.equal(totals.putback,src.totals.fieldGoalAttempts);
 const minutes=new Map(truth.players.map(p=>[p.playerId,(p.on.seconds??0)/60]));
 const players=[...sums.values()].map(p=>({...p,minutes:minutes.get(p.playerId),sourceMeanRecordedFgaSurvival:p.sourceSurvivalWeight?p.sourceWeightedSurvival/p.sourceSurvivalWeight:null}));
 assert.equal(players.reduce((n,p)=>n+p.actual,0),totals.eligibleFresh);for(const k of ['expectedRaw','expectedSurvival'])assert.ok(Math.abs(players.reduce((n,p)=>n+p[k],0)-totals.eligibleFresh)<1e-6);
 const main=players.filter(p=>p.minutes>=500),Mins=main.reduce((s,p)=>s+p.minutes,0),mae=k=>main.reduce((s,p)=>s+36*Math.abs(p[k]-p.actual),0)/Mins;
 const hashes=Object.fromEntries([`${root}/audit-source-fga.mjs`,'reports/player-impact-v26/validation-protocol.json',sf,mf,`reports/player-impact-v22/${season}-putback-events.json`].map(f=>[f,hash(f)]));
 const out={season,design:'Condition on actual offensive/opposing five and observed eligible fresh recorded-FGA count within each strict stint. Compare current raw opportunity transport and analytic survival-adjusted recorded-FGA recipient shares. Source rotation mean energy, current conditional contact/turnover/shooting and EV-based own/received choice. Contact and global handler normalization cancel conditional on FGA. Exclude field-goal-putback proxy matching engine scope; FT-rebound quick shots stay fresh. Exclude <=1.5s period-clock and all last27s ofQ4/OT; shot-clock forced state and within-stint release fatigue/timing are not observed. This is conditional source allocation reconstruction, not season volume, exact replay, causal or out-of-sample skill. No runtime change.',totals,maeFreshFga36:{raw:mae('expectedRaw'),survival:mae('expectedSurvival')},players,games:outGames,hashes};
 fs.writeFileSync(output,JSON.stringify(out));console.log(JSON.stringify({season,totals,mae:out.maeFreshFga36,selected:players.filter(p=>[201939,203999,1628983,1629029,1629674].includes(p.playerId))}));
}

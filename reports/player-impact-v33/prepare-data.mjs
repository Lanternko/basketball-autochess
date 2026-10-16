// Deterministic conditional source predictions. No OVR, names, win results or
// current-stint made outcome labels enter the probability call directly. Frozen
// same-season source shooting/role inputs DO contain aggregate made outcomes.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {loadInput} from '../player-impact-v30/input.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {supplyFlow} from '../player-impact-v11/model.mjs';
import {sourceSupportedSelf} from '../../src/source_self_opportunities.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {terminalDefenseProbabilities} from '../player-impact-v30/model.mjs';
import {spaceProbability} from '../player-impact-v22/model.mjs';
import {observedFoulInputs} from '../player-impact-v5/model.mjs';
import {pressureSignal,attemptMakeProbability} from '../../src/defense_probability.js';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
const root='reports/player-impact-v33',zones=['long','mid','short'];fs.mkdirSync(root,{recursive:true});
const read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seconds=clock=>{const m=clock.match(/PT(?:(\d+)M)?([\d.]+)S/);if(!m)throw Error('Bad clock');return +(m[1]??0)*60 + +m[2];};
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const file=`${root}/${season}-conditional-data.json`;assert.ok(!fs.existsSync(file),'Keep frozen conditional data');
 const b=loadInput(season),truth=read(`reports/player-impact-v1/${season}-on-court-truth.json`),valid=new Set(truth.gameIds),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const stintFile=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`;
 const shotFile=`reports/player-impact-v17/${season}-shot-exposures.json`,shots=read(shotFile),games=new Map();
 const pbpHashes=Object.fromEntries(Object.entries(shots.sources.pbpHashes).map(([k,v])=>[k.replaceAll('\\','/'),v]));
 const manifestFile=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json';
 const manifest=read(manifestFile),specs=new Map(manifest.sources.map(x=>[x.id,x]));
 const hashes={[stintFile]:hash(stintFile),[shotFile]:hash(shotFile),[manifestFile]:hash(manifestFile),[`${root}/prepare-data.mjs`]:hash(`${root}/prepare-data.mjs`)};
 for(const line of fs.readFileSync(stintFile,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;
  const rows=games.get(s.id)??[];rows.push(s);games.set(s.id,rows);
 }
 assert.equal(games.size,valid.size);
 const cache=new Map(),rows=[],gameMetadata=[];let joined=0,selfJoined=0,assistedJoined=0,states=0,zeroShotStates=0,cappedInterceptions=0,done=0;
 for(const [id,stints]of games){
  const spec=specs.get(id),bytes=fs.readFileSync(spec.file);hashes[spec.file]=crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(hashes[spec.file],pbpHashes[spec.file.replaceAll('\\','/')]);
  const actions=JSON.parse(bytes).data.game.actions,putbacks=new Set();let pending=null;
  for(let i=0;i<actions.length;i++){
   const e=actions[i],k=e.actionType;
   if(['2pt','3pt'].includes(k)&&e.isFieldGoal){
    if(pending&&e.personId===pending.personId&&e.teamId===pending.teamId&&e.period===pending.period&&k==='2pt'&&e.area!=='Mid-Range'&&seconds(pending.clock)-seconds(e.clock)>=0&&seconds(pending.clock)-seconds(e.clock)<=3)putbacks.add(i);
    pending=null;
   }else if(k==='rebound'&&e.subType==='offensive'&&e.personId&&!e.qualifiers?.includes('team'))pending=e;
   else if(['turnover','freethrow','foul','period','jumpball'].includes(k)||k==='rebound'&&e.subType==='defensive')pending=null;
  }
  stints.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  const energy=new Map();let lastPeriod=1,gameRows=0;
  const fold=parseInt(crypto.createHash('sha256').update(id).digest('hex').slice(0,8),16)%5;
  for(const s of stints){
   if(s.period>lastPeriod){for(const[k,v]of energy)energy.set(k,periodEnergyRecovery(v,s.period-lastPeriod));lastPeriod=s.period;}
   const active=s.teams.map(t=>{
    const ids=new Set(t.players),current=new Map();
    for(const[pid,p]of teams.get(t.teamId)){
     const key=t.teamId+':'+pid,v=energy.get(key)??1,step=rotationEnergyStep(v,s.seconds,ids.has(pid),p.stamina);energy.set(key,step.end);
     if(ids.has(pid))current.set(pid,M.applyStamina(p,1-step.mean));
    }
    return [...t.players].sort((a,b)=>a-b).map(pid=>current.get(pid));
   });
   const actual=s.teams.map(t=>new Map(t.players.map(pid=>[pid,{attempts:0,selfMakes:0,assistedMakes:0}])));
   for(let i=s.startIndex;i<s.endIndex;i++){
    const e=actions[i];if(!e.isFieldGoal||!['2pt','3pt'].includes(e.actionType)||putbacks.has(i))continue;
    const side=s.teams.findIndex(t=>t.teamId===e.teamId);assert.ok(side>=0);const count=actual[side].get(e.personId);assert.ok(count);
    count.attempts++;
    if(e.shotResult==='Made'){if(e.assistPersonId)count.assistedMakes++;else count.selfMakes++;}
   }
   const shotCounts=shots.games[id][s.startIndex+':'+s.endIndex];assert.ok(shotCounts);
   for(let side=0;side<2;side++){
    states++;
    const os=active[side],ds=active[1-side],ids=os.map(p=>p.playerId),n=ids.map(pid=>actual[side].get(pid)),total=n.reduce((v,c)=>v+c.attempts,0);
    for(const [i,p]of os.entries())assert.equal(n[i].attempts,zones.reduce((v,z)=>v+(shotCounts[p.playerId]?.[z]??0),0));
    if(!total){zeroShotStates++;continue;}
    const key=s.teams[side].teamId+':'+ids.join(','),ls=elasticLineup(os,'elastic-creation');let flow=cache.get(key);
    if(!flow){flow=supplyFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
    const supported=sourceSupportedSelf(flow,ls.map(p=>p.opportunityMeasurement)),unused=flow.self.map((x,i)=>Math.max(0,x-supported[i]));
    const ctx=os.map((_,i)=>measuredContext(os,i)),help=M.helpDefense(ds),phys=M.teamPhysique(ds),onBall=ds.reduce((v,p)=>v+p.onBall,0)/5;
    const tr=lineup=>C.weightedTop(lineup.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound),oreb=tr(os),dreb=tr(ds);
    const pressure=pressureSignal(ds,b.options.stealPriorRate),attemptBase=[],attemptSlope=[],selfMakeBase=[],selfMakeSlope=[],assistedMake=[];
    for(let i=0;i<5;i++){
     const options={...b.options,assist:null,creationPolicy:'rotation-space',contextLongScale:1,pressureAttribute:pressure.attribute};
     function predict(assist){
      const q=terminalDefenseProbabilities(os[i],ctx[i],{onBall},help,oreb,dreb,phys,{...options,assist},ds,b.options);
      const p=spaceProbability(q,os[i],false,options);
      for(const v of [q.pTovTouch,q.pFoul,q.ev,p.pTovTouch,p.pFoul,p.ev,...Object.values(p.make),...Object.values(p.zone)])assert.ok(Number.isFinite(v),'Nonfinite source probability or EV');
      assert.ok(p.pTovTouch>=0&&p.pFoul>=0&&p.pTovTouch+p.pFoul<=1);
      return p;
     }
     function survival(p){
      const foul=observedFoulInputs(p,os[i],b.options,attemptMakeProbability);
      const fga=(1-p.pTovTouch)/zones.reduce((v,z)=>v+p.zone[z]/foul[z].recorded,0);
      const makes=fga*zones.reduce((v,z)=>v+p.zone[z]*p.make[z],0);
      assert.ok(Number.isFinite(fga)&&fga>0&&fga<=1&&makes>=0&&makes<=fga);return {fga,makes};
     }
     const own=predict(null),ownOut=survival(own);let a=supported[i]*ownOut.fga,sm=supported[i]*ownOut.makes,am=0;
     for(let j=0;j<5;j++)if(j!==i&&flow.matrix[j][i]>0){
      const caught=predict(os[j].pass),usedAssist=caught.ev>=own.ev,out=usedAssist?survival(caught):ownOut;
      const lost=ls[j].opportunityMeasurement.passStolenPerMinute*pressure.relative,pass=flow.rows[j]+lost;
      const multiplier=pass*(1-Math.min(.95,lost/pass))/flow.rows[j];
      if(multiplier>1+1e-8)cappedInterceptions++;
      const incoming=flow.matrix[j][i]*multiplier;a+=incoming*out.fga;if(usedAssist)am+=incoming*out.makes;else sm+=incoming*out.makes;
     }
     attemptBase.push(a);attemptSlope.push(unused[i]*ownOut.fga);selfMakeBase.push(sm);selfMakeSlope.push(unused[i]*ownOut.makes);assistedMake.push(am);
    }
    assert.ok(attemptBase.every(v=>v>0));
    rows.push([id,fold,s.teams[side].teamId,s.startIndex,s.endIndex,s.seconds,ids,n.map(x=>x.attempts),n.map(x=>x.selfMakes),n.map(x=>x.assistedMakes),attemptBase,attemptSlope,selfMakeBase,selfMakeSlope,assistedMake]);
    joined+=total;selfJoined+=n.reduce((v,c)=>v+c.selfMakes,0);assistedJoined+=n.reduce((v,c)=>v+c.assistedMakes,0);gameRows++;
   }
  }
  gameMetadata.push({gameId:id,fold,shotStates:gameRows});
  if(++done%200===0)console.log(JSON.stringify({season,games:done,total:games.size,rows:rows.length}));
 }
 assert.equal(joined,shots.totals.all);
 assert.ok(rows.some(r=>r[14].some(v=>v>0)),'No predicted assisted makes in a season');
 const out={season,columns:['gameId','gameFold','teamId','startIndex','endIndex','seconds','playerIds','attempts','selfMakes','assistedMakes','attemptBase','attemptSlope','selfMakeBase','selfMakeSlope','assistedMakeExpected'],
 design:'Linear opportunity mixture lambda in[0,1]: supported-self v31 at0, residual-self v30 at1. Exact same source roles, passing transport, v30 centered shooting probabilities, actual mean-stint energy, touch risk and foul-miss recorded-FGA survival. Received shots choose own/caught by EV exactly as engine best(). No OVR, names or wins in prediction. Local outcome labels do not directly enter the probability call, but frozen full-season FG/role inputs DO contain aggregate made outcomes. Source counts are same-season reconstruction inputs; held-out-game labels are not fully unseen inputs.',
 coverage:{games:games.size,states,zeroShotStates,shotStates:rows.length,freshAttempts:joined,selfMakes:selfJoined,assistedMakes:assistedJoined,cappedInterceptions},gameMetadata,rows,hashes};
 fs.writeFileSync(file,JSON.stringify(out));console.log(JSON.stringify({season,...out.coverage}));
}

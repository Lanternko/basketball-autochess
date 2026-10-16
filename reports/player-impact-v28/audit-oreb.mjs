// Fix actual opposing fives and FG individual-rebound opportunities.
// Do not infer portable or causal ability from this source reconstruction.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../player-impact-v26/input.mjs';
import {reboundChance,reboundWeights} from '../defense-tenth/step4-rebounds-allocation/model.mjs';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import {applyStamina} from '../../src/probability_model.js';
const root='reports/player-impact-v28',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
fs.mkdirSync(root,{recursive:true});
const protocol='reports/player-impact-v26/validation-protocol.json';
for(const [p,h] of Object.entries(read(protocol).hashes))assert.equal(hash(p),h,p);
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-oreb-risksets.json`;assert.ok(!fs.existsSync(output),'Preserve completed audit');
 const b=loadInput(season),truth=read(`reports/player-impact-v1/${season}-on-court-truth.json`),valid=new Set(truth.gameIds);
 const sf=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,stints=new Map();
 for(const line of fs.readFileSync(sf,'utf8').trim().split('\n')){const s=JSON.parse(line);if(valid.has(s.id)){if(!stints.has(s.id))stints.set(s.id,[]);stints.get(s.id).push(s);}}
 const mf=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',paths=new Map(read(mf).sources.map(s=>[s.id,s.file]));
 const teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),names=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p.name]));
 const sums=new Map([...names].map(([id,name])=>[id,{playerId:id,name,fgOreb:0,allOreb:0,fgChances:0,teamWonChances:0,expectedFresh:0,expectedEnergy:0,expectedConditional:0}]));
 const counts={},issues=[],games=[],hashes=Object.fromEntries([`${root}/audit-oreb.mjs`,protocol,sf,mf].map(p=>[p,hash(p)]));
 const inc=k=>counts[k]=(counts[k]??0)+1;
 let totalExpectedFresh=0,totalExpectedEnergy=0;
 for(const[id,ss]of stints){
  const path=paths.get(id);hashes[path]=hash(path);const actions=read(path).data.game.actions,refs=new Map(actions.map(e=>[e.actionNumber,e]));
  const energies=new Map(),joined=new Set(),rows=[];let lastPeriod=1;
  ss.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  for(const s of ss){
   if(s.period>lastPeriod){for(const[k,e]of energies)energies.set(k,periodEnergyRecovery(e,s.period-lastPeriod));lastPeriod=s.period;}
   const fresh=s.teams.map(t=>t.players.map(pid=>teams.get(t.teamId).get(pid)));
   const energy=s.teams.map(t=>{
    const active=new Set(t.players),cards=new Map();
    for(const[pid,p]of teams.get(t.teamId)){
     const key=t.teamId+':'+pid,step=rotationEnergyStep(energies.get(key)??1,s.seconds,active.has(pid),p.stamina);energies.set(key,step.end);
     if(active.has(pid))cards.set(pid,applyStamina(p,1-step.mean));
    }
    return t.players.map(pid=>cards.get(pid));
   });
   for(let i=s.startIndex;i<s.endIndex;i++){
    const e=actions[i];if(e?.actionType!=='rebound')continue;
    assert.ok(!joined.has(i));joined.add(i);inc('allReboundEvents');
    if(!e.personId||(e.qualifiers??[]).includes('team')){inc('teamRebounds');continue;}
    if(e.subType==='offensive'){inc('allIndividualOreb');sums.get(e.personId).allOreb++;}else {assert.equal(e.subType,'defensive');inc('allIndividualDreb');}
    const shot=refs.get(e.shotActionNumber);
    if(!shot){inc('individualMissingShotReference');issues.push({id,index:i,reason:'missing shot reference'});continue;}
    if(shot.actionType==='freethrow'){inc('individualFtRebounds');continue;}
    if(!['2pt','3pt'].includes(shot.actionType)||shot.shotResult!=='Missed'||shot.period!==e.period){inc('individualOtherShotReference');issues.push({id,index:i,reason:'non-missed FG reference',shotAction:shot.actionType,shotResult:shot.shotResult,period:shot.period});continue;}
    const off=s.teams.findIndex(t=>t.teamId===shot.teamId),side=s.teams.findIndex(t=>t.teamId===e.teamId);
    assert.ok(off>=0&&side>=0&&s.teams[side].players.includes(e.personId),'Source recipient/current five mismatch');
    const offensive=side===off;assert.equal(offensive,e.subType==='offensive');
    const os=fresh[off],ds=fresh[1-off],oe=energy[off],de=energy[1-off];
    const zone=shot.actionType==='3pt'?'long':/Restricted Area|In The Paint/.test(shot.area??'')?'short':'mid';
    const settings={zone,side:'offense',shooterIndex:os.findIndex(p=>p.playerId===shot.personId),freeThrow:false};
    const pFresh=reboundChance(os,ds,{...settings,oldChance:0,options:b.options}),pEnergy=reboundChance(oe,de,{...settings,oldChance:0,options:b.options});
    const weights=reboundWeights(os,settings,b.options);assert.ok(Math.abs(weights.reduce((a,b)=>a+b,0)-1)<1e-10);
    const selected=offensive?os.findIndex(p=>p.playerId===e.personId):5;assert.ok(selected>=0);
    for(let j=0;j<5;j++){
     const a=sums.get(os[j].playerId);a.fgChances++;a.fgOreb+=Number(selected===j);a.expectedFresh+=pFresh*weights[j];a.expectedEnergy+=pEnergy*weights[j];
     if(offensive){a.teamWonChances++;a.expectedConditional+=weights[j];}
    }
    totalExpectedFresh+=pFresh;totalExpectedEnergy+=pEnergy;inc('individualFgRebounds');if(offensive)inc('individualFgOreb');
    rows.push({index:i,own:os.map(p=>p.playerId),opponent:ds.map(p=>p.playerId),selected,zone,shooterId:shot.personId,pFresh,pEnergy,weights});
   }
  }
  assert.equal(joined.size,actions.filter(e=>e.actionType==='rebound').length,'Every rebound must map to a unique stint');
  games.push({id,fold:Number(id)%5,rows});if(games.length%250===0)console.log(JSON.stringify({season,games:games.length,fg:counts.individualFgRebounds,issues:issues.length}));
 }
 assert.equal(games.length,truth.strictGames);
 assert.equal(counts.allReboundEvents,counts.teamRebounds+counts.allIndividualOreb+counts.allIndividualDreb);
 const minutes=new Map(truth.players.map(p=>[p.playerId,(p.on.seconds??0)/60])),players=[...sums.values()].map(p=>({...p,minutes:minutes.get(p.playerId)}));
 assert.equal(players.reduce((s,p)=>s+p.fgOreb,0),counts.individualFgOreb);
 assert.ok(Math.abs(players.reduce((s,p)=>s+p.expectedFresh,0)-totalExpectedFresh)<1e-6);
 const main=players.filter(p=>p.minutes>=500),mins=main.reduce((s,p)=>s+p.minutes,0),mae=k=>main.reduce((s,p)=>s+36*Math.abs(p[k]-p.fgOreb),0)/mins;
 const out={season,design:'Conditional source FG rebound audit: fix actual offensive and defensive five at the rebound action and each resolved individual FG rebound; team/FT/unknown-reference rebounds separately counted. Current team-acquisition and recipient paths, fresh cards versus model source-rotation mean energy. This conditions on resolved misses, not their generation, and is descriptive, not causal/portable skill or prospective prediction. No runtime/rank changes.',counts,issues,expectedTeamOreb:{fresh:totalExpectedFresh,energy:totalExpectedEnergy},maeFgOreb36:{fresh:mae('expectedFresh'),energy:mae('expectedEnergy'),conditionalRecipient:mae('expectedConditional')},players,games,hashes};
 fs.writeFileSync(output,JSON.stringify(out));console.log(JSON.stringify({season,counts,issues:issues.length,expected:out.expectedTeamOreb,mae:out.maeFgOreb36,selected:players.filter(p=>[1629011,1641705,1630595,1629674,203999].includes(p.playerId))}));
}

// Source-only decomposition: generic block event rate versus recipient weights.
// Actual FGA, actual rotations and actual team block counts; no candidate engine.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../../player-impact-v30/input.mjs';
import {blockProfile} from '../../../src/rebound_block_model.js';
import {measuredRecipientWeights} from '../../../src/individual_box_allocation.js';
const root='reports/player-impact-diagnostics/block-source-v37',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const output=root+'/audit.json';assert.ok(!fs.existsSync(output));const seasons=[],hashes={};
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const input=loadInput(season),teams=new Map(input.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const truthFile=`reports/player-impact-v1/${season}-on-court-truth.json`,truth=read(truthFile),valid=new Set(truth.gameIds),manifestFile=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',specs=new Map(read(manifestFile).sources.map(s=>[s.id,s]));
 const stintFile=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,frames=new Map(),players=new Map();
 for(const line of fs.readFileSync(stintFile,'utf8').trim().split('\n')){const f=JSON.parse(line);if(valid.has(f.id)&&f.seconds>=0){const rows=frames.get(f.id)??[];rows.push(f);frames.set(f.id,rows);}}
 let fga=0,blocks=0,sourceExpectedUpperBound=0,conditionalAllocated=0;
 for(const [id,stints]of frames){
  const path=specs.get(id).file;hashes[path]=sha(path);const actions=read(path).data.game.actions;
  for(const f of stints){
   const ds=f.teams.map(t=>t.players.map(pid=>teams.get(t.teamId).get(pid))),weights=ds.map(l=>measuredRecipientWeights(l,'blk')),local=[0,0];
   for(let side=0;side<2;side++)for(const p of ds[side]){const row=players.get(p.playerId)??{playerId:p.playerId,name:p.name,position:p.pos,seconds:0,actualBlocks:0,expectedUpperBound:0,expectedGivenActualTeamBlocks:0};row.seconds+=f.seconds;players.set(p.playerId,row);}
   const localFga=[0,0];
   for(let a=f.startIndex;a<f.endIndex;a++){
    const e=actions[a];if(!e.isFieldGoal||!['2pt','3pt'].includes(e.actionType))continue;
    const off=f.teams.findIndex(t=>t.teamId===e.teamId),def=1-off;assert.ok(off>=0);const index=f.teams[off].players.indexOf(e.personId);assert.ok(index>=0);
    const zone=e.actionType==='3pt'?'long':e.area==='Mid-Range'?'mid':'short';
    // makeProbability0 removes only the miss-share cap. This is an upper bound
    // on model *expected* blocks for these FGA, not a maximum random count.
    const probability=blockProfile(ds[def],{zone,shooterIndex:index,makeProbability:0}).perAttempt;
    sourceExpectedUpperBound+=probability;fga++;localFga[def]++;
    for(let i=0;i<5;i++)players.get(ds[def][i].playerId).expectedUpperBound+=probability*weights[def][i];
    if(e.blockPersonId){assert.equal(e.shotResult,'Missed');assert.ok(f.teams[def].players.includes(e.blockPersonId));players.get(e.blockPersonId).actualBlocks++;blocks++;local[def]++;}
   }
   for(let side=0;side<2;side++){
    assert.equal(localFga[side],f.teams[side].opponent.fga);
    for(let i=0;i<5;i++){const n=local[side]*weights[side][i];players.get(ds[side][i].playerId).expectedGivenActualTeamBlocks+=n;conditionalAllocated+=n;}
   }
  }
 }
 assert.ok(Math.abs(conditionalAllocated-blocks)<1e-7);const rows=[...players.values()].map(p=>({...p,minutes:p.seconds/60,actual36:2160*p.actualBlocks/p.seconds,upperBound36:2160*p.expectedUpperBound/p.seconds,conditionalAllocation36:2160*p.expectedGivenActualTeamBlocks/p.seconds})).filter(p=>p.seconds>0);
 for(const p of rows)for(const v of [p.actual36,p.upperBound36,p.conditionalAllocation36])assert.ok(Number.isFinite(v));
 seasons.push({season,games:frames.size,sourceFga:fga,actualBlocks:blocks,expectedUpperBound:sourceExpectedUpperBound,conditionalAllocated,players:rows});
 for(const f of [truthFile,manifestFile,stintFile])hashes[f]=sha(f);
 console.log(JSON.stringify({...seasons.at(-1),players:rows.length}));
}
for(const f of [root+'/audit.mjs','src/rebound_block_model.js','src/individual_box_allocation.js','reports/player-impact-v30/validation-protocol.json'])hashes[f]=sha(f);
fs.writeFileSync(output,JSON.stringify({scope:'Source-only diagnosis of generic block event upper expected rate and measured recipient allocation conditional on actual team blocks. Includes all FG attempts including putbacks, uses original source rotations without inferred assist labels. Not an engine change, accuracy certification, causal estimate or OVR; make probability0 removes the miss-share cap only. Full same-season box rates enter recipient allocation. Positive/negative allocation residuals still confound within-stint zone/exposure and shrinkage.',seasons,hashes}));

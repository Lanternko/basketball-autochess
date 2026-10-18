import fs from 'node:fs';
import assert from 'node:assert/strict';
const root='reports/player-box-audit/allocation',read=f=>JSON.parse(fs.readFileSync(f));
let runs=0,games=0,changedDreb=0,changedBlk=0;
for(const dir of [root,root+'/confirmation']){
 if(!fs.existsSync(dir+'/runs'))continue;
 const protocol=read(dir+'/protocol.json');
 for(const season of protocol.seasons)for(const version of protocol.variants)for(const seed of protocol.seeds){
  const candidate=read(`${dir}/runs/${season}-${version}-${seed}.json`),control=read(`reports/defense-tenth/step4-rebounds-turnover-time/runs/${season}-split-${seed}.json`);
  assert.deepEqual(candidate.matches,control.matches);
  for(let i=0;i<control.teams.length;i++){
   const a=structuredClone(candidate.teams[i]),b=structuredClone(control.teams[i]);
   assert.deepEqual(a.stats,b.stats);assert.deepEqual(a.opponent,b.opponent);
   for(let j=0;j<a.players.length;j++){
    changedDreb+=Number(a.players[j].stats.dreb!==b.players[j].stats.dreb);changedBlk+=Number(a.players[j].stats.blk!==b.players[j].stats.blk);
    if(version!=='block-allocation'){delete a.players[j].stats.dreb;delete b.players[j].stats.dreb;}
    if(version!=='dreb-allocation'){delete a.players[j].stats.blk;delete b.players[j].stats.blk;}
   }
   assert.deepEqual(a,b);
  }
  runs++;games+=candidate.matches.length;
 }
}
const result={passed:true,runs,games,completeTeamStatisticsIdentical:true,allNonTargetPlayerStatisticsIdentical:true,changedDrebPlayerStints:changedDreb,changedBlkPlayerStints:changedBlk};
fs.writeFileSync(root+'/parity.json',JSON.stringify(result,null,2));console.log(result);

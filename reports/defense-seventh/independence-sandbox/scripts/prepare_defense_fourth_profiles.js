import fs from 'node:fs';
import {read} from './defense_io.js';
const league=read('data/season-league.json'),order={},counter={};
for(const g of league.schedule)for(const id of [g.homeId,g.awayId])order[g.id+'/'+id]=counter[id]=(counter[id]??0)+1;
const sums={full:{},pre41:{}},cards=new Map(league.teams.flatMap(t=>t.roster.map(p=>[t.id+'/'+p.playerId,p])));
for(const s of read('data/defense-a-source/manifest.json').sources)for(const e of read(s.file).data.game.actions){
  if(e.isFieldGoal!==1||!['2pt','3pt'].includes(e.actionType))continue;
  const z=e.actionType==='3pt'?'long':e.area==='Mid-Range'?'mid':'short',p=cards.get(e.teamId+'/'+e.personId);if(!p)continue;
  for(const mode of ['full','pre41'])if(mode==='full'||order[s.id+'/'+e.teamId]<=41){const a=sums[mode][z]??=[0,0];a[0]+=p.shotProfile?.freeThrowsPerAttempt??.264;a[1]++;}
}
const means=Object.fromEntries(Object.entries(sums).map(([m,v])=>[m,Object.fromEntries(Object.entries(v).map(([z,a])=>[z,a[0]/a[1]]))]));
fs.writeFileSync('reports/defense-fourth/foul-profile-means.json',JSON.stringify({...means,definition:'Zone-specific recorded-FGA weighted mean of individual FTA/FGA. Division removes correlation between zone mix and overall foul drawing before independent league total calibration. pre41 refreshed with first41 cards by heldout preparation.'},null,2)+'\n');console.log(means);

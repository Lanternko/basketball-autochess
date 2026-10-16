// Join the old impossible marks to the actual new allocation branch and source q.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from './input.mjs';
import {sourceFlow} from './model.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
const root='reports/player-impact-v37',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const prior=read('reports/player-impact-diagnostics/pass-row-feasibility-v36/audit.json'),seasons=[],hashes={};
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const oldFile=`reports/player-impact-v33/${season}-conditional-data.json`,newFile=`${root}/${season}-conditional-data.json`,old=read(oldFile),now=read(newFile),input=loadInput(season),teams=new Map(input.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),cache=new Map();
 const counts={'fixed-pass-rows':0,'relaxed-source-columns':0},restored={'fixed-pass-rows':0,'relaxed-source-columns':0};let maxStrictRowDifference=0;
 assert.equal(old.rows.length,now.rows.length);
 for(let k=0;k<now.rows.length;k++){
  const r=now.rows[k],p=old.rows[k];assert.deepEqual(r.slice(0,10),p.slice(0,10));const key=r[2]+':'+r[6].join(',');let f=cache.get(key);
  if(!f){f=sourceFlow(elasticLineup(r[6].map(pid=>teams.get(r[2]).get(pid)),'elastic-creation'));cache.set(key,f);}
  counts[f.branch]++;
  for(let i=0;i<5;i++){
   assert.ok(r[12][i]>0&&f.self[i]>0);
   if(p[12][i]+p[13][i]===0)restored[f.branch]+=p[8][i];
   if(f.branch==='fixed-pass-rows')maxStrictRowDifference=Math.max(maxStrictRowDifference,Math.abs(f.rows[i]-f.old.rows[i]));
  }
 }
 assert.deepEqual(now.flowBranches,counts);const ref=prior.seasons.find(s=>s.season===season);
 assert.equal(counts['fixed-pass-rows'],ref.strictlyFeasibleShotStates);assert.equal(counts['relaxed-source-columns'],ref.nonStrictShotStates);
 assert.equal(restored['fixed-pass-rows'],ref.unsupportedMakesInStrictlyFeasibleStates);assert.equal(restored['relaxed-source-columns'],ref.unsupportedMakesNeedingSupplyAdjustment);
 assert.ok(maxStrictRowDifference<1e-8);seasons.push({season,shotStates:now.rows.length,counts,restored,maxStrictRowDifference});
 for(const f of [oldFile,newFile,`${root}/${season}-contexts.json`])hashes[f]=sha(f);
 console.log(JSON.stringify(seasons.at(-1)));
}
for(const f of [root+'/verify-branches.mjs',root+'/model.mjs','reports/player-impact-diagnostics/pass-row-feasibility-v36/audit.json'])hashes[f]=sha(f);
fs.writeFileSync(root+'/branch-verification.json',JSON.stringify({passed:true,seasons,restoredByFixedPassRows:seasons.reduce((s,r)=>s+r.restored['fixed-pass-rows'],0),restoredByExplicitRelaxation:seasons.reduce((s,r)=>s+r.restored['relaxed-source-columns'],0),hashes},null,2));

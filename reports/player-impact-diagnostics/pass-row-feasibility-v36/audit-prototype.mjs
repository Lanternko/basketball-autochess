// All strict source fives, without changing a production engine or old files.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../../player-impact-v30/input.mjs';
import {elasticLineup} from '../../player-impact-v8/model.mjs';
import {supplyFlow} from '../../player-impact-v11/model.mjs';
import {ownPoolFlow} from './prototype.mjs';
const root='reports/player-impact-diagnostics/pass-row-feasibility-v36',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),seasons=[],samples=[],hashes={};
if(fs.existsSync(root+'/source-prototype-verification.json'))throw Error('Preserve source prototype evidence');
let maxIterations=0,maxRowDifference=0;
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),file=`reports/player-impact-v33/${season}-conditional-data.json`,data=read(file),cache=new Map();hashes[file]=sha(file);
 let strict=0,rejected=0,restored=0,pending=0;
 for(const r of data.rows){
  const key=r[2]+':'+r[6].join(',');let result=cache.get(key);
  if(!result){
   const ls=elasticLineup(r[6].map(pid=>teams.get(r[2]).get(pid)),'elastic-creation'),old=supplyFlow(ls),total=old.terminal.reduce((s,v)=>s+v,0),own=total-old.rows.reduce((s,v)=>s+v,0),tol=1e-10*Math.max(1,total),feasible=own>tol&&old.rows.every((v,i)=>total-old.terminal[i]-v>tol);
   if(feasible){
    const f=ownPoolFlow(ls);maxIterations=Math.max(maxIterations,f.iterations);
    for(let i=0;i<5;i++){assert.ok(f.self[i]>0);maxRowDifference=Math.max(maxRowDifference,Math.abs(f.rows[i]-old.rows[i]));assert.ok(Math.abs(f.self[i]+f.incoming[i]-old.terminal[i])<1e-8);}
    if(cache.size%500===0)samples.push({tag:{season,teamId:r[2],key},prior:f.prior,joint:f.joint,rows:[...old.rows,f.ownPool],columns:f.terminal});
   }else assert.throws(()=>ownPoolFlow(ls),RangeError);
   result={feasible};cache.set(key,result);
  }
  const n=r[8].reduce((v,m,i)=>v+(r[12][i]+r[13][i]===0?m:0),0);
  if(result.feasible){strict++;restored+=n;}else{rejected++;pending+=n;}
 }
 seasons.push({season,shotStates:data.rows.length,uniqueTeamFives:cache.size,strictSourceStatesChecked:strict,nonStrictSourceStatesRejected:rejected,legacyUnsupportedMakesWithPositiveOwnNow:restored,legacyUnsupportedMakesStillPending:pending});console.log(JSON.stringify(seasons.at(-1)));
}
const out={passed:true,seasons,maxIterations,maxPasserRowAbsoluteDifference:maxRowDifference,legacyUnsupportedMakesWithPositiveOwnNow:seasons.reduce((s,r)=>s+r.legacyUnsupportedMakesWithPositiveOwnNow,0),legacyUnsupportedMakesStillPending:seasons.reduce((s,r)=>s+r.legacyUnsupportedMakesStillPending,0),runtimeChanged:false,
 scope:'All strict source fives checked at source role rates. Fixed passer rows retained, positive own support and terminal columns conserved. Non-strict states intentionally rejected; no engine/probability recentering/full-game verification or OVR claim.',samples,
 hashes:{...hashes,...Object.fromEntries([root+'/audit-prototype.mjs',root+'/prototype.mjs','reports/player-impact-v30/validation-protocol.json'].map(f=>[f,sha(f)]))}};
fs.writeFileSync(root+'/source-prototype-verification.json',JSON.stringify(out,null,2));console.log(JSON.stringify({...out,seasons:undefined,samples:samples.length,hashes:undefined}));

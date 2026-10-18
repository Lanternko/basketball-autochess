// Feasibility diagnostic only: no candidate transport or game changes.
// Can positive own support be restored without changing any legacy passer row?
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../../player-impact-v30/input.mjs';
import {elasticLineup} from '../../player-impact-v8/model.mjs';
import {supplyFlow} from '../../player-impact-v11/model.mjs';
const root='reports/player-impact-diagnostics/pass-row-feasibility-v36',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const file=root+'/audit.json';if(fs.existsSync(file))throw Error('Preserve feasibility evidence');
const seasons=[],hashes={};
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))])),cache=new Map();
 const sourceFile=`reports/player-impact-v33/${season}-conditional-data.json`,data=read(sourceFile);hashes[sourceFile]=sha(sourceFile);
 let fixable=0,unsupported=0,strictStates=0,nonStrictStates=0,allZero=0,allZeroMakes=0;const exceptions=[];
 for(const r of data.rows){
  const key=r[2]+':'+r[6].join(',');let flow=cache.get(key);
  if(!flow){
   const ps=r[6].map(pid=>teams.get(r[2]).get(pid)),ls=elasticLineup(ps,'elastic-creation'),f=supplyFlow(ls),total=f.terminal.reduce((s,v)=>s+v,0),remainingOwn=total-f.rows.reduce((s,v)=>s+v,0),minPassRowSlack=Math.min(...f.rows.map((v,i)=>total-f.terminal[i]-v)),tolerance=1e-10*Math.max(1,total);
   flow={remainingOwn,minPassRowSlack,strictlyFeasible:remainingOwn>tolerance&&minPassRowSlack>tolerance,terminal:f.terminal,passerRows:f.rows};cache.set(key,flow);
  }
  // For a 6x5 matrix, passer i cannot connect to finisher i, while the
  // separate own row can connect to all five. Strict Hall feasibility reduces
  // to positive own-row mass and each passer row below all other columns.
  if(flow.strictlyFeasible)strictStates++;else nonStrictStates++;
  let local=0;
  for(let i=0;i<5;i++)if(r[12][i]+r[13][i]===0)local+=r[8][i];
  unsupported+=local;if(flow.strictlyFeasible)fixable+=local;
  if(r[12].every((v,i)=>v+r[13][i]===0)){allZero++;allZeroMakes+=r[8].reduce((s,v)=>s+v,0);}
  if(local&&!flow.strictlyFeasible)exceptions.push({gameId:r[0],teamId:r[2],startIndex:r[3],endIndex:r[4],playerIds:r[6],unsupportedSelfMakes:local,...flow});
 }
 assert.equal(unsupported,data.rows.reduce((s,r)=>s+r[8].reduce((v,n,i)=>v+(r[12][i]+r[13][i]===0?n:0),0),0));
 seasons.push({season,sourceShotStates:data.rows.length,uniqueTeamFives:cache.size,strictlyFeasibleShotStates:strictStates,nonStrictShotStates:nonStrictStates,legacyUnsupportedSelfMakes:unsupported,unsupportedMakesInStrictlyFeasibleStates:fixable,unsupportedMakesNeedingSupplyAdjustment:unsupported-fixable,allZeroSelfStates:allZero,allZeroSelfMakes:allZeroMakes,exceptions});
 console.log(JSON.stringify({...seasons.at(-1),exceptions:exceptions.length}));
}
const out={scope:'Diagnostic Hall feasibility, no new transport implementation, fitted parameter, runtime change, OVR or adoption. Uses exact frozen v30 roles and v33 source probabilities. A separate own row plus five fixed passer rows may preserve legacy passing without zero own support in strictly feasible states; KL-prior choice and non-strict cases still require implementation and source/full-game verification.',
 totals:{sourceShotStates:seasons.reduce((s,r)=>s+r.sourceShotStates,0),legacyUnsupportedSelfMakes:seasons.reduce((s,r)=>s+r.legacyUnsupportedSelfMakes,0),unsupportedMakesInStrictlyFeasibleStates:seasons.reduce((s,r)=>s+r.unsupportedMakesInStrictlyFeasibleStates,0),unsupportedMakesNeedingSupplyAdjustment:seasons.reduce((s,r)=>s+r.unsupportedMakesNeedingSupplyAdjustment,0)},seasons,
 hashes:{...hashes,[root+'/audit.mjs']:sha(root+'/audit.mjs'),'reports/player-impact-v30/validation-protocol.json':sha('reports/player-impact-v30/validation-protocol.json')}};
fs.writeFileSync(file,JSON.stringify(out,null,2));console.log(JSON.stringify(out.totals));

// When supported-self and old residual-self are equal, changing the transport
// adapter must leave every game and personal counter exactly unchanged.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {ovrInput} from '../player-impact-v30/ovr-input.mjs';
import {impactEngine as previousEngine} from '../player-impact-v30/engine.mjs';
import {impactEngine} from './engine.mjs';
import {source,workloadTeam,opponentTeam,options} from '../player-impact-v29/benchmark.mjs';
process.on('uncaughtException',e=>{console.error(e.stack.split('\n').filter(s=>!s.includes('data:text/javascript;base64')).join('\n'));process.exitCode=1;});
const x=structuredClone(await ovrInput()),cap=source().capMinutes;
for(const p of [...x.profiles,...x.opponents.flatMap(t=>t.roster)]){
 const m=p.opportunityMeasurement;
 p.opportunityMeasurement={...m,terminalOpportunityRate:1,receiveOpportunityRate:.8,selfOpportunityRate:.2,passOpportunityRate:.8,passStolenPerMinute:.02};
}
const old=await previousEngine('rotation-space',{game:true}),next=await impactEngine('rotation-space',{game:true});
let games=0;
for(let i=0;i<24;i++){
 const slot=i%5,phase=i%2,a=workloadTeam(x,x.profiles[slot],slot,cap,cap,phase),b=opponentTeam(x,x.opponents[i%30],cap,phase);
 const o=options(x,20261020+i,[a.schedule,b.schedule]);
 const g=old(a.team,b.team,o),h=next(a.team,b.team,o);
 for(const k of ['scoreA','scoreB','gameSeconds','complete','statA','statB','playersA','playersB'])assert.deepEqual(h[k],g[k],k);
 games+=2;
}
const root='reports/player-impact-v37',files=[root+'/model.mjs',root+'/engine.mjs',root+'/verify-equivalence.mjs'];
fs.writeFileSync(root+'/equivalence-verification.json',JSON.stringify({passed:true,games,comparisons:24,allGameAndPersonalCountersExactlyV30:true,
 scope:'Controlled symmetric self/pass roles give already feasible joint prior: own0.2, pass0.8, terminal1. Both new own-pool and old residual transport identical; original distinct shooting skills remain. Not unchanged behavior for actual inputs or a missing-data fallback.',
 hashes:Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]))},null,2));
console.log(JSON.stringify({passed:true,games,allGameAndPersonalCountersExactlyV30:true}));

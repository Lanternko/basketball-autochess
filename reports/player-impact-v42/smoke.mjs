import fs from 'node:fs';
import assert from 'node:assert/strict';
import {loadInput} from './input.mjs';
import {impactEngine} from './engine.mjs';
import {exposureDefenseProbabilities as candidate} from './model.mjs';
import {exposureDefenseProbabilities as previous} from '../player-impact-v41/model.mjs';
import {measuredContext} from '../../src/measured_creation_context.js';
import * as M from '../../src/probability_model.js';
const b=loadInput('2025-26'),run=await impactEngine('rotation-space',{game:true});let probabilityChecks=0,gameChecks=0;
for(let i=0;i<30;i+=3){
 const a=b.league.teams[i],d=b.league.teams[(i+1)%30],os=a.roster.slice(0,5),ds=d.roster.slice(0,5),ctx=measuredContext(os,0),opts={...b.options,contextLongScale:1,assist:null};
 const args=[os[0],ctx,ds[0],M.helpDefense(ds),70,70,M.teamPhysique(ds),opts,ds];
 const p=candidate(...args),q=previous(...args);assert.deepEqual(p.make,q.make);assert.equal(p.pTovTouch,q.pTovTouch);assert.equal(p.pFoul,q.pFoul);
 args[7]={...opts,putback:true};assert.deepEqual(candidate(...args),previous(...args));probabilityChecks++;
 const r=run(a,d,{...opts,seed:20261012+i,creationPolicy:'rotation-space',spaceCenter:JSON.parse(fs.readFileSync('reports/player-impact-v7/2025-26-center.json')).fullCenter});
 assert.ok(r.complete);assert.equal(r.scoreA,r.statA.pts);assert.equal(r.scoreB,r.statB.pts);
 for(const side of ['A','B']){const s=r['stat'+side];assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);assert.equal(s.fga,s.fg3a+s.mida+s.rima);}
 gameChecks++;
}
fs.writeFileSync('reports/player-impact-v42/smoke-verification.json',JSON.stringify({passed:true,probabilityChecks,gameChecks,makeDefenseAndTurnoversUnchangedBeforeRecentering:true,putbackDefenseExact:true,gameScoreAndZoneAccountingPassed:true},null,2));console.log(JSON.stringify({passed:true,probabilityChecks,gameChecks}));

import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {fourthProbability} from '../../src/defense_fourth_effects.js';
const b=JSON.parse(fs.readFileSync('reports/defense-tenth/step4-t0/2025-26/bundle.json'));
const cal=JSON.parse(fs.readFileSync('reports/defense-tenth/step4-rebounds-oreb/2025-26/calibration-oreb.json')).selected;
const opt={...b.options,...cal.options,neutralContests:false,rimSignal:false,zoneSignal:false};delete opt.defenseSignals;
const attrs=['long','mid','short','drive','tovSkill','pass','ft','rebound','onBall','help','stamina','physique','offBall','screen','handle','breakDbl'];
const neutral=pos=>({pos,...Object.fromEntries(attrs.map(k=>[k,70])),shotProfile:{threeRate:pos==='C'?.05:.4,freeThrowsPerAttempt:.25}});
const base=['PG','SG','SF','PF','C'].map(neutral),def=base.map(p=>structuredClone(p));
const cells=[];
for(const variable of ['long','offBall','pass'])for(const value of [40,70,100])for(const shooter of [1,4]){
  const ls=structuredClone(base);ls[0][variable]=value;
  const ctx=M.teammateContext(ls,shooter);
  const p=fourthProbability(ls[shooter],ctx,def[shooter],M.helpDefense(def),70,70,M.teamPhysique(def),
    {assist:70,forced:false,putback:false,contextScale:opt.contextScale,turnoverScale:opt.turnoverScale,turnoverMode:opt.turnoverMode,pressureAttribute:70,contextLongScale:opt.contextLongScale,contextShortScale:opt.contextShortScale},def,opt);
  cells.push({variable,value,shooter:ls[shooter].pos,context:ctx,make:p.make,zone:p.zone,ev:p.ev});
}
const low=cells.find(x=>x.variable==='long'&&x.value===40&&x.shooter==='SG'),high=cells.find(x=>x.variable==='long'&&x.value===100&&x.shooter==='SG');
assert.equal(opt.contextLongScale,0);assert.equal(low.make.long,high.make.long);
assert.notEqual(high.zone.long,low.zone.long);
const cl=cells.find(x=>x.variable==='long'&&x.value===40&&x.shooter==='C'),ch=cells.find(x=>x.variable==='long'&&x.value===100&&x.shooter==='C');
assert(ch.make.short>cl.make.short);
const result={model:'pure-oreb-turnover-time-1',method:'Deterministic probability-path isolation: change only PG teammate attribute, same SG or sole C shooter, same defense and shot state. These are mechanism responses, not real-world causal effects or simulated per-game results.',contextLongScale:opt.contextLongScale,contextShortScale:opt.contextShortScale,unmeasured:'No independent speed attribute; offBall/screen/handle/breakDbl fixed70 on actual player cards. Synthetic offBall sweep tests wiring only.',checks:{noDirectTeammateThreeAccuracyEffect:true,threeShotAvailabilityResponds:true,soleCenterRimAccuracyResponds:true},cells};
fs.writeFileSync('reports/player-box-audit/spacing-check.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({checks:result.checks,threeMake:[low.make.long,high.make.long],threeShare:[low.zone.long,high.zone.long],soleCenterShortMake:[cl.make.short,ch.make.short]},null,2));

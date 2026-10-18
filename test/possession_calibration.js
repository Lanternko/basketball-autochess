import assert from 'node:assert/strict';
import {BASELINE,TEAMS} from '../src/teams.js';
import * as M from '../src/probability_model.js';
import {simulateGame,teamRebound} from '../src/simulation_engine.js';
const roster=BASELINE.roster;
const ctx={...M.teammateContext(roster,0),defensiveDoubleRate:.3};
const distribution=p=>M.possessionProbabilities(p,ctx,roster[0],70,70,70,70,{consistentTouch:true});
const good=distribution({...roster[0],breakDbl:99,pass:99});
const bad=distribution({...roster[0],breakDbl:40,pass:40});
assert.ok(bad.pTovTouch>good.pTovTouch);
for(const p of [good,bad]) {
 assert.equal(p.TOV,p.pTovTouch);
 assert.ok(Math.abs(['TOV','FOUL','FG3M','FG3X','MIDM','MIDX','RIMM','RIMX'].reduce((s,k)=>s+p[k],0)-1)<1e-12);
 assert.equal(p.ftPct,distribution(roster[0]).ftPct);
 const shootingEv=3*p.zone.long*p.make.long+2*p.zone.mid*p.make.mid+2*p.zone.short*p.make.short;
 assert.ok(Math.abs(p.ev-((1-p.pTovTouch-p.pFoul)*shootingEv+2*p.pFoul*p.ftPct))<1e-12);
}
assert.equal(M.doubleRate({...roster[0],long:150},ctx),.3);
const options={mode:'fixed',possessions:80,fatigue:false,seed:1845,possessionModel:'stable'};
const a=simulateGame(TEAMS.CLE,BASELINE,options);
assert.deepEqual(a,simulateGame(TEAMS.CLE,BASELINE,options));
for(const side of ['A','B']){
 const rows=a['players'+side],s=a['stat'+side];
 for(const k of ['pts','fga','fta','tov','oreb','dreb','blk'])assert.equal(rows.reduce((n,p)=>n+p[k],0),s[k]);
 assert.equal(s.pts,3*s.fg3m+2*(s.midm+s.rimm)+s.ftm);
 assert.ok(Math.abs(rows.reduce((n,p)=>n+p.usagePct,0)-100)<1e-10);
}
assert.throws(()=>simulateGame(BASELINE,BASELINE,{possessionModel:'typo'}));
assert.throws(()=>simulateGame(BASELINE,BASELINE,{rollAccess:NaN}));
assert.throws(()=>simulateGame(BASELINE,BASELINE,{mode:'timed',possessionModel:'stable'}));
const receivers=[...roster].map(p=>({...p}));
receivers[1]={...receivers[1],screen:99,offBall:40,physique:99};
const before=M.receiverWeights([1,1,1,1,1],receivers,0);
const after=M.receiverWeights([1,1,1,1,1],receivers,0,.75);
assert.ok(after[1]>before[1]);
assert.equal(after[0],0);
assert.ok(Math.abs(after.reduce((a,b)=>a+b,0)-1)<1e-12);
assert.ok(M.receiverWeights([1,1.1,1,1,1],roster,0)[1]>M.receiverWeights([1,1,1,1,1],roster,0)[1]);
console.log('PASS stable defense commitment, pressure handling, EV/event consistency, FT invariance, seeded accounting');

// node reports/player-impact-v53/test.mjs
import assert from 'node:assert/strict';
import {deadBallMultiplier, withDeadBallPressure, applyPressure, BASE_NON_STEAL_PER_100} from './pressure.mjs';
const close = (a, b, e = 1e-12) => assert.ok(Math.abs(a - b) < e, `${a} != ${b}`);
// A terminal probability built the v28 way.
function terminal() {
  const q = {pTovTouch: 0.12, measuredTouchLiveShare: 0.55, ftPct: 0.78, zone: {long: 0.4, mid: 0.12, short: 0.48}, make: {long: 0.36, mid: 0.42, short: 0.62}};
  q.TOV = q.pTovTouch; q.pFoul = q.FOUL = 0.08;
  const shot = 1 - q.pTovTouch - q.pFoul;
  for (const [z, m, x] of [['long', 'FG3M', 'FG3X'], ['mid', 'MIDM', 'MIDX'], ['short', 'RIMM', 'RIMX']]) { q[m] = shot * q.zone[z] * q.make[z]; q[x] = shot * q.zone[z] * (1 - q.make[z]); }
  q.ev = q.FG3M * 3 + (q.MIDM + q.RIMM) * 2 + q.pFoul * 2 * q.ftPct;
  return q;
}
const five = c => Array.from({length: 5}, (_, i) => ({name: 'd' + i, pressureMeasurement: c === null ? undefined : {tovNonSteal: c}}));
// Off: no measurement, or a zero sum, leaves the probability object untouched (exact v47).
assert.equal(deadBallMultiplier(five(null)), 1);
const q = terminal();
assert.equal(withDeadBallPressure(q, five(null)), q);
assert.equal(withDeadBallPressure(q, five(0)), q);
// On: +1 per defender -> multiplier (6.79 + 5) / 6.79 on the dead-ball part only.
const m = (BASE_NON_STEAL_PER_100 + 5) / BASE_NON_STEAL_PER_100;
close(deadBallMultiplier(five(1)), m);
const r = withDeadBallPressure(q, five(1));
close(r.pTovTouch * r.measuredTouchLiveShare, q.pTovTouch * q.measuredTouchLiveShare);  // steals unchanged
close(r.pTovTouch * (1 - r.measuredTouchLiveShare), q.pTovTouch * (1 - q.measuredTouchLiveShare) * m);
close(r.pFoul / (1 - r.pTovTouch), q.pFoul / (1 - q.pTovTouch));  // conditional foul kept
close(r.pTovTouch + r.pFoul + r.FG3M + r.FG3X + r.MIDM + r.MIDX + r.RIMM + r.RIMX, 1);
assert.ok(r.ev < q.ev, 'more turnovers lower expected points');
assert.equal(q.pTovTouch, 0.12, 'input not mutated');
// Bounds.
close(deadBallMultiplier(five(-10)), 0.5); close(deadBallMultiplier(five(10)), 2);
// Input side: actual players once, profiles get the confident pool's minute-weighted mean, spread scales every zone.
const md = () => ({makeDefender: {ra: 0.02, paint: -0.01, mid: 0, corner: 0, arc: 0.004}});
const pl = (id, MIN, slot) => ({playerId: id, name: 'p' + id, observed: {MIN}, fineDefenseMeasurement: md(), slot});
const players = [pl(1, 2000, 0), pl(2, 1000, 0), pl(3, 500, 1)];
const x = {players, opponents: [{roster: [players[0], pl(9, 100, 0)]}], profiles: [{fineDefenseMeasurement: md()}, {fineDefenseMeasurement: md()}],
  roleMap: new Map(players.map(p => [p.playerId, {slot: p.slot, lowConfidence: false}]))};
applyPressure(x, new Map([[1, {tovNonSteal: 1.5}], [2, {tovNonSteal: -0.6}]]), 2);
assert.equal(x.players[0].pressureMeasurement.tovNonSteal, 1.5);
assert.equal(x.players[2].pressureMeasurement, undefined, 'unmeasured player stays neutral');
close(x.profiles[0].pressureMeasurement.tovNonSteal, (2000 * 1.5 + 1000 * -0.6) / 3000);
close(x.profiles[1].pressureMeasurement.tovNonSteal, 0);
close(x.players[0].fineDefenseMeasurement.makeDefender.ra, 0.04);  // shared object scaled once
close(x.opponents[0].roster[1].fineDefenseMeasurement.makeDefender.arc, 0.008);
close(x.profiles[1].fineDefenseMeasurement.makeDefender.paint, -0.02);
// Scale 1 and no coefficients: untouched.
const y = {players: [pl(4, 900, 0)], opponents: [], profiles: [{fineDefenseMeasurement: md()}], roleMap: new Map([[4, {slot: 0, lowConfidence: false}]])};
const before = structuredClone(y); applyPressure(y, new Map(), 1); assert.deepEqual(y, before);
console.log('v53 pressure tests pass');

// v53 defensive pressure: two channels measured by four-factor RAPM
// (reports/impact-rapm/four-factors-report.md, split-half reliability 0.61 for both).
//
// 1. Non-steal turnovers forced. v28+ terminal risk scales only the live (steal) part with the
//    defense's steal pressure; the dead-ball part depends on the ball handler alone. Each
//    defender's tovNonSteal coefficient (extra non-steal turnovers per 100 possessions) is
//    added to the league rate and the dead-ball part is multiplied by
//    (BASE + sum of the five) / BASE, bounded to [0.5, 2].
// 2. Shot-making suppression spread. v45 per-defender make logits are strongly shrunk (on-court
//    opponent FG% spread is compressed in the simulator). Every makeDefender is multiplied by
//    one scale chosen by calibrate-spread.mjs from the four-factor eFG coefficients.
//
// Both channels are off (exact v47) when no player carries pressureMeasurement and scale = 1.
export const BASE_NON_STEAL_PER_100 = 6.79;  // four-factor tovNonSteal intercept, 2022-26
export const MULTIPLIER_BOUNDS = [0.5, 2];
const FT_ATTEMPTS = 2;  // src/constants.js FT_ATTEMPTS

export function deadBallMultiplier(lineup) {
  let sum = 0, any = false;
  for (const d of lineup) {
    const c = d.pressureMeasurement?.tovNonSteal;
    if (c === undefined) continue;
    if (!Number.isFinite(c)) throw Error('Invalid tovNonSteal for ' + d.name);
    sum += c; any = true;
  }
  if (!any) return 1;
  const m = (BASE_NON_STEAL_PER_100 + sum) / BASE_NON_STEAL_PER_100;
  return Math.max(MULTIPLIER_BOUNDS[0], Math.min(MULTIPLIER_BOUNDS[1], m));
}

// Same recomputation as reports/player-impact-v28/model.mjs terminalDefenseProbabilities:
// keep the conditional foul rate, rebuild shot outcomes and EV from the new touch risk.
export function withDeadBallPressure(q, lineup) {
  const m = deadBallMultiplier(lineup);
  if (m === 1 || !Number.isFinite(q.pTovTouch) || !Number.isFinite(q.measuredTouchLiveShare)) return q;
  const live = q.pTovTouch * q.measuredTouchLiveShare, dead = q.pTovTouch * (1 - q.measuredTouchLiveShare) * m;
  const total = Math.min(0.95, live + dead);
  const conditionalFoul = q.pFoul / (1 - q.pTovTouch);
  const r = {...q, pTovTouch: total, TOV: total, measuredTouchLiveShare: total > 0 ? live / total : 0};
  r.pFoul = r.FOUL = (1 - total) * conditionalFoul;
  const shot = 1 - r.pTovTouch - r.pFoul;
  for (const [z, made, missed] of [['long', 'FG3M', 'FG3X'], ['mid', 'MIDM', 'MIDX'], ['short', 'RIMM', 'RIMX']]) {
    r[made] = shot * q.zone[z] * q.make[z]; r[missed] = shot * q.zone[z] * (1 - q.make[z]);
  }
  r.ev = r.FG3M * 3 + (r.MIDM + r.RIMM) * 2 + r.pFoul * FT_ATTEMPTS * r.ftPct;
  return r;
}

// Input side. coefficients: Map playerId -> {tovNonSteal}. Synthetic positional teammates get
// the confident natural-position pool's source-minute weighted mean (the v47 profile rule).
export function applyPressure(x, coefficients, spreadScale = 1) {
  if (!(spreadScale > 0)) throw Error('Invalid spread scale');
  const seen = new Set(), actual = [...x.players, ...x.opponents.flatMap(t => t.roster)];
  for (const p of actual) {
    if (seen.has(p)) continue;
    seen.add(p);
    const c = coefficients.get(p.playerId);
    if (c) p.pressureMeasurement = {tovNonSteal: c.tovNonSteal};
    if (spreadScale !== 1) scaleMakeDefender(p, spreadScale);
  }
  for (let slot = 0; slot < x.profiles.length; slot++) {
    const pool = x.players.filter(q => x.roleMap.get(q.playerId).slot === slot && !x.roleMap.get(q.playerId).lowConfidence);
    const total = pool.reduce((s, q) => s + q.observed.MIN, 0);
    const prof = x.profiles[slot];
    if (coefficients.size) prof.pressureMeasurement = {tovNonSteal: pool.reduce((s, q) => s + q.observed.MIN * (q.pressureMeasurement?.tovNonSteal ?? 0), 0) / total};
    if (spreadScale !== 1) scaleMakeDefender(prof, spreadScale);
  }
  return x;
}
function scaleMakeDefender(p, s) {
  const m = p.fineDefenseMeasurement;
  if (!m?.makeDefender) throw Error('Missing fine defense for ' + p.name);
  p.fineDefenseMeasurement = {...m, makeDefender: Object.fromEntries(Object.entries(m.makeDefender).map(([z, v]) => [z, v * s]))};
}

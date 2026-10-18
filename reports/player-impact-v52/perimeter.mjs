// v52: perimeter (three-point) defense from the onBall attribute.
// v45 fine make model: logit(make, zone) = shooter + sum of the five defenders' makeDefender[zone].
// Its three-point zones carry no defender feature (corner sigma 0, arc 0.025 without feature), and
// v20+ neutralises the matched defender's onBall to 70, so perimeter defense is worth zero in the
// simulator. Pooled 2022-26 RAPM defense still rewards onBall after controlling for steals,
// help, blocks, defensive rebounds and height: +0.24 per SD (bootstrap SE 0.10, 261 players),
// i.e. about 0.37 points per 100 possessions per +10 onBall. Read entirely as opponent 3P%,
// that is 0.37 / (38 3PA * 3) = 0.32 pp, a logit of 0.0032 / (0.36 * 0.64) = 0.014 per 10
// points: K = 0.0014 per onBall point per defender. Added to corner and arc makeDefender;
// a player at onBall 70 is unchanged.
export const K_DATA = 0.0014;
export const THREE_ZONES = ['corner', 'arc'];
export function perimeterDelta(player, k) {
  if (!Number.isFinite(player.onBall)) throw Error('Missing onBall for ' + player.name);
  return -k * (player.onBall - 70);
}
export function addPerimeterDefense(player, k) {
  const m = player.fineDefenseMeasurement;
  if (!m?.makeDefender) throw Error('Missing fine defense for ' + player.name);
  const d = perimeterDelta(player, k);
  player.fineDefenseMeasurement = {...m, makeDefender: {...m.makeDefender, ...Object.fromEntries(THREE_ZONES.map(z => [z, m.makeDefender[z] + d]))}};
  return d;
}

// Apply to an OVR input. Synthetic positional teammates keep the v47 rule (confident natural-
// position pool, source-minute weighted), so each profile receives its pool's weighted mean delta.
export function applyPerimeter(x, k) {
  if (!(k >= 0)) throw Error('Invalid perimeter coefficient');
  if (k === 0) return x;  // exact v47
  for (let slot = 0; slot < x.profiles.length; slot++) {
    const pool = x.players.filter(q => x.roleMap.get(q.playerId).slot === slot && !x.roleMap.get(q.playerId).lowConfidence);
    const total = pool.reduce((s, q) => s + q.observed.MIN, 0);
    const mean = pool.reduce((s, q) => s + q.observed.MIN * perimeterDelta(q, k), 0) / total;
    const m = x.profiles[slot].fineDefenseMeasurement;
    m.makeDefender = {...m.makeDefender, ...Object.fromEntries(THREE_ZONES.map(z => [z, m.makeDefender[z] + mean]))};
  }
  const seen = new Set();
  for (const p of [...x.players, ...x.opponents.flatMap(t => t.roster)]) {
    if (seen.has(p)) continue;
    seen.add(p);
    addPerimeterDefense(p, k);
  }
  return x;
}

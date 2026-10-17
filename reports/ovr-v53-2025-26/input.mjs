// v47 OVR input plus v53 pressure (reports/player-impact-v53/pressure.mjs).
// variant: 'control' (exact v47), 'tov' (dead-ball pressure only), 'spread' (scale only), 'both'.
import fs from 'node:fs';
import {ovrInput as v47Input} from '../ovr-v47-2025-26/input.mjs';
import {applyPressure} from '../player-impact-v53/pressure.mjs';
export function pressureCoefficients() {
  const rows = fs.readFileSync('reports/impact-rapm/four-factors.csv', 'utf8').trim().split('\n');
  const head = rows[0].split(','), id = head.indexOf('playerId'), tov = head.indexOf('tovNonSteal_defense');
  return new Map(rows.slice(1).map(l => l.split(',')).map(r => [Number(r[id]), {tovNonSteal: Number(r[tov])}]));
}
export function spreadScale() {
  const f = 'reports/player-impact-v53/spread.json';
  if (!fs.existsSync(f)) throw Error('Run reports/player-impact-v53/calibrate-spread.mjs first');
  return JSON.parse(fs.readFileSync(f, 'utf8')).scale;
}
export async function ovrInput(variant) {
  const x = await v47Input();
  if (variant === 'control') return x;
  if (!['tov', 'spread', 'both'].includes(variant)) throw Error('Unknown variant ' + variant);
  return applyPressure(x, variant === 'spread' ? new Map() : pressureCoefficients(), variant === 'tov' ? 1 : spreadScale());
}

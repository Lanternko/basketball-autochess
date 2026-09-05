// calibrate.js — PR50 對 PR50 是否收斂到聯盟平均
import { BASELINE } from '../src/teams.js';
import { monteCarlo } from '../src/simulation_engine.js';
import { LEAGUE_TARGETS as T } from '../src/constants.js';

const N = 4000;
const r = monteCarlo(BASELINE, BASELINE, N, { mode: 'fixed', possessions: 24 });
const s = r.statA;
const ppp = r.avgScoreA / (r.avgPossessions / 2);

const rows = [
  ['eFG%', s.efg, T.efg],
  ['三分命中', s.longPct, T.longPct],
  ['中投命中', s.midPct, T.midPct],
  ['近射命中', s.shortPct, T.shortPct],
  ['三分佔比', s.longRate, T.longRate],
  ['中投佔比', s.midRate, T.midRate],
  ['近射佔比', s.shortRate, T.shortRate],
  ['TOV%', s.tovPct, T.tovPct],
  ['每回合得分', ppp, T.ppp],
];

console.log(`\n=== PR50 vs PR50 校準 · n=${N} · 固定 24 回合 ===\n`);
console.log('指標          模擬     目標     誤差');
let worst = 0;
for (const [k, got, want] of rows) {
  const err = (got - want) / want;
  worst = Math.max(worst, Math.abs(err));
  const flag = Math.abs(err) < 0.03 ? 'OK' : Math.abs(err) < 0.08 ? '~ ' : 'XX';
  console.log(`${flag} ${k.padEnd(10)} ${got.toFixed(3).padStart(6)}  ${want.toFixed(3).padStart(6)}  ${(err * 100).toFixed(1).padStart(6)}%`);
}
console.log(`\n最大相對誤差 ${(worst * 100).toFixed(1)}%`);
console.log(`同隊對打勝率 ${((r.winRateA + r.tieRate / 2) * 100).toFixed(1)}%（應接近 50%）`);
console.log(`平均比分 ${r.avgScoreA.toFixed(1)} - ${r.avgScoreB.toFixed(1)}\n`);

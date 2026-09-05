// variance.js — 量測賽制對「實力能不能轉換成勝率」的影響
//
// 這是數值模型 §7 驗證清單第 4 項：
//   讓 A 隊比 B 隊強 X%，在不同賽制下實際勝率是多少？
// 若強隊在短局下勝率太接近 50%，玩家的規劃決策會被雜訊蓋掉。

import { monteCarlo } from '../src/simulation_engine.js';

const N = 4000;

const flat = (v) => ({
  name: `ALL-${v}`,
  roster: Array.from({ length: 5 }, (_, i) => ({
    name: `p${i}`, pos: ['PG', 'SG', 'SF', 'PF', 'C'][i],
    shooting: v, drive: v, rebound: v, onBall: v, help: v,
    stamina: v, physique: v, offBall: v, screen: v,
  })),
});

const MODES = [
  ['先到 21 分',        { mode: 'race', targetScore: 21, winBy: 1 }],
  ['先到 21 需贏 2',    { mode: 'race', targetScore: 21, winBy: 2 }],
  ['固定 20 回合',      { mode: 'fixed', possessions: 20 }],
  ['固定 24 回合',      { mode: 'fixed', possessions: 24 }],
  ['固定 40 回合',      { mode: 'fixed', possessions: 40 }],
  ['固定 100 回合(參照)', { mode: 'fixed', possessions: 100 }],
];

// 先量出各屬性差對應的實力差（每回合得分比）
console.log('\n=== 屬性差 -> 實力差 ===');
const base = monteCarlo(flat(70), flat(70), N, { mode: 'fixed', possessions: 40 });
const basePpp = base.avgScoreA / 40;
const deltas = [3, 5, 8, 12, 20];
const strength = {};
for (const d of deltas) {
  const r = monteCarlo(flat(70 + d), flat(70), N, { mode: 'fixed', possessions: 40 });
  strength[d] = (r.avgScoreA / 40) / (r.avgScoreB / 40);
  console.log(`  +${String(d).padStart(2)} 屬性 -> 每回合得分比 ${strength[d].toFixed(3)}  (${((strength[d] - 1) * 100).toFixed(1)}% 強)`);
}

console.log('\n=== 各賽制下的勝率（含平手折半）===');
const header = ['屬性差'.padEnd(8), ...MODES.map(([n]) => n.padEnd(16))].join('');
console.log(header);
for (const d of deltas) {
  const cells = [`+${d} (${((strength[d] - 1) * 100).toFixed(0)}%)`.padEnd(8)];
  for (const [, opts] of MODES) {
    const r = monteCarlo(flat(70 + d), flat(70), N, opts);
    const wr = r.winRateA + r.tieRate / 2;
    cells.push(`${(wr * 100).toFixed(1)}%`.padEnd(16));
  }
  console.log(cells.join(''));
}

console.log('\n=== 各賽制的分差 SD 與長度 ===');
for (const [name, opts] of MODES) {
  const r = monteCarlo(flat(70), flat(70), N, opts);
  console.log(`  ${name.padEnd(20)} 平均比分 ${r.avgScoreA.toFixed(1)}-${r.avgScoreB.toFixed(1)}  分差SD ${r.marginSd.toFixed(2)}  平均回合 ${r.avgPossessions.toFixed(1)}  平手率 ${(r.tieRate * 100).toFixed(1)}%`);
}
console.log('');

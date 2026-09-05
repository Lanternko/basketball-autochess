// round_robin.js — 五隊循環賽
import { TEAMS, BASELINE } from '../src/teams.js';
import { monteCarlo, simulateGame } from '../src/simulation_engine.js';

const N = 4000;
const OPTS = { mode: 'race', targetScore: 21, winBy: 1 };
const keys = Object.keys(TEAMS);

console.log(`\n=== 五隊循環賽 · 先到 21 分 · 每組合 n=${N} ===\n`);
const table = {};
for (const k of keys) table[k] = { w: 0, l: 0, pf: 0, pa: 0 };

for (let i = 0; i < keys.length; i++) {
  for (let j = i + 1; j < keys.length; j++) {
    const A = TEAMS[keys[i]], B = TEAMS[keys[j]];
    const r = monteCarlo(A, B, N, OPTS);
    const wr = r.winRateA + r.tieRate / 2;
    console.log(`${A.name}  vs  ${B.name}`);
    console.log(`  勝率 ${(wr * 100).toFixed(1)}% - ${((1 - wr) * 100).toFixed(1)}%   平均比分 ${r.avgScoreA.toFixed(1)} - ${r.avgScoreB.toFixed(1)}   分差SD ${r.marginSd.toFixed(2)}   平均回合 ${r.avgPossessions.toFixed(1)}`);
    console.log(`  ${keys[i]}: eFG% ${r.statA.efg.toFixed(3)}  近${r.statA.shortRate.toFixed(2)}/中${r.statA.midRate.toFixed(2)}/遠${r.statA.longRate.toFixed(2)}  TOV% ${r.statA.tovPct.toFixed(3)}\n`);
    table[keys[i]].w += wr; table[keys[i]].l += 1 - wr;
    table[keys[j]].w += 1 - wr; table[keys[j]].l += wr;
    table[keys[i]].pf += r.avgScoreA; table[keys[i]].pa += r.avgScoreB;
    table[keys[j]].pf += r.avgScoreB; table[keys[j]].pa += r.avgScoreA;
  }
}

console.log('=== 對 PR50 基準隊 ===');
for (const k of keys) {
  const r = monteCarlo(TEAMS[k], BASELINE, N, OPTS);
  const wr = r.winRateA + r.tieRate / 2;
  console.log(`  ${TEAMS[k].name.padEnd(14)} 勝率 ${(wr * 100).toFixed(1)}%   ${r.avgScoreA.toFixed(1)} - ${r.avgScoreB.toFixed(1)}   eFG% ${r.statA.efg.toFixed(3)}  近/中/遠 ${r.statA.shortRate.toFixed(2)}/${r.statA.midRate.toFixed(2)}/${r.statA.longRate.toFixed(2)}`);
}

console.log('\n=== 循環賽總表（四場對戰的平均）===');
const sorted = keys.sort((a, b) => table[b].w - table[a].w);
for (const k of sorted) {
  const t = table[k];
  console.log(`  ${TEAMS[k].name.padEnd(14)} 期望勝場 ${t.w.toFixed(2)} / 4   得分 ${(t.pf / 4).toFixed(1)}  失分 ${(t.pa / 4).toFixed(1)}`);
}

console.log('\n=== 單場逐回合樣本（GSW vs OKC, seed 42）===');
const g = simulateGame(TEAMS.GSW, TEAMS.OKC, { ...OPTS, seed: 42 });
const label = { TOV: '失誤', FOUL: '犯規罰球', FG3M: '三分命中', FG3X: '三分不進', MIDM: '中投命中', MIDX: '中投不進', RIMM: '近射命中', RIMX: '近射不進' };
for (const e of g.log.slice(0, 16)) {
  console.log(`  #${String(e.poss).padStart(2)} ${(e.off === 0 ? 'GSW' : 'OKC')}  ${e.handler.padEnd(26)} ${label[e.ev]}`);
}
console.log(`  ... 最終 ${g.scoreA} - ${g.scoreB}（共 ${g.possessions} 回合）\n`);

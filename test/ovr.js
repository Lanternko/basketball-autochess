// ovr.js — 由模擬推出 OVR，而不是手寫線性公式
//
// 作法：把球員放進 PR50 基準陣容取代一名 PR50 球員，對 PR50 基準隊打，
// 量「自隊每回合多得 + 對手每回合少得」。五個槽位各跑一次取平均
// （同槽位對位，所以放哪一格會影響他守誰）。
//
// 這樣做的好處：盯防值 0.240、中投值 0.031 這種權重差異會自動被吃進去，
// 不必手調任何係數。線性 ovr 公式做不到這件事。
//
// 兩隊用同一組 seed（paired comparison），雜訊會大幅抵消。

import { TEAMS, BASELINE } from '../src/teams.js';
import { monteCarlo } from '../src/simulation_engine.js';
import * as C from '../src/constants.js';

const N = 1500;
const OPTS = { mode: 'fixed', possessions: 30, seed: 20260905 };

const swap = (idx, player) => ({
  name: 'probe', season: 's',
  roster: BASELINE.roster.map((p, i) => i === idx ? { ...player, name: p.name } : p),
});

const base = monteCarlo(BASELINE, BASELINE, N, OPTS);
const baseOff = base.avgScoreA / (base.avgPossessions / 2);
const baseDef = base.avgScoreB / (base.avgPossessions / 2);

/** 淨貢獻：每回合。放進五個槽位各跑一次取平均。 */
function netValue(player) {
  let off = 0, def = 0;
  for (let i = 0; i < 5; i++) {
    const r = monteCarlo(swap(i, player), BASELINE, N, OPTS);
    off += r.avgScoreA / (r.avgPossessions / 2) - baseOff;
    def += baseDef - r.avgScoreB / (r.avgPossessions / 2);
  }
  return { off: off / 5, def: def / 5, net: (off + def) / 5 };
}

// --- 把淨貢獻映射到 0-99 的 OVR -----------------------------------------
// PR50 球員淨貢獻 = 0 -> OVR 70（跟屬性尺度同一個錨）
// 尺度用「全屬性 99 的球員」定上界，讓 OVR 99 有明確意義。
const flat = (v) => Object.fromEntries(
  ['long', 'mid', 'short', 'drive', 'tovSkill', 'pass', 'ft',
    'rebound', 'onBall', 'help', 'stamina', 'physique', 'offBall', 'screen']
    .map(k => [k, v]));

const top = netValue(flat(99)).net;
const bot = netValue(flat(40)).net;
// 上下各用一段線性，PR50 錨在 70
const toOvr = (net) => net >= 0
  ? Math.round(70 + 29 * net / top)
  : Math.round(70 - 30 * net / bot);

console.log(`\n=== OVR 逆推 · n=${N} · 固定 30 回合 · 五槽位平均 ===`);
console.log(`基準：PR50 每回合得分 ${baseOff.toFixed(3)}`);
console.log(`尺度：全屬性 99 -> 淨 +${top.toFixed(3)} (OVR 99)   全屬性 40 -> 淨 ${bot.toFixed(3)} (OVR 40)\n`);

const rows = [];
for (const [k, T] of Object.entries(TEAMS)) {
  for (const p of T.roster) {
    const v = netValue(p);
    rows.push({ team: T.name, name: p.name, pos: p.pos, ...v, ovr: toOvr(v.net) });
  }
}
rows.sort((a, b) => b.ovr - a.ovr);

console.log('OVR  球員                      位置  進攻    防守    淨值    隊伍');
for (const r of rows) {
  console.log(`${String(r.ovr).padStart(3)}  ${r.name.padEnd(26)} ${r.pos.padEnd(4)} `
    + `${(r.off >= 0 ? '+' : '') + r.off.toFixed(3)}  ${(r.def >= 0 ? '+' : '') + r.def.toFixed(3)}  `
    + `${(r.net >= 0 ? '+' : '') + r.net.toFixed(3)}  ${r.team}`);
}

// 費用分級：依 OVR 分佈切五段
console.log('\n=== 建議費用分級 ===');
const TIERS = [[5, 88], [4, 82], [3, 76], [2, 70], [1, 0]];
for (const [cost, floor] of TIERS) {
  const g = rows.filter(r => r.ovr >= floor && r.ovr < (TIERS.find(t => t[0] === cost + 1)?.[1] ?? 999));
  if (!g.length) continue;
  console.log(`\n${cost} 費（OVR ≥ ${floor}）  ${g.length} 人`);
  for (const r of g) console.log(`   ${String(r.ovr).padStart(3)}  ${r.name.padEnd(26)} ${r.pos}`);
}
console.log('');

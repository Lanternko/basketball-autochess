// run_tests.js — 驗證清單
import { TEAMS, BASELINE, SMALLBALL, BIGBALL } from '../src/teams.js';
import * as M from '../src/probability_model.js';
import * as C from '../src/constants.js';
import { monteCarlo, simulateGame, teamRebound } from '../src/simulation_engine.js';

let pass = 0, fail = 0;
const ok = (cond, msg) => {
  if (cond) { pass++; console.log(`  PASS  ${msg}`); }
  else { fail++; console.log(`  FAIL  ${msg}`); }
};
const sec = (t) => console.log(`\n[${t}]`);

const flat = (over = {}) => ({
  name: 'T', season: 's',
  roster: Array.from({ length: 5 }, (_, i) => ({
    name: `p${i}`, pos: ['PG', 'SG', 'SF', 'PF', 'C'][i],
    long: 70, mid: 70, short: 70, drive: 70, tovSkill: 70, pass: 70, ft: 70,
    rebound: 70, onBall: 70, help: 70, stamina: 70, physique: 70,
    offBall: 70, screen: 70, ...over,
  })),
});
const OPTS = { mode: 'race', targetScore: 21, winBy: 1 };
const wr = (A, B, n = 3000) => {
  const r = monteCarlo(A, B, n, OPTS);
  return r.winRateA + r.tieRate / 2;
};
const D = BASELINE.roster;
const probeOf = (over) => {
  const L = flat(over).roster;
  return M.possessionProbabilities(
    L[0], M.teammateContext(L, 0), D[0], M.helpDefense(D),
    teamRebound(L), teamRebound(D), 70);
};

// ---------------------------------------------------------------- 1
sec('1  單調性：屬性升高不該讓期望得分下降');
{
  let mono = true, prev = -1;
  for (const v of [30, 45, 60, 70, 85, 99, 120]) {
    const ev = probeOf({ long: v, mid: v, short: v, drive: v, tovSkill: v }).ev;
    if (ev < prev - 1e-9) mono = false;
    prev = ev;
  }
  ok(mono, '全進攻屬性 30->120 期望得分單調不減');

  for (const k of ['long', 'mid', 'short', 'tovSkill', 'ft']) {
    let m = true, p = -1;
    for (const v of [30, 50, 70, 90, 110]) {
      const ev = probeOf({ [k]: v }).ev;
      if (ev < p - 1e-9) m = false;
      p = ev;
    }
    ok(m, `${k} 單獨升高，期望得分單調不減`);
  }
  // 防守屬性升高，進攻方期望得分應下降
  for (const k of ['onBall', 'help']) {
    const lo = flat({ [k]: 40 }).roster, hi = flat({ [k]: 99 }).roster;
    const L = BASELINE.roster;
    const evLo = M.possessionProbabilities(L[0], M.teammateContext(L, 0), lo[0],
      M.helpDefense(lo), teamRebound(L), teamRebound(lo), 70).ev;
    const evHi = M.possessionProbabilities(L[0], M.teammateContext(L, 0), hi[0],
      M.helpDefense(hi), teamRebound(L), teamRebound(hi), 70).ev;
    ok(evHi < evLo, `${k} 40->99 讓對手期望得分下降（${evLo.toFixed(3)} -> ${evHi.toFixed(3)}）`);
  }
  for (const k of ['offBall', 'screen', 'pass']) {
    const lo = probeOf({ [k]: 40 }).ev, hi = probeOf({ [k]: 99 }).ev;
    ok(hi > lo, `隊友 ${k} 40->99 提高持球者期望得分（${lo.toFixed(3)} -> ${hi.toFixed(3)}）`);
  }
}

// ---------------------------------------------------------------- 2
sec('2  極端值：機率必須合法');
{
  let allOk = true;
  const KEYS = ['TOV', 'FOUL', 'FG3M', 'FG3X', 'MIDM', 'MIDX', 'RIMM', 'RIMX'];
  for (const v of [0, 1, 40, 70, 99, 150, 400, 999]) {
    const p = probeOf({ long: v, mid: v, short: v, drive: v, tovSkill: v, physique: v });
    let sum = 0;
    for (const k of KEYS) {
      if (!(p[k] >= 0 && p[k] <= 1) || Number.isNaN(p[k])) allOk = false;
      sum += p[k];
    }
    if (Math.abs(sum - 1) > 1e-9) allOk = false;
  }
  ok(allOk, '屬性 0..999，八個事件機率皆在 [0,1] 且總和為 1');

  let zoneOk = true;
  for (const v of [0, 40, 99, 400]) {
    const p = probeOf({ long: v, mid: v, short: v });
    const s = p.FG3M + p.FG3X + p.MIDM + p.MIDX + p.RIMM + p.RIMX;
    const zl = (p.FG3M + p.FG3X) / s, zm = (p.MIDM + p.MIDX) / s, zs = (p.RIMM + p.RIMX) / s;
    if (zl < C.CLAMP.zoneLong[0] - 1e-6 || zl > C.CLAMP.zoneLong[1] + 1e-6) zoneOk = false;
    if (zm < C.CLAMP.zoneMid[0] - 1e-6 || zm > C.CLAMP.zoneMid[1] + 1e-6) zoneOk = false;
    if (zs < C.CLAMP.zoneShort[0] - 1e-6 || zs > C.CLAMP.zoneShort[1] + 1e-6) zoneOk = false;
  }
  ok(zoneOk, '出手區域佔比永遠落在 NBA 球隊真實範圍內');
}

// ---------------------------------------------------------------- 3
sec('3  錨點插值：在錨點上必須精確');
{
  const chk = (curve, x, y) => Math.abs(M.interpolate(x, curve) - y) < 1e-12;
  ok(C.CURVE_3PT.every(([x, y]) => chk(C.CURVE_3PT, x, y)), '三分曲線每個錨點精確');
  ok(C.CURVE_MID.every(([x, y]) => chk(C.CURVE_MID, x, y)), '中投曲線每個錨點精確');
  ok(C.CURVE_SHORT.every(([x, y]) => chk(C.CURVE_SHORT, x, y)), '近射曲線每個錨點精確');
  ok(Math.abs(M.interpolate(200, C.CURVE_3PT) - M.interpolate(150, C.CURVE_3PT)) < 1e-12,
    'SOFT_CAP 之外不再成長');
}

// ---------------------------------------------------------------- 4
sec('4  PR50 校準：基準隊互打要收斂到聯盟平均');
{
  const r = monteCarlo(BASELINE, BASELINE, 4000, { mode: 'fixed', possessions: 24 });
  const s = r.statA, T = C.LEAGUE_TARGETS;
  const near = (g, w, tol) => Math.abs(g - w) / w < tol;
  ok(near(s.efg, T.efg, 0.03), `eFG% ${s.efg.toFixed(3)} 接近 ${T.efg}`);
  ok(near(s.longPct, T.longPct, 0.04), `三分命中 ${s.longPct.toFixed(3)} 接近 ${T.longPct}`);
  ok(near(s.midPct, T.midPct, 0.04), `中投命中 ${s.midPct.toFixed(3)} 接近 ${T.midPct}`);
  ok(near(s.shortPct, T.shortPct, 0.04), `近射命中 ${s.shortPct.toFixed(3)} 接近 ${T.shortPct}`);
  ok(near(s.longRate, T.longRate, 0.05), `三分佔比 ${s.longRate.toFixed(3)} 接近 ${T.longRate}`);
  ok(near(s.midRate, T.midRate, 0.06), `中投佔比 ${s.midRate.toFixed(3)} 接近 ${T.midRate}`);
  ok(near(s.tovPct, T.tovPct, 0.05), `TOV% ${s.tovPct.toFixed(3)} 接近 ${T.tovPct}`);
  const ppp = r.avgScoreA / (r.avgPossessions / 2);
  ok(near(ppp, T.ppp, 0.04), `每回合得分 ${ppp.toFixed(3)} 接近 ${T.ppp}`);
  const w = r.winRateA + r.tieRate / 2;
  ok(Math.abs(w - 0.5) < 0.02, `同隊對打勝率 ${(w * 100).toFixed(1)}%，無先攻偏差`);
}

// ---------------------------------------------------------------- 5
sec('5  決定性：同 seed 必須完全一致');
{
  const a = simulateGame(TEAMS.GSW, TEAMS.LAL, { ...OPTS, seed: 12345 });
  const b = simulateGame(TEAMS.GSW, TEAMS.LAL, { ...OPTS, seed: 12345 });
  ok(a.scoreA === b.scoreA && a.scoreB === b.scoreB && a.possessions === b.possessions,
    `同 seed 重現（${a.scoreA}-${a.scoreB}）`);
  const c = simulateGame(TEAMS.GSW, TEAMS.LAL, { ...OPTS, seed: 999 });
  ok(!(a.scoreA === c.scoreA && a.scoreB === c.scoreB), '不同 seed 產生不同結果');
}

// ---------------------------------------------------------------- 6
sec('6  球權：出手品質搜尋要落在 NBA 真實範圍');
{
  for (const k of Object.keys(TEAMS)) {
    const counts = new Map(TEAMS[k].roster.map(p => [p.name, 0]));
    let tot = 0;
    for (let i = 0; i < 800; i++) {
      const g = simulateGame(TEAMS[k], BASELINE, { ...OPTS, seed: i * 7919 });
      for (const e of g.log) if (e.off === 0) { counts.set(e.handler, counts.get(e.handler) + 1); tot++; }
    }
    const v = [...counts.values()].map(c => c / tot).sort((a, b) => b - a);
    ok(v[0] <= 0.38 && v[4] >= 0.075,
      `${TEAMS[k].name} 球權 ${(v[0] * 100).toFixed(1)}% ~ ${(v[4] * 100).toFixed(1)}%（上限 38%、下限 7.5%）`);
  }
  // 出手品質搜尋的核心主張：期望得分高的人應該拿到較多球權
  const L = flat().roster.map((p, i) => i === 2 ? { ...p, long: 99, mid: 99, short: 99 } : p);
  const team = { name: 'x', season: 's', roster: L };
  const counts = new Map(L.map(p => [p.name, 0]));
  let tot = 0;
  for (let i = 0; i < 600; i++) {
    const g = simulateGame(team, BASELINE, { ...OPTS, seed: i * 104729 });
    for (const e of g.log) if (e.off === 0) { counts.set(e.handler, counts.get(e.handler) + 1); tot++; }
  }
  const star = counts.get('p2') / tot, other = counts.get('p0') / tot;
  ok(star > other * 1.5, `唯一的強射手拿到 ${(star * 100).toFixed(1)}% 球權 vs 隊友 ${(other * 100).toFixed(1)}%`);
}

// ---------------------------------------------------------------- 7
sec('7  肉體：五小 vs 雙塔的克制關係');
{
  const w1 = wr(SMALLBALL, BIGBALL);
  ok(w1 < 0.45, `五小 vs 雙塔勝率 ${(w1 * 100).toFixed(1)}%（雙塔應占優）`);
  const buffed = { ...SMALLBALL, roster: SMALLBALL.roster.map(p => ({ ...p, physique: 95 })) };
  const w2 = wr(buffed, BIGBALL);
  ok(w2 > w1 + 0.05,
    `同隊只改肉體 42->95：勝率 ${(w1 * 100).toFixed(1)}% -> ${(w2 * 100).toFixed(1)}%`);
  const vsSmall = wr(TEAMS.LAL, SMALLBALL), vsBig = wr(TEAMS.LAL, BIGBALL);
  ok(vsSmall > vsBig + 0.15,
    `湖人(Shaq 肉體 99) 打五小 ${(vsSmall * 100).toFixed(1)}% > 打雙塔 ${(vsBig * 100).toFixed(1)}%`);
  const a = monteCarlo(TEAMS.LAL, SMALLBALL, 3000, OPTS).statA;
  const b = monteCarlo(TEAMS.LAL, BIGBALL, 3000, OPTS).statA;
  ok(a.shortRate > b.shortRate,
    `湖人打五小時近射佔比 ${a.shortRate.toFixed(3)} > 打雙塔 ${b.shortRate.toFixed(3)}（有肉體優勢就往禁區鑽）`);
}

// ---------------------------------------------------------------- 8
sec('8  中投：必須是「被防守逼出來的」才有存在意義');
{
  const mk = (v) => ({
    name: `D${v}`, season: 's',
    roster: Array.from({ length: 5 }, (_, i) => ({
      name: `d${i}`, pos: 'C', long: 70, mid: 70, short: 70, drive: 70, tovSkill: 70,
      pass: 70, ft: 70,
      rebound: 70, onBall: v, help: v, stamina: 70, physique: 70, offBall: 70, screen: 70,
    })),
  });
  const weak = monteCarlo(BASELINE, mk(40), 3000, OPTS).statA;
  const strong = monteCarlo(BASELINE, mk(99), 3000, OPTS).statA;
  ok(strong.midRate > weak.midRate * 2,
    `對強防守中投佔比 ${strong.midRate.toFixed(3)} > 對弱防守 ${weak.midRate.toFixed(3)} 的兩倍`);

  const midTeam = (mid) => ({ name: 'm', season: 's', roster: BASELINE.roster.map(p => ({ ...p, mid })) });
  const ppp = (A, B) => { const r = monteCarlo(A, B, 3000, OPTS); return r.avgScoreA / (r.avgPossessions / 2); };
  const gainWeak = ppp(midTeam(95), mk(40)) - ppp(midTeam(45), mk(40));
  const gainStrong = ppp(midTeam(95), mk(99)) - ppp(midTeam(45), mk(99));
  ok(gainStrong > gainWeak,
    `中投 45->95 的價值：對強防守 +${gainStrong.toFixed(3)} > 對弱防守 +${gainWeak.toFixed(3)}`);
  ok(gainStrong > 0.01, `中投對強防守確實有邊際價值 +${gainStrong.toFixed(3)} 分/回合`);
}

// ---------------------------------------------------------------- 9
sec('9  體力：疲勞只削弱屬性，不直接加減機率');
{
  const p = BASELINE.roster[0];
  const fresh = M.applyStamina(p, 0), tired = M.applyStamina(p, 1);
  ok(fresh.long === p.long && fresh._eff === C.STAMINA_MAX_EFF, '零疲勞時屬性不變');
  ok(tired.ft === p.ft, '疲勞不影響罰球（站定投，不吃體能）');
  ok(Math.abs(tired.long - p.long * C.STAMINA_MIN_EFF) < 1e-9, '滿疲勞時屬性乘上 MIN_EFF');
  ok(tired.rebound === p.rebound && tired.onBall === p.onBall, '疲勞不影響籃板與防守屬性');
  const hi = M.fatigueRate({ stamina: 99 }, 40), lo = M.fatigueRate({ stamina: 40 }, 40);
  ok(hi < lo, `體力 99 的疲勞累積 ${hi.toFixed(3)} < 體力 40 的 ${lo.toFixed(3)}`);
}


// ---------------------------------------------------------------- 10
sec('10 罰球：唯一不受防守影響的得分路徑');
{
  const mkD = (v) => ({
    name: `D${v}`, season: 's',
    roster: Array.from({ length: 5 }, (_, i) => ({
      name: `d${i}`, pos: 'C', long: 70, mid: 70, short: 70, drive: 70, tovSkill: 70,
      pass: 70, ft: 70,
      rebound: 70, onBall: v, help: v, stamina: 70, physique: 70, offBall: 70, screen: 70,
    })),
  });
  const ftTeam = (ft) => ({ name: 'f', season: 's', roster: BASELINE.roster.map(q => ({ ...q, ft })) });
  const pppOf = (A, B) => { const r = monteCarlo(A, B, 3000, OPTS); return r.avgScoreA / (r.avgPossessions / 2); };
  const gWeak = pppOf(ftTeam(95), mkD(40)) - pppOf(ftTeam(45), mkD(40));
  const gStrong = pppOf(ftTeam(95), mkD(99)) - pppOf(ftTeam(45), mkD(99));
  ok(gWeak > 0.02 && gStrong > 0.02,
    `罰球 45->95 有價值（弱防守 +${gWeak.toFixed(3)}、強防守 +${gStrong.toFixed(3)}）`);
  ok(Math.abs(gWeak - gStrong) < 0.025,
    `罰球價值不隨防守強度改變（差 ${Math.abs(gWeak - gStrong).toFixed(3)}）——這正是它的戰術定位`);
  const shaq = TEAMS.LAL.roster.find(q => q.name.includes('Neal'));
  ok(shaq.ft <= 45, `Shaq 罰球 ${shaq.ft}（真實 FT% .555 是 pr 1.0），Hack-a-Shaq 在模型裡成立`);
}

// ---------------------------------------------------------------- 11
sec('11 傳球：必須真的影響得分，不能只是重分配球權');
{
  const passTeam = (v) => ({ name: 'p', season: 's', roster: BASELINE.roster.map(q => ({ ...q, pass: v })) });
  const pppOf = (A, B) => { const r = monteCarlo(A, B, 3000, OPTS); return r.avgScoreA / (r.avgPossessions / 2); };
  const gain = pppOf(passTeam(95), BASELINE) - pppOf(passTeam(45), BASELINE);
  ok(gain > 0.03,
    `全隊傳球 45->95 值 +${gain.toFixed(3)} 分/回合（不可為 0——只重分配球權的屬性等於不存在）`);
  const dg = TEAMS.GSW.roster.find(q => q.name.includes('Draymond'));
  ok(dg.pass > 80 && dg.tovSkill < 60,
    `Draymond 傳球 ${dg.pass} / 失誤 ${dg.tovSkill}——真實 corr(AST%, TOV%) = +0.48，合併會抵消訊號`);
}

console.log(`\n===== ${pass} passed, ${fail} failed =====\n`);
process.exit(fail ? 1 : 0);

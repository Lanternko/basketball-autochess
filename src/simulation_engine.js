// simulation_engine.js — possession loop + Monte Carlo

import { makeRng, pickWeighted } from './rng.js';
import * as M from './probability_model.js';
import * as C from './constants.js';

/**
 * 隊伍籃板加權值：五人籃板的加權平均，偏重最高者。
 * 肉體佔 30% —— 卡位吃身材，這是肉體的次要作用之一。
 */
export function teamRebound(lineup) {
  return C.weightedTop(
    lineup.map(p => p.rebound * (1 - C.PHYS_REB_WEIGHT) + p.physique * C.PHYS_REB_WEIGHT),
    C.COMPOSITE.teamRebound);
}

const EVENTS = ['TOV', 'FOUL', 'FG3M', 'FG3X', 'MIDM', 'MIDX', 'RIMM', 'RIMX'];

/**
 * 跑一場比賽。
 * mode: 'fixed' = 每方固定 possessions 個回合
 *       'race'  = 先到 targetScore 分（需贏 winBy 分）
 */
export function simulateGame(teamA, teamB, opts = {}) {
  const {
    mode = 'fixed', possessions = 20, targetScore = 21, winBy = 1,
    maxPossessions = 200, seed = 1,
  } = opts;
  const rng = makeRng(seed);

  const sides = [teamA, teamB].map(t => ({
    lineup: t.roster,
    ctxs: t.roster.map((_, i) => M.teammateContext(t.roster, i)),
    score: 0, stat: newStat(),
    reb: teamRebound(t.roster),
    phys: M.teamPhysique(t.roster),
  }));
  const help = sides.map(s => M.helpDefense(s.lineup));

  let poss = 0, off = 0;
  const log = [];

  // 一個 possession 在「投進 / 失誤 / 被防守籃板」時結束。
  // 進攻籃板延續同一個 possession，不是新的一次——這是 NBA 的定義，
  // 也讓每回合得分可以直接跟真實的 1.15 比較。
  //
  // 結束條件只在 off === 0 時檢查，確保兩隊回合數永遠相等。
  for (;;) {
    if (off === 0) {
      if (mode === 'fixed' && poss >= possessions * 2) break;
      if (mode === 'race') {
        const a = sides[0].score, b = sides[1].score;
        const done = (a >= targetScore || b >= targetScore) && Math.abs(a - b) >= winBy;
        if (done || poss >= maxPossessions) break;
      }
    }

    const O = sides[off], D = sides[1 - off];
    O.stat.poss++;
    let alive = true, chances = 0;

    while (alive && chances < 6) {
      chances++;

      // 出手品質搜尋：算五個人各自持球的期望得分，再依 softmax 抽。
      const fat = Math.floor(poss / 2);
      const handlers = O.lineup.map(p => M.applyStamina(p, M.fatigueRate(p, fat)));
      const dists = M.evaluateLineup(
        O.lineup, O.ctxs, D.lineup, help[1 - off], O.reb, D.reb, D.phys, handlers);
      const hi = pickWeighted(
        M.usageFromEv(dists.map(d => d.ev), handlers.map(M.creationScore)), rng());
      const p = dists[hi];

      let x = rng(), ev = 'RIMX';
      for (const k of EVENTS) { x -= p[k]; if (x <= 0) { ev = k; break; } }

      if (ev === 'TOV') {
        O.stat.tov++; alive = false;
      } else if (ev === 'FOUL') {
        O.stat.fta += C.FT_ATTEMPTS;
        for (let i = 0; i < C.FT_ATTEMPTS; i++) if (rng() < p.ftPct) { O.score++; O.stat.ftm++; }
        alive = false;
      } else if (ev === 'FG3M') {
        O.score += 3; O.stat.fg3m++; O.stat.fg3a++; O.stat.fga++; alive = false;
      } else if (ev === 'MIDM') {
        O.score += 2; O.stat.midm++; O.stat.mida++; O.stat.fga++; alive = false;
      } else if (ev === 'RIMM') {
        O.score += 2; O.stat.rimm++; O.stat.rima++; O.stat.fga++; alive = false;
      } else {
        if (ev === 'FG3X') O.stat.fg3a++;
        else if (ev === 'MIDX') O.stat.mida++;
        else O.stat.rima++;
        O.stat.fga++;
        if (rng() < p.pOreb) O.stat.oreb++; else alive = false;
      }

      if (log.length < 400) log.push({ poss, off, handler: O.lineup[hi].name, ev });
    }

    poss++;
    off = 1 - off;
  }

  return {
    scoreA: sides[0].score, scoreB: sides[1].score,
    winnerA: sides[0].score > sides[1].score,
    tie: sides[0].score === sides[1].score,
    possessions: poss,
    statA: finalize(sides[0].stat), statB: finalize(sides[1].stat),
    log,
  };
}

function newStat() {
  return {
    poss: 0, fga: 0, fg3a: 0, fg3m: 0, mida: 0, midm: 0, rima: 0, rimm: 0,
    tov: 0, oreb: 0, fta: 0, ftm: 0,
  };
}

function finalize(s) {
  const fgm = s.fg3m + s.midm + s.rimm;
  return {
    ...s,
    efg: s.fga ? (fgm + 0.5 * s.fg3m) / s.fga : 0,
    longPct: s.fg3a ? s.fg3m / s.fg3a : 0,
    midPct: s.mida ? s.midm / s.mida : 0,
    shortPct: s.rima ? s.rimm / s.rima : 0,
    longRate: s.fga ? s.fg3a / s.fga : 0,
    midRate: s.fga ? s.mida / s.fga : 0,
    shortRate: s.fga ? s.rima / s.fga : 0,
    tovPct: s.poss ? s.tov / s.poss : 0,
  };
}

/** Monte Carlo：跑 n 場，回傳勝率與平均統計。 */
export function monteCarlo(teamA, teamB, n = 1000, opts = {}) {
  let wins = 0, ties = 0, sumA = 0, sumB = 0, sumPoss = 0;
  // 統計要先累加次數再算比率。中投一場只有約 3 次出手，若把每場的比率平均，
  // 投 0 次的場次會貢獻 0，把中投命中率壓低約 4 個百分點。
  const CNT = ['poss', 'fga', 'fg3a', 'fg3m', 'mida', 'midm', 'rima', 'rimm', 'tov', 'oreb'];
  const c = Object.fromEntries(CNT.map(k => [k, 0]));
  const margins = [];
  for (let i = 0; i < n; i++) {
    const g = simulateGame(teamA, teamB, { ...opts, seed: (opts.seed ?? 1) + i * 7919 });
    if (g.tie) ties++; else if (g.winnerA) wins++;
    sumA += g.scoreA; sumB += g.scoreB; sumPoss += g.possessions;
    margins.push(g.scoreA - g.scoreB);
    for (const k of CNT) c[k] += g.statA[k];
  }
  const agg = { ...c, ...finalize(c) };
  for (const k of CNT) agg[k] = c[k] / n;
  const mean = margins.reduce((s, x) => s + x, 0) / n;
  const sd = Math.sqrt(margins.reduce((s, x) => s + (x - mean) ** 2, 0) / n);
  return {
    n, winRateA: wins / n, tieRate: ties / n,
    avgScoreA: sumA / n, avgScoreB: sumB / n, avgPossessions: sumPoss / n,
    marginMean: mean, marginSd: sd, statA: agg,
  };
}

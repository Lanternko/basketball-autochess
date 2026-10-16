import { monteCarlo } from './simulation_engine.js';
import { withSeasonStyle } from './season_style.js';
import { BASELINE } from './teams.js';

export function exposure36(pace) {
  if (typeof pace !== 'number' || !Number.isFinite(pace) || pace <= 0) {
    throw new RangeError('pace must be a finite positive number');
  }
  const requestedPossessions = pace * 36 / 48;
  const possessions = Math.round(requestedPossessions);
  if (!Number.isSafeInteger(possessions) || possessions < 1) {
    throw new RangeError('pace must round to at least one safe integer possession');
  }
  return { pace, requestedMinutes: 36, requestedPossessions, possessions,
    equivalentMinutes: possessions * 48 / pace,
    per36Scale: requestedPossessions / possessions };
}

const ratio = (a, b) => b ? a / b : null;
export function referencePer36(player) {
  if (!(player.minutes > 0) || !Number.isFinite(player.minutes)) throw new RangeError('Invalid reference minutes');
  const t = player.totals;
  const result = Object.fromEntries(Object.entries(t).map(([k, v]) => [k.toLowerCase(), v * 36 / player.minutes]));
  return { ...result, fgPct: ratio(t.FGM, t.FGA), threePct: ratio(t.FG3M, t.FG3A),
    twoPct: ratio(t.FGM-t.FG3M, t.FGA-t.FG3A),
    ftPct: ratio(t.FTM, t.FTA), usagePct: player.usagePct,
    minutesPerGame: player.minutes / player.games };
}

export function buildPer36Report(team, reference, { n = 1000, seed = 20260908,
  pace = reference?.pace, opponent = BASELINE, reboundModel = 'opportunity', blocks = true, seasonStyle = false, freeThrowStyle = false, contextScale = 1, turnoverScale = 1, turnoverFloor = 0, leagueReboundShare, possessionModel = 'legacy', rollAccess = 0 } = {}) {
  if (!reference || reference.season !== team.season) throw new Error('Reference season must match simulation team');
  const exposure = exposure36(pace);
  const targets = team.roster.map(p => {
    const match = reference.players.find(r => r.name === p.name);
    if (!match) throw new Error(`Missing season reference: ${p.name}`);
    return referencePer36(match);
  });
  const totalRealUsage = targets.reduce((s, p) => s + p.usagePct, 0);
  const simulationTeam = seasonStyle ? withSeasonStyle(team, reference, {freeThrowStyle}) : team;
  const r = monteCarlo(simulationTeam, opponent, n, { mode: 'fixed',
    possessions: exposure.possessions, fatigue: false, seed, reboundModel, blocks, leagueReboundShare, contextScale, turnoverScale,turnoverFloor, possessionModel, rollAccess });
  const scale = exposure.per36Scale;
  const players = r.playersA.map((p, i) => {
    const real = targets[i];
    const simulated = { ...p };
    for (const k of ['pts', 'reb', 'oreb', 'dreb', 'tov', 'stl', 'blk', 'blka', 'fgm', 'fga',
      'fg3m', 'fg3a', 'midm', 'mida', 'rimm', 'rima', 'fta', 'ftm']) simulated[k] *= scale;
    const ci95 = Object.fromEntries(['pts', 'reb', 'tov', 'blk'].map(k => {
      const se = p.standardError[k];
      return [k, se === null ? null : [simulated[k] - 1.96 * se * scale, simulated[k] + 1.96 * se * scale]];
    }));
    const proxyUsagePct = totalRealUsage > 0 ? 100 * real.usagePct / totalRealUsage : null;
    return { name: p.name, pos: p.pos, simulated, real, ci95,
      normalizedSeasonUsageProxy: proxyUsagePct,
      error: { pts: simulated.pts - real.pts, reb: simulated.reb - real.reb,
        tov: simulated.tov - real.tov, fgPercentagePoints: p.fgPct === null || real.fgPct === null
          ? null : (p.fgPct - real.fgPct) * 100,
        usageProxyPercentagePoints: proxyUsagePct === null ? null : p.usagePct - proxyUsagePct },
      diagnostics: { firstTouchShare: ratio(p.firstTouches, r.statA.firstTouches),
        receptionShare: ratio(p.receptions, r.statA.receptions),
        meanEv: p.meanEv, meanDoubleRate: p.meanDoubleRate,
        interceptedPassRate: ratio(p.interceptedPasses, p.passAttempts) } };
  });
  return { schemaVersion: 2, team: team.name, season: team.season,
    opponent: opponent.name, benchmarkKind: opponent.benchmarkKind ?? 'unspecified', n, seed, fatigue: false, exposure, reboundModel, leagueReboundShare, seasonStyle, freeThrowStyle, contextScale, turnoverScale,
    possessionModel, rollAccess,turnoverFloor, sources: reference.sources,
    calibrationInputs: seasonStyle ? [freeThrowStyle ? 'Same-season FG3A/FGA and FTA/FGA supply tendencies; not independent prediction' : 'Same-season FG3A/FGA supplies shot prior; not independent prediction'] : [],
    coverage: { blocks: blocks ? 'miss-decomposition-v1' : 'disabled', steals: 'pass-interceptions-only',
      rebounds: 'live-field-goal-misses-only',
      teamRebounds: 'League recorded OREB share proxy, adjusted by relative location/role/skill opportunity; FT rebounds omitted',
      defensiveReboundAttribution: reboundModel === 'legacy' ? 'Legacy exponential weights'
        : '30% uniform luck + 70% shot-location opportunity and bounded skill; prototype assumptions',
      usage: 'FGA + 0.44 FTA + TOV share; all five players share exposure',
      referenceUsage: 'Official season USG%; normalized five-player values are a proxy, not lineup ground truth',
      doubleRate: 'Model probability at shot opportunities, not sampled double-team event frequency' },
    teamResult: { pointsPer36: r.avgScoreA * scale, opponentPointsPer36: r.avgScoreB * scale,
      offRtg: r.avgScoreA / exposure.possessions * 100,
      defRtg: r.avgScoreB / exposure.possessions * 100,
      winRate: r.winRateA + r.tieRate / 2,
      truncationsPerGame: r.statA.truncations + r.statB.truncations,
      seasonOffRtg: reference.offRtg, seasonDefRtg: reference.defRtg,
      comparison: 'Fixed five-player lineup vs the explicitly named opponent; not historical full-roster team strength' }, players };
}

const f = (v, digits = 1) => v === null || v === undefined ? '—' : v.toFixed(digits);
const pct = v => v === null || v === undefined ? '—' : `${f(v * 100)}%`;
export function renderPer36Markdown(reports) {
  const out = ['# 36 分鐘等效驗證報表', '',
    '疲勞關閉；現有五人陣容全員同時上場，各節標示對手。舊稱 PR90 的對手是全屬性 94 的極端壓力測試，並非球隊綜合實力 PR90，不可用來校準真實強隊表現。數字是多場平均，不是單場預測。', '',
    '**表格為「模擬 / 同季真實 per-36」**。真實計數以賽季總數 × 36 ÷ 總分鐘換算，命中率以總命中 ÷ 總出手計算。', '',
    'USG 欄的真實值是官方整季 USG%，模擬值是五人同時上場的估計使用份額；兩者不是同一陣容口徑。正規化五人 USG 只作代理校準驗收，不代表真實五人陣容的驗收。', '',
    '抄截目前只含傳球攔截。火鍋 beta 將既有未進球依區域／護框／位置細分，不另扣一次命中率；參數尚未以 tracking 校準。籃板以落點、位置、能力及 30% 運氣分配，不含罰球後籃板。未加入新數值屬性；可用 courtPosition 指定場上位置。', '',
    '信賴區間只反映模擬抽樣誤差，不包含模型偏差。歷史整隊攻防包含替補、不同對手與輪換，只供背景參考。', ''];
  for (const r of reports) {
    const e = r.exposure, t = r.teamResult;
    out.push(`## ${r.team}`, '',
      `對手：${r.opponent} · 籃板模型：${r.reboundModel} · 火鍋：${r.coverage.blocks}`,
      '', `球權模型：${r.possessionModel ?? 'legacy'}；情境 ${r.contextScale}；失誤倍率 ${r.turnoverScale}；失誤底值 ${r.turnoverFloor ?? 0}；順下接球 ${r.rollAccess ?? 0}。`,
      ...(r.seasonStyle ? ['', `同季傾向輸入：三分${r.freeThrowStyle ? "、罰球出手" : ""}；情境倍率 ${r.contextScale}；失誤倍率 ${r.turnoverScale}。這些輸入不是獨立預測。`] : []), '',
      `n=${r.n} · seed=${r.seed} · pace=${f(e.pace, 2)} · 每方 ${e.possessions} 回合（${f(e.equivalentMinutes, 3)} 分鐘等效，再按比例換算到 36 分鐘）`, '',
      `模擬比分 ${f(t.pointsPer36)}–${f(t.opponentPointsPer36)}；對基準隊勝率 ${pct(t.winRate)}；每百回合攻／防 ${f(t.offRtg)}／${f(t.defRtg)}。`, '',
      `真實整隊每百回合攻／防 ${f(t.seasonOffRtg)}／${f(t.seasonDefRtg)}（非同一對戰條件）；每場截斷 ${f(t.truncationsPerGame, 4)} 次。`, '',
      '| 球員 | 得分 | 籃板 | 失誤 | 抄截* | 火鍋 | FG% | USG%† |',
      '|---|---:|---:|---:|---:|---:|---:|---:|');
    for (const p of r.players) {
      const s = p.simulated, a = p.real;
      out.push(`| ${p.name} | ${f(s.pts)} / ${f(a.pts)} | ${f(s.reb)} / ${f(a.reb)} | ${f(s.tov)} / ${f(a.tov)} | ${f(s.stl)} / ${f(a.stl)} | ${r.coverage.blocks==='disabled'?'停用':f(s.blk)} / ${f(a.blk)} | ${pct(s.fgPct)} / ${pct(a.fgPct)} | ${f(s.usagePct)} / ${f(a.usagePct)} |`);
    }
    out.push('', '| 球員 | 得分均值 95% CI | 進攻籃板 模/真 | 防守籃板 模/真 | 二分 模/真 | 三分 模/真 | 罰球 模/真 | 真實 MPG |',
      '|---|---:|---:|---:|---:|---:|---:|---:|');
    for (const p of r.players) {
      const s = p.simulated, a = p.real;
      out.push(`| ${p.name} | ${p.ci95.pts ? p.ci95.pts.map(v => f(v)).join('–') : '—'} | ${f(s.oreb)} / ${f(a.oreb)} | ${f(s.dreb)} / ${f(a.dreb)} | ${pct(s.twoPct)} / ${pct(a.twoPct)} | ${pct(s.threePct)} / ${pct(a.threePct)} | ${pct(s.ftPct)} / ${pct(a.ftPct)} | ${f(a.minutesPerGame)} |`);
    }
    out.push('', '### 球權與包夾診斷', '',
      '| 球員 | 初始持球份額 | 接球份額 | 出手機會平均 EV | 模型包夾率 | 傳球被攔截率 | USG 代理誤差 pp |',
      '|---|---:|---:|---:|---:|---:|---:|');
    for (const p of r.players) {
      const d = p.diagnostics;
      out.push(`| ${p.name} | ${pct(d.firstTouchShare)} | ${pct(d.receptionShare)} | ${f(d.meanEv, 3)} | ${pct(d.meanDoubleRate)} | ${pct(d.interceptedPassRate)} | ${f(p.error.usageProxyPercentagePoints)} |`);
    }
    out.push('', ...Object.entries(r.sources).map(([kind, s]) => `- [NBA ${kind}](${s.url}) · 擷取 ${s.fetchedAt}`), '');
  }
  return out.join('\n');
}

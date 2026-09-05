// probability_model.js — 屬性 -> possession 事件機率
//
// 階層式分解（照 Nine_innings 的作法）：
//   L1  possession 大類：TOV / FOUL / SHOT
//   L2  出手區域 (given SHOT)：三分 / 中投 / 近射
//   L3  命中 (given 區域)
//   L4  未命中 -> 進攻籃板
// 每層 clamp，最後 normalize。
//
// 持球者不是靠靜態 usage 權重抽出來的，而是每次進攻機會比較五個人的期望得分
// （見 evaluateLineup / chooseHandler）——這才是「傳球直到找到夠好的出手點」。

import * as C from './constants.js';

// --- 輔助 ---------------------------------------------------------------

/** 分段線性插值。anchors 為 [[x,y],...]，依 x 遞增。 */
export function interpolate(value, anchors) {
  const v = Math.min(value, C.ATTR_SOFT_CAP);
  if (v <= anchors[0][0]) return anchors[0][1];
  if (v >= anchors[anchors.length - 1][0]) return anchors[anchors.length - 1][1];
  for (let i = 0; i < anchors.length - 1; i++) {
    const [x1, y1] = anchors[i], [x2, y2] = anchors[i + 1];
    if (v >= x1 && v < x2) {
      if (x2 === x1) return y1;
      return y1 + (y2 - y1) * (v - x1) / (x2 - x1);
    }
  }
  return anchors[anchors.length - 1][1];
}

/** 屬性 -> -1..1 的 effectiveness。 */
export function tanhEff(attr, scale = 40, midpoint = C.ATTR_MIDPOINT) {
  if (scale === 0) return 0;
  return Math.tanh((attr - midpoint) / scale);
}

export const clamp = (x, [lo, hi]) => Math.max(lo, Math.min(hi, x));

const logistic = (x) => 1 / (1 + Math.exp(-x));

// --- 隊伍情境（每個陣容算一次）------------------------------------------

/**
 * 場上其他四人提供給持球者的情境。
 * 無球 = 其他四人的無球平均（拉開空間）
 * 擋拆 = 其他四人的擋拆，偏重最高者（掩護通常由一個大個子提供）
 */
export function teammateContext(lineup, handlerIdx) {
  const others = lineup.filter((_, i) => i !== handlerIdx);
  const offBall = others.reduce((s, p) => s + p.offBall, 0) / others.length;
  const screen = C.weightedTop(others.map(p => p.screen), C.COMPOSITE.ctxScreen);
  const pass = C.weightedTop(
    others.map(p => p.pass ?? C.ATTR_MIDPOINT), C.COMPOSITE.ctxPass);
  // 引力取「其他四人裡最強的得分威脅」——不平均。
  // 防守要分心去顧的是那一個人，不會因為另外三個是廢咖就不用顧。
  const gravity = Math.max(...others.map(p =>
    C.GRAVITY_W.long * p.long + C.GRAVITY_W.short * p.short));
  return { offBall, screen, pass, gravity };
}

/**
 * 協防值：對方協防最好的人（加權平均前二，避免單點決定一切），
 * 再加上肉體的次要加成——大個子群本身就墊高護框。
 */
export function helpDefense(defLineup) {
  return C.weightedTop(
    defLineup.map(p => p.help + (p.physique - C.ATTR_MIDPOINT) * C.PHYS_HELP_BONUS),
    C.COMPOSITE.helpDefense);
}

/** 隊伍平均肉體。持球者的禁區優勢跟這個值比，五小陣容因此被大個子克制。 */
export function teamPhysique(lineup) {
  return lineup.reduce((s, p) => s + p.physique, 0) / lineup.length;
}

// --- 主函式 -------------------------------------------------------------

/**
 * 計算一個進攻機會的事件機率分布。
 * @param handler     持球者（屬性已套用體力 effectiveness）
 * @param ctx         teammateContext 的結果
 * @param defender    對位防守者（盯防用他的 onBall）
 * @param help        helpDefense 的結果（數值）
 * @param defTeamPhys 對方隊伍平均肉體
 */
export function possessionProbabilities(
  handler, ctx, defender, help, offTeamReb, defTeamReb, defTeamPhys = C.ATTR_MIDPOINT
) {
  const M = C.ATTR_MIDPOINT;
  // 肉體差：持球者 vs 對方全隊平均。這一項是「五小被大個子克制」的來源。
  const physEdge = tanhEff(M + (handler.physique - defTeamPhys), C.PHYS_SCALE);

  // --- L1: TOV / FOUL / SHOT ---
  let pTov = interpolate(handler.tovSkill ?? M, C.CURVE_TOV);
  pTov *= 1 + tanhEff(defender.onBall, 45) * 0.35;   // 防守壓迫提高失誤
  pTov = clamp(pTov, C.CLAMP.tov);

  let pFoul = C.BASE_FOUL_RATE
    * (1 + tanhEff(handler.drive, C.FOUL_DRIVE_SCALE) * C.FOUL_MAX_IMPACT);
  pFoul = clamp(pFoul, C.CLAMP.foul);

  const pShot = Math.max(0, 1 - pTov - pFoul);

  // --- L3 先算：命中 ---
  // 出手選擇要看期望值，所以命中率必須先算出來。
  // pm 已是「被他防守時對手命中率的絕對增減量」，直接相加，不轉 tanh 乘數。
  const pmLong = interpolate(defender.onBall, C.CURVE_DEF_3PT);
  const pmShort = interpolate(help, C.CURVE_DEF_RIM);
  const pmMid = (pmLong * 0.5 + pmShort * 0.5) * C.DEF_MID_SCALE;

  const passBoost = 1 + tanhEff(ctx.pass, C.PASS_SCALE) * C.PASS_MAX_IMPACT;
  const gravBoost = 1 + tanhEff(ctx.gravity ?? M, C.GRAVITY_SCALE) * C.GRAVITY_MAX_IMPACT;
  let makeLong = interpolate(handler.long, C.CURVE_3PT)
    * (1 + tanhEff(ctx.offBall, C.OFFBALL_SCALE) * C.OFFBALL_MAX_IMPACT)
    * passBoost * gravBoost
    + pmLong;
  makeLong = clamp(makeLong, C.CLAMP.makeLong);

  // 中距離幾乎是純技術：沒有隊友情境加成，肉體也幫不上忙。
  let makeMid = interpolate(handler.mid, C.CURVE_MID) + pmMid;
  makeMid = clamp(makeMid, C.CLAMP.makeMid);

  let makeShort = interpolate(handler.short, C.CURVE_SHORT)
    * (1 + tanhEff(ctx.screen, C.SCREEN_SCALE) * C.SCREEN_MAX_IMPACT)
    * (1 + physEdge * C.PHYS_MAX_IMPACT)
    * passBoost * gravBoost
    + pmShort;
  makeShort = clamp(makeShort, C.CLAMP.makeShort);

  // --- L2: 出手區域 ---
  // 兩個乘數：這球值不值得（ΔEV）× 拿不拿得到（可及性）。
  // 防守否決是中投存在的理由：盯防斷三分、協防斷禁區，兩條都被斷就只剩中距離。
  const denyLong = (defender.onBall - M) * C.DENY_LONG;
  const denyShort = (help - M) * C.DENY_SHORT;

  const aLong = (ctx.offBall - M) * C.Z_OFFBALL_W - denyLong;
  const aMid = (handler.drive - M) * C.Z_DRIVE_MID_W;
  const aShort = (ctx.screen - M) * C.Z_SCREEN_W
    + (ctx.pass - M) * C.Z_PASS_RIM_W
    + (handler.drive - M) * C.Z_DRIVE_RIM_W
    + physEdge * C.PHYS_SHOT_PULL
    - denyShort;

  const wLong = C.LEAGUE_ZONE_SHARE.long
    * Math.exp((3 * makeLong - C.EV_REF.long) / C.EV_TEMP + aLong / C.ZONE_TEMP);
  const wMid = C.LEAGUE_ZONE_SHARE.mid
    * Math.exp((2 * makeMid - C.EV_REF.mid) / C.EV_TEMP + aMid / C.ZONE_TEMP);
  const wShort = C.LEAGUE_ZONE_SHARE.short
    * Math.exp((2 * makeShort - C.EV_REF.short) / C.EV_TEMP + aShort / C.ZONE_TEMP);
  const wSum = wLong + wMid + wShort;
  let zLong = clamp(wLong / wSum, C.CLAMP.zoneLong);
  let zMid = clamp(wMid / wSum, C.CLAMP.zoneMid);
  let zShort = clamp(wShort / wSum, C.CLAMP.zoneShort);
  const zSum = zLong + zMid + zShort;
  zLong /= zSum; zMid /= zSum; zShort /= zSum;

  // --- L4: 進攻籃板 ---
  const bias4 = Math.log(C.LEAGUE_OREB_RATE / (1 - C.LEAGUE_OREB_RATE));
  const pOreb = clamp(
    logistic((offTeamReb - defTeamReb) / C.OREB_TEMP + bias4), C.CLAMP.oreb);

  // --- 攤平成事件分布 ---
  const raw = {
    TOV: pTov,
    FOUL: pFoul,
    FG3M: pShot * zLong * makeLong,
    FG3X: pShot * zLong * (1 - makeLong),
    MIDM: pShot * zMid * makeMid,
    MIDX: pShot * zMid * (1 - makeMid),
    RIMM: pShot * zShort * makeShort,
    RIMX: pShot * zShort * (1 - makeShort),
  };

  let total = 0;
  for (const k in raw) { raw[k] = Math.max(0, raw[k]); total += raw[k]; }
  if (total === 0) {
    return { TOV: 1, FOUL: 0, FG3M: 0, FG3X: 0, MIDM: 0, MIDX: 0, RIMM: 0, RIMX: 0, pOreb, ftPct: C.FT_PCT, ev: 0 };
  }
  const norm = {};
  for (const k in raw) norm[k] = raw[k] / total;
  norm.pOreb = pOreb;
  // 期望得分：出手品質搜尋就是比這個值。
  norm.ftPct = clamp(interpolate(handler.ft ?? C.ATTR_MIDPOINT, C.CURVE_FT), [0.30, 0.98]);
  norm.ev = norm.FG3M * 3 + norm.MIDM * 2 + norm.RIMM * 2
    + norm.FOUL * C.FT_ATTEMPTS * norm.ftPct;
  return norm;
}

// --- 出手品質搜尋 -------------------------------------------------------

/**
 * 算出五個人各自持球的機率分布與期望得分。
 * 一次算五個，選中的那個直接沿用——不會重算。
 */
export function evaluateLineup(lineup, ctxs, defLineup, help, oReb, dReb, dPhys, handlers) {
  return handlers.map((h, i) =>
    possessionProbabilities(h, ctxs[i], defLineup[i], help, oReb, dReb, dPhys));
}

/**
 * 依期望得分 softmax 決定誰出手。
 *
 * 純 argmax 會讓最強的人吃掉全部球權；純 usage 權重又跟出手品質脫鉤。
 * softmax 溫度就是球隊的「球商」：低溫 = 球會流動到最好的位置，
 * 高溫 = 誰拿到球誰投。FLOOR_MIX 保底，讓 usage 落在 NBA 真實範圍
 * （頭號球星 28-35%、第五人 10-14%）。
 */
export function usageFromEv(evs, creations) {
  const scores = evs.map((e, i) =>
    e + C.USAGE_CREATE_W * ((creations[i] - C.ATTR_MIDPOINT) / 100));
  const mx = Math.max(...scores);
  const raw = scores.map(s => Math.exp((s - mx) / C.USAGE_TEMP));
  const tot = raw.reduce((s, x) => s + x, 0);
  const uniform = 1 / scores.length;
  let w = raw.map(x => (1 - C.USAGE_FLOOR_MIX) * (x / tot) + C.USAGE_FLOOR_MIX * uniform);
  // 夾在 NBA 真實範圍後重新正規化（迭代兩次即收斂）
  for (let it = 0; it < 3; it++) {
    w = w.map(x => clamp(x, C.USAGE_CLAMP));
    const s = w.reduce((a, b) => a + b, 0);
    w = w.map(x => x / s);
  }
  return w;
}

/**
 * 創造力：能不能自己製造出手。
 *
 * 偏重跳投（三分與中投），因為那是「自己拔起來就投」的能力；近射權重低——
 * 中鋒的近射 98 多半是接球放進去，那是別人創造的。切入補一點自主進攻。
 * 用「三項最高值」會把吃餅中鋒誤判成創造者。
 */
export function creationScore(p) {
  const w = C.CREATE_W;
  return w.long * p.long + w.mid * p.mid + w.short * p.short
    + w.drive * p.drive + w.pass * (p.pass ?? C.ATTR_MIDPOINT)
    - C.CREATE_OFFBALL_PENALTY * (p.offBall - C.ATTR_MIDPOINT);
}

/** 體力：削弱屬性而非加減機率（照 Nine_innings 的 pitcherEffectiveness）。 */
export function applyStamina(player, fatigue) {
  const eff = C.STAMINA_MAX_EFF
    - (C.STAMINA_MAX_EFF - C.STAMINA_MIN_EFF) * Math.max(0, Math.min(1, fatigue));
  return {
    ...player,
    long: player.long * eff,
    mid: player.mid * eff,
    short: player.short * eff,
    drive: player.drive * eff,
    _eff: eff,
  };
}

/** 一名球員在該 possession 消耗的體力，體力屬性越高消耗越慢。 */
export function fatigueRate(player, possessions) {
  const resist = 0.6 + tanhEff(player.stamina, 45) * 0.4;
  return possessions / (150 * resist);
}

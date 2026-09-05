// constants.js — 錨點表、夾值、校準目標
//
// 所有錨點來自 NBA 真實分布，rotation player 母體（G>=30, MPG>=20），
// 各球員在「自己那個賽季」的母體內取百分位，pr1->40 / pr50->70 / pr99->99。
//
// 出手區域取自 leaguedashplayershotlocations（DistanceRange=By Zone）：
//   近射 = Restricted Area + In The Paint (Non-RA)
//   中投 = Mid-Range
//   三分 = Corner 3 + Above the Break 3

export const ATTR_MIDPOINT = 70;
export const ATTR_SOFT_CAP = 150;

// --- 命中率曲線 ---------------------------------------------------------
// attr 70 錨在 2025-26 的「出手數加權聯盟平均」（不是中位數球員——中位數球員
// 比聯盟平均差，因為好射手出手多）。上下展幅取四個賽季百分位展幅的平均。
//
// 2025-26 聯盟平均：近射 .5782  中投 .4216  三分 .3639
// 四季平均展幅：    近射 -.068/+.088  中投 -.078/+.086  三分 -.065/+.069

export const CURVE_3PT = [
  [0, 0.235], [40, 0.2988], [55, 0.3313], [70, 0.3639],
  [85, 0.3985], [99, 0.4330], [120, 0.460], [150, 0.480],
];
export const CURVE_MID = [
  [0, 0.270], [40, 0.3439], [55, 0.3828], [70, 0.4216],
  [85, 0.4645], [99, 0.5073], [120, 0.540], [150, 0.565],
];
export const CURVE_SHORT = [
  [0, 0.430], [40, 0.5099], [55, 0.5441], [70, 0.5782],
  [85, 0.6223], [99, 0.6664], [120, 0.705], [150, 0.735],
];

// --- 防守：對手命中率的絕對增減量 ---------------------------------------
// leaguedashptdefend 的 PLUSMINUS。分類別的原始展幅（±.19 / ±.21）是樣本
// 雜訊灌水，以 Overall 類別（±.08）反推收縮後使用。
export const CURVE_DEF_3PT = [
  [0, 0.120], [40, 0.085], [55, 0.040], [70, 0.003],
  [85, -0.038], [99, -0.076], [120, -0.100], [150, -0.120],
];
export const CURVE_DEF_RIM = [
  [0, 0.150], [40, 0.105], [55, 0.050], [70, 0.004],
  [85, -0.048], [99, -0.095], [120, -0.125], [150, -0.150],
];
/** 中投由盯防與協防各半負責，但整體效果打折——中距離是最難干擾的一區。 */
export const DEF_MID_SCALE = 0.60;

// --- 失誤 ---------------------------------------------------------------
// tovSkill 由真實 TOV/(FGA+0.44*FTA+TOV) 百分位逆推（越低越好 -> 屬性越高）。
// 曲線是「每次進攻機會」而非每 possession：一個 possession 平均 ~1.18 次機會。
export const CURVE_TOV = [
  [0, 0.239], [40, 0.1826], [55, 0.1429], [70, 0.1032],
  [85, 0.0800], [99, 0.0567], [150, 0.047],
];

// --- 進攻端修正因子（tanh 乘數）-----------------------------------------
export const OFFBALL_SCALE = 40.0;      // 隊友無球 -> 拉開空間 -> 三分命中
export const OFFBALL_MAX_IMPACT = 0.10;
export const SCREEN_SCALE = 40.0;       // 隊友擋拆 -> 切入空間 -> 近射命中
export const SCREEN_MAX_IMPACT = 0.12;
// 隊友傳球 -> 出手品質。接球投的命中率就是比自己運球拔起來高，
// 空切被餵到的球也比自己硬鑽好。這跟無球（拉開空間）是兩件事：
// 無球是「我跑出空檔」，傳球是「有人把球準時送到」。
export const PASS_SCALE = 40.0;
export const PASS_MAX_IMPACT = 0.08;
// 引力：身邊有超級得分手，防守必須分心，隊友的出手就變好。
//
// 這是進攻端唯一能「全隊放大」的機制，補的是一個結構不對稱：
// 護框（協防）用 top-2 合成，一個人就能改善對手全部五個回合；
// 而無球是「其他四人平均」，一個超級得分手會被四個隊友稀釋。
// 沒有引力的話，模型會系統性低估後衛——實測 Curry 的 OVR 會掉到 Tristan Thompson 之下。
export const GRAVITY_SCALE = 40.0;
export const GRAVITY_MAX_IMPACT = 0.075;
export const GRAVITY_W = { long: 0.60, short: 0.40 };
export const Z_PASS_RIM_W = 0.20;       // 好的傳球也讓禁區機會變多
export const PHYS_SCALE = 45.0;         // 肉體差 -> 禁區優勢
export const PHYS_MAX_IMPACT = 0.18;
export const PHYS_SHOT_PULL = 12.0;     // 肉體優勢把出手選擇往禁區拉（分數單位）
export const PHYS_REB_WEIGHT = 0.30;    // 隊伍籃板中肉體的權重
export const PHYS_HELP_BONUS = 0.25;    // 大個子墊高協防

// --- 出手區域選擇 -------------------------------------------------------
// p(zone) ∝ leagueShare(zone) × exp(ΔEV / EV_TEMP + 可及性 / ZONE_TEMP)
//
// 兩個乘數是兩件不同的事：
//   ΔEV    這種出手值不值得（命中率 × 分數，相對 PR50 基準）
//   可及性  拿不拿得到這種出手（無球/擋拆/切入/肉體，減去防守否決）
//
// 只用可及性會讓中投變成死屬性：中投練高只是讓你多投一種期望值較低的球，
// 淨值為零。加進 ΔEV 之後，中投高的人投中投時「每球更值錢」，才有邊際價值。
// PR50 全隊時兩項皆為 0，機率恰好等於聯盟佔比——bias 自動校準，不必手調。
export const LEAGUE_ZONE_SHARE = { short: 0.483, mid: 0.110, long: 0.407 };
export const ZONE_TEMP = 30.0;
export const EV_TEMP = 0.60;
// EV_TEMP 不能再小。混合期望值對某區 EV 的偏導是 w_z × (1 + (ev_z - 混合均值)/T)，
// 當 T 小於「最差區與均值的差距」時會變負——中投練高反而變弱。實測 0.55 是臨界值。
/** PR50 對 PR50 時各區的每次出手期望得分，ΔEV 的基準點。 */
export const EV_REF = { long: 1.1007, mid: 0.8474, short: 1.1644 };

// 防守「否決」：好的盯防讓你投不到三分、好的協防讓你切不進去。
// 兩條路都被斷 -> 只剩中距離。這是中投屬性存在的理由。
export const DENY_LONG = 0.45;
export const DENY_SHORT = 0.55;

// 區域分數中隊友情境與創造力的權重（分數單位，直接加減）
export const Z_OFFBALL_W = 0.35;   // 無球 -> 三分機會
export const Z_SCREEN_W = 0.30;    // 擋拆 -> 禁區機會
export const Z_DRIVE_RIM_W = 0.55; // 切入 -> 禁區機會
export const Z_DRIVE_MID_W = 0.15; // 切入 -> 中距離機會（急停跳投）

// --- 持球者選擇：出手品質搜尋 -------------------------------------------
// 舊版是靜態 usage 權重（(投射+切入)/2 的指數），跟實際出手品質脫鉤。
// 現在每次進攻機會都算五個人的期望得分，再依 softmax 抽。
//
// 純比期望得分會把球權給效率最高的人（通常是吃餅中鋒），而不是給創造力最強的人。
// 真實的 usage 同時吃「效率」與「能不能自己製造出手」，所以加一個創造項：
// 三項投籃的最高值——能自己得分的人才會被交付球權，即使他失誤多。
export const USAGE_TEMP = 0.22;
export const USAGE_CREATE_W = 1.10;
export const USAGE_FLOOR_MIX = 0.10;
/** 創造力的成分權重。傳球（AST%）是分開持球創造者與定點射手的主力訊號。 */
export const CREATE_W = { long: 0.30, mid: 0.20, short: 0.05, drive: 0.15, pass: 0.50 };
/** 球權上下限。NBA 真實範圍：頭號球星 28-35%，第五人 10-14%。 */
export const USAGE_CLAMP = [0.085, 0.345];
/** 無球屬性高 = 接球就投型，球權會被扣；持球創造者的無球通常偏低。 */
export const CREATE_OFFBALL_PENALTY = 0.15;

// --- 犯規與罰球 ---------------------------------------------------------
export const BASE_FOUL_RATE = 0.085;
export const FOUL_DRIVE_SCALE = 60.0;
export const FOUL_MAX_IMPACT = 0.55;
export const FT_ATTEMPTS = 2;
/** 沒有 ft 屬性時的退路（2025-26 聯盟平均）。 */
export const FT_PCT = 0.7935;
// 罰球是唯一不受防守影響的得分路徑——對超強防守陣容的解藥。
// FT% 分布左偏（一長串不會罰球的大個子），所以 40->70 的落差遠大於 70->99。
// 低出手量用 log(FTA) 迴歸當先驗；Shaq 2001-02 的 .555 是 pr 1.0。
export const CURVE_FT = [
  [0, 0.450], [40, 0.560], [55, 0.700], [70, 0.7935],
  [85, 0.850], [99, 0.900], [120, 0.925], [150, 0.940],
];

// --- 進攻籃板 -----------------------------------------------------------
export const LEAGUE_OREB_RATE = 0.28;
export const OREB_TEMP = 26.0;

// --- Composite 權重表 ---------------------------------------------------
// 基礎屬性（上卡面、可被玩家經營）與 composite（引擎實際使用）分成兩層。
// 這個結構抄自 zengm——它的常數不能抄（那是自己隨機生成的球員尺度），
// 但「基礎 -> composite」的分層本身是對的：把散落各處的加權集中成一張表，
// 調參才看得見、才測得動。
//
// 排序型權重：先由高到低排序再套用，所以 [0.6, 0.4] 意思是「最高的算 6 成」。
export const COMPOSITE = {
  /** 隊伍籃板：偏重最高者，肉體佔 PHYS_REB_WEIGHT */
  teamRebound: [0.35, 0.25, 0.18, 0.12, 0.10],
  /** 協防：對方前二名的加權，避免單點決定一切 */
  helpDefense: [0.60, 0.40],
  /** 隊友擋拆：掩護通常由一個大個子提供 */
  ctxScreen: [0.60, 0.40],
  /** 隊友傳球：球隊只需要一個會送球的人 */
  ctxPass: [0.55, 0.45],
};

/** 把排序型權重套到一組值上（不足的權重平均分給其餘）。 */
export function weightedTop(values, weights) {
  const v = [...values].sort((a, b) => b - a);
  if (weights.length >= v.length) {
    return v.reduce((s, x, i) => s + x * (weights[i] ?? 0), 0);
  }
  const head = weights.slice(0, -1).reduce((s, w, i) => s + v[i] * w, 0);
  const restW = weights[weights.length - 1];
  const rest = v.slice(weights.length - 1);
  return head + (rest.reduce((s, x) => s + x, 0) / rest.length) * restW;
}

// --- 體力 ---------------------------------------------------------------
export const STAMINA_MIN_EFF = 0.70;
export const STAMINA_MAX_EFF = 1.00;

// --- 夾值 ---------------------------------------------------------------
export const CLAMP = {
  makeLong: [0.05, 0.62],
  makeMid: [0.10, 0.70],
  makeShort: [0.20, 0.88],
  tov: [0.02, 0.28],
  foul: [0.01, 0.25],
  oreb: [0.05, 0.60],
  // 各區佔比的上下限取自 NBA 球隊真實範圍。沒有任何球隊能把 72% 的出手
  // 塞進禁區——防守會塌陷，而 PR50 防守在模型裡不會自動塌陷，所以要夾。
  zoneShort: [0.30, 0.62],
  zoneMid: [0.02, 0.45],
  zoneLong: [0.15, 0.58],
};

// --- 校準目標（2025-26 聯盟）--------------------------------------------
export const LEAGUE_TARGETS = {
  efg: 0.548,
  tovPct: 0.117,
  longPct: 0.3639,
  midPct: 0.4216,
  shortPct: 0.5782,
  shortRate: 0.483,
  midRate: 0.110,
  longRate: 0.407,
  orebPct: 0.28,
  ppp: 1.15,
};

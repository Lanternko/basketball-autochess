"""賽中防守意識加成（defenseBonus，2026-10-30 使用者）：card 0.2.7 UL6 的 D 改成每天重擬合，窗口跟著本季往後滑。
D＝E-104 L 形逐場線性擬合（reports/card-0.2.5+E104-defense-pergame-decay/e104fit.py，λ = 3000），只換時間軸：
  往年第 k 季（2022-23 = 0 … 2025-26 = 3）的場次位置 t = k·82 + slot + 0.5（slot 同 e104fit.game_u）；
  本季位置 t = 328 + (場次序號 − 0.5)/1230·82（gameId 末五碼就是序號）；
  窗口 = 最近 328 格 [c, 328 + c]，c = 聯盟已賽場數/1230·82；權重 u = (t − c)/328，u ≤ 0（滑出窗口）的 stint 不算。
c = 0 時完全等於 def-L-primary.csv（--check 核對）。本季 stints 由 scripts/build_inseason_stints.js 產生。
用法：python -I defense_bonus.py --check | python -I defense_bonus.py <c> <out.csv>"""
import csv, importlib.util, pickle, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E104 = ROOT / 'reports/card-0.2.5+E104-defense-pergame-decay'
_spec = importlib.util.spec_from_file_location('e104fit', E104 / 'e104fit.py')
F = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(F)
RR, R = F.RR, F.RR.R
PAST = ['2022-23', '2023-24', '2024-25', '2025-26']
SEASON = '2026-27'
SLOTS, WIN, GAMES = 82, 328, 1230
CUR_STINTS = ROOT / f'reports/defense-seventh/{SEASON}/stints/stints.jsonl'
PAST_CACHE = ROOT / 'data/_inseason_build/def-obs-past.pkl'     # 往年 stint 觀測不會變，快取省每天 ~1 分鐘
FROZEN = E104 / 'def-L-primary.csv'


def load_data(with_current=True):
    if PAST_CACHE.exists():
        obs = pickle.load(open(PAST_CACHE, 'rb'))
    else:
        obs = {s: list(R.observations([s])) for s in PAST}
        PAST_CACHE.parent.mkdir(exist_ok=True)
        pickle.dump(obs, open(PAST_CACHE, 'wb'))
    if with_current and CUR_STINTS.exists():
        obs[SEASON] = list(R.observations([SEASON], reader=lambda s: open(CUR_STINTS, encoding='utf-8')))
    D = RR.Data.__new__(RR.Data)               # 同 RR.Data.__init__，只是季別不同
    D.obs = obs
    D.players = sorted({p for s in obs for o in obs[s] for p in o[2] + o[3]})
    D.pidx = {p: i for i, p in enumerate(D.players)}
    D.P = len(D.players); D.K = 2 * D.P
    D.s = {s: D._build(o) for s, o in obs.items()}
    return D


def positions(D):
    us, _ = F.game_u(D, PAST)                  # u = (k·82 + slot + 0.5)/328
    t = {s: us[s] * WIN for s in PAST}
    if SEASON in D.s:
        n = np.array([int(str(g)[-5:]) for g in D.s[SEASON]['gid']], float)
        t[SEASON] = WIN + (n - 0.5) / GAMES * SLOTS
    return t


def fit(D, c, lam=F.LAM):
    """回傳 {playerId: {'D','poss','possW'}}（同 e104fit.fit_w 的 parity=None）。"""
    t = positions(D)
    seasons = list(t)
    wu = {s: np.maximum((t[s] - c) / WIN, 0.0) for s in seasons}
    used = set()
    for s in seasons:
        used.update(np.unique(D.s[s]['X'][wu[s] > 0].indices).tolist())
    used.discard(D.K)
    pl = np.array(sorted({j % D.P for j in used}))
    cols = np.concatenate([pl, D.P + pl, [D.K]])
    n = len(pl)
    A = np.zeros((len(cols), len(cols))); b = np.zeros(len(cols))
    diagW = np.zeros(D.K + 1); diag1 = np.zeros(D.K + 1)
    for s in seasons:
        M, bs = F.weighted_normal(D, s, wu[s])
        A += M[cols][:, cols].toarray(); b += bs[cols]
        diagW += M.diagonal()
        diag1 += F.weighted_normal(D, s, (wu[s] > 0).astype(float))[0].diagonal()
    coef = RR._solve(A, b, lam, 2 * n)
    return {D.players[j]: {'D': float(coef[n + k]), 'poss': float(diag1[j] + diag1[D.P + j]),
                           'possW': float(diagW[j] + diagW[D.P + j])} for k, j in enumerate(pl)}


def write_csv(out, path):
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['playerId', 'name', 'D', 'poss', 'possUnweighted'])
        for pid, v in sorted(out.items(), key=lambda kv: -kv[1]['D']):
            wr.writerow([pid, '', repr(v['D']), repr(v['possW']), repr(v['poss'])])


def check():
    out = fit(load_data(with_current=False), 0.0)
    ref = {int(r['playerId']): r for r in csv.DictReader(open(FROZEN, encoding='utf-8'))}
    assert set(out) == set(ref), (len(out), len(ref))
    dd = max(abs(out[p]['D'] - float(ref[p]['D'])) for p in ref)
    dp = max(abs(out[p]['possW'] - float(ref[p]['poss'])) for p in ref)
    print(f'c=0 對 def-L-primary：{len(ref)} 人，D 最大差 {dd:.2e}，possW 最大差 {dp:.2e}')
    assert dd < 1e-9 and dp < 1e-6


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        check()
    else:
        o = fit(load_data(), float(sys.argv[1]))
        write_csv(o, sys.argv[2])
        print(f'c={float(sys.argv[1]):.2f}：{len(o)} 人 → {sys.argv[2]}')

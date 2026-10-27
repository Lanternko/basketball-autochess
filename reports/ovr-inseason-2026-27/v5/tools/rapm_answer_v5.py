"""v5 §R.3：答案卡 RAPM 季集 = 目標季（含）往前最多四季，最早 2021-22。

  2023-24 答案卡  理想 2020-21..2023-24；本機沒有 2020-21 → 實際 2021-22..2023-24（三季）
  2024-25 答案卡  2021-22..2024-25（四季）

做法：用 v4 的 rapm_v4.build（= tools/rapm_2022_25.py 的 ridge + CV，λ 網格不變）
從本機 stint 重算兩組 RAPM 到暫存目錄，逐位比對 §R.3 指定的現有檔：
  v3/data/rapm-2021-22_2023-24.csv
  v4/data/rapm-2021-22_2024-25.csv
相同才算過；答案卡讀的是 §R.3 指定的現有檔（SHA 寫進 v5/data/rapm-answer-v5.json）。
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V4_TOOLS = HERE.parents[1] / 'v4' / 'tools'
sys.path.insert(0, str(V4_TOOLS))
import v4_common as C  # noqa: E402
import rapm_v4 as RV  # noqa: E402
import rapm_2022_25 as R  # noqa: E402

V5 = C.REPORT / 'v5'
V5_DATA = V5 / 'data'
WANTED = {
    '2023-24': ['2020-21', '2021-22', '2022-23', '2023-24'],
    '2024-25': ['2021-22', '2022-23', '2023-24', '2024-25'],
}
PINNED = {
    '2023-24': C.V3_DATA / 'rapm-2021-22_2023-24.csv',
    '2024-25': C.V4_DATA / 'rapm-2021-22_2024-25.csv',
}


def stint_file(season):
    if season == '2021-22':
        return C.V3_DATA / 'derived-2021-22/stints/stints.jsonl'
    return R.stint_path(season)


def main():
    V5_DATA.mkdir(parents=True, exist_ok=True)
    tmp = V5_DATA / '_rapm_rerun'
    tmp.mkdir(exist_ok=True)
    out = {'spec': 'preregistration-v5 §R.3（答案端：含目標季、最多四季、最早 2021-22）',
           'method': 'v4/tools/rapm_v4.build → tools/rapm_2022_25.py fit_rapm（ridge，CV 選 λ，網格 100..30000）',
           'targets': {}}
    ok = True
    for target, wanted in WANTED.items():
        have = [s for s in wanted if stint_file(s).exists()]
        missing = [s for s in wanted if s not in have]
        tag = f'{have[0]}_{have[-1]}'
        path, meta = RV.build(tag, have, outdir=tmp)
        chk = RV.compare(path, PINNED[target])
        out['targets'][target] = {
            'wantedSeasons': wanted,
            'usedSeasons': have,
            'missingSeasons': missing,
            'missingNote': ('本機無 stint/pbp（preregistration-v5 §4.3、§R.3 D1 列）' if missing else ''),
            'pinnedFile': PINNED[target].relative_to(C.ROOT).as_posix(),
            'pinnedSha256': C.sha256_file(PINNED[target]),
            'rerunSha256': meta['sha256'],
            'rerun': {k: meta[k] for k in ('observations', 'players', 'pooled', 'lastSeason')},
            'rerunVsPinned': chk,
            'stintSha256': {s: C.sha256_file(stint_file(s)) for s in have},
        }
        ok = ok and chk['identical']
    shutil.rmtree(tmp)
    out['pass'] = bool(ok)
    C.write_json(V5_DATA / 'rapm-answer-v5.json', out)
    print(json.dumps({t: {k: v[k] for k in ('usedSeasons', 'missingSeasons', 'pinnedSha256')}
                      | {'identical': v['rerunVsPinned']['identical'],
                         'maxAbsDiff': v['rerunVsPinned']['maxAbsDiff'],
                         'lambda': v['rerun']['pooled']['lambda']}
                      for t, v in out['targets'].items()}, ensure_ascii=False, indent=1))
    return 0 if ok else 3


if __name__ == '__main__':
    raise SystemExit(main())

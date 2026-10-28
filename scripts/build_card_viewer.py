"""2025-26 正式卡名單頁（card 0.2.1）：以正式卡名單頁為版型，換成 card 0.2.1 的 OVR／能力值（OVR 為每場、含上場時間、相對替補水準，R-028；能力值同 0.1.2），3PT 顯示 threeValue（R-024）。

輸入：reports/card-0.2.1/ranking.csv（card 0.2.1）、
      reports/card-0.1.1+E057-three-value/three-value.csv（以姓名對 tv_main）、data/season-source/player-games.json。
版型：reports/ovr-v58-card-2025-26/roster-viewer.html（只讀；team／ht／gp 依姓名取自它）。
輸出：reports/card-0.1.2-2025-26/roster-viewer.html（或 argv[1] 指定路徑）

用法：python -I scripts/build_card_viewer.py [輸出路徑]
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_roster_viewer as er  # noqa: E402
from season_nav import add_season_nav, apply_common  # noqa: E402

ROOT = er.ROOT
BASE = ROOT / 'reports/ovr-v58-card-2025-26/roster-viewer.html'
CARD = ROOT / 'reports/card-0.2.1/ranking.csv'
THREE_VALUE = ROOT / 'reports/card-0.1.1+E057-three-value/three-value.csv'
DEFAULT_OUT = ROOT / 'reports/card-0.1.2-2025-26/roster-viewer.html'


def main(out=None):
    out = Path(out) if out else DEFAULT_OUT
    rows = list(csv.DictReader(CARD.open(encoding='utf-8')))
    tv = {r['name']: float(r['tv_main']) for r in csv.DictReader(THREE_VALUE.open(encoding='utf-8'))}
    base = BASE.read_text(encoding='utf-8')
    old = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', base, re.S).group(1))
    oc = old['cols']
    by_old = {r[oc.index('name')]: r for r in old['rows']}
    # 不在樣板的人：球隊與場數取自 2025-26 player-games.json（球隊＝最後一場）
    rs = json.loads(er.SRC.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(rs['headers'])}
    last_team, gp_src = {}, {}
    for row in sorted(rs['rowSet'], key=lambda r: r[h['GAME_DATE']]):
        last_team[row[h['PLAYER_NAME']]] = row[h['TEAM_ABBREVIATION']]
        gp_src[row[h['PLAYER_NAME']]] = gp_src.get(row[h['PLAYER_NAME']], 0) + 1
    cols = ['rank', 'ovr', 'name', 'pos', 'team', 'ht', 'min', 'gp', 'imp', 'dbon', 'threeValue', 'mid', 'short', 'ft',
            'drive', 'foulDraw', 'pass', 'tovSkill', 'creation', 'rebound', 'physique', 'stamina', 'onBall', 'help', 'pressure']
    data_rows, missing, no_tv = [], [], []
    for r in rows:
        num = lambda k: float(r[k])
        o = by_old.get(r['name'])
        if o:
            team, ht, gp = o[oc.index('team')], o[oc.index('ht')], o[oc.index('gp')]
        else:
            missing.append(r['name'])
            team, ht, gp = last_team.get(r['name'], ''), 0, gp_src.get(r['name'], 0)
        if r['name'] in tv:
            three = round(tv[r['name']], 1)
        else:
            no_tv.append(r['name'])
            three = num('long')
        data_rows.append([int(r['rank']), num('ovr'), r['name'], r['pos'], team, ht, round(num('MIN') / gp, 1) if gp else 0.0, gp,
                          num('predictedPer36'), num('defenseBonus'), three, *[num(a) for a in cols[11:25]]])
    s = base
    s = s.replace('<title>OVR 名單檢視</title>', '<title>2025-26 OVR 名單</title>', 1)
    s = re.sub(r'<div class="src">.*?</div>',
               f'<div class="src">OVR：正式卡 card 0.2.1（2025-26 整季；OVR 為每場，含上場時間，相對替補水準；FD 以量為主）；3PT 顯示 threeValue；{len(rows)} 人</div>',
               s, count=1, flags=re.S)
    new_data = json.dumps({'cols': cols, 'rows': data_rows}, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'const DATA=\{.*?\};\nconst COLS', lambda m: f'const DATA={new_data};\nconst COLS', s, count=1, flags=re.S)
    for a, b in [
        ("['long', '3PT', '三分']", "['threeValue', '3PT', '三分']"),
        ("['drive', 'DRV', '切入']", "['drive', 'DRV', '切入'], ['foulDraw', 'FD', '製造犯規']"),
        ('colspan="22"', 'colspan="23"'),
        # 分鐘改顯示場均（使用者 2026-10-29），篩選門檻改成場均分鐘
        ("th('min', 'MIN', '分鐘', 'gl')", "th('min', 'MPG', '場均分鐘', 'gl')"),
        ("[[0, '全部'], [500, '≥500'], [1000, '≥1000'], [1500, '≥1500']]",
         "[[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']]"),
        ('<td class="sub gl${sc(\'min\')}">${p.min.toLocaleString()}</td>',
         '<td class="sub gl${sc(\'min\')}">${p.min.toFixed(1)}</td>'),
        ('<span>上場 <b>${p.min.toLocaleString()}</b> 分鐘</span>', '<span>場均 <b>${p.min.toFixed(1)}</b> 分鐘</span>'),
        ('OVR 同分多半是 2K27 名次封頂造成的', 'OVR 為每場（含上場時間，相對替補水準）；同分多半是 2K27 名次封頂造成的'),
    ]:
        assert s.count(a) >= 1, a
        s = s.replace(a, b)
    s = apply_common(s)
    s = add_season_nav(s, 'card')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')
    er.inject(out, er.aggregate())
    print('wrote', out, len(rows), 'players; missing from template:', len(missing), missing[:10],
          '; no threeValue:', len(no_tv), no_tv[:10])
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)

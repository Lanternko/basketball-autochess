"""賽中 OVR 名單頁：以正式卡名單頁為版型，換成 inseason 0.1.2（C4，先驗 card 0.1.2）的 OVR、現任球隊與 2026-27 場均真實數據。

輸入：reports/ovr-inseason-2026-27/live/<日期>/{ranking.csv,meta.json}、data/season-source-2026-27/player-games.json。
版型：reports/ovr-v58-card-2025-26/roster-viewer.html（只讀）。
注入隊色／隊徽／頭像／真實數據沿用 scripts/enrich_roster_viewer.py 的函式與樣式（不改該檔，在記憶體裡換資料來源與年份文字）。
輸出：live/<日期>/roster-viewer.html

用法：python -I scripts/build_inseason_viewer.py [日期，預設 2026-10-27]
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
SRC26 = ROOT / 'data/season-source-2026-27/player-games.json'


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else '2026-10-27'
    live = ROOT / 'reports/ovr-inseason-2026-27/live' / day
    meta = json.loads((live / 'meta.json').read_text(encoding='utf-8'))
    rows = list(csv.DictReader((live / 'ranking.csv').open(encoding='utf-8')))
    nopr = len(list(csv.DictReader((live / 'no-prior.csv').open(encoding='utf-8'))))
    cols = ['rank', 'ovr', 'name', 'pos', 'team', 'ht', 'min', 'gp', 'imp', 'dbon', 'threeValue', 'mid', 'short', 'ft',
            'drive', 'foulDraw', 'pass', 'tovSkill', 'creation', 'rebound', 'physique', 'stamina', 'onBall', 'help', 'pressure',
            'last', 'dovr']
    base = BASE.read_text(encoding='utf-8')
    old = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', base, re.S).group(1))
    ht = {r[old['cols'].index('name')]: r[old['cols'].index('ht')] for r in old['rows']}
    data_rows = []
    for r in rows:
        num = lambda k: float(r[k])
        data_rows.append([int(r['rank']), num('ovr'), r['name'], r['pos'], r['team'], ht.get(r['name'], 0),
                          round(num('MIN26') / int(r['N']), 1), int(r['N']), num('predictedPer36'), num('defenseBonus'),
                          *[num(a) for a in cols[10:25]], num('lastOVR'), num('dOVR')])
    s = base
    s = s.replace('<title>OVR 名單檢視</title>', '<title>賽中 OVR 名單</title>', 1)
    s = s.replace('<h1>2025-26 <span>OVR</span> 名單</h1>', '<h1>2026-27 <span>OVR</span> 名單</h1>', 1)
    s = re.sub(r'<div class="src">.*?</div>',
               f'<div class="src">OVR：賽中 C4（{meta["version"]}），先驗 {meta["priorCard"]}；數據截至 {meta["dataCutoff"]}；'
               f'N=已打場數 · {len(rows)} 人（另 {nopr} 人無先驗卡，未列入）· 樣本很小，只看趨勢</div>', s, count=1, flags=re.S)
    new_data = json.dumps({'cols': cols, 'rows': data_rows}, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'const DATA=\{.*?\};\nconst COLS', lambda m: f'const DATA={new_data};\nconst COLS', s, count=1, flags=re.S)
    for a, b in [
        ("['long', '3PT', '三分']", "['threeValue', '3PT', '三分']"),
        ("['drive', 'DRV', '切入']", "['drive', 'DRV', '切入'], ['foulDraw', 'FD', '製造犯規']"),
        ('<th class="g" colspan="2">出場</th>', '<th class="g" colspan="3">出場</th>'),
        ('colspan="22"', 'colspan="25"'),
        ("th('min', 'MIN', '分鐘', 'gl') + th('gp', 'GP', '場數')",
         "th('min', 'MPG', '場均分鐘', 'gl') + th('gp', 'N', '已打場數') + th('dovr', 'ΔOVR', '相對上季卡')"),
        ("[[0, '全部'], [500, '≥500'], [1000, '≥1000'], [1500, '≥1500']]",
         "[[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']]"),
        ('<td class="sub${sc(\'gp\')}">${p.gp}</td>',
         '<td class="sub${sc(\'gp\')}">${p.gp}</td>\n'
         '      <td class="sub${sc(\'dovr\')}">${(v => (v > 0 ? \'+\' : \'\') + v.toFixed(1))(Math.abs(p.dovr) < 0.05 ? 0 : p.dovr)}</td>'),
        ('<td class="sub gl${sc(\'min\')}">${p.min.toLocaleString()}</td>',
         '<td class="sub gl${sc(\'min\')}">${p.min.toFixed(1)}</td>'),
        ('<span>上場 <b>${p.min.toLocaleString()}</b> 分鐘</span><span>出賽 <b>${p.gp}</b> 場</span>',
         '<span>場均 <b>${p.min.toFixed(1)}</b> 分鐘</span><span>已打 N=<b>${p.gp}</b> 場</span>'
         "<span>上季卡 OVR <b>${p.last.toFixed(1)}</b>（<b>${(p.dovr > 0 ? '+' : '') + p.dovr.toFixed(2)}</b>）</span>"),
        ('模擬每 36 分鐘淨值', '賽中預測每 36 分鐘淨值'),
        ('OVR 同分多半是 2K27 名次封頂造成的', 'OVR 同分多半是 2K27 名次封頂造成的 · 本頁 MPG 是 2026-27 場均分鐘'),
    ]:
        assert s.count(a) >= 1, a
        s = s.replace(a, b)
    s = apply_common(s)
    s = add_season_nav(s, 'inseason')
    out = live / 'roster-viewer.html'
    out.write_text(s, encoding='utf-8')
    # 注入隊色／頭像／2026-27 場均（換資料來源與年份文字）
    er.SRC = SRC26
    er.JS = er.JS.replace('2025-26 例行賽真實數據 · 場均', '2026-27 賽季至今真實數據 · 場均').replace(
        '2025-26 例行賽紀錄', '2026-27 賽季紀錄')
    er.inject(out, er.aggregate())
    print('wrote', out, len(rows), 'players')


if __name__ == '__main__':
    main()

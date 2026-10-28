"""把 2025-26 例行賽真實 box score（場均）嵌進名單頁卡片。

資料：data/season-source/player-games.json（stats.nba.com leaguegamelog，每人每場一列）。
依 PLAYER_NAME 跨隊合計；交易球員列出所有球隊。重跑會先移除舊的注入再寫入。

用法：python -I scripts/add_real_stats.py reports/ovr-v58-card-2025-26/roster-viewer.html [...]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'season-source' / 'player-games.json'

CSS = """
/* real box score */
.real{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:4px;margin-top:2px}
.real .st{background:var(--panel-2);border:1px solid var(--line);border-radius:3px;padding:3px 6px;text-align:center}
.real .st b{display:block;font:700 1.15rem var(--f-disp);font-variant-numeric:tabular-nums;color:var(--fg)}
.real .st span{display:block;font-size:.68rem;color:var(--muted)}
.real-h{color:var(--muted);font-size:.72rem;letter-spacing:.08em}
"""

JS = r"""
function realBox(p) {
  const r = REAL[p.name];
  if (!r) return '<div class="real-h">真實數據：找不到這位球員的 2025-26 例行賽紀錄</div>';
  const f1 = v => v.toFixed(1), pc = v => (v == null ? '—' : (v * 100).toFixed(1) + '%');
  const pm = v => (v > 0 ? '+' : '') + v.toFixed(1);
  const s = [['得分', f1(r.pts)], ['籃板', f1(r.reb)], ['助攻', f1(r.ast)], ['抄截', f1(r.stl)], ['阻攻', f1(r.blk)],
    ['失誤', f1(r.tov)], ['命中率', pc(r.fg)], ['三分', pc(r.fg3)], ['罰球', pc(r.ft)], ['真實命中', pc(r.ts)],
    ['分鐘', f1(r.mpg)], ['正負值', pm(r.pm)]];
  return `<div class="real-h">2025-26 例行賽真實數據 · 場均 · ${r.gp} 場${r.teams.length > 1 ? ' · ' + r.teams.join('/') : ''}</div>
      <div class="real">${s.map(([l, v]) => `<div class="st"><b>${v}</b><span>${l}</span></div>`).join('')}</div>`;
}
"""

BEGIN, END = '<!-- real-stats:begin -->', '<!-- real-stats:end -->'


def aggregate():
    rs = json.loads(SRC.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(rs['headers'])}
    acc = {}
    for row in rs['rowSet']:
        name = row[h['PLAYER_NAME']]
        a = acc.setdefault(name, {'gp': 0, 'teams': [], **{k: 0 for k in
            ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'PLUS_MINUS']}})
        a['gp'] += 1
        team = row[h['TEAM_ABBREVIATION']]
        if team not in a['teams']:
            a['teams'].append(team)
        for k in a:
            if k.isupper():
                a[k] += row[h[k]] or 0
    out = {}
    for name, a in acc.items():
        n = a['gp']
        pct = lambda m, t: round(m / t, 4) if t else None
        tsa = 2 * (a['FGA'] + 0.44 * a['FTA'])
        out[name] = {
            'gp': n, 'teams': a['teams'],
            'mpg': round(a['MIN'] / n, 2), 'pts': round(a['PTS'] / n, 2), 'reb': round(a['REB'] / n, 2),
            'ast': round(a['AST'] / n, 2), 'stl': round(a['STL'] / n, 2), 'blk': round(a['BLK'] / n, 2),
            'tov': round(a['TOV'] / n, 2), 'pm': round(a['PLUS_MINUS'] / n, 2),
            'fg': pct(a['FGM'], a['FGA']), 'fg3': pct(a['FG3M'], a['FG3A']), 'ft': pct(a['FTM'], a['FTA']),
            'ts': pct(a['PTS'], tsa),
        }
    return out


def inject(path, real):
    s = path.read_text(encoding='utf-8')
    s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    names = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', s, re.S).group(1))
    col = names['cols'].index('name')
    roster = [r[col] for r in names['rows']]
    sub = {n: real[n] for n in roster if n in real}
    block = (f'{BEGIN}\n<style>{CSS}</style>\n<script>const REAL={json.dumps(sub, ensure_ascii=False, separators=(",", ":"))};'
             f'{JS}</script>\n{END}\n')
    assert s.count('<script>const DATA=') == 1
    s = s.replace('<script>const DATA=', block + '<script>const DATA=', 1)
    hook = '<div class="strong">${tops.map(t => chip(t[0], t[1])).join(\'\')}${chip(\'弱項 \' + low[0], low[1], true)}</div>'
    assert hook in s
    if hook + '\n      ${realBox(p)}' not in s:
        s = s.replace(hook, hook + '\n      ${realBox(p)}', 1)
    path.write_text(s, encoding='utf-8')
    missing = [n for n in roster if n not in real]
    print(f'{path}: {len(sub)}/{len(roster)} 人有真實數據；缺 {len(missing)}: {missing[:10]}')


if __name__ == '__main__':
    real = aggregate()
    for p in sys.argv[1:]:
        inject(Path(p), real)

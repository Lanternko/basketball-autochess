"""名單頁加料：卡片顯示 2025-26 例行賽真實場均、球隊配色、球員頭像；表格球隊欄加色標。

資料：data/season-source/player-games.json（stats.nba.com leaguegamelog，每人每場一列）。
依 PLAYER_NAME 跨隊合計；交易球員列出所有球隊。重跑會先移除舊的注入再寫入。
頭像直接連 NBA CDN（260x190 約 14 KB，只載入被點選的那位），沒網路或沒照片就不顯示。

用法：python -I scripts/enrich_roster_viewer.py reports/ovr-v58-card-2025-26/roster-viewer.html [...]
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
/* team colors + headshot */
.card .tag{background:var(--tc,var(--red));box-shadow:inset 0 -7px 0 var(--tc2,transparent);position:relative;min-width:230px}
.tag .pos{color:var(--tc,var(--red))}
.tag .rk{position:relative;z-index:1;text-shadow:0 2px 6px rgba(0,0,0,.55)}
.tag .shot{position:absolute;right:26px;bottom:7px;height:132px;width:auto;pointer-events:none}
.tdot{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;vertical-align:1px;background:var(--tc);box-shadow:inset -4px 0 0 var(--tc2)}
"""

# 主色、副色（官方配色）。主色太暗時副色帶在卡片底部補辨識度。
TEAM_COLORS = {
    'ATL': ['#E03A3E', '#C1D32F'], 'BOS': ['#007A33', '#BA9653'], 'BKN': ['#000000', '#FFFFFF'],
    'CHA': ['#1D1160', '#00788C'], 'CHI': ['#CE1141', '#000000'], 'CLE': ['#860038', '#FDBB30'],
    'DAL': ['#00538C', '#B8C4CA'], 'DEN': ['#0E2240', '#FEC524'], 'DET': ['#C8102E', '#1D42BA'],
    'GSW': ['#1D428A', '#FFC72C'], 'HOU': ['#CE1141', '#C4CED4'], 'IND': ['#002D62', '#FDBB30'],
    'LAC': ['#C8102E', '#1D428A'], 'LAL': ['#552583', '#FDB927'], 'MEM': ['#5D76A9', '#12173F'],
    'MIA': ['#98002E', '#F9A01B'], 'MIL': ['#00471B', '#EEE1C6'], 'MIN': ['#0C2340', '#78BE20'],
    'NOP': ['#0C2340', '#C8102E'], 'NYK': ['#006BB6', '#F58426'], 'OKC': ['#007AC1', '#EF3B24'],
    'ORL': ['#0077C0', '#C4CED4'], 'PHI': ['#006BB6', '#ED174C'], 'PHX': ['#1D1160', '#E56020'],
    'POR': ['#E03A3E', '#000000'], 'SAC': ['#5A2D81', '#63727A'], 'SAS': ['#000000', '#C4CED4'],
    'TOR': ['#CE1141', '#000000'], 'UTA': ['#002B5C', '#F9A01B'], 'WAS': ['#002B5C', '#E31837'],
}

JS = r"""
// 交易球員的 team 是「舊/新」，最後一段是現在的球隊
const teamOf = t => TEAM_COLORS[t.split('/').pop()];
function teamVars(t) {
  const c = teamOf(t);
  return c ? `--tc:${c[0]};--tc2:${c[1]}` : '';
}
function teamDot(t) {
  return teamOf(t) ? `<i class="tdot" style="${teamVars(t)}"></i>` : '';
}
function headshot(p) {
  const r = REAL[p.name];
  return r && r.id ? `<img class="shot" alt="" loading="lazy" src="https://cdn.nba.com/headshots/nba/latest/260x190/${r.id}.png" onerror="this.remove()">` : '';
}
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
        a = acc.setdefault(name, {'id': row[h['PLAYER_ID']], 'gp': 0, 'teams': [], **{k: 0 for k in
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
            'id': a['id'], 'gp': n, 'teams': a['teams'],
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
    js_json = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    block = (f'{BEGIN}\n<style>{CSS}</style>\n<script>const REAL={js_json(sub)};\n'
             f'const TEAM_COLORS={js_json(TEAM_COLORS)};{JS}</script>\n{END}\n')
    assert s.count('<script>const DATA=') == 1
    s = s.replace('<script>const DATA=', block + '<script>const DATA=', 1)
    hook = '<div class="strong">${tops.map(t => chip(t[0], t[1])).join(\'\')}${chip(\'弱項 \' + low[0], low[1], true)}</div>'
    for old, new in [
        (hook, hook + '\n      ${realBox(p)}'),
        ('<div class="tag"><span class="pos">', '<div class="tag" style="${teamVars(p.team)}">${headshot(p)}<span class="pos">'),
        ("<td class=\"sub${sc('team')}\">${p.team}</td>", "<td class=\"sub${sc('team')}\">${teamDot(p.team)}${p.team}</td>"),
    ]:
        if new not in s:
            assert s.count(old) == 1, old
            s = s.replace(old, new, 1)
    path.write_text(s, encoding='utf-8')
    missing = [n for n in roster if n not in real]
    print(f'{path}: {len(sub)}/{len(roster)} 人有真實數據；缺 {len(missing)}: {missing[:10]}')


if __name__ == '__main__':
    real = aggregate()
    for p in sys.argv[1:]:
        inject(Path(p), real)

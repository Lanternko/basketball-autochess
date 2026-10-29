"""名單頁加料：卡片顯示 2025-26 例行賽真實場均、球隊配色、隊徽＋球員頭像；表格球隊欄加色標。

資料：data/season-source/player-games.json（stats.nba.com leaguegamelog，每人每場一列）。
依 PLAYER_NAME 跨隊合計；交易球員列出所有球隊。重跑會先移除舊的注入再寫入。
頭像直接連 NBA CDN（260x190 約 14 KB，只載入被點選的那位），沒網路或沒照片就不顯示。

用法：python -I scripts/enrich_roster_viewer.py reports/ovr-v58-card-2025-26/roster-viewer.html [...]
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'season-source' / 'player-games.json'
RAPM = ROOT / 'reports' / 'impact-rapm' / 'rapm-prior.csv'  # 2025-26 單季 box-prior RAPM（每 100 回合）
ONOFF = ROOT / 'reports' / 'impact-rapm' / 'onoff.csv'

CSS = """
/* real box score */
.real{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:4px;margin-top:2px}
.real .st{background:var(--panel-2);border:1px solid var(--line);border-radius:3px;padding:3px 6px;text-align:center}
.real .st b{display:block;font:700 1.15rem var(--f-disp);font-variant-numeric:tabular-nums;color:var(--fg)}
.real .st span{display:block;font-size:.68rem;color:var(--muted)}
.real-h{color:var(--muted);font-size:.72rem;letter-spacing:.08em}
.real.rx{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px}
.rx .rmain{display:flex;gap:4px}
.rx .rmain .st{min-width:68px;padding:4px 12px}
.rx .rmain .st b{font-size:1.7rem;line-height:1.1}
.rx .rsub{display:grid;gap:4px;font-size:.74rem;color:var(--muted)}
.rx .rsub>div{display:flex;flex-wrap:wrap;gap:2px 14px}
.rx .rsub b{margin-left:5px;font:600 .92rem var(--f-disp);font-variant-numeric:tabular-nums;color:var(--fg)}
/* 球員卡資訊列：手機藏標籤、較上季差值三色（season_nav._compact_facts） */
.facts i{font-style:normal}
.facts .sm{display:none}
.facts b.up{color:var(--g-a)}
.facts b.dn{color:var(--g-f)}
.facts b.flat{color:var(--muted)}
@media (max-width:640px){
  .facts{gap:2px 12px}
  .facts .lb{display:none}
  .facts .sm{display:inline}
}
/* 手機表格（使用者 2026-10-29：很難用）：名字欄變窄可換行、列變矮；OVR 往右滑時釘在名字旁邊，長按不選字 */
@media (max-width:640px){
  #tbl td{padding:5px 3px;font-size:.92rem}
  #tbl th.nm,#tbl td.nm{width:112px;min-width:112px;max-width:112px;box-sizing:border-box;padding-left:8px}
  #tbl td.nm{white-space:normal;overflow-wrap:anywhere;line-height:1.1;font-size:.86rem}
  #tbl td.no{width:28px;font-size:.78rem}
  #tbl th[data-k="ovr"],#tbl td.ovr{position:sticky;left:112px;z-index:1;box-shadow:6px 0 6px -5px rgba(0,0,0,.7)}
  #tbl th[data-k="ovr"]{z-index:2}
  #tbl tbody td.ovr{background:var(--panel);font-size:1rem}
  #tbl tbody td.ovr.sortcol{background:linear-gradient(rgba(242,194,48,.07),rgba(242,194,48,.07)) var(--panel)}
  #tbl tbody tr:hover td.ovr{background:var(--panel-2)}
  #tbl tbody tr.sel td.ovr{background:var(--gold)}
  #tbl tbody{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
}
/* team colors + headshot */
.card .tag{background:var(--card,var(--red));box-shadow:inset 0 -7px 0 var(--tc,transparent);position:relative;min-width:230px}
.tag .pos{background:var(--tc,#fff);color:#fff;position:relative;z-index:1}
.tag .rk{position:relative;z-index:1;color:var(--ink,#fff);text-shadow:0 0 8px var(--card,#000)}
.tag .logo{position:absolute;right:30px;top:50%;transform:translateY(-50%);height:150px;width:150px;object-fit:contain;opacity:.9;pointer-events:none}
.tag .shot{position:absolute;right:26px;bottom:7px;height:132px;width:auto;pointer-events:none}
.tabbr{color:var(--tt);font-weight:600}
tbody tr.sel .tabbr{color:inherit}
/* impact chips：RAPM 攻守淨（對聯盟平均）、在場減不在場（每 100 回合） */
.chip i.up{color:var(--g-a)}
.chip i.dn{color:var(--g-f)}
.chip i.flat{color:var(--muted)}
"""

# [主色, 副色, 卡片底色, 背號字色]。主色、副色是官方配色（表格色標、卡片底帶）；
# 卡片底色多半避開主色，讓球衣和隊徽看得出來；OKC／BOS／MEM 依使用者指定用隊色的淺色版。
# 表格球隊縮寫的字色預設用卡片底色；卡片是灰／米色的隊另給第 5 欄（亮一點的隊色），不然跟預設灰字分不出來。
TEAM_COLORS = {
    'ATL': ['#E03A3E', '#C1D32F', '#C1D32F', '#111'], 'BOS': ['#007A33', '#BA9653', '#2E9E52', '#fff'],
    'BKN': ['#000000', '#FFFFFF', '#A9AEB4', '#111', '#FFFFFF'], 'CHA': ['#1D1160', '#00788C', '#A1A1A4', '#111', '#1FB5C4'],
    'CHI': ['#CE1141', '#000000', '#E6E6E6', '#111', '#EF3A55'], 'CLE': ['#860038', '#FDBB30', '#FDBB30', '#111'],
    'DAL': ['#00538C', '#B8C4CA', '#B8C4CA', '#111', '#3B95E0'], 'DEN': ['#0E2240', '#FEC524', '#FEC524', '#111'],
    'DET': ['#C8102E', '#1D42BA', '#BEC0C2', '#111', '#EF3A55'], 'GSW': ['#1D428A', '#FFC72C', '#FFC72C', '#111'],
    'HOU': ['#CE1141', '#C4CED4', '#C4CED4', '#111', '#EF3A55'], 'IND': ['#002D62', '#FDBB30', '#FDBB30', '#111'],
    'LAC': ['#C8102E', '#1D428A', '#BEC0C2', '#111', '#EF3A55'], 'LAL': ['#552583', '#FDB927', '#7C4DBF', '#fff'],
    'MEM': ['#5D76A9', '#12173F', '#7D9BC1', '#fff'], 'MIA': ['#98002E', '#F9A01B', '#41B6E6', '#111'],
    'MIL': ['#00471B', '#EEE1C6', '#EEE1C6', '#111', '#4CAF62'], 'MIN': ['#0C2340', '#78BE20', '#78BE20', '#111'],
    'NOP': ['#0C2340', '#C8102E', '#B4975A', '#111'], 'NYK': ['#006BB6', '#F58426', '#BEC0C2', '#111', '#F58426'],
    'OKC': ['#007AC1', '#EF3B24', '#4FA3E0', '#fff'], 'ORL': ['#0077C0', '#C4CED4', '#C4CED4', '#111', '#3BA2E6'],
    'PHI': ['#006BB6', '#ED174C', '#ED174C', '#fff'], 'PHX': ['#1D1160', '#E56020', '#F9AD1B', '#111'],
    'POR': ['#E03A3E', '#000000', '#BAC3C9', '#111', '#EF4B4F'], 'SAC': ['#5A2D81', '#63727A', '#A2AAAD', '#111', '#A57BE0'],
    'SAS': ['#000000', '#C4CED4', '#C4CED4', '#111'], 'TOR': ['#CE1141', '#000000', '#A1A1A4', '#111', '#EF3A55'],
    'UTA': ['#002B5C', '#F9A01B', '#F9A01B', '#111'], 'WAS': ['#002B5C', '#E31837', '#C4CED4', '#111', '#EF3A55'],
}

JS = r"""
// 交易球員的 team 是「舊/新」，最後一段是現在的球隊
const teamOf = t => TEAM_COLORS[t.split('/').pop()];
function teamVars(t) {
  const c = teamOf(t);
  return c ? `--tc:${c[0]};--tc2:${c[1]};--card:${c[2]};--ink:${c[3]};--tt:${c[4] || c[2]}` : '';
}
function teamCell(t) {
  return teamOf(t) ? `<span class="tabbr" style="${teamVars(t)}">${t}</span>` : t;
}
function headshot(p) {
  const r = REAL[p.name], tid = TEAM_IDS[p.team.split('/').pop()];
  const logo = tid ? `<img class="logo" alt="" src="https://cdn.nba.com/logos/nba/${tid}/global/L/logo.svg" onerror="this.remove()">` : '';
  return logo + (r && r.id ? `<img class="shot" alt="" loading="lazy" src="https://cdn.nba.com/headshots/nba/latest/260x190/${r.id}.png" onerror="this.remove()">` : '');
}
function realBox(p) {
  const r = REAL[p.name];
  if (!r) return '<div class="real-h">真實數據：找不到這位球員的 2025-26 例行賽紀錄</div>';
  const f1 = v => v.toFixed(1), pc = v => (v == null ? '—' : (v * 100).toFixed(1) + '%');
  const pm = v => (v > 0 ? '+' : '') + v.toFixed(1);
  // 主次分明（使用者 2026-10-29：十二格一樣大太雜）：得分／籃板／助攻大格，其餘分三行小字
  const main = [['得分', f1(r.pts)], ['籃板', f1(r.reb)], ['助攻', f1(r.ast)]];
  const sub = [[['命中率', pc(r.fg)], ['三分', pc(r.fg3)], ['罰球', pc(r.ft)], ['真實命中', pc(r.ts)]],
    [['抄截', f1(r.stl)], ['阻攻', f1(r.blk)], ['失誤', f1(r.tov)]],
    [['分鐘', f1(r.mpg)], ['正負值', pm(r.pm)]]];
  return `<div class="real-h">2025-26 例行賽真實數據 · 場均 · ${r.gp} 場${r.teams.length > 1 ? ' · ' + r.teams.join('/') : ''}</div>
      <div class="real rx"><div class="rmain">${main.map(([l, v]) => `<div class="st"><b>${v}</b><span>${l}</span></div>`).join('')}</div>
      <div class="rsub">${sub.map(g => `<div>${g.map(([l, v]) => `<span>${l}<b>${v}</b></span>`).join('')}</div>`).join('')}</div></div>`;
}
function impactChips(p) {
  const r = REAL[p.name], m = r && IMPACT[r.id];
  if (!m) return '<div class="strong"><span class="chip dim">影響力<i class="flat">無 2025-26 RAPM</i></span></div>';
  const sg = v => (v > 0 ? '+' : '') + v.toFixed(1);
  const cls = v => (v >= 0.5 ? 'up' : v <= -0.5 ? 'dn' : 'flat');
  const chip = (lab, v, tip) => v == null ? '' : `<span class="chip" title="${tip}">${lab}<i class="${cls(v)}">${sg(v)}</i></span>`;
  return `<div class="strong">${chip('進攻影響', m.o, '2025-26 RAPM 進攻：在場時球隊每 100 回合多得幾分（控制隊友與對手，對聯盟平均）')}${
    chip('防守影響', m.d, '2025-26 RAPM 防守：在場時對手每 100 回合少得幾分（正值＝少失分）')}${
    chip('淨影響', m.o + m.d, '2025-26 RAPM 淨值＝進攻＋防守')}${
    chip('在場增益', m.onoff, '2025-26 他在場減不在場的球隊每 100 回合淨效率（扣掉球隊本身強弱；會受替補好壞影響）' + (m.on == null ? '' : '；在場時球隊淨效率 ' + sg(m.on)))}</div>`;
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


def impact():
    """playerId → {o, d, on, onoff}：2025-26 單季 box-prior RAPM 攻守，與在場淨效率、在場減不在場（交易球員依在場回合加權）。"""
    out = {}
    for r in csv.DictReader(RAPM.open(encoding='utf-8')):
        out[int(r['playerId'])] = {'o': float(r['lastSeasonO']), 'd': float(r['lastSeasonD'])}
    acc = {}
    for r in csv.DictReader(ONOFF.open(encoding='utf-8')):
        if r['season'] != '2025-26':
            continue
        a = acc.setdefault(int(r['playerId']), [0.0, 0.0, 0.0])
        w = float(r['onPoss'])
        a[0] += w
        a[1] += w * float(r['onNet'])
        a[2] += w * float(r['onOffNet']) if r['onOffNet'] else 0
    for pid, (w, on, onoff) in acc.items():
        if pid in out and w > 0:
            out[pid].update(on=round(on / w, 2), onoff=round(onoff / w, 2))
    return out


def team_ids():
    rs = json.loads(SRC.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(rs['headers'])}
    return {row[h['TEAM_ABBREVIATION']]: row[h['TEAM_ID']] for row in rs['rowSet']}


def inject(path, real):
    s = path.read_text(encoding='utf-8')
    s = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    names = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', s, re.S).group(1))
    col = names['cols'].index('name')
    roster = [r[col] for r in names['rows']]
    sub = {n: real[n] for n in roster if n in real}
    ids = {v['id'] for v in sub.values()}
    imp = {pid: v for pid, v in impact().items() if pid in ids}
    js_json = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    block = (f'{BEGIN}\n<style>{CSS}</style>\n<script>const REAL={js_json(sub)};\nconst IMPACT={js_json(imp)};\n'
             f'const TEAM_COLORS={js_json(TEAM_COLORS)};\nconst TEAM_IDS={js_json(team_ids())};{JS}</script>\n{END}\n')
    assert s.count('<script>const DATA=') == 1
    s = s.replace('<script>const DATA=', block + '<script>const DATA=', 1)
    hook = '<div class="strong">${tops.map(t => chip(t[0], t[1])).join(\'\')}${chip(\'弱項 \' + low[0], low[1], true)}</div>'
    s = s.replace('${teamDot(p.team)}${p.team}', '${p.team}')  # 舊版注入
    # 能力值前三／弱項改成影響力（使用者 2026-10-29）；樣板可能已含 realBox
    s = s.replace(hook + '\n      ${realBox(p)}', hook)
    for old, new in [
        (hook, '${impactChips(p)}\n      ${realBox(p)}'),
        ('<div class="tag"><span class="pos">', '<div class="tag" style="${teamVars(p.team)}">${headshot(p)}<span class="pos">'),
        ("<td class=\"sub${sc('team')}\">${p.team}</td>", "<td class=\"sub${sc('team')}\">${teamCell(p.team)}</td>"),
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

"""賽中 OVR 名單頁：以正式卡名單頁為版型，換成 inseason 0.2.4（原名 0.2.2，R-050 起跟先驗正式卡同號；C4，先驗 card 0.2.4＝用人回歸＋當季 RAPM 目標；OVR 為每場，R-028；舊版 0.2.1 為 card 0.2.2 先驗）的 OVR、現任球隊與 2026-27 場均真實數據。

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
from season_nav import add_season_nav, apply_common, regroup_attrs  # noqa: E402
import season_nav as sn  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reports/impact-epm-2026-27'))
import epm_live  # noqa: E402

ROOT = er.ROOT
BASE = ROOT / 'reports/ovr-v58-card-2025-26/roster-viewer.html'
SRC26 = ROOT / 'data/season-source-2026-27/player-games.json'


# OVR 折線圖（使用者 2026-10-31：近 5 場表右邊空著）：開季先驗＋逐場重算的 OVR（ovr_history.py 產 ovr-history.json），
# 放在近 5 場表右邊，窄螢幕換行到表下面；沒有這個檔就不畫
OVR_CSS = """
.card .g5.hc{display:flex;flex-wrap:wrap;gap:12px;align-items:stretch;justify-self:stretch;overflow:visible;border:0;background:none}
.card .g5.hc[hidden]{display:none}
.g5.hc>.g5in{flex:0 1 auto;min-width:0;max-width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:3px;background:var(--panel-2);scrollbar-width:thin;scrollbar-color:#38424f transparent}
.g5.hc>.ovc{flex:1 1 300px;min-width:0;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:3px;background:var(--panel-2);padding:6px 10px 4px}
.ovc .ovh{display:flex;justify-content:space-between;align-items:baseline;color:var(--muted);font:600 .7rem var(--f-disp);letter-spacing:.04em;padding-bottom:2px}
.ovc .ovh b{color:var(--fg);font:700 .86rem var(--f-disp);font-variant-numeric:tabular-nums}
.ovc svg{width:100%;height:auto;display:block;overflow:visible;margin:auto 0}
.ovc .ax{font:500 10px var(--f-disp);fill:var(--muted);font-variant-numeric:tabular-nums}
.ovc .gd{stroke:var(--line);stroke-width:1}
.ovc .ref{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 4;opacity:.6}
.ovc .ln{fill:none;stroke:var(--g-a);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.ovc .ar{fill:var(--g-a);opacity:.08}
.ovc .pt{fill:var(--panel-2);stroke:var(--g-a);stroke-width:2}
.ovc .pt.st{stroke:var(--muted)}
.ovc .hit{fill:transparent;cursor:default}
.ovc .tip rect{fill:#0d1117;stroke:var(--line)}
.ovc .tip text{font:600 11px var(--f-disp);fill:var(--fg);font-variant-numeric:tabular-nums}
"""
OVR_JS = r"""
// OVR 折線（使用者 2026-10-31）：開季先驗（新秀＝順位起點）→ 每打一場重算一次；虛線＝開季
function ovrChart(p) {
  const h = OVRH[p.name];
  if (!h || !h.pts.length) return '';
  const md = d => +d.slice(5, 7) + '/' + +d.slice(8);
  const pts = [['開季', h.start], ...h.pts.map(([d, v]) => [md(d), v])];
  const W = 340, H = 170, L = 30, R = 12, T = 12, B = 22;
  const vs = pts.map(q => q[1]);
  let lo = Math.min(...vs), hi = Math.max(...vs);
  const pad = Math.max(1, (6 - (hi - lo)) / 2);
  lo = Math.floor(lo - pad); hi = Math.ceil(hi + pad);
  const x = i => L + (pts.length > 1 ? i * (W - L - R) / (pts.length - 1) : (W - L - R) / 2);
  const y = v => T + (hi - v) * (H - T - B) / (hi - lo);
  const step = Math.max(1, Math.ceil((hi - lo) / 4));
  const ticks = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) ticks.push(v);
  const xl = Math.max(1, Math.ceil(pts.length / 8));          // x 標籤太密就隔幾場標一次（最後一場一定標）
  const path = pts.map((q, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(q[1]).toFixed(1)).join('');
  const area = path + `L${x(pts.length - 1).toFixed(1)} ${H - B}L${x(0).toFixed(1)} ${H - B}Z`;
  const last = vs[vs.length - 1], d = last - h.start;
  const tip = (q, i) => `${i ? q[0] : '開季先驗'}　OVR ${q[1].toFixed(1)}`;
  return `<div class="ovc"><div class="ovh"><span>OVR 走勢 · 每場重算</span><span>開季 <b>${h.start.toFixed(1)}</b> → 現在 <b>${last.toFixed(1)}</b>` +
    ` <b class="${d >= 0.05 ? 'up' : d <= -0.05 ? 'dn' : ''}">${d > 0 ? '+' : ''}${d.toFixed(1)}</b></span></div>` +
    `<svg viewBox="0 0 ${W} ${H}" onmouseleave="ovTip(this)">` +
    ticks.map(v => `<line class="gd" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text class="ax" x="${L - 5}" y="${y(v) + 3.5}" text-anchor="end">${v}</text>`).join('') +
    `<line class="ref" x1="${L}" x2="${W - R}" y1="${y(h.start)}" y2="${y(h.start)}"/>` +
    `<path class="ar" d="${area}"/><path class="ln" d="${path}"/>` +
    pts.map((q, i) => `<circle class="pt${i ? '' : ' st'}" cx="${x(i)}" cy="${y(q[1])}" r="${i === pts.length - 1 ? 4 : 3}"/>` +
      ((i % xl === 0 && pts.length - 1 - i >= xl) || i === pts.length - 1 ? `<text class="ax" x="${x(i)}" y="${H - 6}" text-anchor="middle">${q[0]}</text>` : '') +
      `<circle class="hit" cx="${x(i)}" cy="${y(q[1])}" r="11" data-t="${tip(q, i)}" onmouseenter="ovTip(this.ownerSVGElement,this)"/>`).join('') +
    `<g class="tip" visibility="hidden"><rect rx="3" height="20"/><text y="14"></text></g></svg></div>`;
}
function ovTip(svg, c) {
  const g = svg.querySelector('.tip');
  if (!c) { g.setAttribute('visibility', 'hidden'); return; }
  const t = g.querySelector('text'), r = g.querySelector('rect');
  t.textContent = c.dataset.t;
  const w = t.getComputedTextLength() + 14, vb = svg.viewBox.baseVal;
  const cx = +c.getAttribute('cx'), cy = +c.getAttribute('cy');
  const gx = Math.min(Math.max(cx - w / 2, 0), vb.width - w), gy = cy > 34 ? cy - 30 : cy + 10;
  r.setAttribute('width', w); t.setAttribute('x', 7);
  g.setAttribute('transform', `translate(${gx},${gy})`);
  g.setAttribute('visibility', 'visible');
}
"""


def add_ovr_chart(live):
    """近 5 場表右邊加 OVR 折線（記憶體裡改 er.JS／er.CSS，不改 enrich_roster_viewer.py）。"""
    f = live / 'ovr-history.json'
    if not f.exists():
        print('OVR 折線：沒有 ovr-history.json，不畫', file=sys.stderr)
        return
    h = json.loads(f.read_text(encoding='utf-8'))
    data = {v['name']: {'start': v['start'], 'pts': v['pts']} for v in h['players'].values() if v['pts']}  # N=0（傷兵等）不畫
    old = """<div class="g5${sv ? ' sd' : ''}"${G5_OPEN ? '' : ' hidden'}>${sv ? seasonLog(r) : gameLog(r, p)}</div>"""
    new = ("""<div class="g5${sv ? ' sd' : ''}${!sv && OVRH[p.name] ? ' hc' : ''}"${G5_OPEN ? '' : ' hidden'}>"""
           """${sv ? seasonLog(r) : OVRH[p.name] ? `<div class="g5in">${gameLog(r, p)}</div>${ovrChart(p)}` : gameLog(r, p)}</div>""")
    assert er.JS.count(old) == 1, old
    er.JS = er.JS.replace(old, new) + '\nconst OVRH=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';' + OVR_JS
    er.CSS += OVR_CSS


def main():
    sys.stdout.reconfigure(encoding='utf-8')    # -I 不吃 PYTHONIOENCODING；名字有 ņ 等字時 cp950 印不出來
    day = sys.argv[1] if len(sys.argv) > 1 else '2026-10-27'
    live = ROOT / 'reports/ovr-inseason-2026-27/live' / day
    meta = json.loads((live / 'meta.json').read_text(encoding='utf-8'))
    rows = list(csv.DictReader((live / 'ranking.csv').open(encoding='utf-8')))
    nopr = len(list(csv.DictReader((live / 'no-prior.csv').open(encoding='utf-8'))))
    cols = ['rank', 'ovr', 'name', 'pos', 'team', 'ht', 'min', 'gp', 'imp', 'dbon', 'threeValue', 'mid', 'short', 'ft',
            'drive', 'foulDraw', 'pass', 'tovSkill', 'creation', 'rebound', 'physique', 'stamina', 'onBall', 'help', 'pressure',
            'last', 'dovr']
    # card 0.2.2 先驗（E-074）：ranking.csv 帶 presDisplay／foulDisc → PRES 欄顯示 presDisplay，tooltip 列逼失誤與犯規紀律（同 build_card_viewer.py）
    has_pd = 'presDisplay' in rows[0]
    if has_pd:
        cols += ['force', 'foulDisc']
    base = BASE.read_text(encoding='utf-8')
    old = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', base, re.S).group(1))
    ht = {r[old['cols'].index('name')]: r[old['cols'].index('ht')] for r in old['rows']}
    # DIQ 顯示負分：先試 meta 記的 def-L 檔＋posMeanD，再試今天重擬合的 def-L-live.csv；都對不上就只顯示正值
    ul = next((v['ulBonus'] for v in meta.values() if isinstance(v, dict) and 'ulBonus' in v), None)
    dcen = sn.defense_centered(rows, 'playerId', ([(ROOT / ul['defL'], ul['posMeanD'])] if ul else [])
                               + [(ROOT / 'data/_inseason_build/def-L-live.csv', None)])
    if dcen is None:
        print('DIQ 負分：找不到對得上的 D 檔，只顯示正值', file=sys.stderr)
    data_rows = []
    for r in rows:
        num = lambda k: float(r[k])
        # E-116 新秀先驗列沒有 threeValue／presDisplay／foulDisc（無上季卡）：3PT 退回 long、PRES 退回 pressure、犯規紀律留空
        alt = {'threeValue': 'long', 'presDisplay': 'pressure'}
        opt = lambda k: num(k) if r[k] != '' else (num(alt[k]) if k in alt else None)
        # 舊版型沒有的人（E-116 新秀）身高改取 ranking.csv 的 heightInches（bio）
        h = ht.get(r['name']) or (round(num('heightInches')) if r.get('heightInches') else 0)
        data_rows.append([int(r['rank']), num('ovr'), r['name'], r['pos'], r['team'], h,
                          round(num('MIN26') / int(r['N']), 1) if int(r['N']) else 0.0, int(r['N']), num('predictedPer36'),
                          dcen[r['playerId']] if dcen else (num('defenseBonus') or None),
                          *[opt('presDisplay') if (a == 'pressure' and has_pd) else opt(a) for a in cols[10:25]],
                          num('lastOVR'), num('dOVR'), *([num('pressure'), opt('foulDisc')] if has_pd else [])])
    # ΔOVR 五色：≥+4 深綠、+1～+4 淺綠、±1 內灰、−1～−4 橘、≤−4 紅（沿用等第色）
    dcol = ("(v => v >= 4 ? 'var(--g-a)' : v >= 1 ? 'var(--g-b)' : v > -1 ? 'var(--muted)'"
            " : v > -4 ? 'var(--g-d)' : 'var(--g-f)')(p.dovr)")
    s = base
    s = s.replace('<title>OVR 名單檢視</title>', '<title>新賽季 OVR 名單</title>', 1)
    s = s.replace('<h1>2025-26 <span>OVR</span> 名單</h1>', '<h1>2026-27 <span>OVR</span> 名單</h1>', 1)
    s = re.sub(r'<div class="src">.*?</div>',
               f'<div class="src">OVR：賽中 C4（{meta["version"]}），先驗 {meta["priorCard"]}{"（用人回歸＋當季 RAPM 目標）" if "predNew" in rows[0] else ""}；數據截至 {meta["dataCutoff"]}；'
               f'{"PRES＝逼失誤扣犯規（2025-26，賽中凍結）· " if has_pd else ""}N=已打場數 · {len(rows)} 人（另 {nopr} 人無先驗卡，未列入）· 樣本很小，只看趨勢</div>', s, count=1, flags=re.S)
    new_data = json.dumps({'cols': cols, 'rows': data_rows}, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'const DATA=\{.*?\};\nconst COLS', lambda m: f'const DATA={new_data};\nconst COLS', s, count=1, flags=re.S)
    for a, b in [
        ("['long', '3PT', '三分']", "['threeValue', '3PT', '三分']"),
        ("['drive', 'DRV', '切入']", "['drive', 'DRV', '切入'], ['foulDraw', 'FD', '製造犯規']"),
        ('<th class="g" colspan="2">出場</th>', '<th class="g" colspan="3">出場</th>'),
        ('colspan="22"', 'colspan="25"'),
        ("th('min', 'MIN', '分鐘', 'gl') + th('gp', 'GP', '場數')",
         "th('min', 'MPG', '分鐘', 'gl') + th('gp', 'N', '場數') + th('dovr', 'ΔOVR', '較開季')"),
        ("[[0, '全部'], [500, '≥500'], [1000, '≥1000'], [1500, '≥1500']]",
         "[[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']]"),
        ('<td class="sub${sc(\'gp\')}">${p.gp}</td>',
         '<td class="sub${sc(\'gp\')}">${p.gp}</td>\n'
         '      <td class="sub${sc(\'dovr\')}" style="color:${' + dcol + '}">'
         '${(v => (v > 0 ? \'+\' : \'\') + v.toFixed(1))(Math.abs(p.dovr) < 0.05 ? 0 : p.dovr)}</td>'),
        ('<td class="sub gl${sc(\'min\')}">${p.min.toLocaleString()}</td>',
         '<td class="sub gl${sc(\'min\')}">${p.min.toFixed(1)}</td>'),
        ('<span>上場 <b>${p.min.toLocaleString()}</b> 分鐘</span><span>出賽 <b>${p.gp}</b> 場</span>',
         '<span>場均 <b>${p.min.toFixed(1)}</b> 分鐘</span><span>已打 N=<b>${p.gp}</b> 場</span>'
         "<span>開季卡 OVR <b>${p.last.toFixed(1)}</b>（<b>${(p.dovr > 0 ? '+' : '') + p.dovr.toFixed(2)}</b>）</span>"),
        ('模擬每 36 分鐘淨值', '新賽季預測每 36 分鐘淨值'),
        ('OVR 同分多半是 2K27 名次封頂造成的',
         'OVR 為每場（含上場時間，相對替補水準）；ΔOVR 深綠≥+4、淺綠+1～+4、灰±1 內、橘−1～−4、紅≤−4；'
         'OVR 同分多半是 2K27 名次封頂造成的 · 本頁 MPG 是 2026-27 場均分鐘'),
    ]:
        assert s.count(a) >= 1, a
        s = s.replace(a, b)
    s = apply_common(s)
    if has_pd:
        for a, b in [
            ("['pressure', 'PRES', '壓命中率']", "['pressure', 'PRES', '壓迫']"),
            ('function cell(k, v, first) {', 'function cell(k, v, first, tip) {'),
            ("""return `<td class="${cls.join(' ')}" title="${v}">${g}</td>`;""",
             """return `<td class="${cls.join(' ')}" title="${tip || v}">${g}</td>`;"""),
            ("cell(k, p[k], j === 0)", "cell(k, p[k], j === 0, k === 'pressure' ? `逼失誤 ${p.force}｜犯規紀律 ${p.foulDisc == null ? '—' : Math.round(p.foulDisc)}（2025-26）` : null)"),
            # 數值模式的格子（apply_common 改過那行）也帶 PRES tooltip
            ("""cls.push(gcls(grade(v))); return `<td class="${cls.join(' ')}">${v}</td>`; }""",
             """cls.push(gcls(grade(v))); return `<td class="${cls.join(' ')}"${tip ? ` title="${tip}"` : ''}>${v}</td>`; }"""),
        ]:
            assert s.count(a) == 1, a
            s = s.replace(a, b)
    s = regroup_attrs(s)  # 和 2025-26 頁同分組；要在上面 PRES 改名之後
    s = add_season_nav(s, 'inseason')
    out = live / 'roster-viewer.html'
    out.write_text(s, encoding='utf-8')
    # 注入隊色／頭像／2026-27 場均（換資料來源與年份文字）
    er.SRC = SRC26
    er.JS = er.JS.replace('2025-26 例行賽紀錄', '2026-27 賽季紀錄')
    # 影響力四格改用 2026-27 自製 EPM 式（當季 box 先驗＋生涯 RAPM 先驗＋當季 RAPM；只顯示，不進 OVR）
    epm_rows, _ = epm_live.run()
    # 第四格改放當季 box 估計（boxO＋boxD）：開季在場減不在場雜訊太大（Wembanyama +53.5），使用者 2026-10-30 選換掉
    epm_imp = {r['playerId']: {k: v for k, v in (('o', r['O']), ('d', r['D']),
                                                 ('onoff', None if r['boxO'] is None else r['boxO'] + r['boxD'])) if v is not None}
               for r in epm_rows}
    er.IMPACT_LOADER = lambda: {pid: {k: round(v, 2) for k, v in d.items()} for pid, d in epm_imp.items()}
    add_ovr_chart(live)
    for a, b in [
        ('title="無 2025-26 RAPM"', 'title="本季未上場"'),
        ('2025-26 RAPM 進攻：', '2026-27 自製 EPM 式（當季 box 先驗＋生涯 RAPM 先驗＋當季 RAPM）進攻：'),
        ('2025-26 RAPM 防守：', '2026-27 自製 EPM 式（當季 box 先驗＋生涯 RAPM 先驗＋當季 RAPM）防守：'),
        ('2025-26 RAPM 淨值＝進攻＋防守', '2026-27 自製 EPM 式淨值＝進攻＋防守（當季 box 先驗＋生涯 RAPM 先驗＋當季 RAPM）'),
        ('2025-26 他在場減不在場的球隊每 100 回合淨效率（扣掉球隊本身強弱；會受替補好壞影響）',
         '2026-27 只看本季數據表（得分、出手、助攻、籃板、抄阻、失誤等）估的每 100 回合淨影響，不看比分；打得越少越被拉向同上場時間的平均'),
        ("'在場增益'", "'本季數據估計'"),
    ]:
        assert er.JS.count(a) >= 1, a
        er.JS = er.JS.replace(a, b)
    real = er.aggregate()
    # 在名單上還沒出賽的人（N=0）：沒有逐場紀錄，補 id 讓卡片有頭像，gp 0 讓 realBox 顯示「尚未出賽」
    for r in rows:
        if int(r['N']) == 0:
            real.setdefault(r['name'], {'id': int(r['playerId']), 'gp': 0, 'teams': [r['team']]})
    er.inject(out, real)
    print('wrote', out, len(rows), 'players')


if __name__ == '__main__':
    main()

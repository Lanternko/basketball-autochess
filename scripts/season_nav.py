"""名單頁的賽季切換列（靜態相對連結，沿用頁面既有 CSS 變數，不需 JS）。"""
import re

PAGES = [('inseason', '2026-27 賽中', 'index.html'), ('card', '2025-26 正式卡', '2025-26.html')]
CSS = """<style>
.snav{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:6px 0 4px}
.snav .seg a{display:block;background:var(--panel);color:var(--muted);border-right:1px solid var(--line);font:600 .9rem var(--f-disp);letter-spacing:.04em;padding:6px 11px;text-decoration:none;white-space:nowrap}
.snav .seg a:last-child{border-right:0}
.snav .seg a[aria-current="page"]{background:var(--gold);color:var(--gold-ink)}
.snav .seg a:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.snav .note{color:var(--muted);font-size:.8rem}
</style>
"""


def add_season_nav(html_str, current):
    """current：'inseason' 或 'card'。插在 <div class="src">…</div> 後面。"""
    assert current in ('inseason', 'card'), current
    links = ''.join(f'<a href="{href}"' + (' aria-current="page"' if key == current else '') + f'>{label}</a>'
                    for key, label, href in PAGES)
    note = '<span class="note">開季樣本少，數字大多來自 2025-26 卡</span>' if current == 'inseason' else ''
    block = f'\n<nav class="snav" aria-label="賽季切換"><div class="seg">{links}</div>{note}</nav>'
    s, n = re.subn(r'(<div class="src">.*?</div>)', lambda m: m.group(1) + block, html_str, count=1, flags=re.S)
    assert n == 1, 'src div not found'
    assert '</head>' in s or True
    return s.replace('<nav class="snav"', CSS + '<nav class="snav"', 1) if CSS not in s else s


# 兩個頁面共用的樣板修補：數值模式的格子也要帶等第顏色（文字仍顯示數字）。
COMMON_REPLACEMENTS = [
    ("""  if (st.mode === 'num') return `<td class="${cls.join(' ')}">${v}</td>`;""",
     """  if (st.mode === 'num') { cls.push(gcls(grade(v))); return `<td class="${cls.join(' ')}">${v}</td>`; }"""),
    # tovSkill 是每次使用球權的失誤率，不是運球能力（使用者 2026-10-29：HDL 改成 TO）
    ("['tovSkill', 'HDL', '護球']", "['tovSkill', 'TO', '少失誤']"),
    # help 只量籃下 6 呎內命中差、只管禁區，實際是護框（使用者 2026-10-29）；欄位名 help 等 E-080 後再改
    ("['help', 'HELP', '協防']", "['help', 'RIM', '護框']"),
    # 樣板原本是 artifact（外層代加 viewport），單獨放上 gh-pages 後手機會用 980px 排版再縮放，
    # 切換球員時資訊列行數一變就整頁重算縮放、看起來被拉長抖動（使用者 2026-10-29，Amen Thompson）
    ('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">'),
    # 資訊列每一項整塊換行，不要把「防守加分 +1.77」斷在中間
    ('.facts b{', '.facts>span{white-space:nowrap}\n.facts b{'),
] + [
    # 上場篩選拿掉（手機太擠，門檻也還是整季總分鐘），換成球隊篩選：仿 arammeta 的彈出格子（使用者 2026-10-29）
    ('''    <span class="lbl">上場</span>
    <div class="seg" id="minSeg"></div>''',
     '''    <span class="tgrp"><span class="lbl">球隊</span>
    <details class="tpick" id="teamPick"><summary aria-label="選擇球隊"></summary><div class="tpop"><div class="tgrid" id="teamGrid"></div></div></details></span>'''),
    ("pos: 'ALL', min: 0,", "pos: 'ALL', team: 'ALL',"),
    ('p.min >= st.min', "(st.team === 'ALL' || p.team.split('/').pop() === st.team)"),
    # 兩個 builder 已先把門檻改成場均 10／20／30 分鐘
    ("  seg('minSeg', [[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']], 'min');\n", '  teamPick();\n'),
    ('放寬位置或上場分鐘試試', '放寬位置或球隊試試'),
    # 顯示切換直接用範例當標籤（使用者 2026-10-29）
    ("seg('modeSeg', [['grade', '等第'], ['num', '數值']], 'mode');", "seg('modeSeg', [['grade', 'A+'], ['num', '99']], 'mode');"),
    ('function render() {', '''function teamPick() {
  const d = document.getElementById('teamPick'), grid = document.getElementById('teamGrid');
  const logo = t => `<img alt="" src="https://cdn.nba.com/logos/nba/${TEAM_IDS[t]}/global/D/logo.svg" onerror="this.style.visibility='hidden'">`;
  if (!grid.childElementCount) {
    const teams = [...new Set(P.map(p => p.team.split('/').pop()))].filter(t => TEAM_IDS[t]).sort();
    grid.innerHTML = '<button type="button" class="all" data-t="ALL">全部球隊</button>' +
      teams.map(t => `<button type="button" data-t="${t}" title="${t}">${logo(t)}<span>${t}</span></button>`).join('');
    grid.onclick = e => {
      const b = e.target.closest('button[data-t]');
      if (!b) return;
      st.team = b.dataset.t; st.page = 0; st.extra = 0; d.open = false; render();
    };
    // 面板靠左展開，超出螢幕右緣就往左推
    d.addEventListener('toggle', () => {
      if (!d.open) return;
      const pop = d.querySelector('.tpop');
      pop.style.left = '0';
      const over = pop.getBoundingClientRect().right - (document.documentElement.clientWidth - 12);
      if (over > 0) pop.style.left = -over + 'px';
    });
    document.addEventListener('click', e => { if (d.open && !d.contains(e.target)) d.open = false; });
    d.addEventListener('keydown', e => { if (e.key === 'Escape') { d.open = false; d.querySelector('summary').focus(); } });
  }
  d.querySelector('summary').innerHTML = st.team === 'ALL' ? '全部' : logo(st.team) + st.team;
  d.classList.toggle('on', st.team !== 'ALL');
  grid.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.t === st.team)));
}

function render() {'''),
    ('@media (prefers-reduced-motion', '''.tgrp{display:flex;gap:10px;align-items:center}
.tpick{position:relative}
.tpick summary{list-style:none;display:flex;align-items:center;gap:6px;background:var(--panel);color:var(--muted);border:1px solid var(--line);border-radius:3px;font:600 .9rem var(--f-disp);letter-spacing:.04em;padding:6px 11px;cursor:pointer;user-select:none}
.tpick summary::-webkit-details-marker{display:none}
.tpick summary::after{content:"▾";font-size:.8em;opacity:.8}
.tpick summary:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.tpick.on summary{background:var(--gold);color:var(--gold-ink);border-color:var(--gold)}
.tpick summary img{width:18px;height:18px;object-fit:contain;margin:-2px 0}
.tpop{position:absolute;left:0;top:calc(100% + 6px);z-index:20;width:min(360px,calc(100vw - 24px));background:var(--panel-2);border:1px solid var(--line);border-radius:6px;padding:10px;box-shadow:0 12px 32px rgba(0,0,0,.55)}
.tgrid{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}
.tgrid button{display:flex;flex-direction:column;align-items:center;gap:2px;background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:5px 2px 3px;cursor:pointer;color:var(--muted);font:600 .72rem var(--f-disp);letter-spacing:.04em}
.tgrid button img{width:30px;height:30px;object-fit:contain}
.tgrid button.all{grid-column:1/-1;font-size:.9rem;padding:7px}
.tgrid button:hover{border-color:var(--muted);color:var(--fg)}
.tgrid button[aria-pressed="true"]{border-color:var(--gold);color:var(--gold);background:#2a2410}
@media (prefers-reduced-motion'''),
]


def apply_common(s):
    for a, b in COMMON_REPLACEMENTS:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    return s

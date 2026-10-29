"""名單頁的賽季切換列（靜態相對連結，沿用頁面既有 CSS 變數，不需 JS）。"""
import html
import re

# 標籤用年份（使用者 2026-10-29）：2027 beta＝2026-27 賽中，2026＝2025-26 正式卡
PAGES = [('inseason', '2027 beta', 'index.html'), ('card', '2026', '2025-26.html')]
CSS = """<style>
.snav{position:relative;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:6px 0 4px}
.snav .seg a{display:block;background:var(--panel);color:var(--muted);border-right:1px solid var(--line);font:600 .9rem var(--f-disp);letter-spacing:.04em;padding:6px 11px;text-decoration:none;white-space:nowrap}
.snav .seg a:last-child{border-right:0}
.snav .seg a[aria-current="page"]{background:var(--gold);color:var(--gold-ink)}
.snav .seg a:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.snav .note{color:var(--muted);font-size:.8rem}
.pnote summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;background:var(--panel);color:var(--muted);border:1px solid var(--line);border-radius:3px;font:600 .85rem var(--f-disp);letter-spacing:.04em;padding:5px 10px;user-select:none}
.pnote summary::-webkit-details-marker{display:none}
.pnote summary::after{content:"▾";font-size:.8em;opacity:.8}
.pnote summary:hover{color:var(--fg);border-color:var(--muted)}
.pnote summary:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.pnote[open] summary{color:var(--gold);border-color:var(--gold)}
.pn{position:absolute;left:0;top:calc(100% + 6px);width:min(560px,100%);max-height:min(72vh,680px);overflow:auto;overscroll-behavior:contain;box-sizing:border-box;
  background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:14px;box-shadow:0 16px 40px rgba(0,0,0,.6);scrollbar-width:thin;scrollbar-color:#3a4b60 transparent}
.pn h2{font:800 1.05rem var(--f-disp);letter-spacing:.06em;margin:0 0 10px;text-transform:uppercase}
.pn h2 span{color:var(--gold)}
.pn-now{background:var(--panel-2);border:1px solid var(--line);border-radius:5px;padding:9px 12px;margin-bottom:12px;color:var(--muted);font-size:.78rem;line-height:1.6}
.pn-now b{display:block;color:var(--gold);font:700 .72rem var(--f-disp);letter-spacing:.12em;margin-bottom:2px}
.pn-list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.pn-item{--acc:#5b6b7f;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--acc);border-radius:5px;padding:9px 12px 10px}
.pn-item.tk-card{--acc:var(--gold)}
.pn-item.tk-inseason{--acc:#5aa9e6}
.pn-item.cur{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc) inset}
.pn-item header{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.pn-ver{font:800 1.2rem var(--f-disp);color:var(--fg);font-variant-numeric:tabular-nums;letter-spacing:.02em}
.pn-tag{font:700 .68rem var(--f-disp);letter-spacing:.08em;padding:2px 6px;border-radius:3px;background:var(--panel-2);color:var(--muted)}
.pn-tag.tk-card{background:#3a3110;color:var(--gold)}
.pn-tag.tk-inseason{background:#12304a;color:#8cc8ff}
.pn-cur{font:700 .68rem var(--f-disp);letter-spacing:.08em;padding:2px 6px;border-radius:3px;background:var(--gold);color:var(--gold-ink)}
.pn-item time{margin-left:auto;color:var(--muted);font:500 .75rem var(--f-disp);font-variant-numeric:tabular-nums}
.pn-item ul{margin:6px 0 0;padding-left:1.15em;color:#c9d3df;font-size:.82rem;line-height:1.6}
.pn-item li::marker{color:var(--acc)}
.pn-foot{margin:12px 0 0;color:var(--muted);font-size:.72rem;line-height:1.5}
@media (max-width:640px){.pn{width:calc(100vw - 40px)}}
</style>
"""


# 更新說明：每版一格，新的在上（使用者 2026-10-29）。track：card 正式卡、inseason 賽中、site 網頁；
# 版號一換就在最上面加一格，只更新比賽資料（字母後綴）不加。內容寫成球迷看得懂的話，不寫 E／R 編號。
TRACK = {'card': '正式卡', 'inseason': '賽中', 'site': '網頁'}
PATCH_NOTES = [
    (('card',), '0.2.4', '2026-10-29', [
        '教練用人證據的回歸目標，改成只看 2025-26 單季 RAPM（原本四季合併），修正年輕球員被低估。']),
    (('site',), '', '2026-10-29', [
        '加球隊篩選（隊徽格），拿掉上場時間篩選。',
        '表格自己捲動、表頭固定，看低排名時卡片仍在畫面上；捲軸改細、加捲動陰影。',
        '手機版：卡片改成 OVR 在右上、數據佔滿整寬；修點球員時畫面拉長抖動。',
        '顯示切換改成 A+／99；賽季切換改成 2027 beta／2026；說明收進「更新說明」。']),
    (('card',), '0.2.3', '2026-10-29', [
        'OVR 能力估計納入教練用人證據：上場分鐘、出賽率、年齡、是否下放發展聯盟。',
        '教練不用（DNP）和輪休分開看，輪休不當成被冷凍。']),
    (('inseason',), '0.2.1', '2026-10-29', [
        '賽中先驗改用 card 0.2.2。',
        '製造犯規照新公式（以量為主）隨本季數據更新；壓迫沿用上季值，賽中凍結。']),
    (('card',), '0.2.2', '2026-10-29', [
        '製造犯規（FD）改以量為主：每 36 分鐘罰球數佔 75%、罰球率佔 25%。']),
    (('card',), '0.2.1', '2026-10-29', [
        '壓迫（PRES）改用球員自己逼出的對手失誤、扣掉犯規；原本是從 RAPM 拆出來的數字，雜訊大。']),
    (('card', 'inseason'), '0.2.0', '2026-10-29', [
        'OVR 改成每場價值：含上場時間，以替補水準為基準。每分鐘表現相同時，打得多的人 OVR 較高。',
        '賽中頁加「預測 MPG」欄。']),
    (('inseason',), '0.1.2', '2026-10-28', [
        '賽中先驗換成 card 0.1.2。',
        '拿掉「3P準」欄，加「FD 製造犯規」欄。']),
    (('site',), '', '2026-10-28', [
        '加賽季切換：賽中頁與正式卡頁。',
        '卡片加球員頭像、隊徽與隊色，下方顯示真實場均數據。']),
    (('card',), '0.1.2', '2026-10-28', [
        '對位防守改算「被針對」：依對手實際的出手習慣算預期出手，不再因位置標錯而誤判（例：Wembanyama 被標 F 卻守中鋒）。']),
    (('inseason',), '0.1.1', '2026-10-28', [
        '兩頁的 3PT 欄改顯示三分價值（準度加出手量），OVR 不變。']),
    (('card',), '0.1.1', '2026-10-28', [
        '「切入」拆成切入與製造犯規兩項。',
        '低分鐘球員不再虛胖：比率型能力值往本人上季拉回，沒有歷史才往聯盟平均。']),
    (('card', 'inseason'), '0.1.0', '', [
        '起點：正式卡沿用 v58 模型，賽中用 C4 模型（上季卡當先驗、隨本季數據更新）。']),
]


def patch_notes_html(now_text, current):
    """now_text：原本 <div class="src"> 的版本說明，放最上面當「目前版本」；只標本頁那條線的版號（賽中頁說明裡的先驗 card 版號不算）。"""
    cur = {(current, v) for v in re.findall(rf'\b{current} (\d+\.\d+\.\d+)', now_text)}
    items = []
    for tracks, ver, date, lines in PATCH_NOTES:
        is_cur = any((t, ver) in cur for t in tracks)
        items.append(
            f'<li class="pn-item tk-{tracks[0]}{" cur" if is_cur else ""}"><header>'
            + ''.join(f'<span class="pn-tag tk-{t}">{TRACK[t]}</span>' for t in tracks)
            + (f'<b class="pn-ver">{ver}</b>' if ver else '')
            + ('<span class="pn-cur">目前</span>' if is_cur else '')
            + (f'<time datetime="{date}">{date[5:].replace("-", "/")}</time>' if date else '')
            + '</header><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in lines) + '</ul></li>')
    return ('<details class="pnote"><summary>更新說明</summary><div class="pn" role="region" aria-label="更新說明">'
            '<h2>Patch <span>Notes</span></h2>'
            f'<div class="pn-now"><b>目前版本</b>{now_text}</div>'
            f'<ol class="pn-list">{"".join(items)}</ol>'
            '<p class="pn-foot">版號後面的字母（例如 0.2.1e）代表只更新比賽資料，模型沒動。</p></div></details>'
            # 點面板外或按 Esc 關掉
            "<script>(()=>{const d=document.querySelector('.pnote');"
            "document.addEventListener('click',e=>{if(d.open&&!d.contains(e.target))d.open=false});"
            "d.addEventListener('keydown',e=>{if(e.key==='Escape'){d.open=false;d.querySelector('summary').focus()}})})();</script>")


def add_season_nav(html_str, current):
    """current：'inseason' 或 'card'。取代 <div class="src">…</div>，原說明收進切換列的「更新說明」（點開才看，使用者 2026-10-29）。"""
    assert current in ('inseason', 'card'), current
    links = ''.join(f'<a href="{href}"' + (' aria-current="page"' if key == current else '') + f'>{label}</a>'
                    for key, label, href in PAGES)
    note = '<span class="note">開季樣本少，數字大多來自 2026 卡</span>' if current == 'inseason' else ''
    block = lambda m: (f'\n<nav class="snav" aria-label="賽季切換"><div class="seg">{links}</div>{note}'
                       f'{patch_notes_html(m.group(1), current)}</nav>')
    s, n = re.subn(r'<div class="src">(.*?)</div>', block, html_str, count=1, flags=re.S)
    assert n == 1, 'src div not found'
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
    # 表格自己捲（使用者 2026-10-29：看低排名時頭像卡仍在畫面上）。高度＝卡片下方剩餘視窗，只在載入／縮放時算，
    # 點球員不改高度；換排序、篩選、頁才捲回頂。手機卡片太高放不下兩者，給 60% 視窗，捲到底交還頁面。
    ('.tbox{overflow-x:auto;', '.tbox{overflow:auto;max-height:70vh;overscroll-behavior:contain;'),
    # top:-1px：border-collapse 的半像素邊框會在表頭上緣留一條縫，捲過的列從縫裡露出來
    ('@media (prefers-reduced-motion', '''#tbl thead{position:sticky;top:-1px;z-index:3}
@media (max-width:640px){.tbox{overscroll-behavior:auto}}
@media (prefers-reduced-motion'''),
    ('  card(P.find(p => p.name === st.sel) || P[0]);', '''  const lk = [st.sort, st.asc, st.pos, st.team, st.q, st.page].join('|');
  if (lk !== listKey) { listKey = lk; document.querySelector('.tbox').scrollTop = 0; }
  tboxEdges();
  card(P.find(p => p.name === st.sel) || P[0]);'''),
    ("document.getElementById('q').oninput", '''let listKey = '';
function fitTable() {
  // 以「卡片頂端貼齊視窗頂」為準：卡片＋篩選列以下的空間都給表格
  const t = document.querySelector('.tbox'), above = t.getBoundingClientRect().top - document.getElementById('card').getBoundingClientRect().top;
  const h = innerWidth <= 640 ? innerHeight * 0.6 : Math.max(300, innerHeight - above - 12);
  t.style.maxHeight = Math.round(h) + 'px';
  tboxEdges();
}
// 捲過表頭才浮出陰影；下面還有列時底部淡出
function tboxEdges() {
  const t = document.querySelector('.tbox');
  t.classList.toggle('scrolled', t.scrollTop > 0);
  t.classList.toggle('below', t.scrollTop + t.clientHeight < t.scrollHeight - 2);
}
document.querySelector('.tbox').addEventListener('scroll', tboxEdges, { passive: true });
addEventListener('resize', fitTable);
addEventListener('load', fitTable);
document.fonts && document.fonts.ready.then(fitTable);

document.getElementById('q').oninput'''),
    # 手機卡片：右欄只放 OVR 會把左欄擠成一長條。改成名字＋資訊列在左、OVR 在右上，
    # 長處標籤與真實數據佔滿整寬（使用者 2026-10-29，Jokić）
    ('@media (prefers-reduced-motion', '''@media (max-width:640px){
  .card{grid-template-columns:1fr auto;gap:8px 10px;padding:12px 14px;align-items:start}
  .card .who{display:contents}
  .card .who>*{grid-column:1/-1}
  .card .who>.nm{grid-column:1;grid-row:1}
  .card .who>.facts{grid-column:1;grid-row:2;gap:2px 14px}
  .card .ring{grid-column:2;grid-row:1/3;padding:0;align-self:start}
}
@media (prefers-reduced-motion'''),
    # 表格捲軸（使用者 2026-10-29 要美化）：細、跟面板同色系、滑過才變亮。標準屬性 scrollbar-width／color
    # 給 Firefox、Chrome 121+、Safari 18.2+；不支援的舊 WebKit 才用 ::-webkit-scrollbar（Chrome 有標準屬性時會忽略它）。
    # 捲動提示照 Lea Verou／Roman Komarov 的捲動陰影：表頭捲過才有陰影、底部還有內容時淡出。
    # 儲存格有底色，背景漸層那招會被蓋掉，所以用 sticky 偽元素疊在上面。
    ('@media (prefers-reduced-motion', '''.tbox{scrollbar-width:thin;scrollbar-color:#3a4b60 transparent}
.tbox:hover{scrollbar-color:#5d7089 transparent}
@supports not (scrollbar-color:auto){
  .tbox::-webkit-scrollbar{width:10px;height:10px}
  .tbox::-webkit-scrollbar-track,.tbox::-webkit-scrollbar-corner{background:transparent}
  .tbox::-webkit-scrollbar-thumb{background:#3a4b60;border-radius:10px;border:3px solid var(--panel)}
  .tbox:hover::-webkit-scrollbar-thumb{background:#5d7089}
}
#tbl thead tr:last-child th{transition:box-shadow .15s}
.tbox.scrolled #tbl thead tr:last-child th{box-shadow:0 9px 10px -7px rgba(0,0,0,.75)}
.tbox::after{content:"";position:sticky;left:0;bottom:0;z-index:4;display:block;height:36px;margin-top:-36px;
  background:linear-gradient(rgba(24,34,47,0),var(--panel));pointer-events:none;opacity:0;transition:opacity .15s}
.tbox.below::after{opacity:1}
@media (prefers-reduced-motion'''),
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

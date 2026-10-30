"""名單頁的賽季切換列（靜態相對連結，沿用頁面既有 CSS 變數，不需 JS）。"""
import html
import re

# 標籤用年份（使用者 2026-10-29）：2027 beta＝2026-27 賽中，2026＝2025-26 正式卡
PAGES = [('inseason', '2027 beta', 'index.html'), ('card', '2026', '2025-26.html')]
CSS = """<style>
.top{position:relative;z-index:5}
.snav{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:6px 0 4px}
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
.sright{display:flex;align-items:center;gap:8px}
/* 手機：A+／99 搬到更新說明旁邊、兩個一起靠右，搜尋欄變長（使用者 2026-10-30） */
@media (max-width:640px){
  .snav{display:grid;grid-template-columns:1fr auto;gap:6px 10px}
  .snav .seg{justify-self:start}
  .snav.has-note .seg{grid-column:1/-1}
  .snav .note{line-height:1.4}
  .snav .pnote summary{height:32px;box-sizing:border-box;padding:0 10px}
  .snav #modeSeg{flex:none}
  .snav #modeSeg button{height:30px;padding:0 10px;font:600 .85rem var(--f-disp);letter-spacing:.04em}
}
.pn{position:absolute;left:0;top:calc(100% + 6px);width:min(560px,100%);max-height:min(72vh,680px);overflow:auto;overscroll-behavior:contain;box-sizing:border-box;
  background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:14px;box-shadow:0 16px 40px rgba(0,0,0,.6);scrollbar-width:thin;scrollbar-color:#38424f transparent}
.pn h2{font:800 1.05rem var(--f-disp);letter-spacing:.06em;margin:0 0 10px;text-transform:uppercase}
.pn h2 span{color:var(--gold)}
.pn-now{background:var(--panel-2);border:1px solid var(--line);border-radius:5px;padding:9px 12px;margin-bottom:12px;color:var(--muted);font-size:.78rem;line-height:1.6}
.pn-now b{display:block;color:var(--gold);font:700 .72rem var(--f-disp);letter-spacing:.12em;margin-bottom:2px}
.pn-now dl{display:flex;flex-wrap:wrap;gap:6px 24px;margin:4px 0 0}
.pn-now dt{color:var(--muted);font-size:.7rem}
.pn-now dd{margin:0;color:var(--fg);font:700 .95rem var(--f-disp);font-variant-numeric:tabular-nums}
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
.pn-item li b{color:var(--fg);font-weight:700}
.pn-item .kw{font-weight:700}
.pn-item .kw-ovr{color:var(--gold)}
.pn-item .kw-off{color:#ff7a45}
.pn-item .kw-def{color:#4fa8ff}
.pn-item .kw-etc{color:#c39bff}
.pn-item .kw-num{color:var(--fg);font-weight:700;font-variant-numeric:tabular-nums}
.pn-foot{margin:12px 0 0;color:var(--muted);font-size:.72rem;line-height:1.5}
</style>
"""


# 更新說明：每版一格，新的在上（使用者 2026-10-29）。track：card 正式卡、inseason 新賽季。
# 只寫公式改動（使用者 2026-10-30）：新賽季目前用的那版正式卡加 'inseason' 標籤（只留最新一格），不另開一格、不寫「已跟上／沒跟上」；
# 只更新比賽資料、網頁 UI、欄位顯示都不寫（R-063）；同一基底的字母小版本併進同一格（R-064）。
# 每條寫成「目標：做了什麼」（冒號前會加粗），用球迷看得懂的話，不寫 E／R 編號；代價一句帶過。
TRACK = {'card': '正式卡', 'inseason': '新賽季'}
PATCH_NOTES = [
    (('card', 'inseason'), '0.2.7', '2026-10-30', [
        '防守好的人分數不再被打折：防守越好加越多，Wembanyama 3 → 2 名、Derrick White 8 → 4 名。',
        '防守改看近期：越近的比賽份量越重。',
        '代價：防守普通的進攻型球員往下，Luka 4 → 9 名。',
        '0.2.7a 傳球看量也看率：每 36 分鐘助攻和助攻率各佔一半，Giannis 傳球 97.7 → 96.2、Trae Young 104.4 → 109.5；OVR 前 20 名只換一人。']),
    (('card',), '0.2.6', '2026-10-30', [
        '修正中距離被補籃墊高：補籃、補扣改算近距離（Kessler 中距離 99 → 61）。',
        '能力值改和最近四季一起比：偏弱的一季可以沒人到 99。',
        'OVR 重新擬合：近距離份量變重、中距離變輕，Giannis 11 → 5 名，Curry 23 → 32 名。']),
    (('card',), '0.2.5', '2026-10-29', [
        '分鐘權重改成遞減：上場少但效率高的人不再被埋沒（Caruso 103 → 39 名）。']),
    (('card',), '0.2.4', '2026-10-29', [
        '修正年輕球員被低估：教練用人（上場時間）改為只對照 2025-26 單季 RAPM。']),
    (('card',), '0.2.3', '2026-10-29', [
        '讓 OVR 反映教練實際怎麼用人：能力估計納入上場分鐘、出賽率、年齡、是否下放發展聯盟。',
        '輪休不算被冷凍：教練不用（DNP）和輪休分開計算。']),
    (('card',), '0.2.2', '2026-10-29', [
        '常站上罰球線的人分數更高：製造犯規（FD）改以量為主，每 36 分鐘罰球數佔 75%、罰球率佔 25%。']),
    (('card',), '0.2.1', '2026-10-29', [
        '降低壓迫（PRES）的雜訊：改用球員自己逼出的對手失誤、扣掉犯規，不再從 RAPM 拆出來。']),
    (('card',), '0.2.0', '2026-10-29', [
        'OVR 反映每場實際貢獻：改成每場價值，含上場時間、以替補水準為基準；每分鐘表現相同時，打得多的人 OVR 較高。']),
    (('card',), '0.1.2', '2026-10-28', [
        '修正位置標錯造成的防守誤判（例：Wembanyama 被標 F 卻守中鋒）：對位防守改算「被針對」，依對手實際的出手習慣算預期出手。']),
    (('card',), '0.1.1', '2026-10-28', [
        '分開衝框和造犯規兩種能力：「切入」拆成切入與製造犯規兩項。',
        '修正低分鐘球員虛胖：比率型能力值往本人上季拉回，沒有歷史才往聯盟平均。']),
    (('card',), '0.1.0', '', [
        '起點：正式卡沿用 v58 模型；新賽季用 C4 模型（上季卡當先驗、隨本季數據更新）。']),
]


def _now_facts(now_text, current):
    """從原本的長說明抽出幾個重點（使用者 2026-10-29：原文太長不適合人讀）；抽不到的欄位就不顯示。"""
    pick = lambda pat: (m.group(1) if (m := re.search(pat, now_text)) else None)
    if current == 'card':
        facts = [('版本', pick(r'card (\d+\.\d+\.\d+\w*)')), ('資料', pick(r'（(\d{4}-\d{2}) 整季')),
                 ('球員', pick(r'(\d+) 人'))]
    else:
        cutoff = pick(r'數據截至 (\d{4}-\d{2}-\d{2})')
        facts = [('版本', pick(r'inseason (\d+\.\d+\.\d+\w*)')), ('先驗', pick(r'先驗 card (\d+\.\d+\.\d+\w*)')),
                 ('數據截至', cutoff and cutoff[5:].replace('-', '/')), ('球員', pick(r'· (\d+) 人'))]
        if facts[1][1]:
            facts[1] = ('先驗', '正式卡 ' + facts[1][1])
    facts = [(k, v + ' 人' if k == '球員' else v) for k, v in facts if v]
    if not facts:
        return html.escape(now_text)
    return '<dl>' + ''.join(f'<div><dt>{k}</dt><dd>{html.escape(v)}</dd></div>' for k, v in facts) + '</dl>'


# 內文裡的數值名稱上色、數字加粗（使用者 2026-10-29，參考 arammeta 海克斯說明）。
# 只分四色：OVR 金、進攻＋投籃橘紅、防守藍、其他紫（使用者 2026-10-30 換色）；粗體目標裡的也上色；新名稱出現在說明裡就加進對應組。
NOTE_TERMS = {
    'ovr': ['OVR'],
    'off': ['三分價值', '3PT', '3P準', '罰球數', '罰球率', '罰球線', 'FD 製造犯規', '製造犯規（FD）', '製造犯規', '造犯規',
            '切入', '衝框', '中距離', '近距離', '補籃', '補扣', '進攻型球員'],
    'def': ['壓迫（PRES）', '壓迫', '對位防守', '防守加分', '防守數據', '防守'],
    'etc': ['RAPM', '上場時間', '上場分鐘', '出賽率', '預測 MPG', '每場價值', '分鐘權重', '教練用人', '替補水準', '輪休'],
}
_TERM_CLASS = {t: c for c, ts in NOTE_TERMS.items() for t in ts}
_NOTE_TOKEN = re.compile('|'.join(map(re.escape, sorted(_TERM_CLASS, key=len, reverse=True)))
                         + r'|(?<![A-Za-z\d.])\d+(?:\.\d+)*(?:-\d{2})?%?')


def _note_fmt(text):
    out, at = '', 0
    for m in _NOTE_TOKEN.finditer(text):
        tok, cls = html.escape(m.group(0)), _TERM_CLASS.get(m.group(0))
        out += html.escape(text[at:m.start()]) + (f'<span class="kw kw-{cls}">{tok}</span>' if cls
                                                   else f'<strong class="kw-num">{tok}</strong>')
        at = m.end()
    return out + html.escape(text[at:])


def _note_line(x):
    goal, sep, rest = x.partition('：')
    return f'<li><b>{_note_fmt(goal)}</b>：{_note_fmt(rest)}</li>' if sep else f'<li>{_note_fmt(x)}</li>'


def patch_notes_html(now_text, current):
    """now_text：原本 <div class="src"> 的版本說明，抽重點放最上面當「目前版本」；只標本頁那條線的版號（新賽季頁說明裡的先驗 card 版號不算）。"""
    cur = {(current, v) for v in re.findall(rf'\b{current} (\d+\.\d+\.\d+)', now_text)}
    items = []
    for tracks, ver, date, lines in PATCH_NOTES:
        is_cur = any((t, ver) in cur for t in tracks)
        items.append(
            f'<li class="pn-item tk-{tracks[0]}{" cur" if is_cur else ""}"><header>'
            + ''.join(f'<span class="pn-tag tk-{t}">{TRACK[t]}</span>' for t in tracks)
            + f'<b class="pn-ver">{ver}</b>'
            + ('<span class="pn-cur">目前</span>' if is_cur else '')
            + (f'<time datetime="{date}">{date[5:].replace("-", "/")}</time>' if date else '')
            + '</header><ul>' + ''.join(_note_line(x) for x in lines) + '</ul></li>')
    return ('<details class="pnote"><summary>更新說明</summary><div class="pn" role="region" aria-label="更新說明">'
            '<h2>Patch <span>Notes</span></h2>'
            f'<div class="pn-now"><b>目前版本</b>{_now_facts(now_text, current)}</div>'
            f'<ol class="pn-list">{"".join(items)}</ol>'
            '<p class="pn-foot">版號後面的字母（例如 0.2.1e）代表只更新比賽資料，模型沒動。新賽季版號跟它用的正式卡同號。</p></div></details>'
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
    # 手機寬度把 #modeSeg 從控制列搬進 .sright，桌機搬回搜尋欄前面
    mover = ("<script>addEventListener('DOMContentLoaded',()=>{const m=document.getElementById('modeSeg'),"
             "r=document.querySelector('.sright'),q=document.getElementById('q'),mq=matchMedia('(max-width:640px)');"
             "if(!m||!r||!q)return;const f=()=>mq.matches?r.append(m):q.before(m);f();mq.addEventListener('change',f)})</script>")
    block = lambda m: (f'\n<nav class="snav{" has-note" if note else ""}" aria-label="賽季切換"><div class="seg">{links}</div>{note}'
                       f'<span class="sright">{patch_notes_html(m.group(1), current)}</span>{mover}</nav>')
    s, n = re.subn(r'<div class="src">(.*?)</div>', block, html_str, count=1, flags=re.S)
    assert n == 1, 'src div not found'
    return s.replace('<nav class="snav', CSS + '<nav class="snav', 1) if CSS not in s else s


# 兩個頁面共用的樣板修補：數值模式的格子也要帶等第顏色（文字仍顯示數字）。
COMMON_REPLACEMENTS = [
    ("""  if (st.mode === 'num') return `<td class="${cls.join(' ')}">${v}</td>`;""",
     """  if (st.mode === 'num') { cls.push(gcls(grade(v))); return `<td class="${cls.join(' ')}">${v}</td>`; }"""),
    # tovSkill 是每次使用球權的失誤率，不是運球能力（使用者 2026-10-29：HDL 改成 TO）
    ("['tovSkill', 'HDL', '護球']", "['tovSkill', 'TO', '少失誤']"),
    # help 只量籃下 6 呎內命中差、只管禁區，實際是護框（使用者 2026-10-29）；欄位名 help 等 E-080 後再改
    ("['help', 'HELP', '協防']", "['help', 'RIM', '護框']"),
    # 體力現在是上場分鐘＋年齡，和分鐘欄重複，網站不顯示（R-057）；資料仍留著給 OVR 和引擎用
    (", ['stamina', 'STA', '體力']]", "]"),
    # 樣板原本是 artifact（外層代加 viewport），單獨放上 gh-pages 後手機會用 980px 排版再縮放，
    # 切換球員時資訊列行數一變就整頁重算縮放、看起來被拉長抖動（使用者 2026-10-29，Amen Thompson）
    ('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">'),
    # 資訊列每一項整塊換行，不要把「防守加分 +1.77」斷在中間
    ('.facts b{', '.facts>span{white-space:nowrap}\n.facts b{'),
    # 選中列原本整列金底＋深色字（!important），能力值顏色全被蓋掉；hover 時底色又被蓋回深色，整列變黑（使用者 2026-10-29）。
    # 改成每格保留原本顏色，選中列整列提亮成藍灰（名字格仍是金色，見 enrich_roster_viewer）。
    # 不用半透明金底：金疊深藍會混成橄欖綠，使用者 2026-10-29 嫌髒、廉價，demo 比較後選藍灰（A）
    ('tbody tr.sel td{background:var(--gold);color:var(--gold-ink)!important}',
     'tbody tr.sel td:not(.nm){background:#253040}\n'
     'tbody tr.sel:hover td:not(.nm){background:#2b3748}'),
    # 背景改冷炭：拿掉右上角藍色光暈，底色降彩度（使用者 2026-10-29 嫌雜色，demo 七個炭灰方向選 F）。
    # 排序欄金色淡底疊深色也會偏橄欖綠，改中性淡白
    ('  --bg:#0f1622; --panel:#18222f; --panel-2:#1f2b3a; --line:#2c3a4c;',
     '  --bg:#0d1014; --panel:#151a20; --panel-2:#1c222a; --line:#29313b;'),
    ('background-image:radial-gradient(1200px 500px at 85% -10%,#22324a 0%,transparent 60%);', ''),
    ('thead th{background:#0b1119;', 'thead th{background:#0a0d10;'),
    ('td.sortcol{background:rgba(242,194,48,.07)}', 'td.sortcol{background:rgba(255,255,255,.035)}'),
    ('fill="#0b1119" stroke="#2c3a4c"', 'fill="#0a0d10" stroke="#29313b"'),
] + [
    # 上場篩選拿掉（手機太擠，門檻也還是整季總分鐘），換成球隊篩選：仿 arammeta 的彈出格子（使用者 2026-10-29）
    ('''    <span class="lbl">上場</span>
    <div class="seg" id="minSeg"></div>''',
     '''    <span class="tgrp"><span class="lbl">球隊</span>
    <details class="tpick" id="teamPick"><summary aria-label="選擇球隊"></summary><div class="tpop"><div class="tgrid" id="teamGrid"></div></div></details></span>'''),
    ("pos: 'ALL', min: 0,", "pos: 'ALL', team: 'ALL', rk: false,"),
    ('p.min >= st.min', "(st.team === 'ALL' || p.team.split('/').pop() === st.team) && (!st.rk || ROOKIES.has(p.name))"),
    # 兩個 builder 已先把門檻改成場均 10／20／30 分鐘
    ("  seg('minSeg', [[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']], 'min');\n", '  teamPick();\n'),
    ('放寬位置或上場分鐘試試', '放寬位置或球隊試試'),
    # 表格自己捲（使用者 2026-10-29：看低排名時頭像卡仍在畫面上）。高度＝卡片下方剩餘視窗，只在載入／縮放時算，
    # 點球員不改高度；換排序、篩選、頁才捲回頂。手機篩選移到卡片上方後卡片放得下，也照卡片下方剩餘高度算；
    # 手機表格捲動不傳給頁面、不回彈（使用者 2026-10-29：拖表格有時整頁一起動，捲到頂再拉會露出一大片空白）。
    ('.tbox{overflow-x:auto;', '.tbox{overflow:auto;max-height:70vh;overscroll-behavior:contain;'),
    # top:-1px：border-collapse 的半像素邊框會在表頭上緣留一條縫，捲過的列從縫裡露出來
    ('@media (prefers-reduced-motion', '''#tbl thead{position:sticky;top:-1px;z-index:3}
@media (max-width:640px){.tbox{overscroll-behavior:none}}
@media (prefers-reduced-motion'''),
    ('  card(P.find(p => p.name === st.sel) || P[0]);', '''  const lk = [st.sort, st.asc, st.pos, st.team, st.rk, st.q, st.page].join('|');
  if (lk !== listKey) { listKey = lk; document.querySelector('.tbox').scrollTop = 0; }
  tboxEdges();
  card(P.find(p => p.name === st.sel) || P[0]);'''),
    ("document.getElementById('q').oninput", '''let listKey = '';
function fitTable() {
  // 以「卡片頂端貼齊視窗頂」為準：卡片＋篩選列以下的空間都給表格
  const t = document.querySelector('.tbox'), above = t.getBoundingClientRect().top - document.getElementById('card').getBoundingClientRect().top;
  const h = Math.max(innerWidth <= 640 ? 240 : 300, innerHeight - above - 12);
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
    ('@media (prefers-reduced-motion', '''.tbox{scrollbar-width:thin;scrollbar-color:#38424f transparent}
.tbox:hover{scrollbar-color:#56616f transparent}
@supports not (scrollbar-color:auto){
  .tbox::-webkit-scrollbar{width:10px;height:10px}
  .tbox::-webkit-scrollbar-track,.tbox::-webkit-scrollbar-corner{background:transparent}
  .tbox::-webkit-scrollbar-thumb{background:#38424f;border-radius:10px;border:3px solid var(--panel)}
  .tbox:hover::-webkit-scrollbar-thumb{background:#56616f}
}
#tbl thead tr:last-child th{transition:box-shadow .15s}
.tbox.scrolled #tbl thead tr:last-child th{box-shadow:0 9px 10px -7px rgba(0,0,0,.75)}
.tbox::after{content:"";position:sticky;left:0;bottom:0;z-index:4;display:block;height:36px;margin-top:-36px;
  background:linear-gradient(rgba(21,26,32,0),var(--panel));pointer-events:none;opacity:0;transition:opacity .15s}
.tbox.below::after{opacity:1}
@media (prefers-reduced-motion'''),
    # 顯示切換直接用範例當標籤（使用者 2026-10-29）
    ("seg('modeSeg', [['grade', '等第'], ['num', '數值']], 'mode');", "seg('modeSeg', [['grade', 'A+'], ['num', '99']], 'mode');"),
    # A+／99 是網站設定：選了就存在瀏覽器（localStorage，同網域兩個賽季頁共用），切換賽季頁不變（使用者 2026-10-30）
    ("mode: 'grade',", "mode: (() => { try { return localStorage.getItem('bbac.mode') === 'num' ? 'num' : 'grade'; } catch (e) { return 'grade'; } })(),"),
    ("b.onclick = () => { st[key] = v;",
     "b.onclick = () => { st[key] = v; if (key === 'mode') try { localStorage.setItem('bbac.mode', v); } catch (e) {}"),
    ('function render() {', '''function teamPick() {
  const d = document.getElementById('teamPick'), grid = document.getElementById('teamGrid');
  const logo = t => `<img alt="" src="https://cdn.nba.com/logos/nba/${TEAM_IDS[t]}/global/D/logo.svg" onerror="this.style.visibility='hidden'">`;
  if (!grid.childElementCount) {
    const teams = [...new Set(P.map(p => p.team.split('/').pop()))].filter(t => TEAM_IDS[t]).sort();
    // 新秀放在球隊面板裡、跟「全部球隊」並排（使用者 2026-10-30）；2027 頁沒有新秀時「全部球隊」佔整排
    grid.innerHTML = `<button type="button" class="all${ROOKIES.size ? ' half' : ''}" data-t="ALL">全部球隊</button>` +
      (ROOKIES.size ? '<button type="button" class="all half" data-t="ROOKIE">新秀</button>' : '') +
      teams.map(t => `<button type="button" data-t="${t}" title="${t}">${logo(t)}<span>${t}</span></button>`).join('');
    grid.onclick = e => {
      const b = e.target.closest('button[data-t]');
      if (!b) return;
      st.rk = b.dataset.t === 'ROOKIE'; st.team = st.rk ? 'ALL' : b.dataset.t; st.page = 0; st.extra = 0; d.open = false; render();
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
  const cur = st.rk ? 'ROOKIE' : st.team;
  d.querySelector('summary').innerHTML = cur === 'ALL' ? '全部' : cur === 'ROOKIE' ? '新秀' : logo(cur) + cur;
  d.classList.toggle('on', cur !== 'ALL');
  grid.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.t === cur)));
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
.tgrid button.all.half{grid-column:span 3}
.tgrid button:hover{border-color:var(--muted);color:var(--fg)}
.tgrid button[aria-pressed="true"]{border-color:var(--gold);color:var(--gold);background:#2a2410}
@media (prefers-reduced-motion'''),
]


def apply_common(s):
    for a, b in COMMON_REPLACEMENTS:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    return _compact_facts(s)


# 球員卡資訊列（使用者 2026-10-29：字太多；模擬每 36 分鐘淨值和下方 RAPM「淨影響」看起來同一件事卻不同數字）。
# 模擬值拿掉、改放 OVR 圓環的滑鼠提示；手機藏掉「球隊／身高」這類標籤；新賽季頁較上季差值用綠／灰／紅三色（不漸變）。
# 每格帶 class；手機版只留較上季（箭頭），身高移到隊色橫幅（使用者 2026-10-29：手機用減法）
FACT_LABELS = {'球隊 ': 'f-tm', '身高 ': 'f-ht', '場均 ': 'f-min', '已打 N=': 'f-gp', '出賽 ': 'f-gp'}
DELTA_OLD = "<span>上季卡 OVR <b>${p.last.toFixed(1)}</b>（<b>${(p.dovr > 0 ? '+' : '') + p.dovr.toFixed(2)}</b>）</span>"
# 手機版（.sm）只顯示箭頭＋絕對值，例如紅色 ▼4.3（使用者 2026-10-29）；桌機（.lb）照舊帶正負號
DELTA_NEW = ("<span class=\"f-d\" title=\"較上季卡 OVR ${p.last.toFixed(1)}\"><i class=\"lb\">上季卡 OVR <b>${p.last.toFixed(1)}</b>（</i>"
             "<b class=\"${p.dovr >= 1 ? 'up' : p.dovr <= -1 ? 'dn' : 'flat'}\">"
             "<i class=\"sm\">${p.dovr >= 0.05 ? '▲' : p.dovr <= -0.05 ? '▼' : '＝'}</i>"
             "<i class=\"lb\">${(p.dovr > 0 ? '+' : '') + p.dovr.toFixed(1)}</i>"
             "<i class=\"sm\">${Math.abs(p.dovr).toFixed(1)}</i></b>"
             "<i class=\"lb\">）</i></span>")
# 桌機卡片（使用者 2026-10-29）：身高寫在名字旁；第一排不放球隊，改成分鐘、場次、得分／籃板／助攻；
# 較上季比照手機掛在 OVR 圓環下（箭頭＋絕對值）；下方真實數據只留細項小字（版面在 enrich_roster_viewer.CSS）
NAME_OLD = '<div class="nm"><span class="first">${esc(first)}</span>${esc(last)}</div>'
NAME_NEW = '<div class="nm"><span class="first">${esc(first)}</span>${esc(last)}<span class="nht">${ht(p.ht)}</span></div>'
BIG3 = ("${(r => r ? [['得分', r.pts], ['籃板', r.reb], ['助攻', r.ast]]"
        ".map(([l, v]) => `<span class=\"f-b\">${l} <b>${v.toFixed(1)}</b></span>`).join('') : '')(REAL[p.name])}")
RING_END = 'class="val">${p.ovr.toFixed(1)}</text></svg></div>'
RING_DELTA = ("class=\"val\">${p.ovr.toFixed(1)}</text></svg>"
              "<b class=\"rd ${p.dovr >= 1 ? 'up' : p.dovr <= -1 ? 'dn' : 'flat'}\" title=\"較上季卡 OVR ${p.last.toFixed(1)}\">"
              "${p.dovr >= 0.05 ? '▲' : p.dovr <= -0.05 ? '▼' : '＝'}${Math.abs(p.dovr).toFixed(1)}</b></div>")


def _compact_facts(s):
    s, n = re.subn(r'\n\s*<span>(?:新賽季預測|模擬)每 36 分鐘淨值 <b>\$\{p\.imp[^\n]*</span>', '', s)
    assert n == 1
    ring = '<div class="ring"><svg'
    assert s.count(ring) == 1
    s = s.replace(ring, '<div class="ring" title="模型用能力值模擬的每 36 分鐘淨值 ${(p.imp > 0 ? \'+\' : \'\') + p.imp.toFixed(2)}'
                        '（OVR 由此換算；下方「影響」是真實比賽的 RAPM，兩者不同）"><svg')
    # 圓環滿格＝當季最高 OVR（使用者 2026-10-29）；原本固定 99，OVR 破百的人全都滿圈
    fill = '(p.ovr - 40) / (99 - 40)'
    assert s.count(fill) == 1
    s = s.replace(fill, '(p.ovr - 40) / (OVR_TOP - 40)')
    top = 'const P = DATA.rows.map(r => Object.fromEntries(COLS.map((c, i) => [c, r[i]])));'
    assert s.count(top) == 1
    s = s.replace(top, top + '\nconst OVR_TOP = Math.max(...P.map(p => p.ovr));')
    for lab, c in FACT_LABELS.items():
        s = s.replace(f'<span>{lab}<b>', f'<span class="{c}"><i class="lb">{lab}</i><b>')
    # 防守加分改叫防守意識（使用者 2026-10-30）：真實防守 RAPM 高於同位置平均的部分，補能力值量不到的輪轉、站位
    s = s.replace('<span>防守加分 <b>', '<span class="f-x" title="真實比賽的防守影響力高於同位置平均的部分（防守 RAPM），'
                  '補能力值量不到的輪轉、站位、補位；只有正值，會加進 OVR">防守意識 <b>')
    assert s.count(NAME_OLD) == 1
    s = s.replace(NAME_OLD, NAME_NEW)
    s, n = re.subn(r'(<span class="f-gp">.*?</span>)', lambda m: m.group(1) + BIG3, s, count=1)
    assert n == 1
    assert s.count(DELTA_OLD) <= 1
    if DELTA_OLD in s:
        assert s.count(RING_END) == 1
        s = s.replace(RING_END, RING_DELTA)
    return s.replace(DELTA_OLD, DELTA_NEW)

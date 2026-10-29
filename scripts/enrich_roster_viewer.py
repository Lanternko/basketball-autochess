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
GC = ROOT / 'reports' / 'game-contribution'  # 單場貢獻值：box → RAPM 權重與 2025-26 基準（scripts/fit_game_contribution.py）
CARD_SUMMARY = ROOT / 'reports' / 'card-0.2.6' / 'summary.json'  # 正式卡 OVR 錨點（換算 OVR 傾向）

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
/* 能力值欄一樣寬（使用者 2026-10-29）：原本被中文副標長短撐開 35–67px；副標縮小讓四字（製造犯規）也放得下一行 */
#tbl thead tr:last-child th[data-k]:not([data-k=name],[data-k=pos],[data-k=team],[data-k=ht],[data-k=ovr],[data-k=min],[data-k=gp],[data-k=dovr]){
  width:48px;min-width:48px;box-sizing:border-box}
#tbl thead tr:last-child th[data-k]:not([data-k=name],[data-k=pos],[data-k=team],[data-k=ht],[data-k=ovr],[data-k=min],[data-k=gp],[data-k=dovr]) .zh{font-size:.62rem}
/* 名字欄不再整條金底（使用者 2026-10-29：醜、被列線切得斷裂）；改深色底，只有選中列金色 */
#tbl th.nm{background:#0a0d10;color:var(--muted)}
#tbl td.nm{background:var(--panel);color:var(--fg);box-shadow:inset -1px 0 0 var(--line)}
#tbl tbody tr:hover td.nm{background:var(--panel-2)}
#tbl tbody tr.sel td.nm{background:var(--gold);color:var(--gold-ink)}
/* 手機表格（使用者 2026-10-29）：拿掉 OVR 左邊的位置／球隊／身高；表格手勢由 JS 鎖方向（偏垂直就整段只上下捲，手抖不左右晃）；表頭與名字／OVR 欄的手勢捲整頁（2026-10-30） */
@media (max-width:640px){
  #tbl thead tr:last-child th:is([data-k=pos],[data-k=team],[data-k=ht]),#tbl tbody td:is(:nth-child(3),:nth-child(4),:nth-child(5)):not([colspan]),#tbl th.gx{display:none}
  .tbox{touch-action:none}
  /* 左右捲時群組標題（投籃…）的左框不滑到 OVR 上方：最左那格群組標題釘住，# 欄 28px 捲走後右緣剛好停在 OVR 右側 */
  #tbl th.noh,#tbl td.no{width:28px;min-width:28px;max-width:28px;box-sizing:border-box}
  #tbl tr.grp th:first-child{position:sticky;left:-28px;z-index:3;box-shadow:6px 0 6px -5px rgba(0,0,0,.7)}
}
/* 手機名字欄縮寫（使用者 2026-10-29：全名佔四成寬）：Stephen Curry → S. Curry，太長的截成 … */
#tbl td.nm .ns{display:none}
@media (max-width:640px){#tbl td.nm .nf{display:none}#tbl td.nm .ns{display:inline}}
/* 手機表格（使用者 2026-10-29：很難用）：名字欄變窄可換行、列變矮；OVR 往右滑時釘在名字旁邊，長按不選字 */
@media (max-width:640px){
  #tbl td{padding:5px 3px;font-size:.92rem}
  #tbl th.nm,#tbl td.nm{width:88px;min-width:88px;max-width:88px;box-sizing:border-box;padding-left:6px}
  #tbl td.nm{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.1;font-size:.86rem}
  #tbl td.no{width:28px;font-size:.78rem}
  #tbl th[data-k="ovr"],#tbl td.ovr{position:sticky;left:88px;z-index:1;box-shadow:6px 0 6px -5px rgba(0,0,0,.7)}
  #tbl th[data-k="ovr"]{z-index:2}
  #tbl tbody td.ovr{background:var(--panel);font-size:1rem}
  #tbl tbody td.ovr.sortcol{background:linear-gradient(rgba(255,255,255,.035),rgba(255,255,255,.035)) var(--panel)}
  #tbl tbody tr:hover td.ovr{background:var(--panel-2)}
  #tbl tbody tr.sel td.ovr{background:#253040}
  #tbl tbody{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
}
/* team colors + headshot */
.card .tag{background:var(--card,var(--red));box-shadow:inset 0 -7px 0 var(--tc,transparent);position:relative;min-width:230px}
.tag .pos{background:var(--tc,#fff);color:#fff;position:relative;z-index:1}
.tag .rk{position:relative;z-index:1;color:var(--ink,#fff);text-shadow:0 0 8px var(--card,#000)}
.tag .logo{position:absolute;right:30px;top:50%;transform:translateY(-50%);height:150px;width:150px;object-fit:contain;opacity:.9;pointer-events:none}
.tag .shot{position:absolute;right:26px;bottom:7px;height:132px;width:auto;pointer-events:none}
/* 手機卡片（使用者 2026-10-29：沒有頭像和隊徽；名字和頭像放一起；字太多，用減法）
   隊色橫幅左上放位置＋身高，右上角放排名（和位置同款隊色小標），名字（.tnm/.tht 只在手機顯示）和頭像；下面 OVR 圓環下方掛較上季箭頭，右邊影響力 2×2；
   資訊列其餘（球隊、分鐘、場數、防守加分）不顯示；真實數據只留得分／籃板／助攻三大格 */
.tag .tnm,.tag .tht{display:none}
@media (max-width:640px){
  .card{grid-template-columns:auto 1fr;gap:10px 12px}
  .card .tag{display:flex;flex-direction:row;align-items:center;justify-content:flex-start;gap:8px;grid-column:1/-1;grid-row:1;margin:-12px -14px 0;min-width:0;height:128px;clip-path:none;padding:10px 14px}
  .tag .pos{align-self:flex-start;line-height:19px}
  .tag .tht{display:block;order:1;align-self:flex-start;font:700 1.05rem/21px var(--f-disp);color:var(--ink,#fff);position:relative;z-index:1}
  .tag .rk{position:absolute;top:10px;right:14px;z-index:3;font:700 1rem/19px var(--f-disp);text-shadow:none;background:var(--tc,#fff);color:#fff;padding:1px 8px;border-radius:3px}
  .tag .rk small{font-size:1em;opacity:1;margin:0}
  .tag .logo{right:14px;height:110px;width:110px;opacity:.9}
  .tag .shot{right:6px;height:121px}
  .tag .tnm{display:block;position:absolute;left:14px;right:136px;bottom:15px;z-index:1;font:800 1.55rem/.95 var(--f-disp);text-transform:uppercase;color:var(--ink,#fff);text-shadow:0 0 8px var(--card,#000);overflow-wrap:anywhere}
  .tag .tnm span{display:block;font-size:.9rem;font-weight:600;opacity:.85;margin-bottom:3px}
  .card .who>.nm{display:none}
  .card .ring{grid-column:1;grid-row:2;align-self:end}
  .card .ring svg{width:76px;height:76px}
  .card .who>.facts{grid-column:1;grid-row:3;align-self:start;justify-content:center;display:flex;margin-top:-4px}
  .facts>span:not(.f-d){display:none}
  .facts .f-d b{font:700 1.15rem var(--f-disp)}
  .card .who>.strong{grid-column:2;grid-row:2/5;align-self:center;display:grid;grid-template-columns:repeat(2,1fr);gap:4px}
  .strong .chip{display:flex;flex-direction:column;align-items:center;padding:4px 2px;font-size:.72rem;color:var(--muted);letter-spacing:0}
  .strong .chip i{margin:0;font:700 1.1rem var(--f-disp)}
  .strong .chip.dim{grid-column:1/-1}
  .rx .rmain{flex:1}
  .rx .rmain .st{flex:1}
  /* 場數／分鐘併到 OVR 圓環下方，三大項縮小並補正負值（使用者 2026-10-29：省空間）；交易隊名手機不顯示 */
  .card .who>.real-h{grid-column:1;grid-row:4;justify-self:center;margin-top:-6px;white-space:nowrap;font-size:.7rem;letter-spacing:.02em}
  .real-h .rtm{display:none}
  .rx .rmain .st{min-width:0;padding:3px 4px}
  .rx .rmain .st b{font-size:1.2rem}
  .rx .rmain .st span{font-size:.64rem}
  .rx .rsub{display:none}
}
/* 桌機卡片：影響力四格改 2×2，和 OVR 圓環放同一側（使用者 2026-10-29：省空間）
   .who 拆開讓子元素直接排進 .card 格線：寬螢幕 2×2 在圓環左邊；窄一點（<1100px）疊在圓環下面，讓中間欄夠寬
   比照手機（使用者 2026-10-30）：資訊列拿掉，得分／籃板／助攻／正負值改大格、細項小字在旁；場數·分鐘掛在 OVR 圓環下 */
@media (min-width:641px){
  .card{grid-template-columns:auto minmax(0,1fr) auto auto;row-gap:10px}
  .card .tag{grid-column:1;grid-row:1/span 3}
  .card .who{display:contents}
  .card .who>*{grid-column:2;margin-inline:18px}
  .card .who>.nm{grid-row:1;margin-top:14px;align-self:end}
  .card .who>.facts{display:none}
  .card .who>.real{grid-row:2/span 2;align-self:start;margin-bottom:14px}
  .card .who>.strong{grid-column:3;grid-row:1/span 3;align-self:center;margin:14px 0;display:grid;grid-template-columns:repeat(2,1fr);gap:6px}
  .strong .chip{display:flex;flex-direction:column;align-items:center;min-width:84px;padding:6px 8px;font-size:.74rem;color:var(--muted);letter-spacing:0}
  .strong .chip i{margin:2px 0 0;font:700 1.3rem var(--f-disp)}
  .strong .chip.dim{grid-column:1/-1}
  .card .ring{grid-column:4;grid-row:1/span 2;align-self:end;padding:14px 22px 0}
  .card .who>.real-h{grid-column:4;grid-row:3;align-self:start;justify-self:center;margin:-4px 18px 14px;white-space:nowrap;letter-spacing:.02em}
  .real-h .rtm{display:none}
  /* 身高在名字旁；較上季掛圓環下 */
  .who .nm .nht{margin-left:12px;font-size:1.1rem;font-weight:600;color:var(--muted);text-transform:none;white-space:nowrap}
  .card .ring{flex-direction:column;gap:2px}
  .ring .rd{font:700 1.25rem var(--f-disp);font-variant-numeric:tabular-nums}
  .ring .rd.up{color:var(--g-a)}
  .ring .rd.dn{color:var(--g-f)}
  .ring .rd.flat{color:var(--muted)}
  .rx .rmain .st{min-width:74px}
  .card .who>.g5{grid-column:1/-1;grid-row:4;margin:0 18px 14px}
}
.who .nm .nht,.ring .rd{display:none}
@media (min-width:641px){.who .nm .nht,.ring .rd{display:inline}}
@media (min-width:641px) and (max-width:1099px){
  .card{grid-template-columns:auto minmax(0,1fr) auto}
  .card .ring{grid-column:3;grid-row:1;padding:14px 18px 0}
  .card .who>.real-h{grid-column:3;grid-row:2;margin:-4px 18px 0}
  .card .who>.strong{grid-column:3;grid-row:3;align-self:start;margin:0 18px 14px}
  /* 中間欄窄：四大格平分寬度、字縮小，不壓到右邊影響力 */
  .rx .rmain{flex:1 1 100%}
  .rx .rmain .st{flex:1 1 0;min-width:0;padding:4px 6px}
  .rx .rmain .st b{font-size:1.4rem}
}
/* 近 N 場逐場數據（使用者 2026-10-30：數據旁的 ▼ 展開，像 NBA box score） */
.rx .g5t{flex-basis:100%;display:flex;align-items:center;gap:6px;background:none;border:0;border-top:1px solid var(--line);padding:6px 0 0;
  color:var(--muted);font:600 .8rem var(--f-disp);letter-spacing:.04em;cursor:pointer;text-align:left}
.rx .g5t:hover{color:var(--fg)}
.rx .g5t i{display:inline-block;font-style:normal;font-size:.75em;transition:transform .15s}
.rx .g5t[aria-expanded="true"] i{transform:rotate(180deg)}
.card .g5{justify-self:start;min-width:0;max-width:100%;box-sizing:border-box;overflow-x:auto;border:1px solid var(--line);border-radius:3px;background:var(--panel-2);scrollbar-width:thin;scrollbar-color:#38424f transparent}
.g5 table{min-width:0;border-collapse:collapse;font-variant-numeric:tabular-nums;white-space:nowrap}
.g5 th{background:none;cursor:default;color:var(--muted);font:600 .7rem var(--f-disp);letter-spacing:.04em;text-align:right;padding:6px 10px;border-bottom:1px solid var(--line)}
.g5 td{text-align:right;padding:5px 10px;border-bottom:1px solid var(--line);color:var(--fg);font:500 .9rem var(--f-disp);letter-spacing:.02em}
.g5 :is(th,td):is(:nth-child(1),:nth-child(2)){text-align:left}
.g5 td:nth-child(5){font-weight:700}
.g5 td .w{color:var(--g-a);font-weight:700}
.g5 td .l{color:var(--g-f);font-weight:700}
.g5 tfoot td{color:var(--muted);border-bottom:0}
.g5 .up{color:var(--g-a)}
.g5 .dn{color:var(--g-f)}
.g5 .gcn{position:sticky;left:0;max-width:0;min-width:100%;box-sizing:border-box;padding:6px 10px 7px;border-top:1px solid var(--line);color:var(--muted);font-size:.74rem;line-height:1.5;white-space:normal}
.g5 .gcn b{font:600 .86rem var(--f-disp);font-variant-numeric:tabular-nums;color:var(--fg)}
.g5 .c5a,.g5 .gcn b.c5a{color:var(--g-a)}
.g5 .c5b,.g5 .gcn b.c5b{color:var(--g-b)}
.g5 .c5c,.g5 .gcn b.c5c{color:#a3abb5}
.g5 .c5d,.g5 .gcn b.c5d{color:#f09a8c}
.g5 .c5f,.g5 .gcn b.c5f{color:var(--g-f)}
@media (max-width:1099px){.g5 th,.g5 td{padding-inline:7px}}
@media (max-width:640px){
  .g5 td{font-size:.84rem}
  .g5 th,.g5 td{padding:5px 6px}
  /* 手機 ▼ 放正負值格右上角（使用者 2026-10-30）：右上切一個斜角變五角形，▼ 放在切掉的位置，不另佔一列
     ▼ 用正三角形（60°），缺角也切 60°（橫 16px、直 27.7px），▼ 左斜邊和缺角平行、留 3px 不碰框；展開時不翻轉，改變金色 */
  .real.rx{position:relative}
  .rx .rmain .st:last-child{position:relative;clip-path:polygon(0 0,calc(100% - 16px) 0,100% 27.7px,100% 100%,0 100%)}
  .rx .rmain .st:last-child::after{content:'';position:absolute;top:-1px;right:-1px;width:16px;height:27.7px;pointer-events:none;
    background:linear-gradient(to bottom left,transparent calc(50% - 1px),var(--line) calc(50% - 1px),var(--line) calc(50% + 1px),transparent calc(50% + 1px))}
  .rx .g5t{position:absolute;top:-8.6px;right:-11.4px;width:30px;height:30px;padding:0;border:0;font-size:0;justify-content:center}
  .rx .g5t i,.rx .g5t[aria-expanded="true"] i{display:block;width:9px;height:7.8px;background:var(--muted);clip-path:polygon(0 0,100% 0,50% 100%);transform:none;transition:background .15s}
  .rx .g5t[aria-expanded="true"] i{background:var(--gold)}
}
.tabbr{color:var(--tt);font-weight:600}
/* impact chips：RAPM 攻守淨（對聯盟平均）、在場減不在場（每 100 回合） */
.chip i.up{color:var(--g-a)}
.chip i.dn{color:var(--g-f)}
.chip i.flat{color:var(--muted)}
/* 手機篩選列（使用者 2026-10-29：卡片和表格要能同時看到，篩選擋在中間）：整排移到卡片上方，擠成一排、一樣高；
   位置改成點了才展開的下拉（.pbtn），球隊沒選時顯示「球隊」。桌機也把篩選列移到卡片上方（使用者 2026-10-30） */
.pbtn{display:none}
.wrap>.top{order:-2}
.wrap>.ctrl{order:-1}
@media (max-width:640px){
  .wrap>.ctrl{position:relative;flex-wrap:nowrap;gap:6px}
  .ctrl .lbl{display:none}
  .ctrl .tgrp{display:contents}
  .ctrl .pbtn,.ctrl .tpick summary,.ctrl input[type=search]{height:32px;box-sizing:border-box;padding:0 10px}
  .ctrl .pbtn,.ctrl .tpick summary,.ctrl .seg button{font:600 .85rem var(--f-disp);letter-spacing:.04em}
  .ctrl .pbtn{display:flex;align-items:center;gap:6px;flex:none;background:var(--panel);color:var(--muted);border:1px solid var(--line);border-radius:3px;cursor:pointer}
  .ctrl .pbtn::after{content:"▾";font-size:.8em;opacity:.8}
  .ctrl .pbtn.on{background:var(--gold);color:var(--gold-ink);border-color:var(--gold)}
  .ctrl.popen .pbtn:not(.on){color:var(--fg);border-color:var(--muted)}
  #teamPick:not(.on) summary{font-size:0}
  #teamPick:not(.on) summary::before{content:"球隊";font-size:.85rem}
  #teamPick summary::after{font-size:.7rem}
  .ctrl .seg{flex:none}
  .ctrl .seg button{height:30px;padding:0 10px}
  .ctrl input[type=search]{flex:1;min-width:0;width:auto;font-size:.85rem}
  #posSeg{display:none}
  .ctrl.popen #posSeg{display:flex;position:absolute;left:0;top:calc(100% + 6px);z-index:20;box-shadow:0 12px 32px rgba(0,0,0,.55)}
  .ctrl.popen #posSeg button{height:38px;padding:0 13px}
}
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
// 手機表格用的縮寫名：名縮成首字母，姓（含 Jr. 等）照留
const shortName = n => { const i = n.indexOf(' '); return i > 0 ? n[0] + '. ' + n.slice(i + 1) : n; };
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
  const main = [['得分', f1(r.pts)], ['籃板', f1(r.reb)], ['助攻', f1(r.ast)], ['正負值', pm(r.pm)]];
  const sub = [[['命中率', pc(r.fg)], ['三分', pc(r.fg3)], ['罰球', pc(r.ft)], ['真實命中', pc(r.ts)]],
    [['抄截', f1(r.stl)], ['阻攻', f1(r.blk)], ['失誤', f1(r.tov)]]];
  // 標題只留場數和場均分鐘（使用者 2026-10-29：「例行賽真實數據」字太多）
  const n = r.g5.length;
  return `<div class="real-h">${r.gp} 場 · ${Math.round(r.mpg)} 分鐘${r.teams.length > 1 ? '<span class="rtm"> · ' + r.teams.join('/') + '</span>' : ''}</div>
      <div class="real rx"><div class="rmain">${main.map(([l, v]) => `<div class="st"><b>${v}</b><span>${l}</span></div>`).join('')}</div>
      <div class="rsub">${sub.map(g => `<div>${g.map(([l, v]) => `<span>${l}<b>${v}</b></span>`).join('')}</div>`).join('')}</div>
      <button type="button" class="g5t" aria-expanded="${G5_OPEN}" aria-label="近 ${n} 場比賽" title="近 ${n} 場比賽" onclick="toggleG5(this)"><i>▼</i>近 ${n} 場比賽</button></div>
      <div class="g5"${G5_OPEN ? '' : ' hidden'}>${gameLog(r, p)}</div>`;
}
// 近 N 場逐場（新到舊）：[日期, 對手, 勝負, 分鐘, 得分, 籃板, 助攻, 抄截, 阻攻, 失誤, 投進, 出手, 三分進, 三分出手, 罰進, 罰球, 正負值, 貢獻值]
let G5_OPEN = false;
function toggleG5(b) {
  G5_OPEN = !G5_OPEN;
  b.setAttribute('aria-expanded', String(G5_OPEN));
  document.querySelector('.card .g5').hidden = !G5_OPEN;
  if (typeof fitTable === 'function') fitTable();
}
// 貢獻值（使用者 2026-10-30 選 A）：box score 換算的每 36 分鐘淨影響（權重擬合 2025-26 RAPM），和 2025-26 整季比；
// OVR 傾向＝把差值當成 pred 的變動，照正式卡（card 0.2.6）的錨點與分鐘權重 W(MPG) 換算（只顯示，不改 OVR）
// 數字寫絕對值，顏色看和自己平均的差（使用者 2026-10-30：同樣 +3，替補是進步、SGA 是退步）：
// 五色切點＝2025-26 全部比賽「貢獻值 − 自己整季平均」絕對值的 20／60 百分位，各色約兩成（使用者 2026-10-30 選單場、5 場分開切）：
// 單場（上場 ≥10 分鐘，SD 3.0）±0.7／±2.4；近 5 場合計（SD 1.3）±0.3／±1.1。顏色是排名，不代表顯著
const GC_CUT1 = [0.7, 2.4], GC_CUT5 = [0.3, 1.1];
const sg1 = v => (v > 0 ? '+' : '') + v.toFixed(1);
const gcCls = (d, [a, b]) => d >= b ? 'c5a' : d >= a ? 'c5b' : d > -a ? 'c5c' : d > -b ? 'c5d' : 'c5f';
function gcCell(v, b, cut) {
  if (v == null) return '<td>—</td>';
  return `<td><span class="${b == null ? '' : gcCls(v - b, cut)}">${sg1(v)}</span></td>`;
}
function gcNote(r, p, n) {
  const c = r.gc;
  if (c.r == null) return '';
  // 說明只寫兩個數字（使用者 2026-10-30：太長）；五色怎麼切、換算 OVR 放 tooltip
  if (c.b == null) return `<div class="gcn">${n} 場平均貢獻 <b>${sg1(c.r)}</b>　上季 —</div>`;
  const d = c.r - c.b, cls = gcCls(d, GC_CUT5);
  const [p1, p50, p99] = GC_ANC, w = (1 - Math.exp(-r.mpg / 15)) / (1 - Math.exp(-36 / 15));
  const toG = o => o <= 70 ? p1 + (o - 40) * (p50 - p1) / 30 : p50 + (o - 70) * (p99 - p50) / 29;
  const toO = g => g <= p50 ? 40 + 30 * (g - p1) / (p50 - p1) : 70 + 29 * (g - p50) / (p99 - p50);
  // 照 5 場水準直接換算的 OVR 會跳到 150 這種數字（5 場起伏太大），正文只講排在哪一段，換算值放 tooltip
  const o2 = toO(toG(p.ovr) + d * w);
  const tip = `若整季都維持這個水準，OVR 約 ${o2.toFixed(0)}（目前 ${p.ovr.toFixed(1)}）；5 場樣本很小，不會真的差這麼多`;
  return `<div class="gcn" title="顏色＝和自己 2025-26 平均比，照所有人的起伏五等分（單場 ±0.7／±2.4，5 場 ±0.3／±1.1）；${tip}">` +
    `${n} 場平均貢獻 <b class="${cls}">${sg1(c.r)}</b>　上季 <b>${sg1(c.b)}</b></div>`;
}
function gameLog(r, p) {
  const gs = r.g5;
  const pm = v => `<span class="${v > 0 ? 'up' : v < 0 ? 'dn' : ''}">${v > 0 ? '+' : ''}${v}</span>`;
  const ma = (m, a) => `${m}-${a}`;
  const row = g => `<td>${g[0]}</td><td>${g[1]}</td><td><span class="${g[2] === 'W' ? 'w' : 'l'}">${g[2] === 'W' ? '勝' : '負'}</span></td>` +
    gcCell(g[17], r.gc.b, GC_CUT1) + [4, 5, 6, 7, 8, 9].map(i => `<td>${g[i]}</td>`).join('') +
    `<td>${ma(g[10], g[11])}</td><td>${ma(g[12], g[13])}</td><td>${ma(g[14], g[15])}</td><td>${pm(g[16])}</td><td>${g[3]}</td>`;
  const n = gs.length, sum = i => gs.reduce((s, g) => s + g[i], 0), avg = i => (sum(i) / n).toFixed(1);
  // 平均列的投籃／三分／罰球改顯示 N 場合計命中率（使用者 2026-10-30），滑過看合計進球-出手
  const pct = (m, a) => `<td title="合計 ${sum(m)}-${sum(a)}">${sum(a) ? (sum(m) / sum(a) * 100).toFixed(1) + '%' : '—'}</td>`;
  // 貢獻值放在勝負後面、分鐘移到最右（使用者 2026-10-30）
  const head = ['日期', '對手', '勝負', '貢獻', '得分', '籃板', '助攻', '抄截', '阻攻', '失誤', '投籃', '三分', '罰球', '正負', '分鐘'];
  const gcTip = 'box score 換算的每 36 分鐘淨影響（每 100 回合淨分，權重擬合 2025-26 RAPM）；顏色＝和自己 2025-26 平均比，五等分（單場 ±0.7／±2.4，5 場平均 ±0.3／±1.1）';
  return `<table><thead><tr>${head.map(h => `<th${h === '貢獻' ? ` title="${gcTip}"` : ''}>${h}</th>`).join('')}</tr></thead><tbody>${gs.map(g => `<tr>${row(g)}</tr>`).join('')}</tbody>` +
    `<tfoot><tr><td colspan="3">${n} 場平均</td>${gcCell(r.gc.r, r.gc.b, GC_CUT5)}${[4, 5, 6, 7, 8, 9].map(i => `<td>${avg(i)}</td>`).join('')}` +
    `${pct(10, 11)}${pct(12, 13)}${pct(14, 15)}<td>${pm(+avg(16))}</td><td>${avg(3)}</td></tr></tfoot></table>${gcNote(r, p, n)}`;
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
// 手機位置下拉：按鈕顯示目前位置，點了才展開位置列（#posSeg 每次 render 重建，用 observer 同步）
(() => {
  const seg = document.getElementById('posSeg'), ctrl = seg && seg.closest('.ctrl');
  if (!ctrl) return;
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'pbtn'; btn.setAttribute('aria-label', '選擇位置');
  seg.before(btn);
  const sync = () => {
    const b = seg.querySelector('[aria-pressed="true"]'), all = !b || b === seg.firstElementChild;
    btn.textContent = all ? '位置' : b.textContent;
    btn.classList.toggle('on', !all);
  };
  sync();
  new MutationObserver(sync).observe(seg, { childList: true, subtree: true, attributes: true });
  const close = () => { ctrl.classList.remove('popen'); btn.setAttribute('aria-expanded', 'false'); };
  btn.onclick = () => { const o = ctrl.classList.toggle('popen'); btn.setAttribute('aria-expanded', String(o)); };
  seg.addEventListener('click', e => { if (e.target.closest('button')) close(); });
  document.addEventListener('click', e => { if (!btn.contains(e.target) && !seg.contains(e.target)) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && ctrl.classList.contains('popen')) { close(); btn.focus(); } });
  const q = document.getElementById('q');
  if (q && matchMedia('(max-width:640px)').matches) q.placeholder = '搜尋';
})();
// 手機表格手勢鎖方向（使用者 2026-10-29：往上滑時手會左右偏，表格跟著晃）：先移動 10px 才判方向，
// 水平量要大於垂直 1.5 倍才算左右捲，判定後整段手勢只動那一軸。放手後照速度慣性滑行。
// 表格自己捲只從數值格啟動（使用者 2026-10-30）：從表頭或 #／名字／OVR 欄開始的手勢上下捲整頁，不捲表格。
(() => {
  const box = document.querySelector('.tbox'); if (!box) return;
  const mq = matchMedia('(max-width:640px)'), LOCK = 10, RATIO = 1.5;
  let s = null, raf = 0;
  box.addEventListener('touchstart', e => {
    cancelAnimationFrame(raf); raf = 0; s = null;
    if (!mq.matches || e.touches.length > 1) return;
    const t = e.touches[0];
    const page = !!e.target.closest('thead,td.no,td.nm,td.ovr');
    s = {x: t.clientX, y: t.clientY, el: page ? document.scrollingElement : box, axis: page ? 'y' : null, hist: []};
    s.l = s.el.scrollLeft; s.tp = s.el.scrollTop;
  }, {passive: true});
  box.addEventListener('touchmove', e => {
    if (!s || e.touches.length > 1) return;
    const t = e.touches[0], dx = t.clientX - s.x, dy = t.clientY - s.y;
    if (!s.axis) {
      if (Math.hypot(dx, dy) < LOCK) return;
      s.axis = Math.abs(dx) > Math.abs(dy) * RATIO ? 'x' : 'y';
    }
    if (s.axis === 'x') s.el.scrollLeft = s.l - dx; else s.el.scrollTop = s.tp - dy;
    const now = performance.now();
    s.hist.push([now, s.axis === 'x' ? t.clientX : t.clientY]);
    while (s.hist.length > 2 && now - s.hist[0][0] > 100) s.hist.shift();
  }, {passive: true});
  const end = () => {
    const g = s; s = null;
    if (!g || !g.axis || g.hist.length < 2) return;
    const a = g.hist[0], b = g.hist[g.hist.length - 1], dt = b[0] - a[0];
    let v = dt > 0 && performance.now() - b[0] < 80 ? -(b[1] - a[1]) / dt : 0, last = performance.now();
    const step = now => {
      const d = now - last; last = now; v *= Math.pow(0.996, d);
      if (Math.abs(v) < 0.03) { raf = 0; return; }
      if (g.axis === 'x') g.el.scrollLeft += v * d; else g.el.scrollTop += v * d;
      raf = requestAnimationFrame(step);
    };
    if (Math.abs(v) > 0.1) raf = requestAnimationFrame(step);
  };
  box.addEventListener('touchend', end);
  box.addEventListener('touchcancel', () => { s = null; });
})();
"""

BEGIN, END = '<!-- real-stats:begin -->', '<!-- real-stats:end -->'


def aggregate():
    rs = json.loads(SRC.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(rs['headers'])}
    acc, games = {}, {}
    log_keys = ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'PLUS_MINUS']
    for row in rs['rowSet']:
        name = row[h['PLAYER_NAME']]
        a = acc.setdefault(name, {'id': row[h['PLAYER_ID']], 'gp': 0, 'teams': [], **{k: 0 for k in log_keys}})
        a['gp'] += 1
        games.setdefault(name, []).append(row)
        team = row[h['TEAM_ABBREVIATION']]
        if team not in a['teams']:
            a['teams'].append(team)
        for k in a:
            if k.isupper():
                a[k] += row[h[k]] or 0
    gc = json.loads((GC / 'weights.json').read_text(encoding='utf-8'))
    base = json.loads((GC / 'baseline-2025-26.json').read_text(encoding='utf-8'))
    box = lambda r: gc['intercept'] + sum(b * (r[h[k]] or 0) for k, b in gc['per36'].items()) * 36 / r[h['MIN']]
    out = {}
    for name, a in acc.items():
        n = a['gp']
        last = sorted(games[name], key=lambda r: (r[h['GAME_DATE']], r[h['GAME_ID']]), reverse=True)[:5]
        rm = sum(r[h['MIN']] or 0 for r in last)
        b = base.get(str(a['id']))
        pct = lambda m, t: round(m / t, 4) if t else None
        tsa = 2 * (a['FGA'] + 0.44 * a['FTA'])
        out[name] = {
            'id': a['id'], 'gp': n, 'teams': a['teams'],
            'mpg': round(a['MIN'] / n, 2), 'pts': round(a['PTS'] / n, 2), 'reb': round(a['REB'] / n, 2),
            'ast': round(a['AST'] / n, 2), 'stl': round(a['STL'] / n, 2), 'blk': round(a['BLK'] / n, 2),
            'tov': round(a['TOV'] / n, 2), 'pm': round(a['PLUS_MINUS'] / n, 2),
            'fg': pct(a['FGM'], a['FGA']), 'fg3': pct(a['FG3M'], a['FG3A']), 'ft': pct(a['FTM'], a['FTA']),
            'ts': pct(a['PTS'], tsa),
            # 每列最後一格＝該場貢獻值（每 36 分鐘，沒上場為 null）
            'g5': [game_row(r, h, log_keys) + [round(box(r), 2) if r[h['MIN']] else None] for r in last],
            # 貢獻值：r＝近 N 場合計換算每 36 分鐘，b＝2025-26 整季（沒有 2025-26 紀錄＝null）
            'gc': {'r': round(sum(box(r) * r[h['MIN']] for r in last if r[h['MIN']]) / rm, 2) if rm else None,
                   'b': b['box36'] if b else None},
        }
    return out


def game_row(r, h, keys):
    """一場 → [M/D, 'vs BOS'／'@ BOS', W/L, 分鐘…正負值]（給卡片的近 5 場表）。"""
    _, m, d = r[h['GAME_DATE']][:10].split('-')
    mu = r[h['MATCHUP']].split()
    return [f'{int(m)}/{int(d)}', ('@ ' if mu[1] == '@' else 'vs ') + mu[-1], r[h['WL']]] + [r[h[k]] or 0 for k in keys]


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
    a = json.loads(CARD_SUMMARY.read_text(encoding='utf-8'))['anchors']
    block = (f'{BEGIN}\n<style>{CSS}</style>\n<script>const REAL={js_json(sub)};\nconst IMPACT={js_json(imp)};\n'
             f'const GC_ANC={js_json([a["PR1"], a["PR50"], a["PR99"]])};\n'
             f'const TEAM_COLORS={js_json(TEAM_COLORS)};\nconst TEAM_IDS={js_json(team_ids())};{JS}</script>\n{END}\n')
    assert s.count('<script>const DATA=') == 1
    s = s.replace('<script>const DATA=', block + '<script>const DATA=', 1)
    hook = '<div class="strong">${tops.map(t => chip(t[0], t[1])).join(\'\')}${chip(\'弱項 \' + low[0], low[1], true)}</div>'
    s = s.replace('${teamDot(p.team)}${p.team}', '${p.team}')  # 舊版注入
    s = s.replace('${headshot(p)}<span class="pos">', '${headshot(p)}<div class="tnm"><span>${esc(first)}</span>${esc(last)}</div><span class="tht">${ht(p.ht)}</span><span class="pos">')  # 舊版注入（橫幅名字前）
    # 能力值前三／弱項改成影響力（使用者 2026-10-29）；樣板可能已含 realBox
    s = s.replace(hook + '\n      ${realBox(p)}', hook)
    for old, new in [
        (hook, '${impactChips(p)}\n      ${realBox(p)}'),
        ('<div class="tag"><span class="pos">', '<div class="tag" style="${teamVars(p.team)}">${headshot(p)}<div class="tnm"><span>${esc(first)}</span>${esc(last)}</div><span class="tht">${ht(p.ht)}</span><span class="pos">'),
        ("<td class=\"sub${sc('team')}\">${p.team}</td>", "<td class=\"sub${sc('team')}\">${teamCell(p.team)}</td>"),
        ('<tr class="grp"><th colspan="6"></th>', '<tr class="grp"><th colspan="3"></th><th class="gx" colspan="3"></th>'),
        ('<td class="nm" title="${esc(p.name)}">${esc(p.name)}</td>',
         '<td class="nm" title="${esc(p.name)}"><span class="nf">${esc(p.name)}</span><span class="ns">${esc(shortName(p.name))}</span></td>'),
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

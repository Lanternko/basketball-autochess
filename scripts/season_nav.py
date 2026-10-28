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
]


def apply_common(s):
    for a, b in COMMON_REPLACEMENTS:
        assert s.count(a) == 1, a
        s = s.replace(a, b)
    return s

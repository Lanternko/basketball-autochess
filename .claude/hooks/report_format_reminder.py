"""Claude Code PostToolUse hook（matcher mcp__ccd_turn__wrap_up）：本回合碰過實驗結果時，在寫收尾訊息之前提醒回報格式。

wrap_up 之後才寫給使用者的收尾訊息，所以在這裡注入提醒，第一版回報就照格式，不用事後擋下重寫。
「碰過實驗結果」＝本回合（最後一個使用者訊息之後）的工具呼叫或結果出現 E-xxx、dispatch_result、
預註冊、evaluation.json、status_snapshot 等字樣。格式本身寫在專案 CLAUDE.md「回報實驗結果」。
派工子 session（CLAUDE_DISPATCH_CHILD=1）不提醒。任何錯誤都放行。
"""
import json
import os
import re
import sys

SIGNAL = re.compile(r'\bE-\d{3}\b|dispatch_result|preregistration|evaluation\.json|status_snapshot|預註冊', re.I)

REMINDER = (
    "本回合碰過實驗結果。接下來的收尾訊息是固定模板，不是參考（L-051）："
    "第一行就是「# 總評」，前面不放結論句；六個標題照字面照順序："
    "①總評：標題用「# 總評」（一級標題，## 在 App 裡和粗體一樣大），內容寫成「**4/5 大致達成 有部分退步**」，"
    "五級附分數：5 重大達成／4 大致達成 有部分退步／3 一半一半／2 主目標達成 但是有副作用／1 失敗；"
    "退步段有實質項目就不給 5 "
    "②這次目標 ③進步了什麼 ④退步了什麼（用「誰從第幾名到第幾名」「幾成」這種講法）"
    "⑤直觀證據：球員例子、小表或圖 ⑥要你決定的事（approve 與否、下一步方向）。其他五段用粗體標題。"
    "一則回覆只寫一份六段；稽核也用這六段（進步＝核對成立，退步＝對不上或有疑慮）。"
    "查證過程、Δρ、區間、閘門代號一律放第 6 段之後。這回合不是在回報實驗結果就忽略這段。"
)


def text_of(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return ' '.join(text_of(b) for b in x)
    if isinstance(x, dict):
        return ' '.join(text_of(v) for v in x.values())
    return ''


def current_turn(entries):
    """最後一個使用者文字訊息之後的 entries。"""
    start = 0
    for i, e in enumerate(entries):
        content = (e.get('message') or {}).get('content')
        if e.get('type') == 'user' and (isinstance(content, str) or (isinstance(content, list) and any(
                isinstance(b, dict) and b.get('type') == 'text' for b in content))):
            start = i
    return entries[start + 1:]


def touched_experiment(entries):
    for e in current_turn(entries):
        content = (e.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get('type') in ('tool_use', 'tool_result'):
                if SIGNAL.search(text_of(b.get('input') if b.get('type') == 'tool_use' else b.get('content'))):
                    return True
    return False


def emit(obj):
    data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    if sys.stdout is not None:
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    else:
        os.write(1, data)


def main():
    if os.environ.get('CLAUDE_DISPATCH_CHILD') == '1':
        return
    raw = sys.stdin.buffer.read() if sys.stdin is not None else os.read(0, 1 << 20)
    payload = json.loads(raw.decode('utf-8') or '{}')
    path = payload.get('transcript_path')
    if not path or not os.path.isfile(path):
        return
    with open(path, encoding='utf-8') as f:
        entries = [json.loads(line) for line in f if line.strip()]
    if touched_experiment(entries):
        emit({'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': REMINDER}})


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass
    sys.exit(0)

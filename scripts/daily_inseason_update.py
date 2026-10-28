"""賽中名單每日自動更新並發布到 GitHub Pages（gh-pages 分支的 index.html＝2026-27 賽中頁、2025-26.html＝2025-26 正式卡頁）。

流程：抓比賽 → 抓 PBP/bio → run_c4_live → 依資料 sha256 決定是否發布 → 字母版號 → build viewer
      → 在可丟棄的 git worktree 中把 roster-viewer.html 提交成 gh-pages 的 index.html 並 push。

規則（memory/rulings.md R-023、R-024）：
- 只有比賽資料變、模型沒動：版號加字母 inseason 0.1.1 -> 0.1.1a -> 0.1.1b ... z -> aa。
- 基底版號（meta.json 的 version，由 run_c4_live.py 產生）一變，字母從 a 重來。
- 含字母的版號寫回該日 meta.json 的 `version`（原基底另存 `baseVersion`），build_inseason_viewer.py
  讀 meta["version"] 顯示在 HTML 標題列，所以不需要改它或對 HTML 做字串替換。

用法（工作目錄不限，會自動切到 repo 根）：
  pythonw scripts/daily_inseason_update.py [--dry-run] [--force]
  python -I scripts/daily_inseason_update.py --shell   # deploy-shell：只改頁面（UI／顯示），資料與版號不動
子程序一律 CREATE_NO_WINDOW；排程用 pythonw 啟動。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import logging.handlers
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'reports/ovr-inseason-2026-27/live'
STATE_PATH = LIVE / 'publish_state.json'
LOG_PATH = LIVE / 'logs/daily.log'
LOCK_PATH = LIVE / '.daily_update.lock'
SEASON = '2026-27'
PLAYER_GAMES = ROOT / f'data/season-source-{SEASON}/player-games.json'
PBP_DIR = ROOT / f'data/defense-seventh/{SEASON}/pbp'
BUILD_ROOT = ROOT / 'data/_inseason_build'
RUN_C4 = LIVE / 'run_c4_live.py'
VIEWER = ROOT / 'scripts/build_inseason_viewer.py'
CARD_VIEWER = ROOT / 'scripts/build_card_viewer.py'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

TIMEOUTS = {'games': 900, 'inseason': 3600, 'c4': 3600, 'viewer': 600, 'git': 180}
CO_AUTHOR = 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'

log = logging.getLogger('daily_inseason')


# ----------------------------------------------------------------- 版號
def letter_next(letter: str) -> str:
    """'' -> 'a'，'a' -> 'b'，'z' -> 'aa'，'az' -> 'ba'（Excel 欄名式）。"""
    if not letter:
        return 'a'
    chars = list(letter)
    i = len(chars) - 1
    while i >= 0:
        if chars[i] != 'z':
            chars[i] = chr(ord(chars[i]) + 1)
            return ''.join(chars)
        chars[i] = 'a'
        i -= 1
    return 'a' + ''.join(chars)


def decide(state: dict, base: str, data_sha: str, pbp_count: int, force: bool) -> dict:
    """回傳 {publish, letter, reason}。letter 是這次要用的字母（不發布時為目前字母）。"""
    prev_base = state.get('base')
    prev_letter = state.get('letter', '')
    if prev_base != base:
        return {'publish': True, 'letter': 'a', 'reason': f'基底版號 {prev_base!r} -> {base!r}，字母重來'}
    changed = state.get('dataSha256') != data_sha or state.get('pbpCount') != pbp_count
    if changed:
        return {'publish': True, 'letter': letter_next(prev_letter), 'reason': '資料有變（player-games sha256 或 PBP 檔數）'}
    if force:
        return {'publish': True, 'letter': prev_letter or 'a', 'reason': '--force，資料沒變，沿用同一字母'}
    return {'publish': False, 'letter': prev_letter, 'reason': '資料沒有變化，不發布'}


def display_version(base: str, letter: str) -> str:
    return base + letter


# ----------------------------------------------------------------- 工具
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    try:
        d = json.loads(path.read_text(encoding='utf-8'))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def py_exe() -> str:
    exe = Path(sys.executable)
    if exe.name.lower() == 'pythonw.exe':
        cand = exe.with_name('python.exe')
        if cand.exists():
            return str(cand)
    return str(exe)


def run(cmd, cwd: Path, timeout: int, env: dict | None = None) -> subprocess.CompletedProcess:
    log.info('$ %s  (cwd=%s, timeout=%ss)', ' '.join(map(str, cmd)), cwd, timeout)
    e = dict(os.environ)
    e.update({'GIT_TERMINAL_PROMPT': '0', 'PYTHONIOENCODING': 'utf-8'})
    if env:
        e.update(env)
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=timeout, env=e,
                          creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL)


def log_tail(text: str, n: int = 12) -> None:
    for line in (text or '').strip().splitlines()[-n:]:
        log.info('  | %s', line)


def checked(cmd, cwd: Path, timeout: int, env: dict | None = None) -> subprocess.CompletedProcess:
    try:
        r = run(cmd, cwd, timeout, env)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f'逾時 {timeout}s：{" ".join(map(str, cmd))}')
    if r.returncode != 0:
        log_tail(r.stdout)
        log_tail(r.stderr)
        raise RuntimeError(f'exit={r.returncode}：{" ".join(map(str, cmd))}\n{(r.stderr or r.stdout).strip()[-800:]}')
    return r


def node_exe() -> str:
    for c in (shutil.which('node'), r'C:\Program Files\nodejs\node.exe'):
        if c and Path(c).exists():
            return c
    raise RuntimeError('找不到 node')


# ----------------------------------------------------------------- 鎖
class Lock:
    def __init__(self, path: Path, stale_s: int = 4 * 3600):
        self.path, self.stale_s = path, stale_s

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f'{os.getpid()} {time.time()}'.encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                except FileNotFoundError:
                    continue
                if age > self.stale_s:
                    log.warning('鎖檔已過期（%.0f 分鐘），接手', age / 60)
                    self.path.unlink(missing_ok=True)
                    continue
                raise LockBusy(f'另一個更新正在跑（鎖檔 {self.path}，{age / 60:.0f} 分鐘前）')
        raise LockBusy('取鎖失敗')

    def __exit__(self, *a):
        self.path.unlink(missing_ok=True)


class LockBusy(RuntimeError):
    pass


# ----------------------------------------------------------------- 四步
def step_fetch_games() -> None:
    checked([node_exe(), 'scripts/fetch_season_games.js', SEASON], ROOT, TIMEOUTS['games'])


def step_fetch_inseason() -> dict:
    """fetch_inseason 在有 PBP 抓不到時 exit 1（預期）。末行是 JSON 摘要＝腳本跑完了，才算「預期的 exit 1」；
    沒有摘要（bio 抓失敗、例外、逾時）才是真失敗。"""
    try:
        r = run([node_exe(), 'scripts/fetch_inseason_2026_27.js', SEASON], ROOT, TIMEOUTS['inseason'])
    except subprocess.TimeoutExpired:
        raise RuntimeError('fetch_inseason 逾時')
    summary = None
    for line in reversed((r.stdout or '').strip().splitlines()):
        try:
            cand = json.loads(line)
        except ValueError:
            continue
        if isinstance(cand, dict) and 'failures' in cand:
            summary = cand
            break
    if r.returncode == 0:
        return summary or {}
    if summary is not None and r.returncode == 1:
        log.warning('PBP 不完整（預期）：抓到 %s、快取 %s、失敗 %d 場 %s', summary.get('fetched'),
                    summary.get('cached'), len(summary['failures']),
                    [f.get('id') for f in summary['failures']][:10])
        return summary
    log_tail(r.stdout)
    log_tail(r.stderr)
    raise RuntimeError(f'fetch_inseason 真的失敗 exit={r.returncode}：{(r.stderr or r.stdout).strip()[-500:]}')


def probe_base_version() -> str | None:
    """不執行 run_c4_live，從原始碼讀基底版號（只用來判斷「資料沒變時是否還得重跑」）。"""
    m = re.search(r"^VERSION\s*=\s*'([^']+)'", RUN_C4.read_text(encoding='utf-8'), re.M)
    return m.group(1) if m else None


def step_c4(out_dir: Path) -> dict:
    checked([py_exe(), '-I', str(RUN_C4), str(out_dir)], ROOT, TIMEOUTS['c4'])
    meta = load_json(out_dir / 'meta.json')
    if not meta.get('version') or not meta.get('dataCutoff'):
        raise RuntimeError(f'meta.json 缺 version/dataCutoff：{out_dir}')
    return meta


def step_viewer(out_dir: Path) -> Path:
    checked([py_exe(), '-I', str(VIEWER), str(out_dir)], ROOT, TIMEOUTS['viewer'])
    html = out_dir / 'roster-viewer.html'
    if not html.exists() or html.stat().st_size < 10_000:
        raise RuntimeError(f'roster-viewer.html 不存在或太小：{html}')
    return html


def step_card_viewer(out_dir: Path) -> Path:
    """建 2025-26 正式卡頁（含賽季切換列），輸出到工作夾，與賽中頁一起發布成 2025-26.html。"""
    html = out_dir / 'card-roster-viewer.html'
    checked([py_exe(), '-I', str(CARD_VIEWER), str(html)], ROOT, TIMEOUTS['viewer'])
    if not html.exists() or html.stat().st_size < 10_000:
        raise RuntimeError(f'card-roster-viewer.html 不存在或太小：{html}')
    return html


# ----------------------------------------------------------------- 發布（仿 arammeta static_publish）
class GitRunner:
    def __init__(self, cwd: Path, timeout: int = TIMEOUTS['git']):
        self.cwd, self.timeout = cwd, timeout

    def __call__(self, *args, check: bool = True) -> subprocess.CompletedProcess:
        try:
            r = run(['git', *args], self.cwd, self.timeout)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f'git 逾時：{" ".join(args)}')
        if check and r.returncode != 0:
            raise RuntimeError(f'git {" ".join(args)} exit={r.returncode}: {(r.stderr or r.stdout).strip()[-500:]}')
        return r


def publish_html(repo: Path, html, message: str, *, remote: str = 'origin', branch: str = 'gh-pages',
                 target_name: str = 'index.html', before_push=None) -> str | None:
    """把一或多個檔案提交成 <branch> 上的檔案並 push。回傳新 commit sha；內容都沒變回傳 None。

    html：Path（發布成 target_name，向下相容）或 {目標檔名: 來源 Path}。
    在 temp 目錄開 detached worktree（開發中的 checkout 有未 commit 改動也不受影響），只 stage 白名單
    檔名（files 的鍵）；push 非快轉時 fetch＋merge（-X ours：以我們為準）後再推一次；最後一律移除工作樹。
    before_push：測試用掛鉤，在第一次 push 前呼叫（模擬競態）。
    """
    files = dict(html) if isinstance(html, dict) else {target_name: html}
    for name in files:
        if '/' in name or chr(92) in name or name.startswith('.'):
            raise ValueError(f'不合法的目標檔名：{name}')
    main_git = GitRunner(repo)
    main_git('fetch', remote, branch)
    tmp = Path(tempfile.mkdtemp(prefix='inseason-pages-'))
    wt = tmp / 'wt'
    try:
        main_git('worktree', 'add', '--detach', str(wt), f'{remote}/{branch}')
        g = GitRunner(wt)
        for name, src in files.items():
            shutil.copyfile(src, wt / name)
        g('add', '--', *files)
        if g('diff', '--cached', '--quiet', check=False).returncode == 0:
            log.info('%s:%s 內容與上次相同，不提交', branch, ','.join(files))
            return None
        g('commit', '-m', message)
        if before_push:
            before_push()
        r = g('push', remote, f'HEAD:{branch}', check=False)
        if r.returncode != 0:
            log.warning('push 失敗，fetch＋merge 後重推：%s', (r.stderr or r.stdout).strip()[-300:])
            g('fetch', remote, branch)
            m = g('merge', '--no-edit', '-X', 'ours', f'{remote}/{branch}', check=False)
            if m.returncode != 0:
                g('merge', '--abort', check=False)
                raise RuntimeError(f'無法合併 {remote}/{branch}：{(m.stderr or m.stdout).strip()[-300:]}')
            g('push', remote, f'HEAD:{branch}')
        return g('rev-parse', 'HEAD').stdout.strip()
    finally:
        main_git('worktree', 'remove', '--force', str(wt), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
        main_git('worktree', 'prune', check=False)


def commit_message(version: str, cutoff: str) -> str:
    return f'inseason {version.removeprefix("inseason ")} 數據至 {cutoff}\n\n{CO_AUTHOR}\n'


def shell_commit_message(version: str, cutoff: str) -> str:
    return f'inseason {version.removeprefix("inseason ")} 頁面更新（數據至 {cutoff}，資料不變）\n\n{CO_AUTHOR}\n'


# ----------------------------------------------------------------- 主流程
def setup_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    fh.setFormatter(fmt)
    log.setLevel(logging.INFO)
    log.addHandler(fh)
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        log.addHandler(sh)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='照常建構（輸出到暫存夾），不 push、不寫 publish_state')
    ap.add_argument('--force', action='store_true', help='資料沒變也發布')
    ap.add_argument('--shell', action='store_true',
                    help='只重建頁面（UI／顯示改動）：沿用最後發布那天的 live 資料，不抓資料、不跑 C4、版號不動')
    ap.add_argument('--remote', default='origin')
    ap.add_argument('--branch', default='gh-pages')
    args = ap.parse_args(argv)
    setup_logging()
    log.info('==== 開始 dry_run=%s force=%s shell=%s ====', args.dry_run, args.force, args.shell)
    try:
        with Lock(LOCK_PATH):
            return _run_shell(args) if args.shell else _run(args)
    except LockBusy as e:
        log.warning('%s', e)
        return 0
    except Exception as e:  # noqa: BLE001
        log.error('失敗：%s', e)
        return 1


def _run(args) -> int:
    state = load_json(STATE_PATH)
    step_fetch_games()
    step_fetch_inseason()
    data_sha = sha256_file(PLAYER_GAMES)
    pbp_count = len(list(PBP_DIR.glob('*.json'))) if PBP_DIR.exists() else 0
    log.info('player-games sha256=%s…  pbp=%d', data_sha[:12], pbp_count)

    unchanged = state.get('dataSha256') == data_sha and state.get('pbpCount') == pbp_count
    probe = probe_base_version()
    if unchanged and not args.force and probe is not None and probe == state.get('base'):
        log.info('沒有新比賽資料且基底版號未動（%s%s），不發布', state.get('base'), state.get('letter', ''))
        return 0

    # run_c4_live 的 rel() 要求輸出夾在 repo 內；data/ 已被 .gitignore
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='build-', dir=BUILD_ROOT))
    try:
        meta = step_c4(work)
        base = meta['version']
        d = decide(state, base, data_sha, pbp_count, args.force)
        letter = d['letter']
        log.info('決定：publish=%s 版號=%s（%s）', d['publish'], display_version(base, letter), d['reason'])
        if not d['publish']:
            return 0
        shown = display_version(base, letter)
        meta['baseVersion'] = base
        meta['version'] = shown
        meta['dataSha256'] = data_sha
        save_json(work / 'meta.json', meta)
        html = step_viewer(work)
        card_html = step_card_viewer(work)
        cutoff = meta['dataCutoff']

        if args.dry_run:
            log.info('dry-run：不 push、不寫 state、不複製到 live/。輸出夾 %s（保留）', work)
            work = None
            return 0

        final = LIVE / cutoff
        shutil.copytree(work, final, dirs_exist_ok=True)
        sha = publish_html(ROOT, {'index.html': final / 'roster-viewer.html', '2025-26.html': final / card_html.name},
                           commit_message(shown, cutoff),
                           remote=args.remote, branch=args.branch)
        state.update({'base': base, 'letter': letter, 'displayVersion': shown, 'dataSha256': data_sha,
                      'pbpCount': pbp_count, 'dataCutoff': cutoff,
                      'lastPublished': dt.datetime.now().astimezone().isoformat(timespec='seconds')})
        if sha:
            state['ghPagesCommit'] = sha
        save_json(STATE_PATH, state)
        log.info('已發布 %s 數據至 %s，gh-pages commit=%s', shown, cutoff, sha or '（內容未變）')
        return 0
    finally:
        if work is not None:
            shutil.rmtree(work, ignore_errors=True)


def _run_shell(args) -> int:
    """deploy-shell：OVR 數字不變的頁面改動。改公式會動到數字，要走完整流程並改版號（G2）。"""
    state = load_json(STATE_PATH)
    cutoff = state.get('dataCutoff')
    if not cutoff or not (LIVE / cutoff / 'meta.json').exists():
        raise RuntimeError(f'找不到最後發布的 live 資料（dataCutoff={cutoff}），先跑一次完整發布')
    final = LIVE / cutoff
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='shell-', dir=BUILD_ROOT))
    try:
        shutil.copytree(final, work, dirs_exist_ok=True)
        html = step_viewer(work)
        card_html = step_card_viewer(work)
        if args.dry_run:
            log.info('dry-run（shell）：不 push、不寫 state。輸出夾 %s（保留）', work)
            work = None
            return 0
        shutil.copyfile(html, final / html.name)
        shutil.copyfile(card_html, final / card_html.name)
        shown = state.get('displayVersion', '')
        sha = publish_html(ROOT, {'index.html': final / html.name, '2025-26.html': final / card_html.name},
                           shell_commit_message(shown, cutoff), remote=args.remote, branch=args.branch)
        if sha:
            state['ghPagesCommit'] = sha
            state['lastShellPublished'] = dt.datetime.now().astimezone().isoformat(timespec='seconds')
            save_json(STATE_PATH, state)
        log.info('shell 發布 %s（數據至 %s），gh-pages commit=%s', shown, cutoff, sha or '（內容未變）')
        return 0
    finally:
        if work is not None:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())

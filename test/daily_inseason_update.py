"""daily_inseason_update 的單元測試與本機 bare repo 發布測試。
執行：python -m unittest test/daily_inseason_update.py  （或 pytest test/daily_inseason_update.py）
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import daily_inseason_update as D  # noqa: E402

NW = subprocess.CREATE_NO_WINDOW
ENV = {**os.environ, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t', 'GIT_COMMITTER_NAME': 't',
       'GIT_COMMITTER_EMAIL': 't@t', 'GIT_TERMINAL_PROMPT': '0'}


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', env=ENV, creationflags=NW)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class Letters(unittest.TestCase):
    def test_next(self):
        self.assertEqual(D.letter_next(''), 'a')
        self.assertEqual(D.letter_next('a'), 'b')
        self.assertEqual(D.letter_next('y'), 'z')
        self.assertEqual(D.letter_next('z'), 'aa')
        self.assertEqual(D.letter_next('az'), 'ba')
        self.assertEqual(D.letter_next('zz'), 'aaa')

    def test_decide(self):
        base = 'inseason 0.1.1'
        # 第一次：無 state -> a
        d = D.decide({}, base, 'h1', 5, False)
        self.assertTrue(d['publish']); self.assertEqual(d['letter'], 'a')
        st = {'base': base, 'letter': 'a', 'dataSha256': 'h1', 'pbpCount': 5}
        # 資料沒變不發布
        d = D.decide(st, base, 'h1', 5, False)
        self.assertFalse(d['publish']); self.assertEqual(d['letter'], 'a')
        # 資料變 -> b
        d = D.decide(st, base, 'h2', 5, False)
        self.assertTrue(d['publish']); self.assertEqual(d['letter'], 'b')
        # 只有 PBP 檔數變也算
        self.assertEqual(D.decide(st, base, 'h1', 6, False)['letter'], 'b')
        # force：沿用同一字母
        d = D.decide(st, base, 'h1', 5, True)
        self.assertTrue(d['publish']); self.assertEqual(d['letter'], 'a')
        # 基底版號變 -> 字母歸 a（即使資料沒變）
        st_z = {**st, 'letter': 'z'}
        d = D.decide(st_z, 'inseason 0.1.2', 'h1', 5, False)
        self.assertTrue(d['publish']); self.assertEqual(d['letter'], 'a')
        self.assertEqual(D.display_version('inseason 0.1.2', d['letter']), 'inseason 0.1.2a')

    def test_commit_message(self):
        m = D.commit_message('inseason 0.1.1a', '2026-10-28')
        self.assertTrue(m.startswith('inseason 0.1.1a 數據至 2026-10-28'))
        self.assertTrue(m.rstrip().endswith('Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'))


class Lock(unittest.TestCase):
    def test_lock(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'x.lock'
            with D.Lock(p):
                with self.assertRaises(D.LockBusy):
                    with D.Lock(p):
                        pass
            self.assertFalse(p.exists())
            with D.Lock(p):
                pass


class Publish(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        t = Path(self.t.name)
        self.bare = t / 'origin.git'
        git(t, 'init', '--bare', '-b', 'main', str(self.bare))
        self.dev = t / 'dev'
        git(t, 'clone', str(self.bare), str(self.dev))
        git(self.dev, 'checkout', '-b', 'gh-pages')
        (self.dev / 'index.html').write_text('v0', encoding='utf-8')
        git(self.dev, 'add', '.'); git(self.dev, 'commit', '-m', 'init'); git(self.dev, 'push', 'origin', 'gh-pages')
        # 開發 checkout 有未 commit 改動，不應被碰
        (self.dev / 'wip.txt').write_text('wip', encoding='utf-8')
        self.html = t / 'roster-viewer.html'

    def tearDown(self):
        self.t.cleanup()

    def pub(self, text, **kw):
        self.html.write_text(text, encoding='utf-8')
        self.card = self.html.with_name('card.html')
        self.card.write_text(text + '-card', encoding='utf-8')
        return D.publish_html(self.dev, {'index.html': self.html, '2025-26.html': self.card},
                              D.commit_message('inseason 0.1.1a', '2026-10-28'), **kw)

    def show(self, ref='gh-pages', name='index.html'):
        return git(self.bare, 'show', f'{ref}:{name}')

    def test_publish_and_noop(self):
        sha = self.pub('v1')
        self.assertTrue(sha)
        self.assertEqual(self.show(), 'v1')
        self.assertEqual(git(self.bare, 'rev-parse', 'gh-pages'), sha)
        self.assertEqual(self.show(name='2025-26.html'), 'v1-card')
        self.assertEqual(git(self.bare, 'ls-tree', '--name-only', 'gh-pages').splitlines(), ['2025-26.html', 'index.html'])
        self.assertNotIn('wip.txt', git(self.bare, 'ls-tree', '--name-only', 'gh-pages'))
        self.assertIsNone(self.pub('v1'))  # 內容相同不提交
        self.assertTrue((self.dev / 'wip.txt').exists())
        self.assertNotIn('inseason-pages', git(self.dev, 'worktree', 'list'))  # 工作樹已清掉
        self.assertIn('Claude Opus 5.5', git(self.bare, 'log', '-1', '--format=%B', 'gh-pages'))

    def test_non_fast_forward_retry(self):
        other = Path(self.t.name) / 'other'
        git(Path(self.t.name), 'clone', '-b', 'gh-pages', str(self.bare), str(other))

        def race():  # 在我們 push 前，別處先推了一個 commit（改別的檔）
            (other / 'extra.txt').write_text('x', encoding='utf-8')
            git(other, 'add', '.'); git(other, 'commit', '-m', 'race'); git(other, 'push', 'origin', 'gh-pages')

        sha = self.pub('v2', before_push=race)
        self.assertTrue(sha)
        self.assertEqual(self.show(), 'v2')
        self.assertEqual(self.show(name='2025-26.html'), 'v2-card')
        self.assertIn('extra.txt', git(self.bare, 'ls-tree', '--name-only', 'gh-pages'))
        self.assertEqual(git(self.bare, 'rev-parse', 'gh-pages'), sha)

    def test_race_conflict_on_index_prefers_ours(self):
        other = Path(self.t.name) / 'other2'
        git(Path(self.t.name), 'clone', '-b', 'gh-pages', str(self.bare), str(other))

        def race():
            (other / 'index.html').write_text('theirs', encoding='utf-8')
            git(other, 'add', '.'); git(other, 'commit', '-m', 'race'); git(other, 'push', 'origin', 'gh-pages')

        self.pub('ours', before_push=race)
        self.assertEqual(self.show(), 'ours')
        self.assertEqual(self.show(name='2025-26.html'), 'ours-card')

    def test_single_file_backward_compat(self):
        self.html.write_text('solo', encoding='utf-8')
        self.assertTrue(D.publish_html(self.dev, self.html, 'm'))
        self.assertEqual(self.show(), 'solo')


if __name__ == '__main__':
    unittest.main()

"""Documentation-only OREB closeout; never imports or runs the simulator."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
REPORTS = REPO / 'reports/defense-tenth'
BASE = REPORTS / 'step4-rebounds-turnover-time'
CLOCK = REPORTS / 'step4-rebounds-clock-competing'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def snapshot():
    # Source/protocol/results summaries are hashed. Large archived runs are not
    # read or rewritten; their size and modification time are checked separately.
    paths = list((REPO / 'src').glob('*.js'))
    for folder in REPORTS.glob('step4-rebounds*'):
        if folder == ROOT:
            continue
        for path in folder.rglob('*'):
            if path.is_file() and 'runs' not in path.parts and '__pycache__' not in path.parts:
                if path.suffix in {'.json', '.mjs', '.py', '.md', '.sha256'} and path.stat().st_size < 20_000_000:
                    paths.append(path)
    hashes = {p.relative_to(REPO).as_posix(): sha(p) for p in sorted(set(paths))}
    runs = {p.relative_to(REPO).as_posix(): [p.stat().st_size, p.stat().st_mtime_ns]
            for f in REPORTS.glob('step4-rebounds*') if f != ROOT
            for p in (f / 'runs').glob('*') if p.is_file()}
    return {'sha256': hashes, 'runSizeAndMtime': runs,
            'note': 'Runs checked by size/mtime only; not claiming a fresh content hash of archived runs.'}


if '--register' in sys.argv:
    assert not (ROOT / 'protocol.json').exists(), 'Registration already exists'
    write('protocol.json', {
        'version': 'oreb-closeout-1',
        'registeredUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': '既有輸出的收尾與採用清單；不重跑模擬、不下載資料、不新增估計或校準',
        'baseline': 'pure-oreb-turnover-time-1',
        'retain': ['OREB acquisition', 'individual OREB allocation', 'putback timing with league clock calibration', 'split live/dead turnover timing'],
        'optionalClock': 'oreb-clock-competing-1; retained as opt-in, default off; no further tuning',
        'uncertainty': '無顯著差異不代表等效；不新增事後等效門檻，不宣稱勝率完全不受影響',
        'stopRule': '收尾文件與保護檢查完成即停止；時序與籃板後位置留為已知限制',
        'noChangesToExistingArtifacts': True,
        'evidenceLabel': '四季已看過答案；同季重現，不能宣稱換隊或跨季泛化'
    })
    (ROOT / 'protocol.sha256').write_text(sha(ROOT / 'protocol.json') + '\n', encoding='utf8')
    write('protected-before.json', snapshot())
    print(json.dumps({'registered': True, 'sha256': sha(ROOT / 'protocol.json')}))
    sys.exit(0)

assert sha(ROOT / 'protocol.json') == (ROOT / 'protocol.sha256').read_text().strip()
before = read(ROOT / 'protected-before.json')
assert snapshot() == before, 'Existing inputs changed after closeout registration'
joint = read(CLOCK / 'joint-intervals.json')
pooled = joint['comparisons']['four-seasons-equal']
analysis = read(BASE / 'analysis.json')
cells = [x for x in analysis['cells'] if x['version'] == 'split']
assert len(cells) == 4
assert joint['replicates'] == 20000
arrays = read(BASE / 'seed-arrays.json')
for season, row in arrays.items():
    assert len(row['versions']['split']['net']) == 20
    assert len(row['ids']) == 30

metrics = {k: pooled['versions']['baseline'][k] for k in pooled['versions']['baseline']}
clock_metrics = {k: pooled['paired']['combinedMinusbaseline'][k] for k in pooled['paired']['combinedMinusbaseline']}
write('status.json', {
    'phase': 'closed', 'baseline': 'pure-oreb-turnover-time-1',
    'defaultRunner': 'reports/defense-tenth/step4-rebounds-turnover-time/run.mjs',
    'defaultMode': 'split',
    'retainedComponents': {
        'orebAcquisition': {'enabled': True, 'source': 'step4-rebounds-oreb'},
        'individualOrebAllocation': {'enabled': True, 'source': 'step4-rebounds-allocation'},
        'putbackTimingAndLeagueClockCalibration': {'enabled': True, 'source': ['step4-rebounds-putback-time', 'step4-rebounds-clock']},
        'splitTurnoverTiming': {'enabled': True, 'source': 'step4-rebounds-turnover-time'}
    },
    'optionalClock': {
        'version': 'oreb-clock-competing-1', 'retained': True, 'defaultEnabled': False,
        'switches': ['rimContactClock', 'competingFreshClock', 'postOrebDeadline'],
        'runner': 'reports/defense-tenth/step4-rebounds-clock-competing/run.mjs --full',
        'winsMAEDifference': clock_metrics['winsMAE'],
        'interpretation': '未發現顯著勝場誤差變化；未證明勝率逐場相同或統計等效；時序仍錯，保留可選模式但不升為預設'
    },
    'baselineMetrics': metrics,
    'existingDecisionsPreserved': True,
    'adoptionNote': '本次使用者指示下保留上述組合；舊批報告當時的未升級決策不回寫，也不把保留機制改稱預測準確度顯著提升。',
    'newSimulations': 0, 'newCalibration': False, 'newDownloads': 0,
    'futureWorkAutomaticallyStarted': False
})

residuals = []
for cell in cells:
    m = cell['metrics']; g = cell['global']; y = cell['target']
    residuals.append({
        'season': cell['season'],
        'netRMSE': m['netRMSE'], 'winsMAE': m['winsMAE'],
        'OREBRateCenteredRMSEpp': m['OREB_RMSE'], 'DREBRateCenteredRMSEpp': m['DREB_RMSE'],
        'efficiencyBias': m['efficiencyBias'], 'boxPossessionsBias': m['possessionsBias'],
        'TOVPerGameBias': m['TOVBias'], 'STLPerGameBias': m['STLBias'],
        'FGPercentagePointBias': m['FGpctBias'], 'threePercentagePointBias': m['threePctBias'],
        'FTAPerGameBias': g['fta'] - y['fta'],
        'offensePPGCenteredRMSE': m['offenseRMSE'], 'defensePPGCenteredRMSE': m['defenseRMSE'],
        'largestNetErrors': sorted(cell['teams'], key=lambda t: abs(t['netError']), reverse=True)[:5]
    })
write('residuals.json', {'label': '已看過答案；直接引用既有20 seed基準統計，非新實驗', 'seasons': residuals})

def interval(x):
    return f"{x['point']:+.4f} [{x['joint95'][0]:+.4f}, {x['joint95'][1]:+.4f}]"

lines = [
    '# 進攻籃板收束：保留取得與分配，時鐘保留可選模式', '',
    '本輪已收束。預設組合為 `pure-oreb-turnover-time-1`；保留進攻籃板取得、個人歸屬、補籃耗時＋聯盟時鐘校準、活球／死球失誤耗時拆分。新增的互斥違例時鐘保留為可關閉的實驗選項，預設不開。不再追加時鐘校準、接觸資料搜尋或籃板模型。本次只讀既有輸出、建立收尾文件與採用清單，沒有新模擬。', '',
    '本文件是目前採用狀態；舊版protocol、報告、decision與輸出保留當時內容，沒有回寫。保留有用的機制不等於宣稱每一批都改善勝場準確度。', '',
    '## 已驗證：保留了什麼', '',
    '|項目|證據|收尾狀態|', '|---|---|---|',
    '|球隊OREB取得|同校準對照：OREB率去均值MAE 2.0695→0.4600百分點，net RMSE 3.0748→2.5546，差−0.5202，聯合95% [−0.8236,−0.2047]|保留|',
    '|個人OREB歸屬|真實分鐘加權OREB/36 MAE 0.4605→0.0956，差−0.3650，聯合95% [−0.3902,−0.3312]|保留；這是分配批的獨立比較，不冒稱最終組合重新驗證過個人數字|',
    '|一次投失只分配一次籃板|五人取得份額組成一次隊伍成功機率，再選一人；不會五名高手各拿一板|保留守恆|',
    '|活球／死球失誤耗時|拆分後兩類耗時誤差下降，20 seed主準確度無顯著變化|保留已測組合，不稱為勝場提升|',
    '|分區讀取修正|10,767筆矛盾中距離標籤改為近框，969筆unknown|保留作診斷答案，不改舊原始資料或引擎|', '',
    '各項不同批比較不能連加成因果收益。取得與個人歸屬是兩個獨立目標；個人改善值得保留。', '',
    '## 時鐘是否影響勝率', '',
    '四季×20 seed（20261012–20261031），季內去均值、四季等權，franchise＋seed跨季配對重抽20,000次。以下候選為互斥時鐘combined，差值為候選−保留基準。', '',
    '|指標|預設基準|可選時鐘|差與聯合95%|', '|---|---:|---:|---|'
]
for k, label in [('netRMSE', 'net RMSE（分／場）'), ('winsMAE', '勝場MAE（勝）'), ('winsRMSE', '勝場RMSE（勝）'), ('OREB_RMSE', 'OREB率去均值RMSE（百分點）'), ('DREB_RMSE', 'DREB率去均值RMSE（百分點）')]:
    lines.append(f"|{label}|{metrics[k]['point']:.4f}|{pooled['versions']['combined'][k]['point']:.4f}|{interval(clock_metrics[k])}|")
lines += [
    '', '未發現顯著的勝場誤差影響，但「區間含0」不能證明完全等效；也沒檢定每場勝率是否不變。未事後訂等效門檻。依使用者本次指示保留選項，預設不升級，並停止追校準。', '',
    '時鐘的數量有改善：後半段20 seed全場違例0.670／隊／場，真實0.696；個人OREB後違例0.815%，真實0.674%。但額外時序診斷的違例平均耗時12.970秒，真實3.604秒（471模擬事件／714真實事件），明顯錯置。有效未碰框參數0.2113不是實測物理機率。碰框OREB重設14秒、未碰框沿用剩餘時鐘的規則保留於可選模組；碰框狀態本身仍是未識別的模型假設。', '',
    '可選時鐘另使球權代理約增加0.58–0.66／隊／場，不能全部當成新增實際球權；移除較長的24秒等待與FGA＋TOV代理記帳會共同改變數值。因此不因勝場未顯著變動而宣稱其他統計都更準。', '',
    '## 還有哪些地方不準', '',
    '|球季|net RMSE|勝場MAE|OREB率RMSE pp|DREB率RMSE pp|效率偏差|TOV／場偏差|STL／場偏差|FG偏差pp|3P偏差pp|FTA／場偏差|',
    '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|'
]
for x in residuals:
    keys = ['netRMSE', 'winsMAE', 'OREBRateCenteredRMSEpp', 'DREBRateCenteredRMSEpp', 'efficiencyBias', 'TOVPerGameBias', 'STLPerGameBias', 'FGPercentagePointBias', 'threePercentagePointBias', 'FTAPerGameBias']
    lines.append('|' + x['season'] + '|' + '|'.join(f'{x[k]:.3f}' for k in keys) + '|')
lines += [
    '', '聯盟偏差均為模擬−真實，使用合併計數口徑；球隊RMSE為去均值。效率與籃板總數接近，不代表事件類型都準；歷史三季失誤／抄截偏低，三分偏高、罰球仍有缺口。進攻籃板變準也不代表防守籃板同步完成，最終DREB率RMSE仍約1.310百分點。', '',
    '籃板後的完整進攻價值仍偏低：修正分區後的3 seed診斷為1.191對真實1.267分／OREB球權，差−0.076，聯合95% [−0.087,−0.066]；先失去球權10.50%對8.02%。搶板後先禁區出手少約3.55百分點、先三分少約2.75、中距離多約1.74；禁區第一球命中率低約2.50百分點。這些來自既有獨立事件樣本，不能混成20 seed最終版採用檢定。舊31%左右的真實快速補籃proxy已受分區錯標影響，修正答案是41.02%；未用同口徑重新跑模擬前，不再聲稱補籃頻率已對齊。', '',
    '其他限制：本人搶板位置、隊友卡位貢獻、受壓迫後拉出重攻未被直接觀測；OREB%仍含當季角色／體系影響，尚未證明換隊泛化。個人FG OREB分配改善不涵蓋FT籃板、DREB分配或團隊籃板。時鐘違例暫掛第一槽球員的慣例也不代表個人責任正確。', '',
    '### 攻防誤差與最大剩餘個案（描述，不作歸因）', '',
    '|球季|進攻得分去均值RMSE|防守失分去均值RMSE|最大五個net誤差：隊名、net誤差、進攻O／防守D貢獻|',
    '|---|---:|---:|---|'
]
for x in residuals:
    entries = []
    for t in x['largestNetErrors']:
        entries.append(f"{t['name']} {t['netError']:+.2f}（O {t['O']:+.2f}／D {t['D']:+.2f}）")
    lines.append(f"|{x['season']}|{x['offensePPGCenteredRMSE']:.3f}|{x['defensePPGCenteredRMSE']:.3f}|{'；'.join(entries)}|")
lines += [
    '', 'O為去除聯盟均值後的模擬得分−真實得分，D為同樣去均值的真實失分−模擬失分，兩者相加為去均值net誤差（全聯盟net均值為0）；O／D正值均代表推高模擬net。這是每場得失分拆解，包含節奏影響，不能直接當作純攻守能力因果。', '',
    '## 推測、未完成與停止範圍', '',
    '- 推測：下一個較值得獨立研究的部分是「取得籃板後的位置／補籃或重攻」，可能改善得分、失球、犯規與個人box；目前未證實收益，不自動開始。',
    '- 未完成：碰框物理狀態、短鐘OREB機會與違例時序；沒有聲稱靠配平總得分即可消除這些誤差。',
    '- 本輪收束：不再為時鐘開新一輪；不調失誤、命中率或球隊參數掩蓋；不退回較差的OREB取得／分配。',
    '- 所有四季已看過答案；能力卡含當季資料及真實逐場名單／分鐘軟目標。這是重現成績，不是事前或換隊預測。', '',
    '## 使用與重現', '',
    '採用狀態見status.json，剩餘誤差與個案見residuals.json。原有runner跳過已有輸出；此處不執行新模擬，也不把下列命令視為新任務。', '',
    '```powershell',
    '# 只重建本收尾文件並核對受保護檔案',
    'python reports/defense-tenth/step4-rebounds-closeout/build.py',
    '# 預設已測組合（需要自行要求重現時才執行）',
    'node reports/defense-tenth/step4-rebounds-turnover-time/run.mjs',
    '# 可選時鐘combined；不取代預設',
    'node reports/defense-tenth/step4-rebounds-clock-competing/run.mjs --full',
    '```', '',
    '來源：../step4-rebounds-oreb/report.md、../step4-rebounds-allocation/report.md、../step4-rebounds-turnover-time/analysis.json與seed-arrays.json、../step4-rebounds-zone-reader/report.md、../step4-rebounds-clock-competing/joint-intervals.json與report.md。', '',
    f"收尾protocol SHA-256：`{sha(ROOT / 'protocol.json')}`。不改凍結版本與歷次輸出。"
]
(ROOT / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf8')

after = snapshot()
assert after == before, 'Protected artifact changed during closeout'
write('audit.json', {
    'verifiedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'protocolUnchanged': True, 'sha256ProtectedFiles': len(before['sha256']),
    'runMetadataProtectedFiles': len(before['runSizeAndMtime']),
    'changed': [], 'newSimulations': 0, 'newDownloads': 0, 'newCalibration': False,
    'archivedRunContentRehashed': False,
    'note': '小型證據與來源核對SHA；大型run核對size/mtime，未宣稱全量重新雜湊'
})
write('deliverable-hashes.json', {p.name: sha(p) for p in ROOT.iterdir() if p.is_file() and p.name != 'deliverable-hashes.json'})
print(json.dumps({'closed': True, 'hashProtected': len(before['sha256']), 'runMetadataProtected': len(before['runSizeAndMtime']), 'newSimulations': 0}))

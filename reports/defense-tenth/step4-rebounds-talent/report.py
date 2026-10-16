"""Render registered offline results without changing estimates or predictions."""
from register import HERE
from analyze import read, STATIC, ATHLETIC, BEHAVIOR

NAMES = {'persistence': '原樣沿用前期', 'orebPctOnly': 'OREB%＋分鐘迴歸',
         'history': '籃板歷史＋分鐘', 'static': '歷史＋靜態身材',
         'talent': '歷史＋身材＋體測', 'talentOnly': '只用身材／體測／分鐘',
         'missingOnly': '歷史＋缺漏旗標', 'behavior': '歷史＋身材／體測＋追蹤行為'}
FIELDS = {'height': '身高', 'mass': '體重', 'wingspan': '臂展', 'reach': '站立摸高',
          'standingJump': '原地垂直跳', 'runningJump': '最大垂直跳', 'bench': '臥推次數',
          'agility': '禁區敏捷時間', 'shuttle': '折返敏捷時間', 'sprint': '3/4 場衝刺時間',
          'testAge': '距最新體測年數', 'speedOff': '進攻平均移速', 'speedDef': '防守平均移速',
          'chances36': 'OREB 機會／36 分鐘', 'contestedShare': '競爭中 OREB 占比'}

def f(v, n=4):
    return '—' if v is None else f'{v:.{n}f}'

def ci(pair, key='MAE'):
    x = pair[key]
    return f"{x['point']:+.4f} [{x['joint95'][0]:+.4f}, {x['joint95'][1]:+.4f}]"

def main():
    p = read(HERE / 'protocol.json')
    r = read(HERE / 'results.json')['results']
    extra = read(HERE / 'persistence-supplement.json')['results']
    cov = read(HERE / 'coverage.json')
    assoc = read(HERE / 'associations.json')['rows']
    fits = read(HERE / 'fits.json')
    lines = [
        '# OREB 靜態／動態資料：增量訊號稽核', '',
        '**結論：目的應是超越過去 OREB% 的泛化與預測，解釋力居次。這批已取得更多資料，但沒有證據支持把體測加成寫進卡或引擎。**', '',
        '四季均為「已看過答案」。本報告是時間切分的回溯資料外診斷，不是新盲測；不跑賽季模擬、不修改任何凍結版本／球員卡／引擎。', '',
        '## 目的與判準', '',
        '同季重現可直接用個人 OREB% 作觀測約束；它已經包含身材、彈跳、站位、角色與進攻環境的綜合結果。加入天賦資料的正當理由是：在未來、換隊或樣本少時，比只用既有籃板率更準。', '',
        '同季相關只說明共同變動，不是卡位、力量、彈跳的因果效果。沒有位置軌跡、衝搶選擇與球落點，這批不能識別「如果把同一人換到另一位置／陣容」的因果影響。OREB% 也不是人員互換後必然保持不變的純能力。', '',
        '預先登記主要比較為加入特徵相對 history 的成對區間；另外如實保留原樣沿用前季的 persistence。後者在本次跨季點估計更強，因此另用已存預測補算對它的區間，標為事後補充，未重訓或改模型。', '',
        '## 資料取得與完整度', '',
        '60/60 份官方 API 資料成功、沒有請求失敗或空表：2000–2025 年各兩份體型／體能資料，另四季各兩份籃板追蹤／速度距離資料。10 筆體測記錄缺有效 NBA PLAYER_ID，排除精確串接；不做名字猜配。', '',
        '來源：[NBA 體型測量](https://www.nba.com/stats/draft/combine-anthro)、[NBA 體能測試](https://www.nba.com/stats/draft/combine-strength-agility)、[NBA 進攻籃板追蹤](https://www.nba.com/stats/players/offensive-rebounding)。完整 URL、參數、下載時間與每份 SHA 見 fetch-manifest.json。', '',
        '下表是「具備該欄資料的球員所占真實分鐘」，不是實測覆蓋所有比賽。', '',
        '| 欄位 | 2022–23 | 2023–24 | 2024–25 | 2025–26 |',
        '|---|---:|---:|---:|---:|']
    for field in STATIC + ATHLETIC + ['speedOff', 'speedDef', 'chances36', 'contestedShare']:
        lines.append('| ' + FIELDS[field] + ' | ' + ' | '.join(f"{x['fields'][field]['minuteCoverage']*100:.1f}%" for x in cov['seasons']) + ' |')
    lines += ['', '| 檢查 | 2022–23 | 2023–24 | 2024–25 | 2025–26 |', '|---|---:|---:|---:|---:|']
    for field, title in [('players', '正分鐘球員數'), ('testAgeMedian', '最新體測距今中位年數'),
                         ('testAgeMax', '最新體測距今最大年數')]:
        lines.append('| ' + title + ' | ' + ' | '.join(str(x[field]) for x in cov['seasons']) + ' |')
    for field, title in [('trackedReboundMinuteFraction', '實際籃板追蹤分鐘比'), ('trackedSpeedMinuteFraction', '實際速度追蹤分鐘比')]:
        lines.append('| ' + title + ' | ' + ' | '.join(f"{x[field]*100:.2f}%" for x in cov['seasons']) + ' |')
    lines += ['',
        '臥推只是特定體測項目，不能等同籃球對抗力量；體重不能直接當力量。最大垂直跳也不是疲勞、持續起跳或比賽中搶板的即時彈跳。歷史測試缺漏具選擇性，且可能已過多年；各欄原始年份與來源逐人保存。testAge 是「任一欄最新測量」的年齡，不表示所有欄同年測量。', '',
        '## 同季訊號強度：解釋性相關', '',
        '每季至少 500 分鐘；只對該欄有實測者計算，不補值。下表為個人 OREB% 的 Pearson 相關；各季樣本數、Spearman 與 OREB／36 的對照完整保存在 associations.json。', '',
        '| 指標 | 2022–23 r | 2023–24 r | 2024–25 r | 2025–26 r | 2025–26 n |', '|---|---:|---:|---:|---:|---:|']
    for field in STATIC + ATHLETIC + BEHAVIOR:
        xs = [next(x for x in assoc if x['season'] == s and x['feature'] == field and x['target'] == 'pct') for s in p['seasons']]
        lines.append('| ' + FIELDS[field] + ' | ' + ' | '.join(f(x['Pearson'], 3) for x in xs) + f" | {xs[-1]['n']} |")
    lines += ['',
        '身高／臂展／摸高的單變量相關約 0.62–0.68，不能據此把它們各自加成到既有 OREB% 上，否則可能重複計算已由籃板率涵蓋的優勢。跳躍負相關不表示跳得高有害；位置、角色、選擇參加體測與測量年代都未被這張相關表控制。平均跑速亦屬比賽行為而非最大速度。', '',
        '籃板機會與 OREB% 同季相關約 0.97，兩者共同涵蓋已實現的籃板過程與角色，不能當成獨立天賦的證明。behavior 模型同時加入機會與移速，任何改善不能歸功於移速一項。', '',
        '## 主要跨季測試：2024–25 → 2025–26', '',
        '用 2022–23→2023–24、2023–24→2024–25 訓練，399 名來源季與目標季皆至少 100 分鐘者測試；所有預測特徵只取來源季或更早。MAE／RMSE 依目標季真實分鐘加權。OREB% 欄單位為百分點；OREB／36 欄單位為每 36 分鐘顆數。', '',
        '| 方法 | OREB／36 MAE | OREB／36 RMSE | OREB% MAE | OREB% RMSE |', '|---|---:|---:|---:|---:|']
    for model in NAMES:
        a = r['cross2025-rate']['all']['versions'][model]
        b = r['cross2025-pct']['all']['versions'][model]
        lines.append(f"| {NAMES[model]} | {a['MAE']:.4f} | {a['RMSE']:.4f} | {b['MAE']:.4f} | {b['RMSE']:.4f} |")
    lines += ['', '成對差為候選減對照，負值才是改善。以下為 MAE 差與 95% 球隊＋球員聯合區間。', '',
              '| 候選／比較 | OREB／36 MAE 差 [95%] | OREB% MAE 差 [95%] |', '|---|---:|---:|']
    for model in ['static', 'talent', 'behavior']:
        a = r['cross2025-rate']['all']['paired'][model + 'MinusHistory']
        b = r['cross2025-pct']['all']['paired'][model + 'MinusHistory']
        lines.append(f'| {NAMES[model]} − history（登記主要比較） | {ci(a)} | {ci(b)} |')
        a = extra['cross2025-rate']['all']['paired'][model + 'MinusPersistence']
        b = extra['cross2025-pct']['all']['paired'][model + 'MinusPersistence']
        lines.append(f'| {NAMES[model]} − 原樣沿用（事後較強對照） | {ci(a)} | {ci(b)} |')
    lines += ['',
        '**主要比較全數跨零。** 不用自身籃板歷史、只靠身材體測，OREB／36 MAE 0.652，接近原樣沿用的兩倍，且相對 history 的惡化區間完全大於零。', '',
        '追蹤行為組的 OREB／36 MAE 有較好的點估計，RMSE 卻沒有改善；官方 OREB% 的 MAE 仍略輸原樣沿用。這不是可確認的增益，不能升級。', '',
        '## 換隊與低分鐘檢查', '',
        '換隊定義為兩季最多分鐘的球隊不同，只作分組，不是交易因果推論；低分鐘為來源季 100–499 分鐘。', '',
        '| 分組 | n | 原樣沿用 MAE | history MAE | ＋身材 MAE | ＋體測 MAE | ＋追蹤 MAE |', '|---|---:|---:|---:|---:|---:|---:|']
    for group, title in [('movers', '換隊'), ('stayers', '留隊'), ('lowSourceMinutes', '來源低分鐘'), ('both500', '兩季皆 ≥500 分鐘')]:
        x = r['cross2025-rate'][group]
        v = x['versions']
        lines.append(f"| {title} | {v['history']['n']} | " + ' | '.join(f(v[m]['MAE']) for m in ['persistence', 'history', 'static', 'talent', 'behavior']) + ' |')
    lines += ['', '下表為相對 history 的 OREB／36 MAE 差：', '', '| 分組 | ＋身材 [95%] | ＋體測 [95%] | ＋追蹤 [95%] |', '|---|---:|---:|---:|']
    for group, title in [('movers', '換隊'), ('stayers', '留隊'), ('lowSourceMinutes', '來源低分鐘'), ('both500', '兩季皆 ≥500 分鐘')]:
        x = r['cross2025-rate'][group]['paired']
        lines.append('| ' + title + ' | ' + ' | '.join(ci(x[m + 'MinusHistory']) for m in ['static', 'talent', 'behavior']) + ' |')
    lines += ['',
        '換隊組沒有可確認改善；原樣沿用的點估計比三個增加資料的模型都好。低分鐘組有改善方向，但區間跨零，尚未證實可以泛化。這次不涵蓋來源季少於 100 分鐘或完全無歷史者，不能拿來宣稱已驗證新秀先驗。', '',
        '## 當季前段 → 後段（探索性）', '',
        '前 20／41 次有上場的個人出賽，預測其後出賽；不是球隊前 20／41 場。兩段各至少 100 分鐘。每個目標季只用更早球季訓練；本季全季 OREB%、全季速度與籃板追蹤一律不作早期預測輸入。這裡的 history 是前段 OREB／36＋前段分鐘。', '',
        '| 切分／目標季 | n | history MAE | ＋身材 MAE | ＋體測 MAE | 身材−history [95%] |', '|---|---:|---:|---:|---:|---:|']
    for k in [20, 41]:
        for season in ['2023-24', '2024-25', '2025-26', 'pooled']:
            x = r[f'within{k}-{season}']
            v = x['versions']
            lines.append(f"| {k}／{season} | {v['history']['n']} | {f(v['history']['MAE'])} | {f(v['static']['MAE'])} | {f(v['talent']['MAE'])} | {ci(x['paired']['staticMinusHistory'])} |")
    lines += ['',
        '20 次出賽合併的身材組 MAE 改善約 2.7%，未校正多重比較的 95% 區間不跨零；但 RMSE 區間仍跨零，41 次出賽亦未確認。這僅支持「值得研究小樣本先驗」，不支持一般跨季或引擎升級。合併依個人目標分鐘加權，非各季等權。', '',
        '## 方法、已驗證／推測／失敗', '',
        '已驗證：資料請求完成；精確 ID 串接；來源季時間規則；主要跨季三組皆無可確認的增量；純體測明顯弱於籃板歷史。估計是線性 ridge、訓練內依球員分組 5 折選 λ∈{0.1,1,10,100,1000}，不是看到測試結果再調參。缺值以訓練中位數補並加缺漏旗標，標準化僅用訓練資料；另有純缺漏模型作選擇效應對照。完整係數與折內分數見 fits.json。', '',
        '推測：成熟球員的 OREB% 已吸收多數身材優勢；過時與缺漏的體測、角色與籃板機會比測得的體能更重要。這些是解釋候選，尚未被因果檢定。', '',
        '失敗與限制：沒有找到可採用的跨季天賦增益；沒有直接量到卡位力量、反應／預判、疲勞、起跳時機或位置軌跡；沒有檢定多人籃板互補、團隊留球與搶板後位置。比賽移速不能代替最大速度。歷史身高／體重資料的首次發布日期無法驗證，當季前段測試尤其不能視為完全事前盲測。', '',
        '不確定性為 20,000 次球隊重抽交叉球員 Poisson 權重，同一球員與 franchise 跨季／版本共用權重。這裡沒有模擬 seed；不能冒稱是引擎驗收所要求的球隊＋模擬 seed 區間。未計訓練重估不確定性；分組與多項指標屬探索性，不作多重比較後確認。未做賽季模擬，因此沒有球隊淨勝分、勝場 MAE 或 DREB 改善的證據。', '',
        '球員全年顆數誤差僅把預測率乘上給定的真實分鐘（見 results.json conditionalCountMAE），不是分鐘預測，也尚未控制球隊節奏、可搶投失與球員實際籃板機會，不能稱為不依角色的籃板能力。', '',
        '## 建議：保留率基準，分開測機會與轉換', '',
        '本批採用決策：不改卡、不改引擎，不把身材／體測相關直接變成搶板加成。對有足夠樣本者保留個人 OREB% 為強基準；小樣本身材先驗只留研究候選。', '',
        '若繼續，下一項應先登記把「機會數」與「取得機會後搶到球的機率」分開，逐組比較只加速度、只加機會、只加競爭指標；目前 behavior 是整組測試，無法歸因。只有在新時間切分／換隊樣本贏過率基準，再考慮把它映射到搶板過程。這是下一批提案，本批未開始。', '',
        '## 登記、修復與重跑', '',
        f"Protocol UTC：{p['registeredAt']}。SHA-256：`{(HERE/'protocol.sha256').read_text(encoding='utf-8').split()[0]}`。",
        '',
        '初次分析遇到 NumPy 整數權重不能原地除以浮點平均值。保留 analyze-initial.py、原始程式鎖與 analysis-code-repair-1.json；修復只明確設定 float dtype 並核對已記錄的雜湊轉換，沒有改特徵、切分、模型、指標或採用規則。修復登記時尚未產生預測輸出。', '',
        '既有 protocol 不重建；在專案根目錄重跑：', '', '```powershell',
        'node reports/defense-tenth/step4-rebounds-talent/fetch.mjs',
        'python reports/defense-tenth/step4-rebounds-talent/analyze.py',
        'python reports/defense-tenth/step4-rebounds-talent/supplement.py',
        'python reports/defense-tenth/step4-rebounds-talent/report.py',
        'python reports/defense-tenth/step4-rebounds-talent/audit.py', '```', '',
        'fetch 會優先使用已下載原始資料。覆蓋率 coverage.json、關聯 associations.json、個人來源 features.json、預測 predictions.json、原登記結果 results.json、較強對照補充 persistence-supplement.json、完整性 completion-audit.json 均在同目錄。', '']
    (HERE / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    print('Saved report.md')

if __name__ == '__main__':
    main()

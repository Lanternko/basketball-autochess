"""Render the registered audit without changing its outputs or rules."""
from pathlib import Path
import json
import math

HERE = Path(__file__).resolve().parent
read = lambda name: json.loads((HERE / name).read_text(encoding='utf-8'))
p, a = read('protocol.json'), read('analysis.json')
sha = (HERE / 'protocol.sha256').read_text(encoding='utf-8').split()[0]
lines = [
    '# 籃板第1層：身材資料與表示法稽核', '',
    '**結論：可以先分開保留身高與體重；現有本機來源不足以獨立估計力量、彈跳或觸球高度。現有 physique 是尺寸代理，不是四項能力的實測整合。** 本項未改卡、未改引擎、未跑模擬，不宣稱籃板或 MAE 有任何新改善。', '',
    f"版本 `{p['version']}`；預登記 `{p['registeredAt']}`；SHA-256 `{sha}`。分析程式與表示法規格另在第一次分析輸出前鎖定，見 `analysis-code-registration.json`。", '',
    '四季均已看過答案。樣本是官方 player-games 中整季分鐘合計大於0的唯一球員；交易球員跨隊合併，分鐘只算一次。覆蓋率不是卡片有數字就算有量測。', '',
    '## 已驗證：資料覆蓋', '',
    '| 球季 | 正分鐘球員 | 輪替池 | 身高有值 | 體重有值 | 體重分鐘覆蓋 | 臂展／摸高／力量／兩種彈跳 |',
    '|---|---:|---:|---:|---:|---:|---|']
for s in a['seasons']:
    c = s['coverage']
    lines.append(f"| {s['season']} | {s['players']} | {s['rotationPlayers']} | {c['rawHeightInches']['observedPlayers']}/{s['players']} | {c['rawWeightLb']['observedPlayers']}/{s['players']} | {100*c['rawWeightLb']['minuteCoverage']:.3f}% | 本次來源均無量測 |")
lines += ['', '輪替池沿用 GP≥30、MIN/GP≥20，只用於重現舊排名。2023–24 的 Justin Jackson 在分鐘取整的官方紀錄中合計0分鐘，故本表571人；舊卡含572人。這不是新漏抓一名球員。', '',
          '「身高／體重有值」指季別查詢的官方個人資料有紀錄，不代表確認當季重新量測。臂展、摸高、力量、彈跳的0覆蓋是本次搜尋範圍的結論，不代表外部沒有任何資料。', '',
          '搜尋範圍：data/ 與 reports/ 的 bio/combine/anthro/measurement/player-info/commonplayer/draft/physical 檔名，以及四季已部署 bundle 欄位；略過模擬 runs/ 和逐球 pbp/ 目錄。11個候選JSON中，只有4個bio是相關原始NBA資料表。其餘是已產生的分析輸出；檔名 combined 不能當作 combine 體測資料。完整路徑／schema見 analysis.json。', '',
          '## 已驗證：原始資料與卡片不一致的缺值規則', '',
          '| 球季 | 球員 | 真實分鐘 | 原始體重 | 已部署體重 | 已部署 physique |',
          '|---|---|---:|---|---|---:|']
for s in a['seasons']:
    for r in s['missingRawBody']:
        weight = '欄位未保留' if r['deployedWeightLb'] is None else f"{r['deployedWeightLb']:.0f} lb（預設）"
        lines.append(f"| {s['season']} | {r['name']} | {r['minutes']:.0f} | 缺漏 | {weight} | {r['deployedPhysique']:.3f} |")
lines += ['',
    '- 歷史下載程式先把缺體重填成210 lb，後續建卡因而把它當成有效體重。2024–25 Jaylen Wells 的缺值甚至進入輪替排名池。這是可重現的缺值／來源標示問題；本項不修改凍結卡。',
    '- 2025–26 原始體重有576/582人，卡片卻對所有582人都沒有 bodyWeight 欄位：資料在來源存在，輸出時未保留。缺體重的6人 physique=70，與歷史處理不同。不能把卡片無體重誤報為原始體重全部缺漏。',
    '- 有原始紀錄者的身高、以及歷史有原始體重且卡保留體重者，均與已部署值一致。交易造成的重複卡沒有身材欄位衝突。', '',
    '來源：scripts/fetch_defense_seventh_season.js:22；reports/defense-tenth/step4-t0/prepare.mjs:31–36；scripts/build_season_league.js:56–70。', '',
    '## 已驗證：舊身材值在做什麼', '',
    '`size = 身高(inches) + 體重(lb)/10`，再按當季輪替池百分位映射至40–99，缺值走各自歷史流程。四季合計2261個正分鐘球員季的 physique 均可精確重建，無不一致；這只驗證表示法，沒有驗證籃板預測。', '',
    '這個式子隱含「高1吋」與「重10磅」對尺寸索引完全等價，並未識別力量或跳躍。百分位又依當季參考球員池改變，並非固定物理尺度。', '',
    '| 球季 | 身高–體重 Pearson | 身高–physique Pearson | 體重–physique Pearson |',
    '|---|---:|---:|---:|']
for s in a['seasons']:
    c = s['correlations']
    lines.append(f"| {s['season']} | {c['rawHeightInches vs rawWeightLb']['Pearson']:.3f} | {c['rawHeightInches vs deployedPhysique']['Pearson']:.3f} | {c['rawWeightLb vs deployedPhysique']['Pearson']:.3f} |")
lines += ['',
    '以上只描述欄位重疊；不是力量、體重或身高對進攻籃板的因果係數。未計算 OREB/DREB、球隊net或勝場與身材的相關，未用這些結果挑係數。', '',
    '## 已驗證：身材影響路徑，不能整張卡一起換', '',
    '| 路徑 | 程式位置 | 實際作用 |',
    '|---|---|---|',
    '| FG籃板爭搶與歸屬 | src/rebound_block_model.js:39–49 | 0.7×rebound+0.3×physique，再與位置／衝搶因子結合 |',
    '| 補籃選擇 | src/probability_model.js:178–182 | physique與對手協防影響補籃機率 |',
    '| 協防 | src/probability_model.js:202–204 | physique墊高協防合成值 |',
    '| 近框命中與出手選擇 | src/probability_model.js:231,336,364 | 身材差進入近框優勢及區域選擇 |',
    '| 包夾威脅與引力 | src/probability_model.js:80–95 | physique進入威脅，再影響隊友情境 |',
    '| 封阻分解 | src/rebound_block_model.js:89–91 | physique與onBall/help合成封阻歸屬 |',
    '| 位置代理 | scripts/build_season_league.js:59；src/minute_budget.js:43–45 | 預設角色由身高分帶；逐場官方位置可覆蓋，並非永遠由身高決定 |',
    '| 體能 | scripts/build_season_league.js:69；src/defense_fourth_game.js:122 | stamina來自MPG排名並影響疲勞；不是實測耐力，也不是力量／跳躍 |', '',
    f"純代數敏感度：固定其他輸入，physique增加10時，單一球員該項籃板contest值乘 exp(0.3×10/45)={math.exp(3/45):.5f}，約+6.89%。這不是球隊OREB率增加6.89%，也不是新模擬結果。", '',
    '若直接全域更換 physique，會同時改籃板、補籃與攻防情境，失去歸因。未來身材實驗應只替換指定籃板路徑並獨立開關，其餘路徑凍結；也不能在既有含身材影響的實績卡上再無條件疊加一遍。', '',
    '## 已驗證：資料時間與季間變化', '',
    '| 相鄰球季 | 身高有變／雙季有值 | 體重有變／雙季有值 |',
    '|---|---:|---:|']
for t in a['adjacentSeasonMetadata']:
    h, w = t['changes']['rawHeightInches'], t['changes']['rawWeightLb']
    lines.append(f"| {t['from']}→{t['to']} | {h['changedPlayers']}/{h['matchedObservedPlayers']} | {w['changedPlayers']}/{w['matchedObservedPlayers']} |")
lines += ['',
    '例如2024–25→2025–26，有147/464名共同球員的登錄身高改變。這只能確認metadata不同，不能解讀為147人長高／縮矮，也不能用來估年齡曲線。量測方法、登錄更新與真實改變尚無法區分。', '',
    '四份bio都在2026年取得，measurementDate與最早availabilityDate均未知。來源為指定季查詢，但尚無當季截止日的歷史快照證明；本次同季資料稽核可用，不能自動宣稱符合真正事前測試。各來源fetchedAt與URL列在 analysis.json。', '',
    '## 提案：身材表示法，尚未實作', '',
    '詳細規格見 representation-spec.json，於分析輸出前鎖定。保留身高、臂展、站立摸高、體重、力量測試種類與原值、原地彈跳、助跑彈跳，各自帶單位、來源、量測日、取得日、可用日、缺值與不確定性。', '',
    '1. 不新增萬用0–120身材分；不把體重改名為力量。',
    '2. 只有摸高與彈跳都確實有資料、量測定義相容時，才可描述測試觸球高度；它仍不是每次實戰的有效觸球高度。',
    '3. 缺值保留null；未來若建先驗，須另登記、明示估計值與不確定性，本項不補值。',
    '4. 體能、卡位、積極性與起始位置另屬其他機制；不塞進本層。',
    '5. 下一次若接入身材，必須局部替換指定舊項，逐項消融，不可全域換physique。', '',
    '## 推測與失敗／未解決事項', '',
    '- 推測：尺寸、力量、跳躍混用，可能使不同類型球員被給予相同優勢；未測其籃板與球隊誤差，不能說已找出主因。',
    '- 未能估計：獨立實戰力量、當季彈跳、卡位與身材各自的因果權重。現有資料不足，未硬湊係數。',
    '- 未完成外部覆蓋量測：NBA有[體型量測](https://www.nba.com/stats/draft/combine-anthro)及[力量／敏捷體測](https://www.nba.com/stats/draft/combine-strength-agility)頁面。本項只確認頁面，未下載球員體測資料，加入後的覆蓋率未知。舊體測如何代表當季狀態仍需驗證。',
    '- 不改凍結版本的歷史預設值；僅在新稽核資料中保留原始缺值與來源。',
    '- 沒有新的MAE或籃板成績，也沒有啟動第2–5層。本項完成即停。', '',
    '## 產物與重跑', '',
    '`body-records.json` 是逐球員來源稽核表，包含原始／已部署欄位與缺值，並不是新能力卡。`analysis.json` 包含完整缺漏清單、季間變更、候選檔案schema與描述統計。`completion-audit.json` 記錄舊檔保護與一致性檢查。', '',
    '```powershell',
    'python reports/defense-tenth/step4-rebounds-body/analyze.py',
    'python reports/defense-tenth/step4-rebounds-body/report.py',
    'python reports/defense-tenth/step4-rebounds-body/audit.py',
    '```', '',
    '預登記 register.py 已執行；再次執行會拒絕覆寫。重跑分析需維持登記輸入與程式雜湊一致。']
(HERE / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Report written')

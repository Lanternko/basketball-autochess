import json,csv,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scores=read(R/'scores.json');fit=read(R/'fit-verification.json');iso=read(R/'isolation-verification.json');inputs=read(R/'input-verification.json');assert iso['passed'] and inputs['passed']
old=scores['aggregate']['v30'];new=scores['aggregate']['rotation-space'];failed=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cs={c['version']:c for c in scores['cells'] if c['season']==season}
 if cs['rotation-space']['teamMetrics']['winsMAE']>cs['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:q=csv.DictReader(f);players=list(q);columns=len(q.fieldnames)
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'countsOnlyRepair':True,'allNonBlockOutputsExactlyEqualV30':True,'games':28023,'canonicalWorkloadSmokeGames':40,'sourceGames':4421,'sourceFga':785193,'sourceMisses':414386,'sourceBlocks':42932,'targetPlayers':582,'targetPlayerColumns':columns,'selectedSigma':fit['selectedSigma'],'failedWinGateSeasons':failed,'scope':'Individual block count mechanism repaired and isolated. Team win model remains archived v30 and fails unchanged gates. No ranking or injury coefficient fit.'}
(R/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
lines=['# v39：由場上五人的來源阻攻率決定阻攻分類','',
'**完成四季 28,023 場、2025–26 全 582 人個人數據驗證。所有比分、球員正負分、分鐘、非阻攻計數及在場命中率與 v30 完全相同，只有阻攻分類改變。本版不更新 OVR；v30 的三季勝場誤差門檻仍未通過，沒有採用為正式模型。**','',
'## 本次修正','',
'舊模型先用通用區域／體格／防守公式決定是否產生阻攻，再按球員來源紀錄分配。來源中的高阻攻球員仍會被第一步壓縮。新公式只在既定失投之後，讓五個防守者和「沒有阻攻」共同競爭：λᵢ=exp(區域截距+球員來源對數率)，P(阻攻者=i｜失投)=λᵢ/(1+Σλ)。球員紀錄同時影響總量和分配。','',
'防守命中率公式原本已含阻攻影響，因此不再額外降低命中率。保留舊引擎的亂數消耗順序，用一次均勻亂數做新分類，原本會用到的球員分配亂數照常消耗但不控制新結果。逐欄比較全部輸出，只允許數值欄位 blk 不同，沒有排除整個子樹或只比較平均比分。這是可追蹤的分類修正，不能被解讀成新增了比賽影響值。','',
'## 來源與留出驗證','',
'獨立重接 4,421 場逐球紀錄及當時五人陣容，共 785,193 次出手、414,386 次失投、42,932 次阻攻（含補籃），逐筆分組與分鐘皆重現。球員率採均值零的高斯先驗；只以較早三季五折、整場留出的標記機率負對數似然，從 σ=0、.25、.5、1、2 選出 .5。2025–26 未參與選擇。共 84 次擬合的機率、似然、梯度、整場切分及比較基準均獨立重算。','',
'| 球季 | 留出失投數 | 新公式 NLL | 240 分鐘平滑分配基準 | NLL 改善 |','|---|---:|---:|---:|---:|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 rs=[r for r in fit['heldout'] if r['season']==season and r['sigma']==.5];nll=sum(r['nll'] for r in rs);benchmark=sum(r['benchmarkNll'] for r in rs)
 lines.append(f"| {season} | {sum(r['misses'] for r in rs):,} | {nll:.3f} | {benchmark:.3f} | {100*(benchmark-nll)/benchmark:.3f}% |")
lines+=['','基準也只用各折訓練場次：固定區域阻攻／失投比例，再按球員 BLK／對手失投曝險、等同 240 分鐘先驗分配，比等權基準更強。NLL 同時評估有無阻攻及阻攻者。這是同季局部重建，留出比賽仍可能共享球員與隊伍；不是跨季預測或阻攻純能力的因果估計。完整來源卡本身使用該季結果，來源／模型不確定性不包含在模擬誤差內。','',
'初次數值求解有一筆梯度 0.0016126 高於原定 0.001，停止而未產生參數選擇結果。保留 57 個已通過檔案，另行凍結同一目標的精確 Hessian／Newton 細化程序，沒有放寬容忍值、改資料或改超參數。所有舊新擬合重驗；完整 Hessian 抽樣以梯度差分核對。','',
'## 完整模擬個人誤差','',
'下表是四季各季等權平均的個人 MAE；每季內按真實分鐘加權，主要樣本為至少 500 分鐘，命中率另有出手門檻。所有低分鐘球員仍另行匯出並分組檢查。per36 在此只用來比較相同曝險的數據誤差，不拿來把替補外推成先發。','',
'| 指標 | v30 | v39 |','|---|---:|---:|']
for k in old['individualMAE']:lines.append(f"| {k} | {old['individualMAE'][k]:.6f} | {new['individualMAE'][k]:.6f} |")
lines+=['','高阻攻（真實 BLK36≥2、至少500分鐘）的82個球員季，四季等權MAE由0.782216降到0.267624；被低估者由82個降到73個，仍有殘餘負偏差。低阻攻（BLK36<1）1,150個球員季的MAE亦由0.092148降到0.075173。這些分組用觀察表現定義，是誤差診斷。在場／不在場／隊友／對手命中率十項 MAE 均與 v30 相同。完整分組有 144 個位置／分鐘／版本格、40 個高助攻／得分／阻攻等表現尾端格；閾值依觀察結果定義，含選擇及回歸均值效應，是偏差診斷，沒有拿來調參。','',
'| 2025–26 球員 | 真實 BLK36 | v30 | v39 |','|---|---:|---:|---:|']
target={v['version']:v for v in scores['cells'] if v['season']=='2025-26'}
for name in ['Victor Wembanyama','Mitchell Robinson','Cade Cunningham','Neemias Queta','Nikola Jokić']:
 a=next(p for p in target['v30']['players'] if p['name']==name);b=next(p for p in target['rotation-space']['players'] if p['name']==name);m=a['metrics']['blk36'];n=b['metrics']['blk36'];lines.append(f"| {name} | {m['actual']:.3f} | {m['predicted']:.3f} | {n['predicted']:.3f} |")
lines+=['','這是完整球季模型輸出，與只在來源五人陣容上計算的期望值不同。不能從這張阻攻表直接推論 OVR 次序。','',
'## 勝場門檻與下一步','',
'| 球季 | 已封存正式模型 winsMAE | v30＝v39 | 正式模型＋0.5 門檻 |','|---|---:|---:|---|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cs={c['version']:c for c in scores['cells'] if c['season']==season};control=cs['control']['teamMetrics']['winsMAE'];candidate=cs['rotation-space']['teamMetrics']['winsMAE'];lines.append(f"| {season} | {control:.6f} | {candidate:.6f} | {'未通過' if season in failed else '通過'} |")
lines+=['',
'v38 的 OVR 傳球角色重複修正已保留：實驗 OVR 從不可變來源重建一次，與完整球季來源一致。v39 的 582 人、150 張對手卡、五種不同位置的平均屬性 70 隊友，除新增阻攻描述外逐欄相同；五位球員兩種負荷、雙邊座位共 40 場輸入冒煙測試，亦只有阻攻不同。這不是新的全員排名，也不是健康負荷精度驗證。','',
'使用者的負荷規則沿用：主要看能上場時的貢獻；單季受傷不扣分，只有多季反覆、有足夠紀錄的傷病才小幅折扣（目前為正貢獻 × .10 × 第二高的年度有紀錄傷病比例；.10 是暫定偏好係數，並非醫療風險估計）；低上場負荷的外推限制更強，第六人仍可依貢獻得到高分。分鐘效益飽和，不把 42 分鐘線性加成；既有 34.983 分鐘是來源計算的測試上限，不是生理定律。對手強度、先發長負荷效率與體能仍需分開驗證，不能只靠 per36 或教練使用量宣稱能力。','',
'下一步仍需解決會改變得分／勝負的創造與防守機制及球隊驗證，再跑全員健康負荷／反覆傷病 OVR。SGA、Luka、Jokić 的期望名次只作合理性檢查，不是名字加分或擬合目標。最新完整 OVR 仍是 v24；本版及 v38 都未產生新 Top50。','',
'## 檔案','',
'- `2025-26-player-validation.csv`：582 人的基本數據、總量、分鐘、命中率與在場團隊／隊友／對手命中率，含誤差與樣本曝險。',
'- `scores.json`、`error-strata.json`、`skill-cohort-errors.json`：四季完整比較與偏差分組。',
'- `fit-verification.json`、`data-verification.json`：來源機制及擬合獨立重算。',
'- `isolation-verification.json`：24 份完整輸出、28,023 場逐欄隔離驗證。',
'- `input-verification.json`：來源／平均隊友／canonical OVR 輸入隔離檢查。',
'- `verification.json`：上述結果、報告、狀態與來源程式的最終雜湊驗證。','']
(R/'report.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps(status,indent=2))

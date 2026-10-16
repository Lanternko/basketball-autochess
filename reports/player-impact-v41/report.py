import json,csv,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scores=read(R/'scores.json');old=scores['aggregate']['v39'];new=scores['aggregate']['rotation-space'];probe=read(R/'probe-summary.json');failed=[]
for name in ['fit-verification.json','model-verification.json','context-verification.json','input-verification.json','ledger-verification.json','probe-verification.json']:
 check=read(R/name);assert check['passed']
 for p,h in check['hashes'].items():assert sha(p)==h,p
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cells={c['version']:c for c in scores['cells'] if c['season']==season}
 if cells['rotation-space']['teamMetrics']['winsMAE']>cells['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
with (R/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:reader=csv.DictReader(f);rows=list(reader);columns=len(reader.fieldnames)
assert len(rows)==582
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'latestCompleteOvrVersion':24,'sourceFreshDefenseChanged':True,'sourceRawAttributesPreserved':True,'fullSeasonGames':28023,'workloadDiagnosticGames':19200,'sourceGames':4421,'sourceFreshFga':754914,'targetPlayers':582,'targetPlayerColumns':columns,'failedWinGateSeasons':failed,'selectedSigmaByZone':read(R/'fit-verification.json')['selectedSigmaByZone'],'mainOvrHealthOnly':True,'availabilityDisplayedSeparately':True,'injuryDeductionInMainOvr':False,'stopFurtherMechanismVersionsForRanking':True,'scope':'Close v41 as a verified, unadopted experiment. New display OVR is a separate transparent summary, not constrained to simulated replacement wins. Existing recurrence adjustments remain diagnostics only. User major goal still not achieved.'}
(R/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
lines=['# v41 收束：個人重建改善，整體尚未驗收','',
'**四季28,023場完整／來源場次模擬、2025–26全582人170欄誤差對照，以及19,200場負荷診斷均完成。兩季勝場門檻仍未通過，因此沒有採用、沒有新全員OVR，不再為修榜單繼續新增機制版本。**','',
'## 使用者最新定義','',
'主要OVR只評健康上場時的能力與有證據支持的貢獻，出勤可靠度另外列出。單季、多季受傷都不直接扣主要OVR；這取代早先「反覆傷病輕扣主要分數」的偏好。既有0／.05／.10扣分只保留為歷史敏感度診斷。替補不能按短時間per36外推先發效率，但也不依替補標籤強制降名次。','',
'顯示OVR與模擬器分開驗收：模擬可採細分能力與複雜公式；OVR是使用者理解健康能力強弱的透明摘要，無須作為模擬輸入，也無須只從替換球員後的模擬勝率推導。詳見 `user-rating-spec.json`。','',
'## 本版機制及來源驗證','',
'各投籃區域估計 logit(P命中)=截距＋投籃者參數＋五位防守者參數。防守參數的高斯先驗僅按較早三季、整場五折留出NLL選擇；三分σ=0，中距離.025，近距離.05。共用先驗原型v40完整保留，v41在完整模擬前明確另版，沒有事後改掉原型。三分缺少可重現的個人訊號，因此收縮到零。','',
'原模型保留原始屬性對當前相對來源變動的斜率，來源防守體格基線中立化，避免把同一陣容關聯與來源體格效果重複加入。補籃沿用既有模型；進攻創造、犯規、失誤、籃板與阻攻機制均保持v39。實際來源陣容重算投籃校準，不用模擬殘差補差。','',
'四季2,262個球員季、2,581張球隊卡、270,090個情境全部核對。獨立串流重建來源體力與FGA加權校準，並用中立舊公式＋直接logit參考核對20,142,135個區域機率；加權校準差異最大約4.2e−17。來源出手／分鐘／體力及原始欄位完全保留。27個組合來源擬合、81個區域擬合獨立重算似然、梯度與留出切分。','',
'這些是控制投籃者後的陣容關聯，仍有隊友／對手／戰術混雜與共線性；完整來源參數含同季結果。整場留出可以驗證部分訊號，不能證明跨季預測、純防守能力或健康能力已被因果識別。未知無球、掩護、控球、包夾處理仍保持預設，沒有宣稱已量測。','',
'## 個人數據準確度','',
'下表為四季各季等權平均MAE；每季內至少500真實分鐘、按真實分鐘加權，命中率另有出手門檻。per36只用來比較數據重建誤差，不用來替補外推。','',
'| 指標 | 正式封存模型 | v39 | v41 |','|---|---:|---:|---:|']
for k,v in new['individualMAE'].items():lines.append(f"| {k} | {scores['aggregate']['control']['individualMAE'][k]:.6f} | {old['individualMAE'][k]:.6f} | {v:.6f} |")
individualBetter=[k for k in new['individualMAE'] if new['individualMAE'][k]<old['individualMAE'][k]]
lines+=['',f"相對v39，14項個人平均誤差中{len(individualBetter)}項減少、{14-len(individualBetter)}項增加，多為小幅變化；不能稱所有個人數據都更準。低分鐘／位置共144格，以及高得分／助攻／阻攻尾端40格另有完整誤差檔。來源率本身使用同季產量，因此小重建誤差不是獨立預測證據，也不能直接當OVR客觀性的證明。",'',
'## 在場團隊數據與勝場','',
'| 在場／不在場指標，MAE百分點 | v39 | v41 |','|---|---:|---:|']
for k,v in new['onCourtMAE'].items():lines.append(f"| {k} | {old['onCourtMAE'][k]:.6f} | {v:.6f} |")
lines+=['','對手整體FG誤差改善，但對手3P由1.1862增至1.4354百分點；雖然三分防守個人係數為零，來源體格中立化、個人投籃校準與回合變動仍可改變模擬輸出。不能只用近距離改善掩蓋這個退步。原始ON–OFF受隊友、對手與輪替影響，不是個人因果能力。','',
'| 球季 | 正式封存勝場MAE | v39 | v41 | 正式＋0.5場門檻 |','|---|---:|---:|---:|---|']
for season in ['2022-23','2023-24','2024-25','2025-26']:
 cs={c['version']:c for c in scores['cells'] if c['season']==season};lines.append(f"| {season} | {cs['control']['teamMetrics']['winsMAE']:.6f} | {cs['v39']['teamMetrics']['winsMAE']:.6f} | {cs['rotation-space']['teamMetrics']['winsMAE']:.6f} | {'未過' if season in failed else '通過'} |")
lines += ['',f"四季等權平均勝場MAE：正式{scores['aggregate']['control']['team']['winsMAE']:.4f}、v39 {old['team']['winsMAE']:.4f}、v41 {new['team']['winsMAE']:.4f}。每季淨得分RMSE平均則由v39 {old['team']['netRMSE']:.4f}降到v41 {new['team']['netRMSE']:.4f}，優於正式{scores['aggregate']['control']['team']['netRMSE']:.4f}；仍不能取代逐季勝場門檻或忽略三分退步。",'',
'## 健康上場負荷診斷','',
'固定自然位置，其餘四個不同位置、屬性算術平均各70的隊友，30個固定對手、4組種子／輪替相位、雙邊座位，與相同位置平均球員配對。健康支持負荷是出賽場次內逐場封頂後平均，缺賽不補零；這是已觀察負荷的政策代理，仍可能混入傷後復出或教練選擇，不能當生理上限。全上限情境只用於檢查外推差異。','',
'| 診斷球員 | 支持分鐘 | v39每場相對基準淨分貢獻 | v41 |','|---|---:|---:|---:|']
for p in probe['players']:
 a=next(a for a in p['arms'] if a['arm']=='supportedHealthy');lines.append(f"| {p['name']} | {a['minutes']:.2f} | {a['v39']['mean']:.4f} | {a['v41']['mean']:.4f} |")
lines+=['','這10人不是聯盟排名，不能把其順序當新前20。完整13項計數、雙臂配對差及條件式近似95%區間在 `probe-summary.json`。區間只反映固定模型與來源下的模擬變動，未含來源／模型不確定性或多重比較修正。v39基準與v38 canonical v30的比分及全部非阻攻計數逐筆完全一致；新阻攻計數另行保留。','',
'## 可收束的結論','',
'本輪研究可收束為「已驗證的未採用實驗」，大目標尚未完成。個人同季重建大幅優於正式封存模型，但球隊勝場尚未全面過關；兩者存在權衡，不能宣稱系統已足夠準。','',
'最新完整582人榜仍是v24，按固定模型模擬勝率排序；其中替補中鋒過高與未知技巧預設等缺口仍存在，不能當作最新健康能力OVR。後續顯示OVR應先固定定義、證據來源、負荷／小樣本處理、權重與驗收，再出全員榜及分項解釋，不再等所有模擬機制完全一致才開始。','',
'使用者所貼影片摘要支持多種影響證據交叉檢查；本次讀的是摘要，未獨立核驗影片排名。不能只把多個指標相加就稱客觀，需檢查是否重複計算、是否偏重累積出勤，以及隊友／對手與小樣本影響。健康能力、當季總貢獻、潛力、出勤可靠度必須明確分開。','',
'檔案：`2025-26-player-validation.csv`、`scores.json`、`error-strata.json`、`skill-cohort-errors.json`、`probe-summary.json`、`user-rating-spec.json`，以及各項獨立驗證／凍結協定。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('v41 report/status: unadopted;failed gates '+','.join(failed)+';mainOVR health-only,availability separate.')

import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=['source-fit-protocol.json','target-null-protocol.json','data-verification.json','fit-verification.json']
for name in checks:
 d=read(R/name)
 if 'passed' in d:assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
selection=read(R/'selection.json')
assert selection['selectedSigma']==.05
status={'officialModelAdopted':False,'goalComplete':False,'fullOvrThisVersion':False,'fullSeasonSimulationThisVersion':False,'latestCompleteOvrVersion':24,'sourceOnlyPrototype':True,'selectedCommonSigma':.05,'sourceGames':4421,'freshFga':754914,'freshFgm':354082,'verifiedFits':104,'refinement':'v41 explicitly selects zone-specific priors before full simulation. v40 common-prior prototype remains preserved.'}
assert not (R/'status.json').exists();(R/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
lines=['# v40：五人防守來源模型，共用先驗原型','',
'**來源建模與獨立驗證完成；沒有跑完整賽季、沒有新 OVR、沒有採用。後續 v41 明確另版改成分投籃區域選先驗，保留本版結果。**','',
'資料是四季 4,421 場的 754,914 次非快速補籃出手、354,082 次命中，逐筆重接投籃者及雙方場上五人。快速補籃沿用既有同一籃板手 0–3 秒的來源分類，並非追蹤資料證實的投籃種類；零秒陣容事件也保留。','',
'各區域使用 logit(P命中)=區域截距＋投籃者參數＋場上五個防守者參數。投籃者採等同60分鐘的聯盟來源先驗，防守者採均值零高斯先驗。只用較早三季、按整場分五折的出手 NLL，從 σ=0、.025、.05、.1、.2、.4 選共同 σ；2025–26 不參與選擇。相同球員仍可能出現在訓練與留出場次，並非跨季預測或純個人防守能力的因果估計。','',
'| 共同 σ | 較早三季留出 NLL |','|---|---:|']
for row in selection['olderOnlyScores']:lines.append(f"| {row['sigma']} | {row['heldoutNll']:.6f} |")
lines+=['','選出 .05 的總 NLL 優於零防守者模型，但三分區的留出誤差在四季都變差；改善主要來自近距離。這表示一個共用收縮強度掩蓋區域差異，因此後續 v41 另行凍結「各區域只以較早三季選擇」的規則。沒有看完完整模擬後再回頭更換本版係數。','',
'90次較早三季留出、4次完整來源、2025–26五折候選及五折零防守基準，共104次擬合均獨立重算直接陣列形式的機率、似然、先驗、梯度與切分；目標與 Hessian 另以差分核對。最大未縮放梯度為8.133e−6，低於原定0.001。','',
'沒有使用名字、名次、勝場誤差、模擬殘差、在場正負值或只有命中才存在的助攻標記作預測欄位。仍有陣容共線、隊友／對手與未觀測戰術混雜，不能把係數當成已識別的個人能力。未量測的無球、掩護、控球、包夾處理仍保持原本預設，沒有宣稱已量測。','',
'使用者的健康／替補負荷政策延續：看能上場時的貢獻；單季受傷不扣，反覆多季才輕扣，替補不能以短時間 per36 直接外推為先發。這份來源防守研究尚未執行新的全員負荷評分。','',
'`data-verification.json`、`fit-verification.json` 保存獨立驗證；`source-fit-protocol.json`、`target-null-protocol.json` 保存擬合前規則與雜湊。`all-verification.json` 封存本版根目錄及所有來源／擬合依賴。']
(R/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

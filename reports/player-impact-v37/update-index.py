import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous=read('reports/player-impact-v36/verification.json')
for p,h in previous['hashes'].items():assert sha(p)==h,p
index=Path('reports/player-impact-validation/report.md');transition=read('reports/player-impact-v36/index-transition.json');assert sha(index)==transition['updatedIndexSha256']
snapshot=R/'index-before-v37.md';assert not snapshot.exists();snapshot.write_bytes(index.read_bytes())
note='最新完整四季試驗為[v37保留傳球與自主餘額](../player-impact-v37/report.md)，附[全582人176欄](../player-impact-v37/2025-26-player-validation.csv)與[核對](../player-impact-v37/verification.json)。28,023場完整／嚴格比賽與逐球來源核對完成，原891次零自主支援消除，但9項個人MAE退步、四季勝場界線皆未過，未採用。另發現OVR輸入重複校正傳球率，v29、v30、v34至v37負荷數字不能直接當成控制相同來源角色的比較；v37原9,600場負荷比較撤回有效性，數字保留供追溯。四季來源路徑與v24角色率另經檢查，不受此重複組裝影響。修復與同來源角色重跑見[v38](../player-impact-v38/report.md)。正式模型與最新完整v24實驗榜不變，目標未完成。'
text=index.read_text(encoding='utf-8');head,rest=text.split('\n\n',1);index.write_text(head+'\n\n'+note+'\n\n'+rest,encoding='utf-8')
out={'scope':'Mutable shared index updated; exact prior bytes archived and all frozen v36 files unchanged. v37 freezes versioned artifacts only. OVR comparability issue explicitly supersedes historical workload interpretations.','previousIndexSha256':sha(snapshot),'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(index).replace('\\','/'),'updatedIndexSha256':sha(index)}
(R/'index-transition.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

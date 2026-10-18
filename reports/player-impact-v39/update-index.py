import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in [R/'verification.json',Path('reports/player-impact-v38/all-verification.json')]:
 d=read(name);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
index=Path('reports/player-impact-validation/report.md');previous=read('reports/player-impact-v38/index-transition.json');assert sha(index)==previous['updatedIndexSha256']
snapshot=R/'index-before-v39.md';assert not snapshot.exists();snapshot.write_bytes(index.read_bytes())
note='最新個人數據修正為[v39阻攻分類](../player-impact-v39/report.md)，完成四季28,023場、[2025–26全582人170欄對照](../player-impact-v39/2025-26-player-validation.csv)及[獨立驗證](../player-impact-v39/all-verification.json)。從414,386次真實失投的場上五人共同估計阻攻／無阻攻，先驗僅由較早三季整場留出選定；四季留出皆優於固定區域總量＋240分鐘平滑分配基準。完整模擬BLK36平均MAE由0.144927降至0.094494；高阻攻82球員季由0.782216降至0.267624，但73個仍被低估。Wemby完整球季BLK36真實3.801、v30 2.311→v39 3.559。所有非blk輸出與每場比分完全等於v30；因此這是計數改善，不是OVR加分。v38的canonical角色修復保留，單季傷病不扣、多季反覆輕扣、替補不按per36外推及飽和負荷政策不變。v30＝v39勝場門檻仍有三季未過，沒有採用，亦沒有新全員Top50；目標未完成。'
text=index.read_text(encoding='utf-8');head,rest=text.split('\n\n',1);index.write_text(head+'\n\n'+note+'\n\n'+rest,encoding='utf-8')
(R/'index-transition.json').write_text(json.dumps({'scope':'Mutable shared index updated after verified v39 results. Exact v38 index bytes archived; all frozen historical files preserved. Future index updates need not alter versioned verification.','previousIndexSha256':sha(snapshot),'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(index).replace('\\','/'),'updatedIndexSha256':sha(index)},indent=2),encoding='utf-8')
print('v39 summary added; previous index bytes archived.')

"""Preserve the prior mutable index and point to the complete current experiment."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v36');main=Path('reports/player-impact-validation/report.md');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous=json.loads(Path('reports/player-impact-v35/index-transition.json').read_text(encoding='utf-8'));expected=previous['updatedIndexSha256'];assert sha(main)==expected
frozen=json.loads(Path('reports/player-impact-v35/verification.json').read_text(encoding='utf-8'))
for p,h in frozen['hashes'].items():assert sha(p)==h,p
snapshot=R/'index-before-v36.md';assert not snapshot.exists();snapshot.write_bytes(main.read_bytes());assert sha(snapshot)==expected
old=main.read_text(encoding='utf-8');heading=old.index('\n\n')
pointer='最新完整試驗為[v36逐球標記校準](../player-impact-v36/report.md)，附[全582人176欄](../player-impact-v36/2025-26-player-validation.csv)與[核對](../player-impact-v36/verification.json)。四季28,023場、10人9,600場健康負荷配對完成；四季原始PBP另核對754,914次一般出手及助攻者身分。移除共同發動端總量限制，僅用舊三季標記估計共用自主比例0.972314，沒有按名字／OVR／ON–OFF／勝場擬合。零自主支援891球仍全部消除，在場球隊／隊友FG及3P誤差改善，但個人14項有9項退步，助攻／36 MAE 0.206→0.266，2023–24及2025–26未過原勝場門檻，未採用。探索性尾端檢查更確認：至少500分鐘的82個高阻攻球員季全部低估，64個高助攻球員季有62個低估；不能靠聯盟平均誤差掩蓋。另完成條件助攻歸屬診斷，尚未改動執行參數，也不能當作助攻總量修復。正式模型及最新完整v24實驗榜不變，目標未完成。'
main.write_text(old[:heading]+'\n\n'+pointer+old[heading:],encoding='utf-8')
out={'scope':'Mutable shared index intentionally updated; exact post-v35 bytes archived and all frozen v35 versioned files verified unchanged. v36 freezes versioned artifacts only.','previousIndexSha256':expected,'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(main).replace('\\','/'),'updatedIndexSha256':sha(main)}
(R/'index-transition.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'indexUpdated':True,'priorV35SnapshotPreserved':True,'allV35FrozenFilesIntact':True}))

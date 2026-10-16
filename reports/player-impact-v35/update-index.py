"""Update the mutable report index and preserve the previous version's exact index."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v35');main=Path('reports/player-impact-validation/report.md')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous=json.loads(Path('reports/player-impact-v34/index-transition.json').read_text(encoding='utf-8'))
expected=previous['updatedIndexSha256'];assert sha(main)==expected
snapshot=R/'index-before-v35.md';assert not snapshot.exists();snapshot.write_bytes(main.read_bytes());assert sha(snapshot)==expected
old=main.read_text(encoding='utf-8');heading=old.index('\n\n')
pointer='最新完整試驗為[v35自主與傳球共同發動分配](../player-impact-v35/report.md)，附[全582人176欄](../player-impact-v35/2025-26-player-validation.csv)與[核對](../player-impact-v35/verification.json)。四季28,023場及10人9,600場同負荷配對完成；來源零自主支援891球仍全部消除。相較v30，失誤／36、抄截／36與3P等9項個人誤差改善，但得分／36 MAE 0.775→0.798、助攻／36 0.206→0.290，另3項退步；2023–24及2025–26未過既有勝場界線，未採用。共同發動總量仍是假設，Jokić的傳球被壓縮問題尚未解決。全部來源逐球計數、獨立矩陣重建、個人與在場誤差、負荷配對區間完成核對；來源條件出手分配有極小退步，未隱藏不利結果。健康貢獻優先、單季傷缺不扣、多季小扣及替補不外推先發負荷的政策保留，正式模型與最新完整v24實驗榜不變，目標未完成。'
main.write_text(old[:heading]+'\n\n'+pointer+old[heading:],encoding='utf-8')
transition={'scope':'The shared report index is intentionally mutable. Its exact post-v34 bytes are preserved in this version; all frozen v34 artifacts remain unchanged. v35 freezes versioned artifacts only.','previousIndexSha256':expected,'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(main).replace('\\','/'),'updatedIndexSha256':sha(main)}
frozen=json.loads(Path('reports/player-impact-v34/verification.json').read_text(encoding='utf-8'))
for p,h in frozen['hashes'].items():assert sha(p)==h,p
(R/'index-transition.json').write_text(json.dumps(transition,indent=2),encoding='utf-8')
print(json.dumps({'indexUpdated':True,'v34IndexSnapshotPreserved':True,'allV34FrozenFilesIntact':True}))

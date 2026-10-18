"""Update the mutable report index while preserving its v33-hashed snapshot."""
import hashlib,json
from pathlib import Path
R=Path('reports/player-impact-v34');main=Path('reports/player-impact-validation/report.md');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
previous=json.loads(Path('reports/player-impact-v33/verification.json').read_text(encoding='utf-8'))
expected=previous['hashes'][str(main).replace('\\','/')];assert sha(main)==expected
snapshot=R/'index-before-v34.md';assert not snapshot.exists();snapshot.write_bytes(main.read_bytes());assert sha(snapshot)==expected
old=main.read_text(encoding='utf-8');heading=old.index('\n\n')
pointer='最新完整試驗為[v34接球與自主共同分配](../player-impact-v34/report.md)，附[全582人176欄](../player-impact-v34/2025-26-player-validation.csv)與[核對](../player-impact-v34/verification.json)。四季28,023場及10人9,600場同負荷配對完成；來源零自主支援891球已消除，得分／36 MAE 0.775→0.752、DREB／36 0.288→0.281，但助攻／36 0.206→0.304、3P 1.596→1.756百分點退步。四季勝場界線通過三季，2023–24未過，未採用。硬性保留來源自主量也壓縮Jokić在平均70隊友中的傳球機會，健康負荷模擬助攻6.913→5.508；不能把來源角色當能力下限，或為肉C名次下降宣稱修好。全部來源情境及逐球重讀核對完成，來源仍是同季描述、不是因果或盲測。正式模型及最新完整v24實驗榜不變，目標未完成。'
main.write_text(old[:heading]+'\n\n'+pointer+old[heading:],encoding='utf-8')
transition={'scope':'The unversioned report index is intentionally mutable, not a runtime source. v33 verification recorded its former hash; those exact bytes are preserved at snapshot. All other v33 hashes still verify at original paths. New v34 freezes versioned artifacts only.','previousIndexSha256':expected,'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(main).replace('\\','/'),'updatedIndexSha256':sha(main)}
for p,h in previous['hashes'].items():
 if p!=str(main).replace('\\','/'):assert sha(p)==h,p
(R/'index-transition.json').write_text(json.dumps(transition,indent=2),encoding='utf-8');print(json.dumps({'indexUpdated':True,'v33IndexSnapshotPreserved':True,'otherV33FrozenFilesIntact':True}))

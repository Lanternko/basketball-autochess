import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v38');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['reports/player-impact-v37/verification.json','reports/player-impact-diagnostics/block-source-v37/all-verification.json','reports/player-impact-diagnostics/pass-release-v37/verification.json']:
 d=read(name);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
index=Path('reports/player-impact-validation/report.md');t=read('reports/player-impact-v37/index-transition.json');assert sha(index)==t['updatedIndexSha256']
snapshot=R/'index-before-v38.md';assert not snapshot.exists();snapshot.write_bytes(index.read_bytes())
note='最新輸入修復與控制實驗為[v38修正OVR重複校正](../player-impact-v38/report.md)，附[19,200場同來源角色負荷對照](../player-impact-v38/summary.json)與[核對](../player-impact-v38/all-verification.json)。已找到並修復OVR卡片組裝反覆乘入傳球成功率修正的錯誤：v29、v30、v34至v37的受查582人皆受影響，多數被壓低；四季來源卡與v24角色率另確認不受此重複組裝影響。修復從原始卡重建，2,262球員季／2,581隊伍卡連續套用五次不漂移。全582人與150名對手卡改用完全相同來源角色後，Jokić健康支持分鐘的模擬助攻由原v30 6.91回到8.70、原v37 5.97回到8.81；原版本差異不得再單歸因於分配。v37四季勝場仍皆未過、部分後衛貢獻退步，未採用。另確認高阻攻尾端的事件生成量偏低。正式模型與最新完整v24實驗榜不變，無新版全員OVR，目標未完成。'
text=index.read_text(encoding='utf-8');head,rest=text.split('\n\n',1);index.write_text(head+'\n\n'+note+'\n\n'+rest,encoding='utf-8')
(R/'index-transition.json').write_text(json.dumps({'scope':'Mutable shared index updated; exact prior bytes archived, all frozen v37 and diagnostic artifacts unchanged. v38 freezes only versioned files and explicit code dependencies. Historical workload interpretation retracted, numerical files preserved.','previousIndexSha256':sha(snapshot),'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(index).replace('\\','/'),'updatedIndexSha256':sha(index)},indent=2),encoding='utf-8')

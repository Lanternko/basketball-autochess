import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v41');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for f in [R/'verification.json',Path('reports/player-impact-v40/all-verification.json'),Path('reports/player-impact-diagnostics/team-error-v39/all-verification.json')]:
 d=read(f);assert d['passed']
 for p,h in d['hashes'].items():assert sha(p)==h,p
index=Path('reports/player-impact-validation/report.md');old=read('reports/player-impact-v39/index-transition.json');assert sha(index)==old['updatedIndexSha256']
snapshot=R/'index-before-v41.md';assert not snapshot.exists();snapshot.write_bytes(index.read_bytes())
note='最新收束為[v41四季個人／團隊驗證](../player-impact-v41/report.md)：28,023場賽季模擬、19,200場健康負荷診斷與[全582人170欄](../player-impact-v41/2025-26-player-validation.csv)。分區域五人防守模型使淨得分RMSE平均2.8602→2.5968、勝場MAE6.2222→6.1611，但2023–24及2025–26仍未過正式＋0.5門檻，對手3P誤差亦變大，因此未採用，亦沒有新全員OVR。[v40共用先驗原型](../player-impact-v40/report.md)及[球隊誤差來源診斷](../player-impact-diagnostics/team-error-v39/report.md)均完整封存。使用者最新規格：[主要OVR只評健康能力、出勤另列，顯示OVR與複雜模擬分開驗收](../player-impact-v41/user-rating-spec.json)，取代早先反覆傷病扣主要分數的偏好；不再為修榜單繼續加機制。最新完整榜仍為有已知偏差、未驗收的v24；十人測試不能冒充新前20。大目標尚未完成。'
text=index.read_text(encoding='utf-8');head,rest=text.split('\n\n',1);index.write_text(head+'\n\n'+note+'\n\n'+rest,encoding='utf-8')
(R/'index-transition.json').write_text(json.dumps({'scope':'Mutable shared index updated after verified v41 closure. Exact previous v39 index bytes archived; all historical frozen versions preserved.','previousIndexSha256':sha(snapshot),'snapshot':str(snapshot).replace('\\','/'),'updatedIndex':str(index).replace('\\','/'),'updatedIndexSha256':sha(index)},indent=2),encoding='utf-8');print('Updated shared index;previous exact bytes preserved.')

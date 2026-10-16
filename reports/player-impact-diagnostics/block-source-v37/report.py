import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-diagnostics/block-source-v37');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=read(R/'audit.json');v=read(R/'verification.json');assert v['passed']
for p,h in v['hashes'].items():assert sha(p)==h,p
lines=['# 阻攻來源診斷：事件總量與歸屬分開','',
'這是來源條件診斷，未改任何比賽引擎、能力值或OVR。原始四季嚴格PBP場次、實際五人陣容與全部FG出手（含補籃）；與個人驗證的全年per36範圍不同。','',
'比較兩項：','',
'1. 現有通用阻攻生成公式的預期上界：對每次真實FGA計算原先位置／協防／體格公式，移除「阻攻最多占失投65%」限制。它是這批來源出手下的**期望值上界**，不是隨機比賽阻攻次數的上限，也不是實際引擎的精確期望。','2. 條件歸屬：保留每個實際陣容時段發生的真實球隊阻攻總數，僅用既有240分鐘平滑BLK／MIN權重分配給五人。這直接使用同季個人結果作權重，不能視為盲測或能力證明。','',
'| 球季 | PBP場次 | 全部FG出手 | 實際阻攻 | 生成公式預期上界 |','|---|---:|---:|---:|---:|']
for s in d['seasons']:lines.append(f"| {s['season']} | {s['games']} | {s['sourceFga']} | {s['actualBlocks']} | {s['expectedUpperBound']:.2f} |")
lines+=['','全來源FG出手、阻攻、分鐘、兩項預期及個人per36以獨立Python公式逐次重建；包括來源卡片與原始PBP雜湊核對。','',
'## 2025–26同範圍比較','',
'| 球員 | 嚴格來源分鐘 | 真實BLK／36 | 生成預期上界／36 | 保留實際球隊總量的歸屬／36 |','|---|---:|---:|---:|---:|']
players=next(s for s in d['seasons'] if s['season']=='2025-26')['players'];by={p['name']:p for p in players}
for name in ['Victor Wembanyama','Mitchell Robinson','Cade Cunningham','Neemias Queta','Nikola Jokić']:
 p=by[name];lines.append(f"| {name} | {p['minutes']:.2f} | {p['actual36']:.4f} | {p['upperBound36']:.4f} | {p['conditionalAllocation36']:.4f} |")
lines+=['','Wemby在同一批來源陣容中的真實阻攻／36約3.76；通用生成公式連移除失投占比上限後的預期也只有約2.24，保留實際球隊總量後的個人歸屬約3.55。這支持優先檢查阻攻事件總量公式；平滑與時段內歸屬仍有誤差，不能說全部由同一原因造成，也不能只用一人選係數。','',
'## 對模型的意義','',
'現有blockProfile在進球／失投已決定後，將部分失投標記為阻攻。球員投籃防守曲線已包含阻攻造成的失投，單純修阻攻計數不會再降低對手命中率；若額外重扣FG，會重複計算防守效果。後續需分清「阻攻計數修復」與「防守對終結機率的影響」。本檢查不能直接決定Wemby與Robinson的OVR順序。','',
'這裡使用實際對手與出手，沒有重建若球員換隊或承擔不同負荷會產生多少出手。來源描述、球員角色、樣本噪音與先發／替補對手品質仍有限制；沒有擬合新參數，也沒有採用候選模型。','',
'檔案：[全部球員與情境結果](audit.json)、[來源卡片](source-cards.json)、[獨立重算](verification.json)。']
f=R/'report.md';assert not f.exists();f.write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Wrote verified source-only block diagnosis.')

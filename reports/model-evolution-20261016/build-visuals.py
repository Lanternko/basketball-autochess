import json, re, subprocess
from pathlib import Path
root=Path('reports/model-evolution-20261016')
dest=Path('C:/Users/柯子捷/.codex/visualizations/2026/10/15/01a13f24-4e8d-7442-a17a-392b55f3191b')
dest.mkdir(parents=True,exist_ok=True)
d=json.loads((root/'chart-data.json').read_text(encoding='utf-8'))
def m(key,label,color):return {'key':key,'label':label,'color':color}
def group(title,unit,metrics,error='MAE'):return {'title':title,'unit':unit,'metrics':metrics,'error':error}
personal=[
 group('得分','分／36分',[m('pts36','得分',1)]),
 group('助攻','次／36分',[m('ast36','助攻',2)]),
 group('籃板','次／36分',[m('oreb36','進攻籃板',4),m('dreb36','防守籃板',5)]),
 group('失誤與防守計數','次／36分',[m('tov36','失誤',1),m('stl36','抄截',2),m('blk36','阻攻',3)]),
 group('出手量','次／36分',[m('fga36','出手',1),m('fg3a36','三分出手',2),m('fta36','罰球出手',3)]),
 group('命中率','百分點',[m('fgPct','投籃',1),m('threePct','三分',2),m('ftPct','罰球',3)]),
 group('使用球權失誤率','每百次使用',[m('tovPer100Uses','失誤率',1)])]
team=[
 group('整季勝場','勝',[m('winsMAE','勝場誤差',1)]),
 group('每場淨得分','分／場',[m('netRMSE','淨分誤差',1)],'RMSE'),
 group('得分','分／場',[m('pts','得分',1)]),
 group('助攻與總籃板','次／場',[m('ast','助攻',2),m('reb','籃板',3)]),
 group('進攻與防守籃板','次／場',[m('oreb','進攻籃板',4),m('dreb','防守籃板',5)]),
 group('失誤、抄截與阻攻','次／場',[m('tov','失誤',1),m('stl','抄截',2),m('blk','阻攻',3)]),
 group('命中率','百分點',[m('fgPct','投籃',1),m('threePct','三分',2),m('ftPct','罰球',3)])]
template=(root/'error-curves.template.html').read_text(encoding='utf-8')
for kind,groups,title,meta in [
 ('personal',personal,'個人數據：誤差隨版本變化','2025–26 · 378 人（實際 ≥500 分鐘）· 相同 3 組種子 · 實際分鐘加權 MAE'),
 ('team',team,'球隊數據：誤差隨版本變化','2025–26 · 30 隊 · 相同 3 組種子先平均 · 逐隊 MAE／淨分 RMSE')]:
    payload={'kind':kind,'versions':d['versions'],'values':d[kind],'groups':groups}
    html=template.replace('model-personal-curves',f'model-{kind}-curves').replace('個人數據：誤差隨版本變化',title).replace('2025–26 · 378 人（實際 ≥500 分鐘）· 相同 3 組種子 · 實際分鐘加權 MAE',meta)
    html=html.replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    (dest/f'{kind}-error-curves.html').write_text(html,encoding='utf-8')
ovr=(root/'ovr-evolution.template.html').read_text(encoding='utf-8').replace('__PAYLOAD__',json.dumps(d['media'],ensure_ascii=False,separators=(',',':')))
(dest/'ovr-evolution.html').write_text(ovr,encoding='utf-8')
for p in dest.glob('*.html'):
    s=p.read_text(encoding='utf-8');assert '__PAYLOAD__' not in s;assert not re.search(r'<!doctype|<html|<head|<body',s,re.I)
    js='\n'.join(re.findall(r'<script>([\s\S]*?)</script>',s))
    q=root/(p.stem+'.syntax.js');q.write_text(js,encoding='utf-8')
    check=subprocess.run(['node','--check',str(q)],capture_output=True,text=True);assert check.returncode==0,check.stderr
    print(p.name,p.stat().st_size,'bytes; syntax OK')

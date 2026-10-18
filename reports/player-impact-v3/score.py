import json,importlib.util
from pathlib import Path
ROOT=Path('reports/player-impact-v3');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def trialread(p):
 p=Path(p)
 if not p.exists() and p.parent.name=='runs' and p.parent.parent.name.startswith('player-impact-v'):
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 return oldread(p)
box.read=trialread
cells=[]
for folder,version in [('reports/player-impact-v1','control'),('reports/player-impact-v1','creation-flow-balanced'),('reports/player-impact-v2','opportunity-flow')]+[(str(ROOT),v) for v in read(ROOT/'protocol.json')['variants']]:
 c=box.score('2025-26',version,[20261012],Path(folder));cells.append(c)
 print(version,'MAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','tov36','stl36','oreb36','dreb36','blk36','fgPct','threePct']},'team',c['teamMetrics'],flush=True)
 for g in ['G','C']:print(g,'means',{k:(round(c['summary'][g][k]['actual'],2),round(c['summary'][g][k]['predicted'],2)) for k in ['pts36','ast36','stl36','tov36']},flush=True)
 for name in ['Shai Gilgeous-Alexander','Luka Dončić','Nikola Jokić','Stephen Curry','Neemias Queta']:
  p=next(p for p in c['players'] if p['name']==name);print(name,{k:tuple(round(z,2) for z in p['metrics'][k].values()) for k in ['pts36','ast36','fga36']},flush=True)
(ROOT/'scores-diagnostic.json').write_text(json.dumps({'label':'One-seed same-season mechanism diagnosis, not promotion','cells':cells},ensure_ascii=False,indent=2),encoding='utf-8')

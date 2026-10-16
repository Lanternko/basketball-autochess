import json,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path('reports/player-impact-validation');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('boxscore','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def mapped(p):
 p=Path(p)
 if not p.exists() and p.parent==Path('reports/player-impact-v6/runs'):
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 return oldread(p)
box.read=mapped
protocol=read(ROOT/'confirmation-protocol.json');cells=[];arrays=[]
for season in protocol['seasons']:
 truth=read('reports/defense-tenth/step4-rebounds-turnover-time/seed-arrays.json')[season];actual=truth['truth'];ids=truth['ids'];pair=[]
 for version in ['control','terminal-flow']:
  c=box.score(season,version,protocol['seeds'],Path('reports/player-impact-v6'));cells.append(c);values=[]
  for seed in protocol['seeds']:
   f=f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{season}-split-{seed}.json' if version=='control' else f'reports/player-impact-v6/runs/{season}-terminal-flow-full-{seed}.json'
   run=read(f);ts={t['id']:t for t in run['teams']};values.append([[ts[i]['wins'],(ts[i]['stats']['pts']-ts[i]['opponent']['pts'])/82] for i in ids])
  pair.append(np.array(values))
  print(season,version,'individualMAE',{k:round(c['summary']['ALL'][k]['mae'],3) for k in ['pts36','ast36','tov36','stl36','oreb36','dreb36','blk36','threePct']},'team',c['teamMetrics'],flush=True)
 arrays.append((season,np.array(pair),np.array(actual['wins']),np.array(actual['net'])))
rng=np.random.default_rng(20261015);resamples=rng.integers(0,20,size=(10000,20));comparisons=[]
for season,ar,wins,net in arrays:
 preds=ar[:,resamples,:,:].mean(axis=2);we=np.abs(preds[:,:,:,0]-wins).mean(axis=2);ne=preds[:,:,:,1]-net;ne-=ne.mean(axis=2,keepdims=True);nr=np.sqrt((ne*ne).mean(axis=2))
 c=next(c for c in cells if c['season']==season and c['version']=='control');p=next(c for c in cells if c['season']==season and c['version']=='terminal-flow')
 comparisons.append({'season':season,'winsMAEDifference':p['teamMetrics']['winsMAE']-c['teamMetrics']['winsMAE'],'winsDifferencePairedSeedCI95':np.quantile(we[1]-we[0],[.025,.975]).tolist(),
  'netRMSEDifference':p['teamMetrics']['netRMSE']-c['teamMetrics']['netRMSE'],'netDifferencePairedSeedCI95':np.quantile(nr[1]-nr[0],[.025,.975]).tolist()})
out={'limits':'Twenty matching random seeds, same-season cards, all seasons seen. Paired seed bootstrap measures simulation Monte Carlo uncertainty only; no prospective, input or causal uncertainty claim. On-court remains independent three-seed validation.', 'cells':cells,'comparisons':comparisons}
(ROOT/'confirmation-scores.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('PAIRED-SEED DIFFERENCES',json.dumps(comparisons,indent=2),flush=True)

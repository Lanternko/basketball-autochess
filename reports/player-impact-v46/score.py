import json,csv,importlib.util,hashlib,sys
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
ROOT=Path('reports/player-impact-v46');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
protocol=read(ROOT/'protocol.json');auditedTeamTruth=read('reports/player-impact-diagnostics/team-error-v39/audit.json')['rows']
seasons=sys.argv[1:] or protocol['seasons'];assert all(s in protocol['seasons'] for s in seasons);prefix='' if seasons==protocol['seasons'] else '-'.join(seasons)+'-'
spec=importlib.util.spec_from_file_location('box_score','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
original_read=box.read
def redirected(p):
 p=Path(p)
 if p.parent==ROOT/'runs':
  stem,seed=p.stem.rsplit('-',1);season=stem[:7];p=p.with_name(f'{season}-v46-full-{seed}.json')
 elif p.parent==Path('reports/player-impact-v41/runs'):
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 return original_read(p)
box.read=redirected

def metrics(p):
 result={}
 for arm in ['on','off']:
  c=p[arm];seconds=p[arm+'Seconds'];n=c.get('fga',0)
  result[arm+'FGA48']=48*60*n/seconds if seconds>0 else None
  result[arm+'FGpct']=100*c.get('fgm',0)/n if n>=100 else None
  for z in ['long','mid','short']:
   a=c.get(z+'A',0);m=c.get(z+'M',0)
   result[arm+z+'Share']=100*a/n if n>=100 else None
   result[arm+z+'FGpct']=100*m/a if a>=100 else None
   result[arm+z+'FGA48']=48*60*a/seconds if seconds>0 else None
 for key in ['FGA48','FGpct',*[z+k for z in ['long','mid','short'] for k in ['Share','FGpct','FGA48']]]:
  a=result['on'+key];b=result['off'+key];result['delta'+key]=a-b if a is not None and b is not None else None
 return result

def summary(rows,group=None):
 keys=list(rows[0]['metrics']);out={}
 for k in keys:
  rs=[r for r in rows if r['minutes']>=500 and (not group or r['roleGroup']==group) and r['metrics'][k] is not None]
  if not rs:out[k]=None;continue
  weights=np.array([r['minutes'] for r in rs]);weights=weights/weights.sum();errors=np.array([r['metrics'][k]['predicted']-r['metrics'][k]['actual'] for r in rs])
  out[k]={'players':len(rs),'mae':float(weights@abs(errors)),'bias':float(weights@errors),'rmse':float(np.sqrt(weights@(errors**2)))}
 return out

cells=[];exports=[]
for season in seasons:
 truth=read(Path('reports/player-impact-v42')/f'{season}-defense-truth.json');actual={p['playerId']:p for p in truth['players']};teamsTruth=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams'];role={p['playerId']:p['roleGroup'] for s in box.baseline['seasons'] if s['season']==season for p in s['players']}
 for variant in ['v41','v46']:
  full=[read(f'reports/player-impact-v41/runs/{season}-rotation-space-full-{seed}.json' if variant=='v41' else ROOT/f'runs/{season}-v46-full-{seed}.json') for seed in protocol['seeds']]
  fullstats=defaultdict(Counter);wins=Counter()
  for run in full:
   assert len(run['matches'])==1230
   for t in run['teams']:
    assert t['games']==82
    fullstats[t['id']].update({k:v/len(full) for k,v in t['stats'].items() if isinstance(v,(int,float))});wins[t['id']]+=t['wins']/len(full)
  teamRows=[]
  for t in teamsTruth:
   pred=fullstats[t['id']];a=next(r for r in auditedTeamTruth if r['season']==season and r['version']=='control' and r['teamId']==t['id']);actualPPG=a['stats']['own']['actual']['pts']/82;predictedPPG=pred['pts']/82
   teamRows.append({'teamId':t['id'],'name':t['name'],'actualPPG':actualPPG,'predictedPPG':predictedPPG,'errorPPG':predictedPPG-actualPPG})
  ppg={'mae':float(np.mean([abs(t['errorPPG']) for t in teamRows])),'rmse':float(np.sqrt(np.mean([t['errorPPG']**2 for t in teamRows]))),'bias':float(np.mean([t['errorPPG'] for t in teamRows])),'teams':teamRows}
  pred=defaultdict(lambda:{'on':Counter(),'off':Counter(),'onSeconds':0.,'offSeconds':0.})
  for seed in protocol['seeds']:
   r=read((Path('reports/player-impact-v42') if variant=='v41' else ROOT)/f'runs/{season}-{variant}-strict-{seed}.json');assert set(m['id'] for m in r['matches'])==set(truth['gameIds']);assert r['defense']['games']==truth['games']
   if variant=='v41':assert r['baselineParityPassed']
   for p in r['defense']['players']:
    q=pred[p['playerId']]
    for arm in ['on','off']:q[arm].update(p[arm]);q[arm+'Seconds']+=p[arm+'Seconds']
  rows=[]
  for pid,a in actual.items():
   am=metrics(a);pm=metrics(pred[pid]);ms={k:{'actual':am[k],'predicted':pm[k],'error':pm[k]-am[k]} if am[k] is not None and pm[k] is not None else None for k in am}
   rows.append({'playerId':pid,'name':a['name'],'minutes':a['onSeconds']/60,'roleGroup':role[pid],'metrics':ms})
  b=box.score(season,'rotation-space',protocol['seeds'],Path('reports/player-impact-v41') if variant=='v41' else ROOT)
  cell={'season':season,'variant':variant,'teamPPG':ppg,'teamMetrics':b['teamMetrics'],'individualSummary':b['summary'],'individualPlayers':b['players'],'defenseSummary':{g:summary(rows,None if g=='ALL' else g) for g in ['ALL','G','F','C']},'players':rows};cells.append(cell)
  for p in rows:exports.append({'season':season,'variant':variant,**p})
  print(json.dumps({'season':season,'variant':variant,'ppgMAE':ppg['mae'],'defenseMAE':{k:cell['defenseSummary']['ALL'][k]['mae'] for k in ['onshortShare','onlongShare','onshortFGpct','onlongFGpct','onFGA48']}}),flush=True)

core=['onshortShare','onlongShare','onshortFGpct','onlongFGpct'];gates=[]
for season in seasons:
 a=next(c for c in cells if c['season']==season and c['variant']=='v41');b=next(c for c in cells if c['season']==season and c['variant']=='v46')
 gates.append({'season':season,'teamPPGNonRegression':b['teamPPG']['mae']<=a['teamPPG']['mae']+1e-9,'baselinePPGMAE':a['teamPPG']['mae'],'candidatePPGMAE':b['teamPPG']['mae'],'defenseImproved':{k:b['defenseSummary']['ALL'][k]['mae']<a['defenseSummary']['ALL'][k]['mae'] for k in core}})
aggregate={variant:{k:float(np.mean([c['defenseSummary']['ALL'][k]['mae'] for c in cells if c['variant']==variant])) for k in core+['onFGA48','deltashortShare','deltalongShare','deltashortFGpct','deltalongFGpct']} for variant in ['v41','v46']}
decision=read(ROOT/'decision.json') if (ROOT/'decision.json').exists() else {}
result={'scope':'Four already-seen seasons, same-season reconstruction; attempt intent is an association. Source minutes weighted >=500 strict minutes, zone make rates >=100 actual attempts. Errors from three-seed pooled counters. Team PPG errors use 30 teams, three-seed mean totals then MAE.','aggregateDefenseMAE':aggregate,'gates':gates,'adopted':decision.get('adopted',False),'adoptionScope':decision.get('adoptionScope'),'cells':cells}
(ROOT/(prefix+'scores.json')).write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
with (ROOT/(prefix+'defense-players.csv')).open('w',encoding='utf-8-sig',newline='') as f:
 fields=['season','variant','playerId','name','minutes','roleGroup']+[k+'_'+v for k in exports[0]['metrics'] for v in ['actual','predicted','error']];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for p in exports:
  row={k:p[k] for k in fields[:6]}
  for k,m in p['metrics'].items():
   if m:row.update({k+'_'+v:m[v] for v in ['actual','predicted','error']})
  w.writerow(row)
print(json.dumps({'aggregateDefenseMAE':aggregate,'gates':gates}),flush=True)

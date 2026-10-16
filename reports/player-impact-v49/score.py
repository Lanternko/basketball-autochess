import json,importlib.util,sys
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
R=Path('reports/player-impact-v49');B=Path('reports/player-impact-v47');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));protocol=read(R/'protocol.json')
seasons=sys.argv[1:] or protocol['seasons'];assert all(s in protocol['seasons'] for s in seasons);prefix='' if seasons==protocol['seasons'] else '-'.join(seasons)+'-'
spec=importlib.util.spec_from_file_location('box','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box);original=box.read
def redirected(p):
 p=Path(p)
 if p.parent in [R/'runs',B/'runs']:
  season=p.stem[:7];seed=p.stem.rsplit('-',1)[1];variant='v49' if p.parent==R/'runs' else 'v47';p=p.with_name(f'{season}-{variant}-full-{seed}.json')
 return original(p)
box.read=redirected
def metrics(p):
 out={}
 for arm in ['on','off']:
  c=p[arm];sec=p[arm+'Seconds'];n=c.get('fga',0);out[arm+'FGA48']=48*60*n/sec if sec>0 else None;out[arm+'FGpct']=100*c.get('fgm',0)/n if n>=100 else None
  for z in ['long','mid','short']:
   a=c.get(z+'A',0);m=c.get(z+'M',0);out[arm+z+'Share']=100*a/n if n>=100 else None;out[arm+z+'FGpct']=100*m/a if a>=100 else None;out[arm+z+'FGA48']=48*60*a/sec if sec>0 else None
 for k in ['FGA48','FGpct',*[z+k for z in ['long','mid','short'] for k in ['Share','FGpct','FGA48']]]:
  a,b=out['on'+k],out['off'+k];out['delta'+k]=a-b if a is not None and b is not None else None
 return out
def summary(rows,group):
 out={}
 for k in rows[0]['metrics']:
  rs=[p for p in rows if p['minutes']>=500 and (group=='ALL' or p['roleGroup']==group) and p['metrics'][k] is not None];w=np.array([p['minutes'] for p in rs]);w=w/w.sum();e=np.array([p['metrics'][k]['error'] for p in rs]);out[k]={'players':len(rs),'mae':float(w@abs(e)),'bias':float(w@e),'rmse':float(np.sqrt(w@(e*e)))}
 return out
baseline=read(B/'scores.json');cells=[]
for season in seasons:
 actual=read(f'reports/player-impact-v42/{season}-defense-truth.json');roles={p['playerId']:p['roleGroup'] for s in box.baseline['seasons'] if s['season']==season for p in s['players']};base=next(c for c in baseline['cells'] if c['season']==season and c['variant']=='v47')
 cells.append(base)
 b=box.score(season,'rotation-space',protocol['seeds'],R);pred=defaultdict(lambda:{'on':Counter(),'off':Counter(),'onSeconds':0.,'offSeconds':0.});teamtotals=Counter();seedDiagnostics=[]
 for seed in protocol['seeds']:
  full=read(R/f'runs/{season}-v49-full-{seed}.json');ppg={t['id']:t['stats']['pts']/82 for t in full['teams']};teamtotals.update({k:v/len(protocol['seeds']) for k,v in ppg.items()});curry=Counter()
  for t in full['teams']:
   for p in t['players']:
    if p['playerId']==201939:curry.update(p['stats'])
  strict=read(R/f'runs/{season}-v49-strict-{seed}.json');assert set(m['id'] for m in strict['matches'])==set(actual['gameIds'])
  for p in strict['defense']['players']:
   q=pred[p['playerId']]
   for arm in ['on','off']:q[arm].update(p[arm]);q[arm+'Seconds']+=p[arm+'Seconds']
  seedDiagnostics.append({'seed':seed,'curryFTpct':100*curry['ftm']/curry['fta'],'curryPTS36':2160*curry['pts']/curry['seconds'],'teamPPGMAE':float(np.mean([abs(ppg[t['teamId']]-t['actualPPG']) for t in base['teamPPG']['teams']]))})
 rows=[]
 for a in actual['players']:
  am,pm=metrics(a),metrics(pred[a['playerId']]);ms={k:{'actual':v,'predicted':pm[k],'error':pm[k]-v} if v is not None and pm[k] is not None else None for k,v in am.items()};rows.append({'playerId':a['playerId'],'name':a['name'],'minutes':a['onSeconds']/60,'roleGroup':roles[a['playerId']],'metrics':ms})
 teamRows=[{**t,'predictedPPG':teamtotals[t['teamId']],'errorPPG':teamtotals[t['teamId']]-t['actualPPG']} for t in base['teamPPG']['teams']];e=np.array([t['errorPPG'] for t in teamRows]);ppg={'mae':float(abs(e).mean()),'bias':float(e.mean()),'rmse':float(np.sqrt((e*e).mean())),'teams':teamRows}
 cells.append({'season':season,'variant':'v49','teamPPG':ppg,'teamMetrics':b['teamMetrics'],'individualSummary':b['summary'],'individualPlayers':b['players'],'defenseSummary':{g:summary(rows,g) for g in ['ALL','G','F','C']},'players':rows,'seedDiagnostics':seedDiagnostics})
 print(json.dumps({'season':season,'ftMAE':b['summary']['ALL']['ftPct']['mae'],'baselineFTMAE':base['individualSummary']['ALL']['ftPct']['mae'],'ppgMAE':ppg['mae'],'baselinePPGMAE':base['teamPPG']['mae']}),flush=True)
result={'scope':baseline['scope'],'baseline':'v47','candidate':'v49','cells':cells};(R/(prefix+'scores.json')).write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')

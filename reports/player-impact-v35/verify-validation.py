import csv,hashlib,json,math
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v35');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10),(a,b)
protocol=read(root/'validation-protocol.json')
mechanism=read(root/'mechanism-protocol.json')
for p,h in mechanism['hashes'].items():assert sha(p)==h,p
for p,h in protocol['hashes'].items():assert sha(p)==h,p
manifest=read(root/'validation-manifest.json');assert len(manifest['jobs'])==24
games=0;pred=defaultdict(Counter);onc=defaultdict(lambda:defaultdict(Counter));strict=defaultdict(Counter)
for j in manifest['jobs']:
 assert sha(j['file'])==j['sha256'];r=read(j['file']);games+=len(r['matches'])
 if j['strict']:
  truth=read(f"reports/player-impact-v1/{j['season']}-on-court-truth.json");assert {m['id'] for m in r['matches']}==set(truth['gameIds'])
  for k in ['fga','fgm','fg3a','fg3m']:
   n=sum(t['stats'][k] for t in r['teams'])
   for g,mult in [('own',1),('on',5),('teammates',4)]:assert sum(p[g][k] for p in r['onCourt']['players'])==mult*n
 else:assert len(r['matches'])==1230
 if j['season']=='2025-26':
  target=strict if j['strict'] else pred
  for t in r['teams']:
   for p in t['players']:
    for k,n in p['stats'].items():
     if isinstance(n,(int,float)):target[p['playerId']][k]+=n/3
  if j['strict']:
   for p in r['onCourt']['players']:
    for g in ['on','off','own','teammates']:
     for k,n in p[g].items():onc[p['playerId']][g][k]+=n/3
assert games==28023
ledger=read(root/'ledger-verification.json');assert ledger['passed'] and ledger['games']==games
sv=read(root/'source-verification.json');assert sv['passed'] and sv['sourceRoleCards']==2262 and sv['sourceContextStates']==270090
scores=read(root/'scores.json');assert len(scores['cells'])==12
for c in scores['cells']:
 for group,s in c['summary'].items():
  for k,m in s.items():
   if m:
    ps=[p for p in c['players'] if p['minutes']>=500 and p['metrics'].get(k) and (group=='ALL' or p['roleGroup']==group)];w=sum(p['minutes'] for p in ps)
    assert m['players']==len(ps);close(m['mae'],sum(p['minutes']*abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']) for p in ps)/w)
 for group,s in c['onCourtSummary'].items():
  for k,m in s.items():
   if m:
    ps=[p for p in c['onCourtPlayers'] if p['minutes']>=500 and p['metrics'].get(k) and (group=='ALL' or p['roleGroup']==group)];w=sum(p['minutes'] for p in ps)
    assert m['players']==len(ps);close(m['mae'],sum(p['minutes']*abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']) for p in ps)/w)
 for v in ['v30','control']:
  if c['version']==v:
   previous=read('reports/player-impact-v30/scores.json');old=next(p for p in previous['cells'] if p['season']==c['season'] and p['version']==('rotation-space' if v=='v30' else v))
   for k in ['summary','teamMetrics','players','onCourtSummary','onCourtPlayers']:assert c[k]==old[k],(c['season'],v,k)
for v,a in scores['aggregate'].items():
 cs=[c for c in scores['cells'] if c['version']==v]
 for group,collection in [('individualMAE','summary'),('onCourtMAE','onCourtSummary')]:
  for k,n in a[group].items():close(n,sum(c[collection]['ALL'][k]['mae'] for c in cs)/4)
 for k,n in a['team'].items():close(n,sum(c['teamMetrics'][k] for c in cs)/4)
c=next(c for c in scores['cells'] if c['season']=='2025-26' and c['version']=='rotation-space');by={p['playerId']:p for p in c['players']};onby={p['playerId']:p for p in c['onCourtPlayers']}
with (root/'2025-26-player-validation.csv').open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f);rows=list(r);cols=len(r.fieldnames)
assert len(rows)==582 and {int(p['playerId']) for p in rows}==set(by)
fa=read(root/'flow-audit.json')
sf={p['playerId']:p for s in fa['seasons'] if s['season']=='2025-26' for p in s['players']}
mf={p['playerId']:next(r for r in p['rows'] if r['playerId']==p['playerId']) for p in fa['mean70']}
for r in rows:
 pid=int(r['playerId']);p=by[pid];o=onby[pid]
 close(float(r['actualMinutes']),p['minutes']);close(float(r['predictedMinutes']),pred[pid]['seconds']/60);close(float(r['strictPredictedMinutes']),strict[pid]['seconds']/60)
 for collection in [p['metrics'],o['metrics']]:
  for k,m in collection.items():
   for label in ['actual','predicted']:
    if m:close(float(r[k+'_'+label]),m[label])
    else:assert r[k+'_'+label]==''
   if m:close(float(r[k+'_error']),m['predicted']-m['actual'])
   else:assert r[k+'_error']==''
 for k in ['pts','fgm','fga','fg3m','fg3a','fta','ftm','oreb','dreb','ast','tov','stl','blk']:
  close(float(r[k+'Total_predicted']),pred[pid][k]);close(float(r[k+'Total_error']),float(r[k+'Total_predicted'])-float(r[k+'Total_actual']))
 for k in ['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']:
  if p['metrics'][k+'36']:close(p['metrics'][k+'36']['predicted'],36*pred[pid][k]/p['predictedMinutes'])
 for field,key in [('sourceStrictMeanSelfRoleRate','sourceSelf'),('sourceStrictMeanAssignedSelf_v30','previousAssignedSelf'),('sourceStrictMeanAssignedSelf_v35','assignedSelf'),('sourceStrictMeanAddedSelf','addedSelf')]:
  if pid in sf:close(float(r[field]),sf[pid]['rates'][key])
  else:assert r[field]==''
 close(float(r['mean70AssignedSelf_v30']),mf[pid]['previousAssignedSelf']);close(float(r['mean70AssignedSelf_v35']),mf[pid]['assignedSelf'])
for name in ['source-verification.json','equivalence-verification.json','profile-verification.json','probability-verification.json','data-verification.json','source-comparison-verification.json','supplement-verification.json','transport-verification.json']:
 check=read(root/name);assert check['passed']
 for p,h in check['hashes'].items():assert sha(p)==h,p
strata=read(root/'error-strata.json');assert len(strata['rows'])==144
for p,h in strata['hashes'].items():assert sha(p)==h,p
for row in strata['rows']:
 cell=next(c for c in scores['cells'] if c['season']==row['season'] and c['version']==row['version'])
 for field in ['players','onCourtPlayers']:
  for k,value in row[field].items():
   ps=[]
   for p in cell[field]:
    if p['minutes']<=0 or not p['metrics'].get(k):continue
    if row['roleGroup']!='ALL' and p['roleGroup']!=row['roleGroup']:continue
    if row['sample']=='primary500' and p['minutes']<500:continue
    if row['sample']=='lowMinutes' and p['minutes']>=500:continue
    ps.append(p)
   if not ps:assert value is None;continue
   w=sum(p['minutes'] for p in ps);assert value['players']==len(ps);close(value['actualMinutes'],w)
   close(value['mae'],sum(p['minutes']*abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']) for p in ps)/w)
   close(value['signedBias'],sum(p['minutes']*(p['metrics'][k]['predicted']-p['metrics'][k]['actual']) for p in ps)/w)
   pairs=sorted((abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']),p['minutes']) for p in ps);cumulative=0
   for absolute,weight in pairs:
    cumulative+=weight
    if cumulative>=.9*w:close(value['weightedAbsoluteP90'],absolute);break
diagnostic=read(root/'probe-role-diagnostics.json');assert len(diagnostic['rows'])==20
for p,h in diagnostic['hashes'].items():assert sha(p)==h,p
nowProbe=read(root/'ovr-probe-checkpoint.json');priorProbe=read('reports/player-impact-v30/ovr-probe-checkpoint.json')
nowBy={r['result']['playerId']:r['result'] for r in nowProbe['rows']};priorBy={r['result']['playerId']:r['result'] for r in priorProbe['rows']}
for d in diagnostic['rows']:
 pid=d['playerId'];a=next(x for x in priorBy[pid]['arms'] if x['arm']==d['arm']);b=next(x for x in nowBy[pid]['arms'] if x['arm']==d['arm'])
 assert d['mean70FrozenFlow']==mf[pid] and d['minutes']==a['minutes']==b['minutes']
 for k,m in d['stats'].items():
  close(m['v30PerWorkloadGame'],sum(v['playerStats'][k] for g in a['games'] for v in g['pair'])/240)
  close(m['v35PerWorkloadGame'],sum(v['playerStats'][k] for g in b['games'] for v in g['pair'])/240)
  grouped=defaultdict(list)
  for x,y in zip(a['games'],b['games']):
   assert (x['opponent'],x['seed'],x['i'],x['phase'])==(y['opponent'],y['seed'],y['i'],y['phase'])
   grouped[x['opponent']].append(sum(v['playerStats'][k] for v in y['pair'])/2-sum(v['playerStats'][k] for v in x['pair'])/2)
  change=sum(sum(v)/4 for v in grouped.values())/30
  se=math.sqrt(sum(sum((x-sum(v)/4)**2 for x in v)/3/4 for v in grouped.values())/900)
  close(m['pairedChange'],change);close(m['standardError'],se)
  close(m['pointwise95'][0],change-1.96*se);close(m['pointwise95'][1],change+1.96*se)
status=read(root/'status.json');assert not status['officialModelAdopted'] and not status['goalComplete'] and not status['fullOvrThisVersion'] and status['latestCompleteOvrVersion']==24
failed=[]
for season in protocol['seasons']:
 cs={c['version']:c for c in scores['cells'] if c['season']==season}
 if cs['rotation-space']['teamMetrics']['winsMAE']>cs['control']['teamMetrics']['winsMAE']+.5:failed.append(season)
assert status['failedWinGateSeasons']==failed and status['targetPlayerColumns']==cols
files=[p for p in root.iterdir() if p.is_file() and p.name!='verification.json']
out={'passed':True,'games':games,'files':24,'targetPlayers':582,'columns':cols,'allIndividualAndOnCourtMAEsRecomputed':True,'previousV30AndControlScoresExactlyReproduced':True,'failedWinGateSeasons':failed,'scope':'Joint creator/terminal transport, four-season same-season reconstruction; not causal/predictive/OVR certification. No adoption.','hashes':{str(p).replace('\\','/'):sha(p) for p in files}}
(root/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='hashes'},ensure_ascii=False,indent=2))

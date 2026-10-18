"""Audit archived adopted-model seasons against individual official box totals.

Descriptive same-season checks; the original cards use these seasons' inputs.
No player rating is changed by this script.
"""
import csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path('reports/player-box-audit')
MODEL = Path('reports/defense-tenth/step4-rebounds-turnover-time')
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']
COUNTS = ['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']
RAW = COUNTS + ['fgm','fg3m','ftm','seconds','liveTov','deadTov','touchTov','passSteals','touchSteals','offensiveFoulTov','passOutTov','handlingOutTov','passes']
RATE = {'fgPct':('fgm','fga',100),'threePct':('fg3m','fg3a',100),'ftPct':('ftm','fta',50)}
ROLE = ['PG','SG','SF','PF','C']
TRUTH = {k:k.upper() for k in COUNTS + ['fgm','fg3m','ftm']}
sources = {}

def read(path):
    p = Path(path); raw = p.read_bytes()
    sources[str(p).replace('\\','/')] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)

def basic_metrics(rows, key):
    rs = [r for r in rows if r['minutes']>=500 and r['metrics'].get(key) is not None]
    if not rs: return None
    w=np.array([r['minutes'] for r in rs]);w=w/w.sum()
    a=np.array([r['metrics'][key]['actual'] for r in rs]); b=np.array([r['metrics'][key]['predicted'] for r in rs]);e=b-a
    am=np.sum(w*a);bm=np.sum(w*b);asd=np.sqrt(np.sum(w*(a-am)**2));bsd=np.sqrt(np.sum(w*(b-bm)**2))
    return {'players':len(rs),'actual':float(am),'predicted':float(bm),'bias':float(np.sum(w*e)),
      'mae':float(np.sum(w*np.abs(e))),'rmse':float(np.sqrt(np.sum(w*e**2))),
      'correlation':float(np.sum(w*(a-am)*(b-bm))/(asd*bsd)) if asd*bsd else None,
      'sdRatio':float(bsd/asd) if asd else None}

def season_audit(season):
    b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
    protocol=read(MODEL/'protocol.json'); seeds=protocol['seeds']
    truth={}; stints={}
    for t in b['league']['teams']:
      for p in t['roster']:
        q=truth.setdefault(p['playerId'],{'playerId':p['playerId'],'name':p['name'],'minutes':0,'counts':defaultdict(float),'teamMinutes':defaultdict(float),'height':p['heightInches'],'fallbackPosition':p['pos']})
        q['minutes']+=p['observed']['MIN'];q['teamMinutes'][t['id']]+=p['observed']['MIN']
        for k,col in TRUTH.items():q['counts'][k]+=p['observed'][col]
        stints[(t['id'],p['playerId'])]=p
    votes=defaultdict(lambda:np.zeros(5));starts=defaultdict(int);exact=0;proxy=0
    for game in b['exposure']['games']:
      for t in game['teams']:
        ss=[p for p in t['players'] if p.get('starter') and p['seconds']>0]
        if len(ss)==5 and all(sum(p.get('position')==pos for p in ss)==1 for pos in ROLE):
          ordered=[next(p for p in ss if p.get('position')==pos) for pos in ROLE];exact+=1
        else:
          gs=[p for p in ss if p.get('position')=='G'];fs=[p for p in ss if p.get('position')=='F'];cs=[p for p in ss if p.get('position')=='C']
          if len(gs)!=2 or len(fs)!=2 or len(cs)!=1:continue
          gs.sort(key=lambda p:-truth[p['playerId']]['counts']['ast']/truth[p['playerId']]['minutes'])
          fs.sort(key=lambda p:truth[p['playerId']]['height']);ordered=gs+fs+cs;proxy+=1
        for i,p in enumerate(ordered):votes[p['playerId']][i]+=p['seconds'];starts[p['playerId']]+=1
    arrays={pid:np.zeros((len(seeds),len(RAW))) for pid in truth}
    team_arrays={t['id']:np.zeros((len(seeds),len(RAW))) for t in b['league']['teams']}
    for si,seed in enumerate(seeds):
      run=read(MODEL/f'runs/{season}-split-{seed}.json')
      assert len(run['matches'])==1230 and all(t['games']==82 for t in run['teams'])
      for t in run['teams']:
        for ki,k in enumerate(RAW):team_arrays[t['id']][si,ki]=t['stats'].get(k,0)
        for p in t['players']:
          assert p['playerId'] in arrays
          for ki,k in enumerate(RAW):arrays[p['playerId']][si,ki]+=p['stats'].get(k,0)
    rows=[]
    for pid,q in truth.items():
      arr=arrays[pid];avg=arr.mean(axis=0);sim=dict(zip(RAW,map(float,avg)));sm=sim['seconds']/60
      pos=ROLE[int(np.argmax(votes[pid]))] if starts[pid] else q['fallbackPosition']
      role='G' if pos in ['PG','SG','G'] else 'C' if pos=='C' else 'F'
      metrics={}
      for k in COUNTS:
        if q['minutes']<=0 or sm<=0:metrics[k+'36']=None;continue
        metrics[k+'36']={'actual':36*q['counts'][k]/q['minutes'],'predicted':36*sim[k]/sm}
      for key,(made,attempt,threshold) in RATE.items():
        metrics[key]={'actual':100*q['counts'][made]/q['counts'][attempt],'predicted':100*sim[made]/sim[attempt] if sim[attempt]>0 else 0} if q['counts'][attempt]>=threshold else None
      if q['counts']['tov']>0 and sim['tov']>0:metrics['astToTov']={'actual':q['counts']['ast']/q['counts']['tov'],'predicted':sim['ast']/sim['tov']}
      tu=q['counts']['fga']+.44*q['counts']['fta']+q['counts']['tov'];su=sim['fga']+.44*sim['fta']+sim['tov']
      metrics['tovPer100Uses']={'actual':100*q['counts']['tov']/tu,'predicted':100*sim['tov']/su} if tu>0 and su>0 else None
      rows.append({'playerId':pid,'name':q['name'],'season':season,'position':pos,'roleGroup':role,'positionStarts':starts[pid],
        'positionLowConfidence':starts[pid]<5,'minutes':q['minutes'],'predictedMinutes':sm,
        'minuteDifference':sm-q['minutes'],'teamId':max(q['teamMinutes'],key=q['teamMinutes'].get),
        'actualCounts':dict(q['counts']),'predictedCounts':sim,'metrics':metrics})
    keys=[k+'36' for k in COUNTS]+list(RATE)+['astToTov','tovPer100Uses']
    summary={group:{k:basic_metrics([r for r in rows if group=='ALL' or r['roleGroup']==group],k) for k in keys} for group in ['ALL','G','F','C']}
    # Role summaries also reported with only >=5 observed starts: avoid hiding
    # uncertainty from height-band fallback classifications.
    confident={group:{k:basic_metrics([r for r in rows if r['roleGroup']==group and not r['positionLowConfidence']],k) for k in keys} for group in ['G','F','C']}
    global_counts={k:{'actual':sum(q['counts'][k] for q in truth.values())/2460,'predicted':sum(a[:,RAW.index(k)].mean() for a in arrays.values())/2460} for k in COUNTS}
    team_summary={}
    for k in COUNTS:
      actual={t['id']:sum(p['observed'][TRUTH[k]] for p in t['roster'])/82 for t in b['league']['teams']}
      predicted={tid:a[:,RAW.index(k)].mean()/82 for tid,a in team_arrays.items()}
      errors=np.array([predicted[tid]-actual[tid] for tid in actual]);team_summary[k]={'actual':float(np.mean(list(actual.values()))),'predicted':float(np.mean(list(predicted.values()))),'bias':float(errors.mean()),'mae':float(np.abs(errors).mean()),'rmse':float(np.sqrt(np.mean(errors**2)))}
    return {'season':season,'players':rows,'summary':summary,'confidentRoleSummary':confident,'teamSummary':team_summary,'globalPlayerCountsPerTeamGame':global_counts,
      'positionCoverage':{'exactTeamGames':exact,'proxyTeamGames':proxy,'lowConfidencePlayers':sum(r['positionLowConfidence'] for r in rows)},
      'zeroSimulationMinutes':[r['playerId'] for r in rows if r['predictedMinutes']==0]}

ROOT.mkdir(parents=True,exist_ok=True)
protocol={'version':'individual-box-audit-1','model':'pure-oreb-turnover-time-1','seasons':SEASONS,'seeds':list(range(20261012,20261032)),
 'scope':'Retrospective all-player box-stat reconstruction from archived adopted-model simulations; no new simulation or rating change.',
 'aggregation':'Merge traded stints by player ID before rates; predicted per36 = 36 * seed-mean count / seed-mean simulated minutes; actual per36 uses official season minutes.',
 'population':'Export every player; primary summary actual MIN>=500, weighted by actual MIN. Official starter-role classification and low-confidence sensitivity reported.',
 'percentageSupport':'Actual FGA>=100 for FG%; 3PA>=100 for 3P%; FTA>=50 for FT%. Never infer missing denominator as measured accuracy.',
 'separation':'Minutes error, event-volume error, shooting accuracy and AST/TOV distinguished. Guard total turnovers need not be lower: compare observed workload and turnover per100 used possessions.',
 'limits':'Conditional same-season reconstruction, not forecast or transferable ability. PBP event-type truth and spacing/counterfactual tests require separate measurement.'}
pf=ROOT/'protocol.json'
if pf.exists():assert json.loads(pf.read_text(encoding='utf-8'))==protocol
else:pf.write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
results=[season_audit(s) for s in SEASONS]
(ROOT/'baseline.json').write_text(json.dumps({'protocol':protocol,'seasons':results},ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'players.csv').open('w',encoding='utf-8-sig',newline='') as f:
  base_fields=['season','playerId','name','position','positionLowConfidence','minutes','predictedMinutes']
  metric_fields=[k+'36' for k in COUNTS]+list(RATE)+['astToTov','tovPer100Uses']
  fields=base_fields+metric_fields
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for s in results:
    for p in s['players']:
      writer.writerow({**{k:p[k] for k in base_fields},**{k:json.dumps(p['metrics'].get(k),ensure_ascii=False) for k in metric_fields}})
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
print(json.dumps({'season':results[-1]['season'],'summary':results[-1]['summary'],'teamSummary':results[-1]['teamSummary']},ensure_ascii=False,indent=2))

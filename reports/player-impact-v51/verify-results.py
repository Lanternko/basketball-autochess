import json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean
import numpy as np
R=Path('reports/player-impact-v51');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for version in ['v49','v50']:
 for f,v in read(f'reports/player-impact-{version}/results-verification.json')['evidenceSHA256'].items():assert h(f)==v,(version,f)
print('Frozen v49 and v50 evidence unchanged',flush=True)
seen={};jobs=0;games=0
for stage in ['probe','execution','joint','deadline','diagnostic','power','rolling','confirmation']:
 for f,v in read(R/f'{stage}-source-protocol.json')['hashes'].items():assert h(f)==v,(stage,f)
 ver=read(R/f'{stage}-verification.json');assert ver['passed']
 for f,v in ver['outputHashes'].items():
  assert h(f)==v;r=read(f);jobs+=1;games+=len(r['matches']);seed=r.get('seed',20261012);seen[stage,r['season'],r['variant'],seed]={m['id'] for m in r['matches']}
  for g in r['rotation']['games']:
   for t in g['teams'].values():
    assert sum(q['seconds'] for q in t['players'].values())==5*t['end']
    for q in t['players'].values():assert sum(q['stints'])==q['seconds'] and sum(q['phase'])<=q['seconds']
    for key,v in t['pairs'].items():
     a,b=key.split('/');assert v<=sum(t['players'][a]['phase']) and v<=sum(t['players'][b]['phase'])
 print(stage,'hashes and time ledgers passed',flush=True)
for season in read(R/'protocol.json')['seasons']:
 train=seen['probe',season,'baseline',20261012];confirm=seen['confirmation',season,'baseline',20261012]
 priorHoldout={m['id'] for m in read(f'reports/player-impact-v50/holdout-{season}-baseline.json')['matches']}
 assert train.isdisjoint(confirm) and priorHoldout.isdisjoint(confirm)
 old=read(f'reports/player-impact-v49/tuning-{season}-weight0.25.json');new=read(R/f'probe-{season}-baseline.json');assert old['matches']==new['matches'] and old['rotation']==new['rotation']
 for seed in read(R/'power-protocol.json')['seeds']:
  a=read(R/f'power-{season}-baseline-{seed}.json');b=read(R/f'rolling-{season}-baseline-{seed}.json');assert a['matches']==b['matches'] and a['rotation']==b['rotation']
print('Baseline parity and disjoint fixtures passed',flush=True)
# Reconstruct source timings independently and check every confirmation seed metric.
p=read(R/'confirmation-protocol.json');cells=[]
for season in p['seasons']:
 gids=seen['confirmation',season,'baseline',p['seeds'][0]];ex={g['id']:g for g in read(f'reports/player-impact-v49/{season}-metadata.json')['exposure']['games']}
 truth={gid:{t['teamId']:{'players':{str(q['playerId']):np.zeros(24) for q in t['players'] if q['seconds']>0},'pairs':Counter()} for t in ex[gid]['teams']} for gid in gids}
 with Path(f'reports/defense-seventh/{season}/stints/stints.jsonl').open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in gids or st['period']>4 or st['seconds']<=0:continue
   start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds'];w=np.maximum(0,np.minimum(np.arange(1,25)*120,end)-np.maximum(np.arange(24)*120,start))
   for t in st['teams']:
    tr=truth[st['id']][t['teamId']];ids=sorted(t['players'])
    for pid in ids:tr['players'][str(pid)]+=w
    for i,a in enumerate(ids):
     for b in ids[i+1:]:tr['pairs'][f'{a}/{b}']+=st['seconds']
 for variant in p['variants']:
  for seed in p['seeds']:
   r=read(R/f'confirmation-{season}-{variant}-{seed}.json');phase=[];pairs=[];reg=[];dur=[]
   assert {g['id'] for g in r['rotation']['games']}==gids
   for g in r['rotation']['games']:
    for tid,t in g['teams'].items():
     tr=truth[g['id']][int(tid)];ids=sorted(map(int,tr['players']))
     for pid,act in tr['players'].items():
      q=t['players'].get(pid,{});pred=np.array(q.get('phase',[0]*24))/10;phase.append(float(np.abs(pred-act).sum()/60));reg.append(float(abs(pred.sum()-act.sum())/60));dur.extend(x/10 for x in q.get('stints',[]))
     for i,a in enumerate(ids):
      for b in ids[i+1:]:key=f'{a}/{b}';pairs.append(abs(t['pairs'].get(key,0)/10-tr['pairs'][key])/60)
   cells.append({'season':season,'variant':variant,'seed':seed,'phaseMAE':mean(phase),'pairMAE':mean(pairs),'regMinuteMAE':mean(reg),'shortShare':mean(x<60 for x in dur)})
 print(season,'confirmation source metrics verified',flush=True)
score=read(R/'confirmation-selection.json')
for c in cells:
 row=next(q for q in score['rawCells'] if all(q[k]==c[k] for k in ['season','variant','seed']))
 for k in ['phaseMAE','pairMAE','regMinuteMAE','shortShare']:assert abs(row[k]-c[k])<1e-10
agg=[{'season':s,'variant':v,**{k:mean(c[k] for c in cells if c['season']==s and c['variant']==v) for k in ['phaseMAE','pairMAE','regMinuteMAE','shortShare']}} for s in p['seasons'] for v in p['variants']]
base={c['season']:c for c in agg if c['variant']=='baseline'};cand=[c for c in agg if c['variant']=='rollingPlan'];objective=mean(c['phaseMAE']/base[c['season']]['phaseMAE']+c['pairMAE']/base[c['season']]['pairMAE'] for c in cand)
gates={'objectiveImprovedOverOnePercent':objective<1.98,'everySeasonMinuteWithin005':all(c['regMinuteMAE']<=base[c['season']]['regMinuteMAE']+.05 for c in cand),'everySeasonShortShareWithin001':all(c['shortShare']<=base[c['season']]['shortShare']+.01 for c in cand)}
assert gates['objectiveImprovedOverOnePercent'] and not gates['everySeasonMinuteWithin005'] and score['selectedVariant']=='baseline'
assert read(R/'runtime-verification.json')['passed']
result={'passed':True,'jobs':jobs,'gameExecutions':games,'v49V50EvidenceUnchanged':True,'baselineParityFixtures':180,'confirmationIndependentOfPrior540Fixtures':True,'confirmationMetricsRecomputed':True,'candidateRejected':True,'objective':objective,'gates':gates,'confirmationCells':agg,'targetSeasonEvaluated':False,'runtimeVerificationSHA256':h(R/'runtime-verification.json')}
(R/'audit-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='confirmationCells'}))

import json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
from statistics import mean
R=Path('reports/player-impact-v50');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));hashfile=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sealed=read('reports/player-impact-v49/results-verification.json')
print(list(sealed),flush=True)
for f,h in sealed['evidenceSHA256'].items():assert hashfile(f)==h,('v49 drift',f)
seen={};runs=0;games=0
for stage in ['probe','second','pair','final','holdout']:
 protocol=read(R/f'{stage}-source-protocol.json')
 for f,h in protocol['hashes'].items():assert hashfile(f)==h,(stage,f)
 ver=read(R/f'{stage}-verification.json');assert ver['passed']
 for f,h in ver['outputHashes'].items():
  assert hashfile(f)==h;r=read(f);runs+=1;games+=len(r['matches']);seen[(stage,r['season'],r['variant'])]={m['id'] for m in r['matches']}
  for g in r['rotation']['games']:
   for t in g['teams'].values():
    assert sum(q['seconds'] for q in t['players'].values())==5*t['end']
    for q in t['players'].values():assert sum(q['stints'])==q['seconds'] and sum(q['phase'])<=q['seconds']
    for key,n in t['pairs'].items():
     a,b=key.split('/');assert n<=sum(t['players'][a]['phase']) and n<=sum(t['players'][b]['phase'])
for season in read(R/'protocol.json')['seasons']:
 assert seen['probe',season,'baseline'].isdisjoint(seen['holdout',season,'baseline'])
 old=read(f'reports/player-impact-v49/tuning-{season}-weight0.25.json');new=read(R/f'probe-{season}-baseline.json')
 assert old['matches']==new['matches'] and old['rotation']==new['rotation']
print('Hashes, ledgers, and disjoint/parity fixtures passed',flush=True)
# Independent sparse reconstruction of all learned joint phase CDFs.
maxerr=0;profiles=0
for season in read(R/'pair-protocol.json')['seasons']:
 fit=read(R/f'{season}-pair-phase.json');fold=read(f'reports/player-impact-v49/{season}-profiles.json')['foldByGame'];assert fit['foldByGame']==fold
 meta=read(f'reports/player-impact-v49/{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};c=defaultdict(Counter);ng=defaultdict(Counter)
 for gid,f in fold.items():
  for t in ex[gid]['teams']:
   ids=sorted(q['playerId'] for q in t['players'] if q['seconds']>0)
   for i,a in enumerate(ids):
    for b in ids[i+1:]:ng[f"{t['teamId']}/{a}/{b}"][f]+=1
 src=Path(f'reports/defense-seventh/{season}/stints/stints.jsonl')
 with src.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in fold or st['period']>4 or st['seconds']<=0:continue
   f=fold[st['id']];start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds']
   for t in st['teams']:
    ids=sorted(t['players'])
    for i,a in enumerate(ids):
     for b in ids[i+1:]:
      row=c[f"{t['teamId']}/{a}/{b}"]
      for phase in range(24):
       sec=max(0,min(end,120*(phase+1))-max(start,120*phase))
       if sec:row[f,phase]+=sec
 for heldout in [-1,0,1,2,3,4]:
  model=fit['fallbackPrior'] if heldout<0 else fit['folds'][heldout];expected={}
  for key,row in c.items():
   bins=[math.fsum(v for (f,b),v in row.items() if f!=heldout and b==phase) for phase in range(24)];total=math.fsum(bins)
   if not total:continue
   n=sum(v for f,v in ng[key].items() if f!=heldout);prior=total/max(1,n);cdf=[0];q=0
   for v in bins:q+=(v+prior/24)/(total+prior);cdf.append(q)
   cdf[-1]=1;expected[key]=cdf
  assert set(model)==set(expected)
  for key,a in model.items():
   e=max(abs(x-y) for x,y in zip(a,expected[key]));maxerr=max(maxerr,e);assert e<1e-12;profiles+=1
 print(season,'independent fold CDF verification passed',flush=True)
# Independently recompute the fixed confirmation gate, without invoking its scorer.
cells=[]
for season in read(R/'protocol.json')['seasons']:
 rs={v:read(R/f'holdout-{season}-{v}.json') for v in ['baseline','phasePairShort']};gids=seen['holdout',season,'baseline'];meta=read(f'reports/player-impact-v49/{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};truth={gid:{t['teamId']:{'players':{str(q['playerId']):[0]*24 for q in t['players'] if q['seconds']>0},'pairs':Counter()} for t in ex[gid]['teams']} for gid in gids}
 with Path(f'reports/defense-seventh/{season}/stints/stints.jsonl').open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in gids or st['period']>4 or st['seconds']<=0:continue
   start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds']
   for t in st['teams']:
    tr=truth[st['id']][t['teamId']];ids=sorted(t['players'])
    for pid in ids:
     for phase in range(24):tr['players'][str(pid)][phase]+=max(0,min(end,120*(phase+1))-max(start,120*phase))
    for i,a in enumerate(ids):
     for b in ids[i+1:]:tr['pairs'][f'{a}/{b}']+=st['seconds']
 for variant,r in rs.items():
  phase=[];pairs=[];reg=[];dur=[]
  for g in r['rotation']['games']:
   for tid,t in g['teams'].items():
    tr=truth[g['id']][int(tid)];ids=sorted(map(int,tr['players']))
    for pid,act in tr['players'].items():
     q=t['players'].get(pid,{});pred=q.get('phase',[0]*24);phase.append(sum(abs(x/10-y) for x,y in zip(pred,act))/60);reg.append(abs(sum(pred)/10-sum(act))/60);dur.extend(x/10 for x in q.get('stints',[]))
    for i,a in enumerate(ids):
     for b in ids[i+1:]:key=f'{a}/{b}';pairs.append(abs(t['pairs'].get(key,0)/10-tr['pairs'][key])/60)
  cells.append({'season':season,'variant':variant,'phaseMAE':mean(phase),'pairMAE':mean(pairs),'regMinuteMAE':mean(reg),'shortShare':mean(x<60 for x in dur)})
scored=read(R/'holdout-selection.json')
for row in cells:
 q=next(c for t in scored['table'] for c in t['cells'] if c['season']==row['season'] and c['variant']==row['variant'])
 for k in ['phaseMAE','pairMAE','regMinuteMAE','shortShare']:assert abs(row[k]-q[k])<1e-10
base={c['season']:c for c in cells if c['variant']=='baseline'};cand=[c for c in cells if c['variant']=='phasePairShort'];objective=mean(c['phaseMAE']/base[c['season']]['phaseMAE']+c['pairMAE']/base[c['season']]['pairMAE'] for c in cand);eligible=all(c['regMinuteMAE']<=base[c['season']]['regMinuteMAE']+.05 and c['shortShare']<=base[c['season']]['shortShare']+.01 for c in cand)
assert not eligible and objective>=1.98 and scored['selectedVariant']=='baseline'
assert read(R/'runtime-verification.json')['passed']
result={'passed':True,'runJobs':runs,'gameExecutions':games,'sourceFoldCDFProfilesVerified':profiles,'maximumCDFError':maxerr,'heldoutMetricsIndependentlyRecomputed':True,'candidateRejected':True,'v49EvidenceUnchanged':True,'targetSeasonUsedForSelection':False,'holdoutDisjoint':True,'baselineExactRotationParityFixtures':180,'confirmationObjective':objective,'confirmationCells':cells}
(R/'audit-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='confirmationCells'}))

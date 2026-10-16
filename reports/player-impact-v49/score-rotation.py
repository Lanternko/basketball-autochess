import json,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'protocol.json');seasons=sys.argv[1:] or p['seasons'];cells=[];sources={}
for season in seasons:
 meta=read(R/f'{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);actual={};names={str(q['playerId']):q['name'] for t in meta['teams'] for q in t['players']}
 for gid in valid:
  actual[gid]={t['teamId']:{'players':{str(q['playerId']):np.zeros(24) for q in t['players'] if q['seconds']>0},'pairs':Counter()} for t in ex[gid]['teams']}
 file=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');sources[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
 with file.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in valid or st['period']>4 or st['seconds']<=0:continue
   start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds'];weights=np.maximum(0,np.minimum(np.arange(1,25)*120,end)-np.maximum(np.arange(24)*120,start))
   for t in st['teams']:
    team=actual[st['id']][t['teamId']];ids=sorted(t['players'])
    for pid in ids:team['players'][str(pid)]+=weights
    for i,a in enumerate(ids):
     for b in ids[i+1:]:team['pairs'][f'{a}/{b}']+=st['seconds']
 for variant in ['v47','v49']:
  phaseErrors=[];pairErrors=[];minuteErrors=[];curry=defaultdict(Counter);seedSummary=[];stints=[];fullMinute=[];fullReg=[];totals=Counter()
  for seed in p['seeds']:
   file=R/f'runs/{season}-{variant}-strict-{seed}.json';r=read(file);sources[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest();assert len(r['rotation']['games'])==len(valid)
   phase=[];pairs=[];reg=[]
   for g in r['rotation']['games']:
    for tid,t in g['teams'].items():
     truth=actual[g['id']][int(tid)];ap=truth['players'];pp=t['players'];ids=sorted(int(x) for x in ap)
     for pid,aph in ap.items():
      pred=np.array(pp.get(pid,{}).get('phase',[0]*24))/10;phase.append(float(np.abs(pred-aph).sum()/60));reg.append(float(abs(pred.sum()-aph.sum())/60));stints.extend(v/10 for v in pp.get(pid,{}).get('stints',[]))
     for i,a in enumerate(ids):
      for b in ids[i+1:]:key=f'{a}/{b}';pairs.append(abs(t['pairs'].get(key,0)/10-truth['pairs'][key])/60)
     if '201939' in ap:
      for pid in ids:
       if pid==201939:continue
       key=f'{min(pid,201939)}/{max(pid,201939)}';on=truth['pairs'][key];pon=t['pairs'].get(key,0)/10;seconds=float(ap[str(pid)].sum());psec=sum(pp.get(str(pid),{}).get('phase',[0]*24))/10
       curry[pid].update({'actualOn':on/3,'predictedOn':pon/3,'actualOff':(seconds-on)/3,'predictedOff':(psec-pon)/3})
   phaseErrors.extend(phase);pairErrors.extend(pairs);minuteErrors.extend(reg)
   full=read(f'reports/player-impact-v47/runs/{season}-v47-full-{seed}.json' if variant=='v47' else R/f'runs/{season}-v49-full-{seed}.json');n=sum(t['playerGames'] for t in full['teams']);am=sum(t['minuteError'] for t in full['teams'])/n;rm=sum(t['regulationMinuteError'] for t in full['teams'])/n;fullMinute.append(am);fullReg.append(rm)
   seedSummary.append({'seed':seed,'phaseAbsoluteMinutesPerAppearance':float(np.mean(phase)),'pairOverlapMinutesMAE':float(np.mean(pairs)),'strictRegulationSourceMinutesMAE':float(np.mean(reg)),'fullActualMinutesMAE':am,'fullRegulationTargetMinutesMAE':rm})
  c={'season':season,'variant':variant,'phaseAbsoluteMinutesPerAppearance':float(np.mean(phaseErrors)),'pairOverlapMinutesMAE':float(np.mean(pairErrors)),'strictRegulationSourceMinutesMAE':float(np.mean(minuteErrors)),'fullActualMinutesMAE':float(np.mean(fullMinute)),'fullRegulationTargetMinutesMAE':float(np.mean(fullReg)),'phaseErrorP90':float(np.quantile(phaseErrors,.9)),'pairErrorP90':float(np.quantile(pairErrors,.9)),'strictMinuteErrorP90':float(np.quantile(minuteErrors,.9)),'stintDurationSeconds':{'count':len(stints),'median':float(np.median(stints)),'p90':float(np.quantile(stints,.9)),'under60Share':float(np.mean(np.array(stints)<60)),'over900Share':float(np.mean(np.array(stints)>900))},'curryTeammates':[{'playerId':pid,'name':names.get(str(pid),str(pid)),**{k:v/60 for k,v in v.items()}} for pid,v in curry.items()],'seeds':seedSummary};cells.append(c);print(json.dumps({k:v for k,v in c.items() if k not in ['curryTeammates','seeds']}),flush=True)
out={'scope':'Full official per-game minute error includes overtime-duration differences. Regulation target error uses the existing48-minute-normalized official game targets. Strict phase discrepancy sums absolute bin-minute differences per appearance; pair overlap MAE averages all pairs of actual participants per game, including zero overlap. Source phase/pairs exclude overtime; baseline is exact-parity observer rerun. Curry on/off conditional minutes are regulation only.','cells':cells,'sourceSHA256':sources}
prefix='' if seasons==p['seasons'] else '-'.join(seasons)+'-';(R/(prefix+'rotation-scores.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')

import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path('reports/player-impact-v49');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));p=read(R/'protocol.json');seasons=p['seasons'];grid=p['priorGameGrid'];sourceHashes={};allData={}
def data(season):
 src=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');sourceHashes[src.as_posix()]=hashlib.sha256(src.read_bytes()).hexdigest()
 meta=read(R/f'{season}-metadata.json');ex={g['id']:g for g in meta['exposure']['games']};fold={gid:f for gid,f,ps in read(f'reports/player-impact-v45/{season}-fga-data.json')['minutes']};games=defaultdict(list)
 with src.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] in fold and st['period']<=4:games[st['id']].append(st)
 phase=np.zeros((5,2,24,2));players=defaultdict(lambda:np.zeros((5,24,2)));pairs=defaultdict(lambda:np.zeros((5,4)));durations=[];rests=[]
 for gid,stints in games.items():
  f=fold[gid]
  for team in ex[gid]['teams']:
   tid=team['teamId'];ps=sorted(x['playerId'] for x in team['players'] if x['seconds']>0);starters={x['playerId']:int(bool(x.get('starter'))) for x in team['players']};last={};runs={}
   for st in sorted(stints,key=lambda x:(x['period'],-x['startClock'])):
    own=next(t for t in st['teams'] if t['teamId']==tid);on=set(own['players']);start=(st['period']-1)*720+720-st['startClock'];end=start+st['seconds']
    for b in range(max(0,int(start//120)),min(24,int(np.ceil(end/120)))):
     sec=max(0,min(end,(b+1)*120)-max(start,b*120))
     for pid in ps:
      state=int(pid in on);players[(tid,pid,starters[pid])][f,b,0]+=sec*state;players[(tid,pid,starters[pid])][f,b,1]+=sec;phase[f,starters[pid],b,0]+=sec*state;phase[f,starters[pid],b,1]+=sec
    for i,a in enumerate(ps):
     for b in ps[i+1:]:pairs[(tid,a,b)][f,(0 if a in on and b in on else 1 if a in on else 2 if b in on else 3)]+=st['seconds']
    for pid in ps:
     state=pid in on
     if pid not in last:last[pid]=(state,start)
     if last[pid][0]!=state:
      length=start-last[pid][1]
      if length>0:(durations if last[pid][0] else rests).append((f,length))
      last[pid]=(state,start)
   for pid,(state,start) in last.items():
    if 2880-start>0:(durations if state else rests).append((f,2880-start))
 print(json.dumps({'season':season,'games':len(games),'players':len(players),'pairs':len(pairs)}),flush=True)
 return {'phase':phase,'players':players,'pairs':pairs,'durations':durations,'rests':rests,'games':dict(fold)}
def profiles(d,fold,kphase,kpair,score=False):
 keep=[i for i in range(5) if i!=fold];phase=d['phase'][keep].sum(0);prior=(phase[:,:,0]+1)/(phase[:,:,1]+2);out={'players':{},'pairs':{}};loss=np.zeros(4)
 for (tid,pid,starter),v in d['players'].items():
  c=v[keep].sum(0);prob=(c[:,0]+kphase*120*prior[starter])/(c[:,1]+kphase*120);out['players'][f'{tid}/{pid}/{starter}']=prob.tolist()
  if score:
   test=v[fold];loss[0]-=np.sum(test[:,0]*np.log(prob)+(test[:,1]-test[:,0])*np.log1p(-prob));loss[1]+=test[:,1].sum()
 for (tid,a,b),v in d['pairs'].items():
  c=v[keep].sum(0);n=c.sum();pa=(c[0]+c[1]+.5)/(n+1);pb=(c[0]+c[2]+.5)/(n+1);prior4=np.array([pa*pb,pa*(1-pb),(1-pa)*pb,(1-pa)*(1-pb)]);q=(c+kpair*2880*prior4)/(n+kpair*2880);out['pairs'][f'{tid}/{a}/{b}']=float(np.log(q[0])+np.log(q[3])-np.log(q[1])-np.log(q[2]))
  if score:loss[2]-=np.dot(v[fold],np.log(q));loss[3]+=v[fold].sum()
 return out,loss
for s in seasons:allData[s]=data(s)
table=[]
for k in grid:
 cells=[]
 for s in seasons[:3]:
  loss=sum((profiles(allData[s],f,k,k,True)[1] for f in range(5)),np.zeros(4));cells.append({'season':s,'phaseNLL':float(loss[0]/loss[1]),'pairNLL':float(loss[2]/loss[3])})
 table.append({'priorGames':k,'phaseNLL':float(np.mean([c['phaseNLL'] for c in cells])),'pairNLL':float(np.mean([c['pairNLL'] for c in cells])),'cells':cells})
kp=min(table,key=lambda x:(x['phaseNLL'],x['priorGames']))['priorGames'];kb=min(table,key=lambda x:(x['pairNLL'],x['priorGames']))['priorGames'];selection={'phasePriorGames':kp,'pairPriorGames':kb,'table':table,'targetExcluded':True};(R/'selection.json').write_text(json.dumps(selection,indent=2),encoding='utf-8')
for s,d in allData.items():
 thresholds=lambda f:{'minimumStint':float(np.quantile([v for g,v in d['durations'] if g!=f],.25)),'minimumRest':float(np.quantile([v for g,v in d['rests'] if g!=f],.25))}
 out={'season':s,'foldByGame':d['games'],'folds':[profiles(d,f,kp,kb)[0] for f in range(5)],'minimumByFold':[thresholds(f) for f in range(5)],'minimumStintSeconds':thresholds(-1)['minimumStint'],'minimumRestSeconds':thresholds(-1)['minimumRest'],'fallbackPrior':profiles(d,-1,kp,kb)[0]}
 # Full training fallback only for games without strict source stints; tested strict games always use their excluded fold.
 (R/f'{s}-profiles.json').write_text(json.dumps(out),encoding='utf-8')
(R/'source-hashes.json').write_text(json.dumps(sourceHashes,indent=2),encoding='utf-8');print(json.dumps(selection),flush=True)

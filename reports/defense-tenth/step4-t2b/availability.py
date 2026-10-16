import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def table(p):
 t=read(p)['data']['resultSets'][0];return [dict(zip(t['headers'],r)) for r in t['rowSet']]
P=read(O/'protocol.json');assert hashlib.sha256((O/'protocol.json').read_bytes()).hexdigest()==(O/'protocol.sha256').read_text().split()[0]
D=read(R/'reports/defense-tenth/step4-t2/players.json');profiles=read(O/'profiles.json');org=read(O/'organizers.json');manifest=read(O/'fetch-manifest.json');raw={}
fields=['FG2A','FG2M','FG3A','FG3M'];audits=[];results=[]
for source in manifest['sources']:
 if source['date'] or source['team']:
  assert hashlib.sha256((R/source['file']).read_bytes()).hexdigest()==source['sha256']
  group={}
  for r in table(R/source['file']):
   pid=str(r['PLAYER_ID']);a=group.setdefault(pid,np.zeros(4));a+=np.array([r[k] or 0 for k in fields])
  raw[source['season'],str(source['team']),source['kind'],source['date']]=group
def role(s,tid,pid):
 x=profiles[s].get(tid+':'+pid,{});si=P['seasons'].index(s);anchors=[org[s].get(tid)]+([org[P['seasons'][si-1]].get(tid)] if si else [])
 rotation=sorted([r for r in profiles[s].values() if str(r['teamId'])==tid],key=lambda r:r['MIN'],reverse=True)
 eligible=x.get('MIN',0)>=500 or int(pid) in [r['id'] for r in rotation[:10]]
 return eligible and all(not a or a['id']!=int(pid) for a in anchors) and x.get('AST_PCT') is not None and x.get('USG_PCT') is not None and x['AST_PCT']<.2 and x['USG_PCT']<.25
for case in P['cases']:
 s=case['season'];tid=next(t for t,x in D[s]['teams'].items() if x['name']==case['team']);base=R/('data/season-source' if s=='2025-26' else f'data/defense-seventh/{s}')
 logs=[x for x in table(base/'player-games.json') if str(x['TEAM_ID'])==tid];dates=sorted({x['GAME_DATE'][:10] for x in logs});pids=sorted({str(x['PLAYER_ID']) for x in logs});pi={x:i for i,x in enumerate(pids)};bydate=defaultdict(dict)
 for x in logs:bydate[x['GAME_DATE'][:10]][str(x['PLAYER_ID'])]=x
 cube=np.zeros((len(dates),len(pids),12));mismatch=[];partitions=[];fullDif=[]
 for di,date in enumerate(dates):
  allr=raw[s,tid,'all',date];catch=raw[s,tid,'catch',date];pull=raw[s,tid,'pull',date]
  for pid in pids:
   a=allr.get(pid,np.zeros(4));c=catch.get(pid,np.zeros(4));u=pull.get(pid,np.zeros(4));cube[di,pi[pid]]=np.r_[a,c,u]
   box=bydate[date].get(pid,{});da=float(a[0]+a[2]-(box.get('FGA',0) or 0));dm=float(a[1]+a[3]-(box.get('FGM',0) or 0))
   if da or dm:mismatch.append({'date':date,'id':pid,'trackingMinusBoxFGA':da,'trackingMinusBoxFGM':dm})
   if np.any(a-c-u<0):partitions.append({'date':date,'id':pid})
 for cat,ix in [('all',0),('catch',4),('pull',8)]:
  full=raw[s,tid,cat,'']
  for pid in pids:
   delta=cube[:,pi[pid],ix:ix+4].sum(axis=0)-full.get(pid,np.zeros(4))
   if np.any(delta):fullDif.append({'id':pid,'category':cat,'sumDatesMinusFull':delta.tolist()})
 audits.append({'season':s,'team':case['team'],'dates':len(dates),'boxMismatches':mismatch,'invalidPartitions':partitions,'dateSumVsFullDifferences':fullDif,'dateTrackingFGA':float(cube[:,:,[0,2]].sum()),'officialFGA':sum(x['FGA'] for x in logs)})
 assert not partitions,'overlapping tracking categories'
 # Missing tracking is retained as missing coverage, never converted to an observed zero-rate.
 for kind,anchor in [('current',org[s].get(tid)),('prior',org[P['seasons'][P['seasons'].index(s)-1]].get(tid))]:
  if not anchor:continue
  state=np.array([int((bydate[d].get(str(anchor['id']),{}).get('MIN',0) or 0)>0) for d in dates]);on=state.sum();off=len(state)-on
  for subset in ['all','role']:
   keep=[i for i,pid in enumerate(pids) if int(pid)!=anchor['id'] and (subset=='all' or role(s,tid,pid))];g=cube[:,keep,:]
   both=np.stack([g[state==j].sum(axis=0) for j in [0,1]],axis=1);elig=np.minimum(both[:,0,0]+both[:,0,2],both[:,1,0]+both[:,1,2])>=50
   g=g[:,elig];both=both[elig];npids=g.shape[1];masks={}
   for name,cat,three in [('catchFG',4,False),('catch3FG',4,True),('pullFG',8,False),('pull3FG',8,True)]:
    masks[name]=[(zone,np.minimum(both[:,0,cat+zone],both[:,1,cat+zone])>=20) for zone in ([2] if three else [0,2])]
   def calc(a):
    ans={}
    for name,cat in [('catchFG',4),('catch3FG',4),('pullFG',8),('pull3FG',8)]:
     top=bot=0.
     for zone,mask in masks[name]:
      aa=a[mask,:,cat+zone];mm=a[mask,:,cat+zone+1];w=np.minimum(aa[:,0],aa[:,1]);rr=np.divide(mm,aa,out=np.zeros_like(mm),where=aa>0);top+=np.sum(w*(rr[:,1]-rr[:,0]));bot+=w.sum()
     ans[name]=100*top/bot if bot else None
    den=a[:,:,0]+a[:,:,2];w=np.minimum(den[:,0],den[:,1])
    for name,cat in [('catchShare',4),('pullShare',8)]:
     num=a[:,:,cat]+a[:,:,cat+2];rr=np.divide(num,den,out=np.zeros_like(num),where=den>0);ans[name]=float(100*np.sum(w*(rr[:,1]-rr[:,0]))/w.sum()) if w.sum() else None
    return ans
   row={'season':s,'team':case['team'],'kind':kind,'organizer':anchor['name'],'subset':subset,'playedGames':int(on),'dnpGames':int(off),'eligiblePlayers':int(npids),'onMinusDnpPP':calc(both),'ci95':None,'limitation':'whole-game availability, not on-court effect; conditional on observed lineups, roles and opponent schedules'}
   if on and off and npids:
    a=np.zeros((len(dates),npids,2,12))
    for i,st in enumerate(state):a[i,:,st,:]=g[i]
    rng=np.random.default_rng(P['portability']['rng']);dist=defaultdict(list)
    for start in range(0,20000,100):
     ww=rng.multinomial(len(dates),np.ones(len(dates))/len(dates),size=100);sample=np.tensordot(ww,a,axes=1)
     for value in sample:
      for k,v in calc(value).items():
       if v is not None:dist[k].append(v)
    row['ci95']={k:np.quantile(v,[.025,.975]).tolist() for k,v in dist.items()}
   results.append(row)
 print('AVAILABILITY',s,case['team'],flush=True)
save('tracking-date-audit.json',audits);save('availability-results.json',results)

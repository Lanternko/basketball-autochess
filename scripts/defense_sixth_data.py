"""Shared strict, chronological stint dataset; team keys join/evaluate only."""
import json,hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import minimize
R=Path(__file__).resolve().parents[1];O=R/'reports/defense-sixth'
def read(f):return json.loads((R/f).read_text(encoding='utf-8'))
def save(f,d): (O/f).write_text(json.dumps(d,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def table(f):
 s=read(f)['data']['resultSets'][0];return [dict(zip(s['headers'],r)) for r in s['rowSet']]
def metrics(a,b):
 a=np.asarray(a);b=np.asarray(b);ac=a-a.mean();bc=b-b.mean()
 return dict(RMSE=float(np.sqrt(np.mean((ac-bc)**2))),correlation=float(np.corrcoef(a,b)[0,1]),calibrationSlope=float(bc@ac/(bc@bc)),SDRatio=float(np.std(b)/np.std(a)))
class Data:
 def __init__(self,k):
  self.k=k;self.league=read('data/season-league.json');self.pids=sorted({p['playerId'] for t in self.league['teams'] for p in t['roster']});self.pi={p:i for i,p in enumerate(self.pids)};self.P=len(self.pids)
  self.cards=read(f'reports/defense-sixth/card-values-pre{k}.json');self.cv={p['id']:p for p in self.cards['players']};self.bycard={(p['teamId'],p['id']):p for p in self.cards['players']}
  self.order={};counter={t['id']:0 for t in self.league['teams']};self.gmap={g['id']:g for g in self.league['schedule']}
  for g in self.league['schedule']:
   for t in [g['homeId'],g['awayId']]:counter[t]+=1;self.order[g['id'],t]=counter[t]
  self.box=table('data/season-source/player-games.json');self.team=table('data/season-source/team-games.json');self.tb={(r['GAME_ID'],r['TEAM_ID']):r for r in self.team}
  model=read(f'reports/defense-fourth/model-pre{k}/engine-signals.json' if k==41 else f'reports/defense-fifth/model-pre{k}/engine-signals.json');self.trainids=set(model['trainGames'])
  sample=read('reports/defense-b1/defensive-samples.json');exclude={x if isinstance(x,str) else x['id'] for key in ['lineupFailed','uncertainPossessionGames','counterMismatchGames','missingPbp'] for x in sample[key]}
  groups={}
  for line in (R/'reports/defense-b1/stints.jsonl').open(encoding='utf-8'):
   s=json.loads(line)
   if s['id'] in exclude:continue
   for side,t in enumerate(s['teams']):
    off=s['teams'][1-side];key=(s['id'],off['teamId'],tuple(sorted(off['players'])),tuple(sorted(t['players'])))
    if key not in groups:groups[key]=dict(id=s['id'],team=off['teamId'],opponent=t['teamId'],offense=off['players'],defense=t['players'],n=0,points=0,seconds=0)
    r=groups[key];r['n']+=t['defensivePossessionEnds'];r['points']+=t['opponent']['points'];r['seconds']+=s['seconds']
  self.zeroY=sum(r['points'] for r in groups.values() if r['n']==0);self.rows=[r for r in groups.values() if r['n']>0];N=len(self.rows)
  self.n=np.array([r['n'] for r in self.rows],float);self.y=np.array([r['points'] for r in self.rows],float);self.gids=np.array([r['id'] for r in self.rows]);self.tids=np.array([r['team'] for r in self.rows]);self.train=np.array([g in self.trainids for g in self.gids]);self.test=np.array([self.order[r['id'],r['team']]>k for r in self.rows])
  ii=[];jj=[]
  for i,r in enumerate(self.rows):ii.extend([i]*10);jj.extend([self.pi[p] for p in r['offense']]+[self.P+self.pi[p] for p in r['defense']])
  self.X=sparse.csr_matrix((np.full(len(ii),.2),(ii,jj)),shape=(N,2*self.P));self.A=sparse.hstack([np.ones((N,1)),self.X],format='csr')
  self.off=np.array([self.cv[p]['offense'] for p in self.pids]);self.defa=np.array([self.cv[p]['defenseAllowed'] for p in self.pids]);w=np.asarray(self.X[self.train,:self.P].T@self.n[self.train]).ravel();self.oc=float(w@self.off/w.sum());dw=np.asarray(self.X[self.train,self.P:].T@self.n[self.train]).ravel();self.dc=float(dw@self.defa/dw.sum());self.leaguePPP=float(self.y[self.train].sum()/self.n[self.train].sum())
  predicted=self.leaguePPP+(self.X[:,:self.P]@(self.off-self.oc)+self.X[:,self.P:]@(self.defa-self.dc))/100;self.offset=np.log(np.clip(predicted,.5,1.8))
  self.minutes=np.zeros(self.P);self.gp=np.zeros(self.P);self.stats={p:dict(MIN=0,GP=0,PTS=0,FGA=0,FGM=0,FG3A=0,FG3M=0,FTA=0,FTM=0,AST=0,TOV=0,OREB=0,DREB=0,STL=0,BLK=0,PF=0) for p in self.pids}
  for b in self.box:
   if self.order[b['GAME_ID'],b['TEAM_ID']]>k:continue
   s=self.stats[b['PLAYER_ID']];s['GP']+=1
   for key in s:
    if key!='GP':s[key]+=b.get(key,0)
  for p,i in self.pi.items():self.minutes[i]=self.stats[p]['MIN'];self.gp[i]=self.stats[p]['GP']
  self.mpg=self.minutes/np.maximum(1,self.gp)
def fit_count(d,mask,penalty,offset=None):
 a=d.A[mask];n=d.n[mask];y=d.y[mask];off=d.offset[mask] if offset is None else offset[mask];w=np.full(a.shape[1],float(penalty));w[0]=0
 def fg(b):
  e=np.clip(off+a@b,-8,8);mu=n*np.exp(e);return (np.sum(mu-y*e)+.5*np.dot(w*b,b))/len(y),np.asarray(a.T@(mu-y)+w*b).ravel()/len(y)
 f=minimize(fg,np.zeros(a.shape[1]),jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-11,'gtol':1e-6})
 return f.x,dict(converged=bool(f.success),iterations=int(f.nit),gradient=float(abs(f.jac).max()))
def choose(d,mask,offset=None):
 folds={g:int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%3 for g in set(d.gids[mask])};grid=[3,10,30,100,300,1000,3000];scores={p:0. for p in grid}
 for f in range(3):
  tm=mask&np.array([folds.get(g,-1)!=f for g in d.gids]);vm=mask&np.array([folds.get(g,-1)==f for g in d.gids])
  for p in grid:
   b,_=fit_count(d,tm,p,offset);off=d.offset if offset is None else offset;e=np.clip(off[vm]+d.A[vm]@b,-8,8);scores[p]+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
 p=min(scores,key=scores.get);b,diag=fit_count(d,mask,p,offset);return b,dict(selected=p,loss=scores,folds=3,diagnostics=diag)

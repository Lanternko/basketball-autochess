"""Player-only scoring model. No team columns, wins, or later outcomes.
Cross-validation rebuilds box priors inside each game fold.
"""
from defense_sixth_data import *
from scipy.special import expit
import sys,time
k=int(sys.argv[1]);d=Data(k);start=time.time();P=d.P
def features(allowed,role):
 stats=np.zeros((P,13));keys=['MIN','PTS','FGA','FG3A','FTA','AST','TOV','OREB','DREB','STL','BLK','PF','GP']
 for b in d.box:
  if b['GAME_ID'] not in allowed:continue
  i=d.pi[b['PLAYER_ID']];stats[i,:12]+=np.array([b.get(z,0) for z in keys[:12]]);stats[i,12]+=1
 n=stats[:,0]/48*100;mean=stats[:,1:12].sum(axis=0)/max(1,n.sum());rates=(stats[:,1:12]+200*mean)/(n[:,None]+200)
 # Shared full-league box prior, no lineup identity or team intercept.
 z=(rates-mean)/(np.std(rates,axis=0)+1e-6);pos=np.array([[float(d.cv[p]['pos']==x) for x in ['PG','SG','SF','PF','C']] for p in d.pids])
 minutes=stats[:,0]/np.maximum(1,stats[:,12]);bins=np.digitize(minutes,[10,20,30]);rr=np.column_stack([bins==b for b in range(4)]).astype(float)
 fo=np.column_stack((z[:,[0,1,2,3,4,5,6]],pos,*([rr] if role else [])));fd=np.column_stack((z[:,[7,8,9,10]],pos,*([rr] if role else [])))
 a=np.column_stack((np.ones(len(d.rows)),d.X[:,:P]@fo,d.X[:,P:]@fd));return a,fo,fd,stats
def prior_fit(a,mask):
 n=d.n[mask];y=d.y[mask];x=a[mask];w=np.full(x.shape[1],3.);w[0]=0
 def fg(b):
  e=np.clip(x@b,-8,8);mu=n*np.exp(e);return (np.sum(mu-y*e)+.5*np.dot(w*b,b))/len(y),(x.T@(mu-y)+w*b)/len(y)
 r=minimize(fg,np.zeros(x.shape[1]),jac=True,method='L-BFGS-B',options={'maxiter':500,'ftol':1e-11,'gtol':1e-6});return r.x,dict(converged=bool(r.success),gradient=float(abs(r.jac).max()))
fold={g:int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%3 for g in d.trainids};grid=[3,10,30,100,300,1000,3000];models={}
for role in [False,True]:
 scores={p:0. for p in grid};prior_loss=0.;folds=[]
 for f in range(3):
  allowed={g for g in d.trainids if fold[g]!=f};tm=np.array([g in allowed for g in d.gids]);vm=d.train&np.array([fold.get(g,-1)==f for g in d.gids]);a,_,_,_=features(allowed,role);beta,_=prior_fit(a,tm);off=a@beta;e=np.clip(off[vm],-8,8);prior_loss+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
  for l in grid:
   b,_=fit_count(d,tm,l,off);e=np.clip(off[vm]+d.A[vm]@b,-8,8);scores[l]+=float(np.sum(d.n[vm]*np.exp(e)-d.y[vm]*e))
 selected=min(scores,key=scores.get);a,fo,fd,stats=features(d.trainids,role);beta,dp=prior_fit(a,d.train);offset=a@beta;b,dr=fit_count(d,d.train,selected,offset);no=fo.shape[1]
 offp=fo@beta[1:1+no];defp=fd@beta[1+no:];models['role' if role else 'plain']=dict(priorOffense=offp.tolist(),priorDefenseAllowed=defp.tolist(),offenseResidual=b[1:1+P].tolist(),defenseResidual=b[1+P:].tolist(),intercept=float(beta[0]+b[0]),priorIntercept=float(beta[0]),priorCVLoss=prior_loss,CV={'selected':selected,'loss':scores},diagnostics={'prior':dp,'residual':dr},roleFeatures=role)
 print('FIT',k,role,selected,round(time.time()-start,1),flush=True)
 train_pred=np.exp(np.clip(offset+d.A@b,-8,8));teammetric=[]
 for t in d.league['teams']:
  m=d.train&(d.tids==t['id']);teammetric.append(dict(id=t['id'],observed=float(d.y[m].sum()/d.n[m].sum()*100),predicted=float(d.n[m]@train_pred[m]/d.n[m].sum()*100)))
 models['role' if role else 'plain']['trainingTeamOffense']=teammetric
selected_role=models['role']['priorCVLoss']<models['plain']['priorCVLoss']
save(f'model-pre{k}.json',dict(cutoff=k,players=d.pids,trainGames=sorted(d.trainids),minutes=d.minutes.tolist(),leaguePPP=d.leaguePPP,models=models,trainingSelectRole=selected_role,zeroExposurePointsDropped=d.zeroY,method='Simultaneous five-offense/five-defense Poisson points/count model; individual pre-cutoff box prior, optional MPG/position role prior, player residual ridge selected by three game folds. Each fold rebuilds all personal prior features from fold-training boxes. No team or win column. Card translation separately inverts existing unchanged engine attributes. No post-cutoff outcome used.',sources={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['scripts/estimate_defense_sixth.py','scripts/defense_sixth_data.py','reports/defense-b1/stints.jsonl']}))

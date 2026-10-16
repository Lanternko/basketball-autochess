import json,sys,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit,logit
from scipy.optimize import minimize
from scipy.sparse.linalg import spsolve
ROOT=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={}
ZONES=['ra','paint','mid','corner','arc'];BRANCHES=['three','paintGivenTwo','raGivenPaint','cornerGivenThree']

def data(season):
 if season in cache:return cache[season]
 doc=read(ROOT/f'{season}-fga-data.json');ids=[p['playerId'] for p in doc['players']];lookup={p:i for i,p in enumerate(ids)};k=len(ids);zs=[]
 for zi,z in enumerate(ZONES):
  rows=[r for r in doc['rows'] if r[2]==zi];own=np.array([lookup[r[3]] for r in rows]);ds=np.array([[lookup[p] for p in r[5]] for r in rows]);n=len(rows)
  matrix=sparse.csr_matrix((np.ones(n*7),(np.repeat(np.arange(n),7),np.column_stack([own,k+ds,np.full(n,2*k)]).ravel())),shape=(n,2*k+1))
  blocked=sparse.csr_matrix(([b for r in rows for p,b in r[8]],([i for i,r in enumerate(rows) for p,b in r[8]],[lookup[p] for r in rows for p,b in r[8]])),shape=(n,k))
  zs.append({'x':matrix,'own':own,'ds':ds,'n':np.array([r[6] for r in rows],float),'b':np.array([r[7] for r in rows],float),'fold':np.array([r[1] for r in rows]),'blocks':blocked})
 groups={}
 for r in doc['rows']:
  key=(r[0],r[1],r[3],tuple(r[5]));groups.setdefault(key,np.zeros(5))[r[2]]+=r[6]
 keys=list(groups);counts=np.array(list(groups.values()));own=np.array([lookup[r[2]] for r in keys]);ds=np.array([[lookup[p] for p in r[3]] for r in keys]);n=len(keys)
 matrix=sparse.csr_matrix((np.ones(n*7),(np.repeat(np.arange(n),7),np.column_stack([own,k+ds,np.full(n,2*k)]).ravel())),shape=(n,2*k+1))
 result={'doc':doc,'ids':ids,'k':k,'zones':zs,'choice':{'x':matrix,'counts':counts,'fold':np.array([r[1] for r in keys])}};cache[season]=result;return result

def prepare(d,raw,fold,sigma,feature,choice=False):
 k=d['k'];train=(raw['n']>0)&(np.ones(len(raw['n']),bool) if fold is None else raw['fold']!=fold);test=(raw['n']>0)&(np.ones(len(raw['n']),bool) if fold is None else raw['fold']==fold)
 n=raw['n'][train];b=raw['b'][train];mu=b.sum()/n.sum();minutes=sum(v for _,f,ps in d['doc']['minutes'] if fold is None or f!=fold for _,v in ps);nu=.5 if choice else 60*n.sum()/minutes
 x=raw['x'] if sigma else raw['x'][:,list(range(k))+[2*k]];features=np.zeros(k)
 if feature:
  opportunities=np.asarray(raw['x'][train,k:2*k].T@n);blocks=np.asarray(raw['blocks'][train].sum(axis=0)).ravel();league=blocks.sum()/opportunities.sum()
  features=10*((blocks+200*league)/(opportunities+200)-league)
  column=np.asarray(raw['x'][:,k:2*k]@features).reshape(-1,1);x=sparse.hstack([x[:,:-1],column,x[:,-1]],format='csr')
 return {'x':x,'train':train,'test':test,'n':n,'b':b,'mu':mu,'nu':nu,'base':float(logit(mu)),'k':k,'sigma':sigma,'feature':feature,'features':features}

def loss(params,t,withHessian=False):
 x=t['x'][t['train']];k=t['k'];eta=x@params;p=expit(eta);res=t['n']*p-t['b'];a=params[:k];q=expit(t['base']+a)
 value=float(np.sum(t['n']*np.logaddexp(0,eta)-t['b']*eta)+t['nu']*np.sum(np.logaddexp(0,t['base']+a)-t['mu']*(t['base']+a)))
 grad=np.asarray(x.T@res);grad[:k]+=t['nu']*(q-t['mu']);diag=np.zeros(len(params));diag[:k]=t['nu']*q*(1-q)
 if t['sigma']:
  delta=params[k:2*k];value+=float(delta@delta)/(2*t['sigma']**2);grad[k:2*k]+=delta/t['sigma']**2;diag[k:2*k]=1/t['sigma']**2
 if t['feature']:value+=params[-2]**2/2;grad[-2]+=params[-2];diag[-2]=1
 if withHessian:return (x.T@x.multiply((t['n']*p*(1-p))[:,None])+sparse.diags(diag)).tocsc()
 return value,grad

def fit(t):
 k=t['k'];own=t['x'][t['train'],:k];n=np.asarray(own.T@t['n']);b=np.asarray(own.T@t['b']);initial=np.zeros(t['x'].shape[1]);initial[:k]=logit((b+t['nu']*t['mu'])/(n+t['nu']))-t['base'];initial[-1]=t['base'];total=t['n'].sum()
 def obj(p):v,g=loss(p,t);return v/total,g/total
 r=minimize(obj,initial,jac=True,method='L-BFGS-B',options={'maxiter':1500,'ftol':1e-15,'gtol':2e-11,'maxcor':25,'maxls':50});p=r.x.copy()
 for _ in range(8):
  v,g=loss(p,t)
  if abs(g).max()<1e-5:break
  step=spsolve(loss(p,t,True),-g);scale=1
  while scale>2**-20:
   trial=p+scale*step
   if loss(trial,t)[0]<=v+1e-9:break
   scale/=2
  assert scale>2**-20;p=trial
 v,g=loss(p,t);assert abs(g).max()<.001
 return p,{'maxGradient':float(abs(g).max()),'penalizedNll':v,'iterations':r.nit}

def path(job):
 kind,s,sigma,feature,fold=job;return ROOT/'fits'/f'{kind}-{s}-sigma{sigma:g}-feature{int(feature)}-fold{fold}.json'

def task(job):
 if path(job).exists():return str(path(job))
 kind,s,sigma,feature,fold=job;d=data(s);results=[]
 for zi,name in enumerate(ZONES if kind=='make' else BRANCHES):
  if kind=='make':raw=d['zones'][zi]
  else:
   c=d['choice'];v=c['counts'];a=v.sum(axis=1) if name=='three' else v[:,:3].sum(axis=1) if name=='paintGivenTwo' else v[:,:2].sum(axis=1) if name=='raGivenPaint' else v[:,3:].sum(axis=1)
   b=v[:,3:].sum(axis=1) if name=='three' else v[:,:2].sum(axis=1) if name=='paintGivenTwo' else v[:,0] if name=='raGivenPaint' else v[:,3]
   raw={'x':c['x'],'n':a,'b':b,'fold':c['fold']}
  t=prepare(d,raw,fold,sigma,feature,kind=='choice');params,diagnostic=fit(t);eta=t['x'][t['test']]@params
  n=raw['n'][t['test']];b=raw['b'][t['test']];nll=float(np.sum(n*np.logaddexp(0,eta)-b*eta));residual=params[d['k']:2*d['k']] if sigma else np.zeros(d['k']);slope=float(params[-2]) if feature else 0
  results.append({'name':name,'intercept':float(params[-1]),'shooterLogits':params[:d['k']].tolist(),'defenderLogits':(residual+slope*t['features']).tolist(),'defenderResiduals':residual.tolist(),'blockFeatures':t['features'].tolist(),'blockSlope':slope,'trainingTrials':int(t['n'].sum()),'testTrials':int(n.sum()),'nll':nll,'fit':diagnostic})
 result={'kind':kind,'season':s,'sigma':sigma,'feature':feature,'fold':fold,'playerIds':d['ids'],'models':results};path(job).write_text(json.dumps(result),encoding='utf-8');return str(path(job))

def jobs_run(jobs):
 pending=[j for j in jobs if not path(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in pending]),1):
   f.result()
   if i%10==0 or i==len(pending):print(json.dumps({'done':i,'total':len(pending)}),flush=True)

if __name__=='__main__':
 (ROOT/'fits').mkdir(exist_ok=True);protocol=read(ROOT/'protocol.json');seasons=protocol['seasons'];kind=sys.argv[1];stage=sys.argv[2]
 grid=[(s,f) for s in protocol['makeGrid']['sigma'] for f in [False,True]] if kind=='make' else [(s,False) for s in protocol['choiceGrid']['sigma']]
 if stage=='select':
  jobs_run([(kind,s,a,b,f) for s in seasons[:3] for a,b in grid for f in range(5)])
  scores=[];selected={}
  for name in ZONES if kind=='make' else BRANCHES:
   table=[]
   for sigma,feature in grid:
    models=[next(m for m in read(path((kind,s,sigma,feature,f)))['models'] if m['name']==name) for s in seasons[:3] for f in range(5)]
    table.append({'name':name,'sigma':sigma,'feature':feature,'nll':sum(m['nll'] for m in models),'trials':sum(m['testTrials'] for m in models)})
   best=min(table,key=lambda v:(v['nll']/v['trials'],v['feature'],v['sigma']));selected[name]={k:best[k] for k in ['sigma','feature']};scores+=table
  (ROOT/f'{kind}-selection.json').write_text(json.dumps({'selected':selected,'scores':scores,'targetExcluded':True},indent=2),encoding='utf-8');print(json.dumps({'kind':kind,'selected':selected}),flush=True)
 else:
  selected=read(ROOT/f'{kind}-selection.json')['selected'];pairs={(v['sigma'],v['feature']) for v in selected.values()}|{(0,False)}
  jobs_run([(kind,s,a,b,None) for s in seasons for a,b in pairs]+[(kind,'2025-26',a,b,f) for a,b in pairs for f in range(5)])
  results=[]
  for s in seasons:
   models=[]
   for name,p in selected.items():
    d=read(path((kind,s,p['sigma'],p['feature'],None)));models.append(next(m for m in d['models'] if m['name']==name))
   results.append({'season':s,'playerIds':d['playerIds'],'models':models})
  (ROOT/f'{kind}-fit.json').write_text(json.dumps({'selected':selected,'seasons':results}),encoding='utf-8')

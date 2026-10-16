import json,sys,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit,logit
from scipy.sparse.linalg import spsolve
ROOT=Path('reports/player-impact-v46');SOURCE=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={}
def data(season):
 if season in cache:return cache[season]
 doc=read(SOURCE/f'{season}-fga-data.json');ids=[p['playerId'] for p in doc['players']];lookup={p:i for i,p in enumerate(ids)};k=len(ids);rows=[r for r in doc['rows'] if r[2]<2];n=len(rows)
 own=np.array([lookup[r[3]] for r in rows]);zone=np.array([r[2] for r in rows]);ds=np.array([[lookup[p] for p in r[5]] for r in rows]);trial=np.array([r[6] for r in rows],float);made=np.array([r[7] for r in rows],float);fold=np.array([r[1] for r in rows])
 defense=sparse.csr_matrix((np.ones(n*5),(np.repeat(np.arange(n),5),ds.ravel())),shape=(n,k));shooter=sparse.csr_matrix((np.ones(n),(np.arange(n),zone*k+own)),shape=(n,2*k));intercept=sparse.csr_matrix((np.ones(n),(np.arange(n),zone)),shape=(n,2));blocks=sparse.csr_matrix(([b for r in rows for p,b in r[8]],([i for i,r in enumerate(rows) for p,b in r[8]],[lookup[p] for r in rows for p,b in r[8]])),shape=(n,k))
 minutes=np.zeros(k)
 for gid,f,ps in doc['minutes']:
  for p,m in ps:minutes[lookup[p]]+=m
 d={'doc':doc,'ids':ids,'k':k,'rows':rows,'own':own,'zone':zone,'ds':ds,'n':trial,'b':made,'fold':fold,'defense':defense,'shooter':shooter,'intercept':intercept,'blocks':blocks,'minutes':minutes};cache[season]=d;return d
def prepare(d,common,contrast,fold):
 k=d['k'];train=np.ones(len(d['n']),bool) if fold is None else d['fold']!=fold;test=np.ones(len(d['n']),bool) if fold is None else d['fold']==fold;features=np.zeros((2,k));mu=[];nu=[];featureColumns=[]
 totalMinutes=sum(m for gid,f,ps in d['doc']['minutes'] if fold is None or f!=fold for p,m in ps)
 for z in range(2):
  mask=train&(d['zone']==z);n=d['n'][mask];b=d['b'][mask];mu.append(b.sum()/n.sum());nu.append(60*n.sum()/totalMinutes)
  opportunities=np.asarray(d['defense'][mask].T@n);blocks=np.asarray(d['blocks'][mask].sum(axis=0)).ravel();league=blocks.sum()/opportunities.sum();features[z]=10*((blocks+200*league)/(opportunities+200)-league);featureColumns.append(np.asarray(d['defense']@features[z])*(d['zone']==z))
 sign=np.where(d['zone']==0,1.,-1.);pieces=[d['shooter'],d['defense']];precision=np.r_[np.zeros(2*k),np.full(k,1/common**2)]
 if contrast:pieces.append(d['defense'].multiply(sign[:,None]));precision=np.r_[precision,np.full(k,1/contrast**2)]
 pieces.extend([sparse.csr_matrix(np.column_stack(featureColumns)),d['intercept']]);precision=np.r_[precision,np.ones(2),np.zeros(2)];x=sparse.hstack(pieces,format='csr');mu=np.repeat(mu,k);nu=np.repeat(nu,k)
 return {'x':x,'train':train,'test':test,'mu':mu,'nu':nu,'base':logit(mu),'precision':precision,'features':features,'k':k,'common':common,'contrast':contrast,'n':d['n'][train],'b':d['b'][train]}
def loss(p,t,hessian=False):
 x=t['x'][t['train']];eta=x@p;q=expit(eta);a=p[:2*t['k']];prior=expit(t['base']+a);res=t['n']*q-t['b'];grad=np.asarray(x.T@res)+t['precision']*p;grad[:len(a)]+=t['nu']*(prior-t['mu'])
 value=float(np.sum(t['n']*np.logaddexp(0,eta)-t['b']*eta)+np.sum(t['nu']*(np.logaddexp(0,t['base']+a)-t['mu']*(t['base']+a)))+.5*np.sum(t['precision']*p*p))
 if hessian:
  diag=t['precision'].copy();diag[:len(a)]+=t['nu']*prior*(1-prior);return (x.T@x.multiply((t['n']*q*(1-q))[:,None])+sparse.diags(diag)).tocsc()
 return value,grad
def fit(t):
 k=t['k'];x=t['x'][t['train']];own=x[:,:2*k];n=np.asarray(own.T@t['n']);b=np.asarray(own.T@t['b']);p=np.zeros(x.shape[1]);p[:2*k]=logit((b+t['nu']*t['mu'])/(n+t['nu']))-t['base'];p[-2:]=[t['base'][0],t['base'][k]]
 for iteration in range(40):
  value,g=loss(p,t)
  if abs(g).max()<1e-5:break
  step=spsolve(loss(p,t,True),-g);scale=1.
  while scale>2**-25:
   trial=p+scale*step
   if loss(trial,t)[0]<=value+1e-9:break
   scale/=2
  assert scale>2**-25;p=trial
 value,g=loss(p,t);assert np.isfinite(p).all() and abs(g).max()<.001,(iteration,abs(g).max());return p,{'iterations':iteration+1,'maxGradient':float(abs(g).max()),'penalizedNLL':value}
def path(job):
 season,common,contrast,fold=job;return ROOT/'fits'/f'{season}-common{common:g}-contrast{contrast:g}-fold{fold}.json'
def task(job):
 if path(job).exists():return str(path(job))
 season,common,contrast,fold=job;d=data(season);t=prepare(d,common,contrast,fold);p,diagnostics=fit(t);k=d['k'];test=t['test'];eta=t['x'][test]@p;pred=d['n'][test]*expit(eta);nll=d['n'][test]*np.logaddexp(0,eta)-d['b'][test]*eta;commonDef=p[2*k:3*k];contrastDef=p[3*k:4*k] if contrast else np.zeros(k);models=[]
 for z,name in enumerate(['ra','paint']):
  mask=d['zone'][test]==z;effective=commonDef+(1 if z==0 else -1)*contrastDef+p[-4+z]*t['features'][z]
  models.append({'name':name,'intercept':float(p[-2+z]),'shooterLogits':p[z*k:(z+1)*k].tolist(),'defenderLogits':effective.tolist(),'commonDefender':commonDef.tolist(),'contrastDefender':contrastDef.tolist(),'blockFeatures':t['features'][z].tolist(),'blockSlope':float(p[-4+z]),'nll':float(nll[mask].sum()),'testTrials':int(d['n'][test][mask].sum())})
 counts=np.column_stack([np.bincount(d['ds'][test].ravel(),weights=np.repeat(v,5),minlength=k) for v in [d['n'][test],d['b'][test],pred]])
 result={'season':season,'commonSigma':common,'contrastSigma':contrast,'fold':fold,'playerIds':d['ids'],'models':models,'onCounts':counts.tolist(),'fit':diagnostics,'sourceDataSHA256':hashlib.sha256((SOURCE/f'{season}-fga-data.json').read_bytes()).hexdigest()};tmp=path(job).with_suffix('.tmp');tmp.write_text(json.dumps(result),encoding='utf-8');tmp.replace(path(job));return str(path(job))
def run(jobs):
 pending=[j for j in jobs if not path(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in pending]),1):
   f.result()
   if i%5==0 or i==len(pending):print(json.dumps({'done':i,'total':len(pending)}),flush=True)
if __name__=='__main__':
 (ROOT/'fits').mkdir(parents=True,exist_ok=True);protocol=read(ROOT/'protocol.json');seasons=protocol['seasons'];grid=[(a,b) for a in protocol['grid']['commonSigma'] for b in protocol['grid']['contrastSigma']];stage=sys.argv[1]
 if stage=='probe':run([(seasons[0],.05,0,0)])
 elif stage=='select':
  run([(s,a,b,f) for s in seasons[:3] for a,b in grid for f in range(5)]);table=[]
  for a,b in grid:
   cells=[]
   for s in seasons[:3]:
    d=data(s);fs=[read(path((s,a,b,f))) for f in range(5)];counts=sum(np.array(f['onCounts']) for f in fs);mask=(d['minutes']>=500)&(counts[:,0]>=100);err=100*(counts[mask,2]-counts[mask,1])/counts[mask,0];cells.append({'season':s,'mae':float(d['minutes'][mask]@abs(err)/d['minutes'][mask].sum()),'nll':sum(m['nll'] for f in fs for m in f['models']),'trials':sum(m['testTrials'] for f in fs for m in f['models'])})
   table.append({'commonSigma':a,'contrastSigma':b,'meanPlayerPaintMAE':float(np.mean([c['mae'] for c in cells])),'nll':sum(c['nll'] for c in cells),'cells':cells})
  best=min(table,key=lambda c:(c['meanPlayerPaintMAE'],c['nll'],c['contrastSigma'],c['commonSigma']));(ROOT/'selection.json').write_text(json.dumps({'selected':{k:best[k] for k in ['commonSigma','contrastSigma']},'table':table,'targetExcluded':True},indent=2),encoding='utf-8');print(json.dumps({'selected':best}),flush=True)
 elif stage=='full':
  c=read(ROOT/'selection.json')['selected'];a=c['commonSigma'];b=c['contrastSigma'];run([(s,a,b,None) for s in seasons]+[('2025-26',a,b,f) for f in range(5)]);old=read(SOURCE/'make-fit.json');output=[]
  for s in seasons:
   f=read(path((s,a,b,None)));prior=next(v for v in old['seasons'] if v['season']==s);assert f['playerIds']==prior['playerIds'];output.append({'season':s,'playerIds':f['playerIds'],'models':f['models']+[m for m in prior['models'] if m['name'] not in ['ra','paint']]})
  (ROOT/'make-fit.json').write_text(json.dumps({'selected':c,'seasons':output}),encoding='utf-8')

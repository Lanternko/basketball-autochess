"""Training-only defender offsets; jointly estimate shooter and four teammates."""
import json,hashlib,sys
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit,logit
from scipy.sparse.linalg import spsolve
R=Path('reports/player-impact-v48');S=Path('reports/player-impact-v45');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));cache={};names=['ra','paint','mid']
def data(season):
 if season in cache:return cache[season]
 doc=read(S/f'{season}-fga-data.json');ids=[p['playerId'] for p in doc['players']];idx={p:i for i,p in enumerate(ids)};k=len(ids);minutes=np.zeros(k);sides=defaultdict(dict)
 for gid,f,ps in doc['minutes']:
  for pid,m in ps:minutes[idx[pid]]+=m
 source=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl');valid={g for g,f,ps in doc['minutes']}
 with source.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in valid:continue
   for team in st['teams']:
    for pid in team['players']:sides[st['id']][pid]=team['teamId']
 groups=sorted({(gid,tid) for gid,ps in sides.items() for tid in ps.values()});gi={v:i for i,v in enumerate(groups)};ei=[];ej=[]
 for gid,f,ps in doc['minutes']:
  for pid,m in ps:
   if m>0:ei.append(idx[pid]);ej.append(gi[(gid,sides[gid][pid])])
 exposure=sparse.csr_matrix((np.ones(len(ei)),(ei,ej)),shape=(k,len(groups)));zones=[]
 for zi,z in enumerate(names):
  rows=[r for r in doc['rows'] if r[2]==zi];n=len(rows);own=np.array([idx[r[3]] for r in rows]);mates=np.array([[idx[p] for p in r[4] if p!=r[3]] for r in rows]);ds=np.array([[idx[p] for p in r[5]] for r in rows]);assert mates.shape==(n,4)
  shooter=sparse.csr_matrix((np.ones(n),(np.arange(n),own)),shape=(n,k));team=sparse.csr_matrix((np.ones(n*4),(np.repeat(np.arange(n),4),mates.ravel())),shape=(n,k));defense=sparse.csr_matrix((np.ones(n*5),(np.repeat(np.arange(n),5),ds.ravel())),shape=(n,k));group=np.array([gi[(r[0],sides[r[0]][r[3]])] for r in rows]);groupmatrix=sparse.csr_matrix((np.ones(n),(group,np.arange(n))),shape=(len(groups),n))
  zones.append({'rows':rows,'own':own,'mates':mates,'ds':ds,'shooter':shooter,'team':team,'defense':defense,'groupmatrix':groupmatrix,'n':np.array([r[6] for r in rows],float),'b':np.array([r[7] for r in rows],float),'fold':np.array([r[1] for r in rows])})
 d={'doc':doc,'ids':ids,'k':k,'minutes':minutes,'exposure':exposure,'zones':zones,'stintsSHA256':hashlib.sha256(source.read_bytes()).hexdigest()};cache[season]=d;return d
def base(season,fold,z,ids):
 if z in ['ra','paint']:file=Path('reports/player-impact-v46/fits')/f'{season}-common0.1-contrast0.05-fold{fold}.json'
 else:file=S/'fits'/f'make-{season}-sigma0.025-feature1-fold{fold}.json'
 doc=read(file);assert doc['playerIds']==ids;return next(m for m in doc['models'] if m['name']==z),file
def prepare(d,zi,sigma,fold):
 raw=d['zones'][zi];k=d['k'];mask=np.ones(len(raw['n']),bool) if fold is None else raw['fold']!=fold;test=np.ones(len(raw['n']),bool) if fold is None else ~mask;model,file=base(d['doc']['season'],fold,names[zi],d['ids']);offset=np.asarray(raw['defense']@np.array(model['defenderLogits']));pieces=[raw['shooter']]
 if sigma:pieces.append(raw['team'])
 pieces.append(sparse.csr_matrix(np.ones((len(mask),1))));x=sparse.hstack(pieces,format='csr');n=raw['n'][mask];b=raw['b'][mask];mu=b.sum()/n.sum();mins=sum(m for gid,f,ps in d['doc']['minutes'] if fold is None or f!=fold for pid,m in ps);nu=60*n.sum()/mins;precision=np.r_[np.zeros(k),np.full(k,1/sigma**2) if sigma else [],0.];initial=np.r_[model['shooterLogits'],np.zeros(k) if sigma else [],model['intercept']]
 return {'x':x[mask],'allx':x,'n':n,'b':b,'offset':offset[mask],'alloffset':offset,'k':k,'mu':mu,'nu':nu,'base':logit(mu),'precision':precision,'initial':initial,'test':test,'raw':raw,'model':model,'basePath':file}
def loss(p,t,hessian=False):
 eta=t['x']@p+t['offset'];q=expit(eta);a=p[:t['k']];prior=expit(t['base']+a);g=np.asarray(t['x'].T@(t['n']*q-t['b']))+t['precision']*p;g[:t['k']]+=t['nu']*(prior-t['mu']);v=float(np.sum(t['n']*np.logaddexp(0,eta)-t['b']*eta)+t['nu']*np.sum(np.logaddexp(0,t['base']+a)-t['mu']*(t['base']+a))+.5*np.sum(t['precision']*p*p))
 if hessian:
  diag=t['precision'].copy();diag[:t['k']]+=t['nu']*prior*(1-prior);return (t['x'].T@t['x'].multiply((t['n']*q*(1-q))[:,None])+sparse.diags(diag)).tocsc()
 return v,g
def fit(t):
 p=t['initial'].copy()
 for iteration in range(35):
  v,g=loss(p,t)
  if abs(g).max()<1e-5:break
  step=spsolve(loss(p,t,True),-g);scale=1.
  while scale>2**-24:
   new=p+scale*step
   if loss(new,t)[0]<=v+1e-9:break
   scale/=2
  assert scale>2**-24;p=new
 v,g=loss(p,t);assert abs(g).max()<.001 and np.isfinite(p).all();return p,{'iterations':iteration+1,'maxGradient':float(abs(g).max()),'penalizedNLL':v}
def path(job):
 s,sigma,fold=job;return R/'fits'/f'{s}-sigma{sigma:g}-fold{fold}.json'
def task(job):
 if path(job).exists():return str(path(job))
 season,sigma,fold=job;d=data(season);models=[]
 for zi,z in enumerate(names):
  t=prepare(d,zi,sigma,fold);p,diag=fit(t);test=t['test'];raw=t['raw'];eta=t['allx'][test]@p+t['alloffset'][test];n=raw['n'][test];b=raw['b'][test];pred=n*expit(eta);nll=float(np.sum(n*np.logaddexp(0,eta)-b*eta));k=d['k'];counter={}
  for label,values in [('actualAttempts',n),('actualMakes',b),('predictedMakes',pred)]:
   whole=np.zeros(len(raw['n']));whole[test]=values;on=np.asarray((raw['shooter']+raw['team']).T@whole);mates=np.asarray(raw['team'].T@whole);off=np.asarray(d['exposure']@(raw['groupmatrix']@whole))-on;counter[label]={'on':on.tolist(),'teammates':mates.tolist(),'off':off.tolist()};assert abs(on.sum()-5*values.sum())<1e-7 and abs(mates.sum()-4*values.sum())<1e-7
  models.append({'name':z,'intercept':float(p[-1]),'shooterLogits':p[:k].tolist(),'teammateLogits':p[k:2*k].tolist() if sigma else np.zeros(k).tolist(),'baseDefenderLogits':t['model']['defenderLogits'],'baseModelPath':t['basePath'].as_posix(),'baseModelSHA256':hashlib.sha256(t['basePath'].read_bytes()).hexdigest(),'nll':nll,'testAttempts':int(n.sum()),'counters':counter,'fit':diag})
 result={'season':season,'sigma':sigma,'fold':fold,'playerIds':d['ids'],'models':models,'sourceDataSHA256':hashlib.sha256((S/f'{season}-fga-data.json').read_bytes()).hexdigest(),'stintsSHA256':d['stintsSHA256']};tmp=path(job).with_suffix('.tmp');tmp.write_text(json.dumps(result),encoding='utf-8');tmp.replace(path(job));return str(path(job))
def run(jobs):
 pending=[j for j in jobs if not path(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in pending]),1):
   f.result()
   if i%5==0 or i==len(pending):print(json.dumps({'fitsDone':i,'total':len(pending)}),flush=True)
if __name__=='__main__':
 (R/'fits').mkdir(parents=True,exist_ok=True);p=read(R/'protocol.json');seasons=p['seasons'];stage=sys.argv[1]
 if stage=='select':
  run([(s,a,f) for s in seasons[:3] for a in p['teammateSigmaGrid'] for f in range(5)]);table=[]
  for sigma in p['teammateSigmaGrid']:
   cells=[]
   for s in seasons[:3]:
    fs=[read(path((s,sigma,f))) for f in range(5)];nll=sum(m['nll'] for f in fs for m in f['models']);n=sum(m['testAttempts'] for f in fs for m in f['models']);cells.append({'season':s,'nll':nll,'attempts':n,'nllPerAttempt':nll/n})
   table.append({'sigma':sigma,'meanNllPerAttempt':float(np.mean([c['nllPerAttempt'] for c in cells])),'cells':cells})
  best=min(table,key=lambda c:(c['meanNllPerAttempt'],c['sigma']));(R/'selection.json').write_text(json.dumps({'selectedSigma':best['sigma'],'targetExcluded':True,'table':table},indent=2),encoding='utf-8');print(json.dumps({'selected':best}),flush=True)
 elif stage=='full':
  sigma=read(R/'selection.json')['selectedSigma'];run([(s,sigma,None) for s in seasons]+[(seasons[-1],a,f) for a in set([sigma,0]) for f in range(5)]);output=[]
  for s in seasons:
   f=read(path((s,sigma,None)));output.append({'season':s,'playerIds':f['playerIds'],'models':[{k:v for k,v in m.items() if k not in ['counters']} for m in f['models']]})
  (R/'make-fit.json').write_text(json.dumps({'selectedSigma':sigma,'seasons':output}),encoding='utf-8')

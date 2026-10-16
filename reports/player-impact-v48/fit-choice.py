import json,hashlib,sys,importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
from scipy.special import expit,logit
R=Path('reports/player-impact-v48');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));branches=['paintGivenTwo','raGivenPaint'];cache={}
spec=importlib.util.spec_from_file_location('make_solver',R/'fit.py');solver=importlib.util.module_from_spec(spec);spec.loader.exec_module(solver)
def data(season):
 if season in cache:return cache[season]
 doc=read(f'reports/player-impact-v45/{season}-fga-data.json');ids=[p['playerId'] for p in doc['players']];idx={p:i for i,p in enumerate(ids)};groups={}
 for gid,f,zi,pid,own,ds,n,m,blocks in doc['rows']:
  if zi<3:groups.setdefault((gid,f,pid,tuple(own),tuple(ds)),np.zeros(3))[zi]+=n
 keys=list(groups);counts=np.array(list(groups.values()));k=len(ids);n=len(keys);own=np.array([idx[r[2]] for r in keys]);mates=np.array([[idx[p] for p in r[3] if p!=r[2]] for r in keys]);defenders=np.array([[idx[p] for p in r[4]] for r in keys]);shooter=sparse.csr_matrix((np.ones(n),(np.arange(n),own)),shape=(n,k));team=sparse.csr_matrix((np.ones(n*4),(np.repeat(np.arange(n),4),mates.ravel())),shape=(n,k));defense=sparse.csr_matrix((np.ones(n*5),(np.repeat(np.arange(n),5),defenders.ravel())),shape=(n,k));d={'doc':doc,'ids':ids,'k':k,'keys':keys,'counts':counts,'own':own,'mates':mates,'defenders':defenders,'shooter':shooter,'team':team,'defense':defense,'fold':np.array([r[1] for r in keys])};cache[season]=d;return d
def prepare(d,bi,sigma,fold):
 k=d['k'];counts=d['counts'];n=counts.sum(axis=1) if bi==0 else counts[:,:2].sum(axis=1);b=counts[:,:2].sum(axis=1) if bi==0 else counts[:,0];train=(n>0)&(np.ones(len(n),bool) if fold is None else d['fold']!=fold);test=(n>0)&(np.ones(len(n),bool) if fold is None else d['fold']==fold);file=Path('reports/player-impact-v45/fits')/f'choice-{d["doc"]["season"]}-sigma0.05-feature1-fold{fold}.json';old=read(file);assert old['playerIds']==d['ids'];m=next(m for m in old['models'] if m['name']==branches[bi]);offset=np.asarray(d['defense']@np.array(m['defenderLogits']));parts=[d['shooter']]
 if sigma:parts.append(d['team'])
 parts.append(sparse.csr_matrix(np.ones((len(n),1))));x=sparse.hstack(parts,format='csr');mu=b[train].sum()/n[train].sum();return {'x':x[train],'allx':x,'n':n[train],'b':b[train],'offset':offset[train],'alloffset':offset,'k':k,'mu':mu,'nu':.5,'base':logit(mu),'precision':np.r_[np.zeros(k),np.full(k,1/sigma**2) if sigma else [],0.],'initial':np.r_[m['shooterLogits'],np.zeros(k) if sigma else [],m['intercept']],'test':test,'alln':n,'allb':b,'model':m,'file':file}
def path(job):
 s,a,f=job;return R/'choice-fits'/f'{s}-sigma{a:g}-fold{f}.json'
def task(job):
 if path(job).exists():return str(path(job))
 season,sigma,fold=job;d=data(season);models=[]
 for bi,z in enumerate(branches):
  t=prepare(d,bi,sigma,fold);p,diag=solver.fit(t);test=t['test'];eta=t['allx'][test]@p+t['alloffset'][test];n=t['alln'][test];b=t['allb'][test];nll=float(np.sum(n*np.logaddexp(0,eta)-b*eta));k=d['k'];models.append({'name':z,'intercept':float(p[-1]),'shooterLogits':p[:k].tolist(),'teammateLogits':p[k:2*k].tolist() if sigma else np.zeros(k).tolist(),'baseDefenderLogits':t['model']['defenderLogits'],'baseModelPath':t['file'].as_posix(),'baseModelSHA256':hashlib.sha256(t['file'].read_bytes()).hexdigest(),'nll':nll,'testAttempts':int(n.sum()),'fit':diag})
 result={'season':season,'sigma':sigma,'fold':fold,'playerIds':d['ids'],'models':models,'testTwoAttempts':models[0]['testAttempts'],'sourceDataSHA256':hashlib.sha256(Path(f'reports/player-impact-v45/{season}-fga-data.json').read_bytes()).hexdigest()};tmp=path(job).with_suffix('.tmp');tmp.write_text(json.dumps(result),encoding='utf-8');tmp.replace(path(job));return str(path(job))
def run(jobs):
 pending=[j for j in jobs if not path(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in pending]),1):
   f.result()
   if i%5==0 or i==len(pending):print(json.dumps({'choiceFitsDone':i,'total':len(pending)}),flush=True)
if __name__=='__main__':
 (R/'choice-fits').mkdir(parents=True,exist_ok=True);proto=read(R/'choice-protocol.json');seasons=proto['seasons'];stage=sys.argv[1]
 if stage=='select':
  run([(s,a,f) for s in seasons[:3] for a in proto['sigmaGrid'] for f in range(5)]);table=[]
  for a in proto['sigmaGrid']:
   cells=[]
   for s in seasons[:3]:
    fs=[read(path((s,a,f))) for f in range(5)];nll=sum(m['nll'] for f in fs for m in f['models']);n=sum(f['testTwoAttempts'] for f in fs);cells.append({'season':s,'nll':nll,'twoAttempts':n,'nllPerTwoAttempt':nll/n})
   table.append({'sigma':a,'meanNllPerTwoAttempt':float(np.mean([c['nllPerTwoAttempt'] for c in cells])),'cells':cells})
  best=min(table,key=lambda c:(c['meanNllPerTwoAttempt'],c['sigma']));(R/'choice-selection.json').write_text(json.dumps({'selectedSigma':best['sigma'],'targetExcluded':True,'table':table},indent=2),encoding='utf-8');print(json.dumps({'selected':best}),flush=True)
 else:
  a=read(R/'choice-selection.json')['selectedSigma'];run([(s,a,None) for s in seasons]+[(seasons[-1],sig,f) for sig in set([0,a]) for f in range(5)]);output=[read(path((s,a,None))) for s in seasons];(R/'choice-fit.json').write_text(json.dumps({'selectedSigma':a,'seasons':output}),encoding='utf-8')

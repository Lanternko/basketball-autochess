"""Conditional identity diagnostic only; never imported by the v36 runtime."""
import hashlib,json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.special import logsumexp
R=Path('reports/player-impact-v36');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=read(R/'passer-choice-protocol.json');inputs=read(R/'passer-choice-inputs.json');old=inputs['beta']
for doc in [protocol,inputs]:
 for p,h in doc['hashes'].items():assert sha(p)==h,p
data={}
for season in [*protocol['trainingSeasons'],protocol['checkSeason']]:
 d=read(R/f'{season}-marked-data.json');rates=inputs['inputs'][season];x=[];offset=[];actual=[];fold=[]
 for r in d['rows']:
  lograte=np.log([rates[str(r[2])][str(pid)] for pid in r[6]])
  for i in range(5):
   counts=np.array(r[9][i],float)
   if not counts.sum():continue
   g=np.array(r[10][i][6],float);assert np.all(g[counts>0]>0)
   logg=np.full(5,-np.inf);positive=g>0;logg[positive]=np.log(g[positive])
   x.append(lograte);offset.append(logg);actual.append(counts);fold.append(r[1])
 data[season]={'x':np.array(x),'offset':np.array(offset),'actual':np.array(actual),'fold':np.array(fold)}
 print(json.dumps({'season':season,'assistedMakes':int(np.array(actual).sum()),'positiveAssistedStints':len(x)}),flush=True)
 del d,x,offset,actual,fold

def calc(beta,season,excluded=None,test=False):
 d=data[season];mask=np.ones(len(d['x']),dtype=bool) if excluded is None else ((d['fold']==excluded) if test else (d['fold']!=excluded))
 x,o,y=[d[k][mask] for k in ['x','offset','actual']];counts=y.sum(axis=1);z=o+(beta-old)*x;den=logsumexp(z,axis=1);prob=np.exp(z-den[:,None])
 chosen=np.where(y>0,z,0.);loss=float(np.sum(counts*den)-np.sum(y*chosen));gradient=float(np.sum(counts*np.sum(prob*x,axis=1))-np.sum(y*x));n=float(counts.sum())
 return {'nll':loss,'assistedMakes':int(n),'gradientPerMake':gradient/n,'nllPerMake':loss/n}

def score(beta,fold=None):return sum(calc(beta,s,fold)['gradientPerMake'] for s in protocol['trainingSeasons'])/3
def fit(fold=None):
 lo,hi=-1.,3.
 while score(lo,fold)>0:lo=2*lo-1
 while score(hi,fold)<0:hi=2*hi+1
 b=brentq(lambda x:score(x,fold),lo,hi,xtol=1e-11);return {'excludedGameFold':fold,'beta':b,'score':score(b,fold)}
main=fit();folds=[fit(i) for i in range(5)];rows=[]
for season in data:
 a,b=calc(old,season),calc(main['beta'],season);rows.append({'season':season,'old':a,'fitted':b,'gainPerAssistedMake':a['nllPerMake']-b['nllPerMake']})
for f in folds:
 f['heldout']=[{'season':s,'old':calc(old,s,f['excludedGameFold'],True),'fitted':calc(f['beta'],s,f['excludedGameFold'],True)} for s in protocol['trainingSeasons']]
out={'scope':protocol['scope'],'runtimeChanged':False,'oldBeta':old,'diagnosticFit':main,'folds':folds,'seasons':rows,'limits':protocol['limits'],'hashes':protocol['hashes']|{str(R/'passer-choice-protocol.json').replace('\\','/'):sha(R/'passer-choice-protocol.json')}}
(R/'passer-choice-diagnostic.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k not in ['hashes','folds']},indent=2))

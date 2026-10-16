import json,importlib.util,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
spec=importlib.util.spec_from_file_location('fine_fit45','reports/player-impact-v45/fit.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
ROOT=lib.ROOT;read=lib.read;original_prepare=lib.prepare;lagcache={}
def prepare(d,raw,fold,sigma,feature,choice=False):
 if feature!=2:return original_prepare(d,raw,fold,sigma,feature,choice)
 t=original_prepare(d,raw,fold,sigma,False,choice);season=d['doc']['season'];zi=next(i for i,z in enumerate(d['zones']) if z is raw)
 key=(season,zi)
 if key not in lagcache:
  previous=f'{int(season[:4])-1}-{int(season[:4])%100:02d}';file=Path(f'reports/player-impact-v20/{previous}-defense-exposure.json');features=np.zeros(d['k'])
  if file.exists() and zi!=2:
   prior=read(file);zone='short' if zi<2 else 'long'
   for i,pid in enumerate(d['ids']):
    c=prior['cards'].get(str(pid),{}).get(zone)
    if c and not c['sourceMissing'] and c['rawDifference'] is not None:
     features[i]=10*c['rate']/prior['leagueAttemptsPerTeamMinute'][zone]*c['rawDifference']*c['attempts']/(c['attempts']+200)
  lagcache[key]=features
 features=lagcache[key];column=np.asarray(raw['x'][:,d['k']:2*d['k']]@features).reshape(-1,1)
 t['x']=sparse.hstack([t['x'][:,:-1],column,t['x'][:,-1]],format='csr');t['feature']=2;t['features']=features;return t
lib.prepare=prepare
def task(job):return lib.task(job)
def run(jobs):
 jobs=[j for j in jobs if not lib.path(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in jobs]),1):
   f.result()
   if i%10==0 or i==len(jobs):print(json.dumps({'stage':'lag-tracking','done':i,'total':len(jobs)}),flush=True)
if __name__=='__main__':
 protocol=read(ROOT/'protocol.json');seasons=protocol['seasons'];grid=protocol['makeGrid']['sigma'];stage=sys.argv[1]
 if stage=='select':
  run([('make',s,a,2,f) for s in seasons[:3] for a in grid for f in range(5)])
  scores=[];selected={}
  for name in lib.ZONES:
   table=[]
   for a in grid:
    for feature in [0,1,2]:
     vals=[next(m for m in read(lib.path(('make',s,a,feature,f)))['models'] if m['name']==name) for s in seasons[:3] for f in range(5)]
     table.append({'name':name,'sigma':a,'feature':feature,'nll':sum(m['nll'] for m in vals),'trials':sum(m['testTrials'] for m in vals)})
   minimum=min(c['nll']/c['trials'] for c in table);best=min([c for c in table if c['nll']/c['trials']<=minimum+1e-10],key=lambda c:(c['feature'],c['sigma']));selected[name]={k:best[k] for k in ['sigma','feature']};scores+=table
  (ROOT/'make-extended-selection.json').write_text(json.dumps({'selected':selected,'scores':scores,'targetExcluded':True},indent=2),encoding='utf-8');print(json.dumps({'selected':selected}),flush=True)
 else:
  selected=read(ROOT/'make-extended-selection.json')['selected'];pairs={(v['sigma'],v['feature']) for v in selected.values()}|{(0,0)}
  run([('make',s,a,b,None) for s in seasons for a,b in pairs]+[('make','2025-26',a,b,f) for a,b in pairs for f in range(5)])
  assembled=[]
  for s in seasons:
   models=[]
   for name,c in selected.items():
    d=read(lib.path(('make',s,c['sigma'],c['feature'],None)));m=next(m for m in d['models'] if m['name']==name);models.append({**m,'featureCode':c['feature'],'featureSlope':m['blockSlope']})
   assembled.append({'season':s,'playerIds':d['playerIds'],'models':models})
  (ROOT/'make-fit.json').write_text(json.dumps({'selected':selected,'seasons':assembled}),encoding='utf-8')

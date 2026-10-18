import json,importlib.util,shutil,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from scipy import sparse
spec=importlib.util.spec_from_file_location('fine_fit45','reports/player-impact-v45/fit.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
ROOT=lib.ROOT;read=lib.read;original_prepare=lib.prepare;cache={}
def prepare(d,raw,fold,sigma,feature,choice=False):
 if not(choice and feature):return original_prepare(d,raw,fold,sigma,feature,choice)
 c=d['choice']['counts'];n=raw['n'];branch='three' if np.array_equal(n,c.sum(axis=1)) else 'paintGivenTwo' if np.array_equal(n,c[:,:3].sum(axis=1)) else 'raGivenPaint' if np.array_equal(n,c[:,:2].sum(axis=1)) else 'cornerGivenThree'
 key=(d['doc']['season'],branch)
 if key not in cache:
  groups={}
  for r in d['doc']['rows']:groups.setdefault((r[0],r[1],r[3],tuple(r[5])),len(groups))
  idx={pid:i for i,pid in enumerate(d['ids'])};allowed={'three':{0,1,2,3,4},'paintGivenTwo':{0,1,2},'raGivenPaint':{0,1},'cornerGivenThree':{3,4}}[branch];rr=[];cc=[];vv=[]
  for r in d['doc']['rows']:
   if r[2] not in allowed:continue
   i=groups[(r[0],r[1],r[3],tuple(r[5]))]
   for pid,b in r[8]:rr.append(i);cc.append(idx[pid]);vv.append(b)
  cache[key]=sparse.csr_matrix((vv,(rr,cc)),shape=(len(groups),d['k']))
 return original_prepare(d,{**raw,'blocks':cache[key]},fold,sigma,feature,choice)
lib.prepare=prepare
def task(j):return lib.task(j)
def run(jobs):
 jobs=[j for j in jobs if not lib.path(j).exists()]
 with ProcessPoolExecutor(max_workers=2) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,j) for j in jobs]),1):
   f.result()
   if i%5==0 or i==len(jobs):print(json.dumps({'stage':'choice-activity','done':i,'total':len(jobs)}),flush=True)
if __name__=='__main__':
 seasons=read(ROOT/'protocol.json')['seasons'];stage=sys.argv[1]
 if stage=='probe':
  run([('choice',s,.05,True,f) for s in seasons[:3] for f in range(5)]);sys.exit(0)
 if stage=='select':
  run([('choice',s,.05,True,f) for s in seasons[:3] for f in range(5)]);scores=[];selected={}
  for name in lib.BRANCHES:
   table=[]
   for sigma,feature in [(s,False) for s in read(ROOT/'protocol.json')['choiceGrid']['sigma']]+[(.05,True)]:
    ms=[next(m for m in read(lib.path(('choice',s,sigma,feature,f)))['models'] if m['name']==name) for s in seasons[:3] for f in range(5)]
    table.append({'name':name,'sigma':sigma,'feature':feature,'nll':sum(m['nll'] for m in ms),'trials':sum(m['testTrials'] for m in ms)})
   minimum=min(c['nll']/c['trials'] for c in table);best=min([c for c in table if c['nll']/c['trials']<=minimum+1e-10],key=lambda c:(c['feature'],c['sigma']));selected[name]={k:best[k] for k in ['sigma','feature']};scores+=table
  (ROOT/'choice-extended-selection.json').write_text(json.dumps({'selected':selected,'scores':scores,'targetExcluded':True},indent=2),encoding='utf-8');print(json.dumps({'selected':selected}),flush=True)
 else:
  selected=read(ROOT/'choice-extended-selection.json')['selected'];pairs={(v['sigma'],v['feature']) for v in selected.values()}|{(0,False)}
  run([('choice',s,a,b,None) for s in seasons for a,b in pairs]+[('choice','2025-26',a,b,f) for a,b in pairs for f in range(5)])
  output=[]
  for s in seasons:
   models=[]
   for name,c in selected.items():
    d=read(lib.path(('choice',s,c['sigma'],c['feature'],None)));models.append(next(m for m in d['models'] if m['name']==name))
   output.append({'season':s,'playerIds':d['playerIds'],'models':models})
  old=ROOT/'choice-fit.json'
  if old.exists() and not (ROOT/'choice-initial-fit.json').exists():shutil.copyfile(old,ROOT/'choice-initial-fit.json')
  old.write_text(json.dumps({'selected':selected,'seasons':output}),encoding='utf-8')

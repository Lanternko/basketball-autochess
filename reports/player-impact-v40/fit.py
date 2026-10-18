import json,hashlib,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();seasons=['2022-23','2023-24','2024-25','2025-26'];grid=[0,.025,.05,.1,.2,.4]
def run():
 from fitlib import task
 stage=sys.argv[1];protocol=read(R/'source-fit-protocol.json')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
 if stage=='select':jobs=[(s,sigma,k) for s in seasons[:3] for sigma in grid for k in range(5)]
 elif stage=='final':
  sigma=read(R/'selection.json')['selectedSigma'];jobs=[(s,sigma,None) for s in seasons]+[(seasons[-1],sigma,k) for k in range(5)]
 else:raise ValueError(stage)
 (R/'fits').mkdir(exist_ok=True);file=lambda j:R/'fits'/f'{j[0]}-sigma{j[1]}-fold{j[2]}.json';pending=[j for j in jobs if not file(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(task,j):j for j in pending}
  for future in as_completed(futures):
   job=futures[future];d=future.result();file(job).write_text(json.dumps(d),encoding='utf-8');print(json.dumps({'stage':stage,'job':job,'nll':d['nll'],'fit':[z['fit'] for z in d['zones']]}),flush=True)
 if stage=='select':
  scores=[]
  for sigma in grid:
   docs=[read(file(j)) for j in jobs if j[1]==sigma];scores.append({'sigma':sigma,'heldoutNll':sum(d['nll'] for d in docs),'fga':sum(d['evaluatedFga'] for d in docs)})
  minimum=min(d['heldoutNll']/d['fga'] for d in scores);selected=min(d['sigma'] for d in scores if d['heldoutNll']/d['fga']<=minimum+1e-10);out={'selectedSigma':selected,'olderOnlyScores':scores,'hashes':{str(file(j)).replace('\\','/'):sha(file(j)) for j in jobs}};f=R/'selection.json';assert not f.exists();f.write_text(json.dumps(out,indent=2),encoding='utf-8');print('SELECTED',selected,flush=True)
 else:
  f=R/'fit.json';assert not f.exists();f.write_text(json.dumps({'selectedSigma':sigma,'seasons':[read(file(j)) for j in jobs if j[2] is None],'targetHeldout':[read(file(j)) for j in jobs if j[2] is not None],'hashes':{str(file(j)).replace('\\','/'):sha(file(j)) for j in jobs}}),encoding='utf-8')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
if __name__=='__main__':run()

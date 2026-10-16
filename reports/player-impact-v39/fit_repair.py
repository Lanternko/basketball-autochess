import hashlib,json,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 from fitlib_repair import task
 stage=sys.argv[1];protocol=read(R/'solver-repair-protocol.json')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
 (R/'fits').mkdir(exist_ok=True)
 if stage=='select':jobs=[(season,sigma,fold) for season in ['2022-23','2023-24','2024-25'] for sigma in [0,.25,.5,1,2] for fold in range(5)]
 elif stage=='final':
  sigma=read(R/'selection.json')['selectedSigma'];jobs=[(s,sigma,None) for s in ['2022-23','2023-24','2024-25','2025-26']]+[('2025-26',sigma,k) for k in range(5)]
 else:raise ValueError(stage)
 def file(j):return R/'fits'/f'{j[0]}-sigma{j[1]}-fold{j[2]}.json'
 pending=[j for j in jobs if not file(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(task,j):j for j in pending}
  for f in as_completed(futures):
   j=futures[f];d=f.result();file(j).write_text(json.dumps(d),encoding='utf-8');print(json.dumps({'stage':stage,'job':j,'nll':d['nll'],'fit':d['fit']}),flush=True)
 if stage=='select':
  scores=[]
  for sigma in [0,.25,.5,1,2]:
   docs=[read(file(j)) for j in jobs if j[1]==sigma];scores.append({'sigma':sigma,'heldoutNll':sum(d['nll'] for d in docs),'misses':sum(d['evaluatedMisses'] for d in docs)})
  minimum=min(d['heldoutNll']/d['misses'] for d in scores);selected=min(d['sigma'] for d in scores if d['heldoutNll']/d['misses']<=minimum+1e-10)
  assert not (R/'selection.json').exists();(R/'selection.json').write_text(json.dumps({'selectedSigma':selected,'olderOnlyScores':scores,'scope':'Older3 seasons whole-game heldout marked NLL per miss; target season excluded. Same-season local reconstruction diagnostic, not forecasting.','hashes':{str(file(j)).replace('\\','/'):sha(file(j)) for j in jobs}},indent=2),encoding='utf-8');print('SELECTED',selected,flush=True)
 else:
  out={'selectedSigma':sigma,'seasons':[read(file(j)) for j in jobs if j[2] is None],'targetHeldout':[read(file(j)) for j in jobs if j[2] is not None],'hashes':{str(file(j)).replace('\\','/'):sha(file(j)) for j in jobs}}
  (R/'fit.json').write_text(json.dumps(out),encoding='utf-8')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
if __name__=='__main__':run()


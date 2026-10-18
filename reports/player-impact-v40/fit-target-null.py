"""Add a target-season null diagnostic, never used for hyperparameter selection."""
import json,hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
R=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 from fitlib import task
 protocol=read(R/'target-null-protocol.json')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
 assert (R/'selection.json').exists() and (R/'fit.json').exists();jobs=[('2025-26',0,k) for k in range(5)];file=lambda j:R/'fits'/f'{j[0]}-sigma{j[1]}-fold{j[2]}.json'
 with ProcessPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(task,j):j for j in jobs if not file(j).exists()}
  for future in as_completed(futures):
   j=futures[future];d=future.result();file(j).write_text(json.dumps(d),encoding='utf-8');print('Target NULL',j[2],d['nll'],flush=True)
 out={'scope':__doc__,'jobs':[read(file(j)) for j in jobs],'hashes':{str(file(j)).replace('\\','/'):sha(file(j)) for j in jobs}};f=R/'target-null.json';assert not f.exists();f.write_text(json.dumps(out),encoding='utf-8')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
if __name__=='__main__':run()

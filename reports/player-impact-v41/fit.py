import json,hashlib,sys,importlib.util
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
R=Path('reports/player-impact-v41');V=Path('reports/player-impact-v40');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();seasons=['2022-23','2023-24','2024-25','2025-26'];zones=['long','mid','short'];sys.path.insert(0,str(V.resolve()))
def run():
 from fitlib import task
 selection=read(R/'selection.json');protocol=read(R/'fit-protocol.json');sigmas=sorted({0,*selection['selectedSigmaByZone'].values()})
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
 jobs=[(s,sigma,None) for s in seasons for sigma in sigmas]+[('2025-26',sigma,k) for sigma in sigmas for k in range(5)];file=lambda j:R/'fits'/f'{j[0]}-sigma{j[1]}-fold{j[2]}.json';oldfile=lambda j:V/'fits'/file(j).name;(R/'fits').mkdir(exist_ok=True)
 pending=[j for j in jobs if not file(j).exists() and not oldfile(j).exists()]
 with ProcessPoolExecutor(max_workers=4) as pool:
  futures={pool.submit(task,j):j for j in pending}
  for future in as_completed(futures):
   job=futures[future];d=future.result();file(job).write_text(json.dumps(d),encoding='utf-8');print(json.dumps({'job':job,'nll':d['nll']}),flush=True)
 source=lambda j:oldfile(j) if oldfile(j).exists() else file(j)
 def assemble(season,fold):
  chosen=[];ids=None;paths=[]
  for i,z in enumerate(zones):
   path=source((season,selection['selectedSigmaByZone'][z],fold));d=read(path);ids=d['playerIds'] if ids is None else ids;assert ids==d['playerIds'];chosen.append(d['zones'][i]);paths.append({'zone':z,'sigma':selection['selectedSigmaByZone'][z],'file':str(path).replace('\\','/'),'sha256':sha(path)})
  return {'season':season,'heldoutFold':fold,'playerIds':ids,'zones':chosen,'sources':paths}
 out={'selectedSigmaByZone':selection['selectedSigmaByZone'],'seasons':[assemble(s,None) for s in seasons],'targetHeldout':[assemble('2025-26',k) for k in range(5)],'jobs':[{'season':j[0],'sigma':j[1],'fold':j[2],'file':str(source(j)).replace('\\','/'),'sha256':sha(source(j))} for j in jobs],'hashes':{str(source(j)).replace('\\','/'):sha(source(j)) for j in jobs}}
 f=R/'fit.json';assert not f.exists();f.write_text(json.dumps(out),encoding='utf-8')
 for p,h in protocol['hashes'].items():assert sha(p)==h,p
if __name__=='__main__':run()

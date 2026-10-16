"""Every recorded field except the block count must equal archived v30."""
import json,hashlib
from pathlib import Path
R=Path('reports/player-impact-v39');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def walk(a,b,path=''):
 assert type(a)==type(b),(path,type(a),type(b))
 if isinstance(a,dict):
  assert a.keys()==b.keys(),path
  for k in a:
   if k=='blk':
    assert isinstance(a[k],(int,float)) and isinstance(b[k],(int,float));continue
   walk(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i))
 else:assert a==b,(path,a,b)
rows=[]
for j in read(R/'validation-manifest.json')['jobs']:
 candidate=j['file'];baseline=candidate.replace('player-impact-v39','player-impact-v30');a=read(baseline);b=read(candidate);assert sha(candidate)==j['sha256'];walk(a,b)
 old=sum(t['stats']['blk'] for t in a['teams']);new=sum(t['stats']['blk'] for t in b['teams']);rows.append({'season':j['season'],'strict':j['strict'],'seed':j['seed'],'games':len(a['matches']),'baselineBlocks':old,'candidateBlocks':new,'baselineSha256':sha(baseline),'candidateSha256':sha(candidate)});print(rows[-1],flush=True)
assert len(rows)==24 and sum(j['games'] for j in rows)==28023
out={'passed':True,'jobs':24,'games':28023,'onlyPermittedDifference':'Numeric dictionary field named blk; dictionary keys/list order/types/every other scalar exactly equal, including every match score, player plusMinus, minutes, all non-block counters, all on-court records and FT/contact/putback audits. No whole subtrees excluded.','rows':rows,'hashes':{str(p).replace('\\','/'):sha(p) for p in [R/'verify-isolation.py',R/'validation-manifest.json']}}
(R/'isolation-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

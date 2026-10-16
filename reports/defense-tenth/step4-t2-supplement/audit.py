import json,hashlib,datetime,math,ast
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=read(O/'protocol.json');issues=[]
for name,h in p['protectedHashes'].items():
 f=R/name
 if not f.exists() or sha(f)!=h:issues.append({'protectedChanged':name})
for base in ['protocol','named-pairs-supplement']:
 if sha(O/(base+'.json'))!=(O/(base+'.sha256')).read_text().split()[0]:issues.append({'registrationMismatch':base})
def finite(x,path=''):
 if isinstance(x,float) and not math.isfinite(x):issues.append({'nonFinite':path})
 elif isinstance(x,dict):
  for k,v in x.items():finite(v,path+'/'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):finite(v,path+'/'+str(i))
for f in O.glob('*.json'):finite(read(f),f.name)
for f in O.glob('*.py'):ast.parse(f.read_text(encoding='utf8'))
cases=read(O/'cases.json');bins=read(O/'lineup-observations.json');pairs=read(O/'named-pairs.json');facts=read(O/'cached-factors.json')
assert len(cases)==len(facts)==8
for c in cases:
 assert len(c['players'])==10
 for kind in ['rimProtector','sizeOnly']:
  rr=[x for x in bins if x['season']==c['season'] and x['team']==c['team'] and x['type']==kind]
  assert len(rr)==3 and abs(sum(x['stats']['poss'] for x in rr)-c['observed']['poss'])<1e-7
  assert abs(sum(x['stats']['minutes'] for x in rr)-c['observed']['minutes'])<1e-7
 for player in c['players']:
  m=player['matchups']
  if m:assert abs(sum(v for v in m['positions'].values() if v is not None)-1)<1e-8
 assert all(abs(c['T0'][v]['O']+c['T0'][v]['D']-c['T0'][v]['netError'])<1e-8 for v in ['pure','v3'])
for s in ['2022-23','2023-24']:
 pp=[x for x in pairs if x['season']==s];c=next(c for c in cases if c['season']==s)
 assert len(pp)==4 and abs(sum(x['stats']['poss'] for x in pp)-c['observed']['poss'])<1e-7
for c in cases:
 fact=next(x for x in facts if x['season']==c['season'] and x['team']==c['team'])
 for version in ['pure','v3']:
  # Compare our paired proxy with the authoritative engine helper's formula
  # independently on the pooled immutable counters.
  own={};opp={}
  for seed in range(20261012,20261032):
   run=read(R/f'reports/defense-tenth/step4-t0/runs/{c["season"]}-{version}-{seed}.json')
   t=next(t for t in run['teams'] if t['id']==c['teamId'])
   for target,source in [(own,t['stats']),(opp,t['opponent'])]:
    for k,v in source.items():target[k]=target.get(k,0)+v
  bp=lambda a:a['fga']-a['oreb']+a['tov']+.44*a['fta']
  assert abs(fact['fullSeason'][version]['defProxy']-100*opp['pts']/((bp(own)+bp(opp))/2))<1e-8
manifest={f.relative_to(R).as_posix():sha(f) for f in O.iterdir() if f.is_file() and f.name!='completion-audit.json'}
out={'completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protectedFiles':len(p['protectedHashes']),'issues':issues,'cases':len(cases),'playerRows':sum(len(c['players']) for c in cases),'strictReconciliations':read(O/'stint-audit.json')['validation'],'newGamesSimulated':0,'newDataDownloads':0,'newCardFits':0,'checks':['protocol SHAs','protected file SHA parity','finite values','syntax','G/F/C shares','bin totals','pair totals','O+D identity','cached paired proxy independent recomputation'],'outputHashes':manifest}
(O/'completion-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:out[k] for k in ['completedAt','protectedFiles','issues','cases','playerRows']}))
assert not issues

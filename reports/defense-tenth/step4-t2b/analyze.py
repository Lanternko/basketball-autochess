import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,hashlib,ast
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from scipy.stats import rankdata
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;OLD=R/'reports/defense-tenth/step4-t2'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def table(p):
 t=read(p)['data']['resultSets'][0];return [dict(zip(t['headers'],r)) for r in t['rowSet']]
P=read(O/'protocol.json');assert sha(O/'protocol.json')==(O/'protocol.sha256').read_text().split()[0]
manifest=read(O/'fetch-manifest.json');profiles=read(O/'profiles.json');org=read(O/'organizers.json');D=read(OLD/'players.json');pbp=read(O/'overall-pbp-counts.json');counts=read(O/'onoff-game-counts.json')
idx={(x['season'],str(x['team']),x['kind'],x['date']):x for x in manifest['sources']};raw={};audit=[];inventory=[]
cols=['FGM','FGA','FG2M','FG2A','FG3M','FG3A']
for source in manifest['sources']:
 assert sha(R/source['file'])==source['sha256']
 group={}
 for x in table(R/source['file']):
  pid=str(x['PLAYER_ID']);z=group.setdefault(pid,dict.fromkeys(cols,0.))
  for k in cols:z[k]+=x.get(k,0) or 0
 raw[source['season'],str(source['team']),source['kind'],source['date']]=group
dataset={};metricnames=['catchFG','catch3FG','pullFG','pull3FG','catchShare','pullShare','assistedMakeShare']
allpbp=defaultdict(Counter)
for r in pbp:
 for key in [(r['season'],str(r['team']),str(r['player'])),(r['season'],'0',str(r['player']))]:allpbp[key].update({k:r[k] for k in ['a','m','am','pullA','pullM']})
def ratio(a,b,k=1):return k*a/b if b>0 else None
for s,S in D.items():
 dataset[s]={}
 for tid in ['0']+list(S['teams']):
  total=raw.get((s,tid,'all',''),{});catch=raw.get((s,tid,'catch',''),{});pull=raw.get((s,tid,'pull',''),{})
  for pid,x in S['players'].items():
   if tid!='0' and tid not in x['teams']:continue
   a=total.get(pid);pb=allpbp[s,tid,pid]
   if a is None:
    dataset[s][pid,tid]={'metrics':{'assistedMakeShare':ratio(pb['am'],pb['m'],100)},'samples':{'pbpM':pb['m']},'tracking':None};continue
   z=dict.fromkeys(cols,0.);c=catch.get(pid,z);u=pull.get(pid,z);other={k:a[k]-c[k]-u[k] for k in cols}
   invalid=any(v<-.01 for v in other.values())
   if invalid:audit.append({'season':s,'team':tid,'player':pid,'issue':'category counts exceed all','other':other})
   metrics={'catchFG':ratio(c['FGM'],c['FGA'],100),'catch3FG':ratio(c['FG3M'],c['FG3A'],100),'pullFG':ratio(u['FGM'],u['FGA'],100),'pull3FG':ratio(u['FG3M'],u['FG3A'],100),'catchShare':ratio(c['FGA'],a['FGA'],100),'pullShare':ratio(u['FGA'],a['FGA'],100),'assistedMakeShare':ratio(pb['am'],pb['m'],100)}
   if invalid:metrics={k:v for k,v in metrics.items() if k=='assistedMakeShare'}
   dataset[s][pid,tid]={'metrics':metrics,'samples':{'allA':a['FGA'],'catchA':c['FGA'],'catch3A':c['FG3A'],'pullA':u['FGA'],'pull3A':u['FG3A'],'pbpM':pb['m']},'tracking':{'all':a,'catch':c,'pull':u,'other':other},'invalidCategories':invalid}
  players=list(S['players']);have=[pid for pid in players if (pid,tid) in dataset[s] and dataset[s][pid,tid]['tracking'] is not None]
  if tid=='0':
   mm=sum(x['minutes'] for x in S['players'].values());inventory.append({'season':s,'players':len(players),'trackingPlayers':len(have),'minuteCoverage':sum(S['players'][pid]['minutes'] for pid in have)/mm,'trackingFGA':sum(total[pid]['FGA'] for pid in have),'officialFGA':sum(x['box']['FGA'] for x in S['players'].values()),'trackingFGM':sum(total[pid]['FGM'] for pid in have),'officialFGM':sum(x['box']['FGM'] for x in S['players'].values()),'catchFGA':sum(catch.get(pid,{}).get('FGA',0) for pid in have),'pullFGA':sum(pull.get(pid,{}).get('FGA',0) for pid in have)})
 # Validate traded global counts against team-filtered sums before portability.
 for pid,x in S['players'].items():
  if len(x['teams'])<2:continue
  g=dataset[s].get((pid,'0'),{})
  for cat in ['all','catch','pull']:
   rows=[dataset[s].get((pid,t),{}).get('tracking') for t in x['teams']]
   if not g.get('tracking') or any(not t for t in rows):continue
   if any(abs(sum(t[cat][k] for t in rows)-g['tracking'][cat][k])>.01 for k in cols):
    audit.append({'season':s,'player':pid,'category':cat,'issue':'split counts not global; exclude within-season tracking metric'})
    for t in x['teams']:dataset[s][pid,t]['invalidSplit']=True
save('tracking-player-data.json',{s:{pid+':'+tid:r for (pid,tid),r in v.items()} for s,v in dataset.items()});save('tracking-coverage.json',{'inventory':inventory,'countIssues':audit,'requests':manifest['jobs'],'failures':manifest['failures']})

tree=ast.parse((OLD/'analyze.py').read_text(encoding='utf8'));funcs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['corr','evaluate']],type_ignores=[]);p={'uncertainty':{'rng':P['portability']['rng']}};exec(compile(funcs,'old-cluster-statistics','exec'),globals())
def sufficient(x,m,move=False):
 if not x or x['metrics'].get(m) is None:return False
 if move and x.get('invalidSplit') and m!='assistedMakeShare':return False
 threshold={'catchFG':('catchA',50 if move else 100),'catch3FG':('catch3A',40 if move else 75),'pullFG':('pullA',50 if move else 100),'pull3FG':('pull3A',40 if move else 75),'catchShare':('allA',100 if move else 200),'pullShare':('allA',100 if move else 200),'assistedMakeShare':('pbpM',50 if move else 100)}
 k,n=threshold[m];return x['samples'].get(k,0)>=n
adj=[];moves=[]
for a,b in zip(P['seasons'][:-1],P['seasons'][1:]):
 for pid in sorted(set(D[a]['players'])&set(D[b]['players'])):
  x,y=D[a]['players'][pid],D[b]['players'][pid]
  if min(x['minutes'],y['minutes'])<500 or min(x['dominantShare'],y['dominantShare'])<.6:continue
  for m in metricnames:
   u,v=dataset[a].get((pid,'0')),dataset[b].get((pid,'0'))
   if sufficient(u,m) and sufficient(v,m):adj.append({'metric':m,'group':'same' if x['dominantTeam']==y['dominantTeam'] else 'moved','period':a+'→'+b,'id':int(pid),'teams':[x['dominantTeam'],y['dominantTeam']],'x':u['metrics'][m],'y':v['metrics'][m]})
for r in read(OLD/'move-samples.json')['audit']:
 if r['reason']:continue
 s=r['season'];pid=str(r['id']);ts=sorted([t for t in D[s]['players'][pid]['teams'].values() if t['minutes']>=300],key=lambda t:min(t['dates']))
 if len(ts)<2:continue
 a,b=ts[0],ts[-1]
 for m in metricnames:
  u,v=dataset[s].get((pid,str(a['id']))),dataset[s].get((pid,str(b['id'])))
  if sufficient(u,m,True) and sufficient(v,m,True):moves.append({'metric':m,'group':'seasonMove','period':s,'id':int(pid),'teams':[a['id'],b['id']],'x':u['metrics'][m],'y':v['metrics'][m],'confirmed':r['officialTradeParticipant']})
results=[]
for m in metricnames:
 for group in ['same','moved','seasonMove','officialTradeParticipant']:
  source=adj if group in ['same','moved'] else moves
  rr=[x for x in source if x['metric']==m and (x['group']==group or group=='officialTradeParticipant' and x['confirmed'])]
  results.append({'metric':m,'group':group,**evaluate(rr,m+group)})
 print('BOOT',m,flush=True)
save('portability.json',results);save('portability-samples.json',{'adjacent':adj,'within':moves})

# Within-player, zone-standardized ON/OFF; selection is based on attempts only.
def role(s,tid,pid):
 x=profiles[s].get(str(tid)+':'+str(pid),{});a=x.get('AST_PCT');u=x.get('USG_PCT')
 si=P['seasons'].index(s);anchors=[org[s].get(str(tid))]+([org[P['seasons'][si-1]].get(str(tid))] if si else [])
 rotation=sorted([r for r in profiles[s].values() if str(r['teamId'])==str(tid)],key=lambda r:r['MIN'],reverse=True)
 eligible=x.get('MIN',0)>=500 or int(pid) in [r['id'] for r in rotation[:10]]
 return eligible and all(not x or x['id']!=int(pid) for x in anchors) and a is not None and u is not None and a<.20 and u<.25
def onoff(rows,subset='all',ci=False):
 if subset=='role':rows=[r for r in rows if role(r['season'],r['team'],r['player'])]
 groups=defaultdict(lambda:np.zeros((2,5)))
 totals=defaultdict(lambda:np.zeros(2))
 for r in rows:groups[r['season'],r['team'],r['player'],r['zone']][r['on']]+=np.array([r[k] for k in ['a','m','am','pullA','pullM']]);totals[r['season'],r['team'],r['player']][r['on']]+=r['a']
 strata=[k for k,v in groups.items() if min(v[:,0])>=20 and min(totals[k[:3]])>=50]
 def calc(arr):
  ans={}
  for name,col,den in [('FG',1,0),('assistedMakeShare',2,1),('explicitPullupShare',3,0)]:
   a=arr[:,:,col];d=arr[:,:,den];w=np.minimum(d[:,0],d[:,1]);gap=np.divide(a[:,1],d[:,1],out=np.zeros(len(d)),where=d[:,1]>0)-np.divide(a[:,0],d[:,0],out=np.zeros(len(d)),where=d[:,0]>0)
   ans[name]=float(np.dot(w,gap)/w.sum()*100) if w.sum() else None
  return ans
 point=calc(np.array([groups[k] for k in strata])) if strata else dict.fromkeys(['FG','assistedMakeShare','explicitPullupShare'])
 out={'subset':subset,'players':len({k[:3] for k in strata}),'strata':len(strata),'rawOnFGA':sum(r['a'] for r in rows if r['on']),'rawOffFGA':sum(r['a'] for r in rows if not r['on']),'standardizedOnMinusOffPP':point,'ci95':None,'limitation':'assisted share among makes; explicit pullup proxy, not exact catch/pull tracking; descriptive confounding remains'}
 if ci and strata:
  games=sorted({r['game'] for r in rows});gi={g:i for i,g in enumerate(games)};ki={k:i for i,k in enumerate(strata)};a=np.zeros((len(games),len(strata),2,5))
  for r in rows:
   key=r['season'],r['team'],r['player'],r['zone']
   if key in ki:a[gi[r['game']],ki[key],r['on']]+=np.array([r[k] for k in ['a','m','am','pullA','pullM']])
  rng=np.random.default_rng(P['portability']['rng']);v=defaultdict(list)
  for start in range(0,20000,200):
   w=rng.multinomial(len(games),np.ones(len(games))/len(games),size=200)
   sampled=np.tensordot(w,a,axes=1)
   for arr in sampled:
    for k,x in calc(arr).items():
     if x is not None:v[k].append(x)
  out['ci95']={k:np.quantile(x,[.025,.975]).tolist() for k,x in v.items()};out['bootstrapGames']=len(games)
 return out
onresults=[]
for s in P['seasons']:
 for kind in ['current','prior']:
  rr=[r for r in counts if r['season']==s and r['kind']==kind]
  for subset in ['all','role']:onresults.append({'season':s,'team':'league','kind':kind,**onoff(rr,subset)})
for case in P['cases']:
 s=case['season'];tid=next(t for t,x in D[s]['teams'].items() if x['name']==case['team'])
 for kind in ['current','prior']:
  rr=[r for r in counts if r['season']==s and str(r['team'])==tid and r['kind']==kind]
  for subset in ['all','role']:onresults.append({'season':s,'team':case['team'],'kind':kind,**onoff(rr,subset,True)})
 print('ONOFF',s,case['team'],flush=True)
save('onoff-results.json',onresults)

card={ (r['season'],str(r['id'])):r for r in read(O/'card-comparisons.json')};cases=[]
for case in P['cases']:
 s=case['season'];prior=P['seasons'][P['seasons'].index(s)-1];tid=next(t for t,x in D[s]['teams'].items() if x['name']==case['team']);rotation=sorted([x for x in profiles[s].values() if str(x['teamId'])==tid],key=lambda x:x['MIN'],reverse=True);eligible={x['id'] for x in rotation[:10]}|{x['id'] for x in rotation if x['MIN']>=500};rows=[]
 for x in rotation:
  if x['id'] not in eligible:continue
  pid=str(x['id']);old=dataset[prior].get((pid,'0'));cur=dataset[s].get((pid,tid));previous=D[prior]['players'].get(pid);c=card.get((s,pid));contr={}
  if old and cur and old.get('tracking') and cur.get('tracking') and not old.get('invalidCategories') and not cur.get('invalidCategories'):
   for cat in ['catch','pull','other']:
    a,b=old['tracking'][cat],cur['tracking'][cat];v=0.;known=0
    for mk,ak,value in [('FG2M','FG2A',2),('FG3M','FG3A',3)]:
     if a[ak]>0:v+=value*b[ak]*(a[mk]/a[ak]-(b[mk]/b[ak] if b[ak] else 0));known+=b[ak]
    contr[cat]={'oldMinusCurrentPointsPer82Games':v/82,'coveredCurrentAttempts':known,'currentAttempts':b['FGA']}
  pb=allpbp[s,tid,pid];opb=allpbp[prior,'0',pid]
  rows.append({'id':x['id'],'name':x['name'],'minutes':x['MIN'],'GP':x['GP'],'AGE':x['AGE'],'role':role(s,tid,pid),'previousMinutes':previous['minutes'] if previous else None,'cards':c,'priorTracking':old,'currentTracking':cur,'assistedMakesPriorPct':ratio(opb['am'],opb['m'],100),'assistedMakesCurrentPct':ratio(pb['am'],pb['m'],100),'categoryScoringGap':contr,'injury':'not individually verified; GP is not a medical diagnosis'})
 def summarize(rr):return {cat:sum(r['categoryScoringGap'].get(cat,{}).get('oldMinusCurrentPointsPer82Games',0) for r in rr) for cat in ['catch','pull','other']}
 cases.append({'season':s,'team':case['team'],'prior':prior,'organizer':org[s].get(tid),'priorOrganizer':org[prior].get(tid),'players':rows,'allCategoryGap':summarize(rows),'roleCategoryGap':summarize([r for r in rows if r['role']]),'gapDefinition':'target attempt counts times old-current raw within-category 2P/3P rate, points per scheduled team game; not a simulation or causal contribution; zero prior zone attempts omitted and coverage shown'})
save('cases.json',cases)
print('ANALYSIS DONE',len(results),'portability',len(cases),'cases',flush=True)

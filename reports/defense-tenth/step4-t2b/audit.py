import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
P=read(O/'protocol.json');expected=(O/'protocol.sha256').read_text().split()[0];assert sha(O/'protocol.json')==expected
protected=[f for f,h in P['protectedHashes'].items() if not (R/f).exists() or sha(R/f)!=h];assert not protected,protected
print('PROTECTED',len(P['protectedHashes']),'unchanged',flush=True)
manifest=read(O/'fetch-manifest.json');assert manifest['jobs']==864 and len(manifest['sources'])==864 and not manifest['failures']
rawbad=[r['file'] for r in manifest['sources'] if sha(R/r['file'])!=r['sha256']];assert not rawbad
changedInputs=[f for f,h in read(O/'input-hashes.json').items() if sha(f)!=h];assert not changedInputs
coverage=read(O/'pbp-coverage.json');assert [r['strictGames'] for r in coverage]==[1079,1063,1091,1188]
assert all(r['matchedFGA']==r['strictFGA'] and not r['unmatched'] and r['missingAssistIdOnNamedAssistedMake']==0 for r in coverage)
tracking=read(O/'tracking-coverage.json');assert not tracking['countIssues']
date=read(O/'tracking-date-audit.json');assert all(r['dates']==82 and not r['dateSumVsFullDifferences'] and not r['invalidPartitions'] for r in date)
cards=read(O/'card-comparisons.json');assert all(r['prior']['handle']==70 and r['currentEffective']['handle']==70 and r['prior']['offBall']==70 and r['currentEffective']['offBall']==70 for r in cards)
cases=read(O/'cases.json');assert len(cases)==2
for c in cases:
 for group,key in [(c['players'],'allCategoryGap'),([r for r in c['players'] if r['role']],'roleCategoryGap')]:
  for cat in ['catch','pull','other']:assert abs(sum(r['categoryScoringGap'].get(cat,{}).get('oldMinusCurrentPointsPer82Games',0) for r in group)-c[key][cat])<1e-10
 for q in c['players']:
  for t in [q['priorTracking'],q['currentTracking']]:
   if not t or not t.get('tracking'):continue
   for k,v in t['tracking']['all'].items():assert abs(v-sum(t['tracking'][cat][k] for cat in ['catch','pull','other']))<1e-10
port=read(O/'portability.json');assert len(port)==28
for x in port:
 if x.get('pearson') is not None:assert -1<=x['pearson']<=1 and x['ci95'][0]>=-1-1e-10 and x['ci95'][1]<=1+1e-10
org=read(O/'organizers.json');bycase={c['team']:c for c in cases};assert bycase['Indiana Pacers']['priorOrganizer']['id']==1630169 and org['2023-24']['1610612763']['id']==1630590
av=read(O/'availability-results.json');assert all(r['playedGames']==0 and all(v is None for v in r['onMinusDnpPP'].values()) for r in av if r['team']=='Indiana Pacers' and r['kind']=='prior')
onoff=read(O/'onoff-results.json');assert all(r['rawOnFGA']==0 and r['rawOffFGA']==0 for r in onoff if r['team']=='Indiana Pacers' and r['kind']=='prior')
old=read(R/'reports/defense-tenth/step4-t2/players.json');tracked=read(O/'tracking-player-data.json');countaudit=[]
for s,S in old.items():
 rr=[]
 for pid,p in S['players'].items():
  t=tracked[s].get(pid+':0',{}).get('tracking')
  if not t:continue
  delta={k:t['all'][k]-p['box'][k] for k in ['FGA','FGM']}
  if any(delta.values()):rr.append({'id':int(pid),'name':p['name'],'trackingMinusBox':delta})
 countaudit.append({'season':s,'playersWithCountDifference':len(rr),'rows':sorted(rr,key=lambda x:abs(x['trackingMinusBox']['FGA']),reverse=True),'label':'unadjusted source discrepancy, not imputed coverage'})
(O/'tracking-box-differences.json').write_text(json.dumps(countaudit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
deliverables={p.name:sha(p) for p in O.iterdir() if p.is_file() and p.name not in ['audit.json','deliverable-manifest.json']}
result={'completedAt':datetime.now(timezone.utc).isoformat(),'status':'pass with explicitly recorded source limitations','protocolSHA256':expected,'protectedFiles':len(P['protectedHashes']),'protectedChanged':protected,'sourceResponsesVerified':len(manifest['sources']),'inputChanges':changedInputs,'strictGames':[r['strictGames'] for r in coverage],'strictShotLineupMatches':sum(r['matchedFGA'] for r in coverage),'unmatchedStrictShots':0,'strictDREBvsOfficialBox':'exact each team in all four seasons (assertions in prepare.py)','dateFullSeasonCounts':'exact for all category/player counts in both cases','caseTrackingMinusBoxFGA':{r['season']:r['dateTrackingFGA']-r['officialFGA'] for r in date},'portabilityMetrics':len(port),'perPlayerOnOffContrasts':len(read(O/'onoff-players.json')),'cardsModified':False,'simulationsRun':False,'codeModifiedInThisStep':'new T2b directory only','knownLimitations':['no exact on-court catch/shoot or full pullup tracking label','no assisted-miss labels','tracking/box discrepancies not all traced','Haliburton target-season zero ON','injury effects not causally identified','card recipes differ between frozen A2/T0','posthoc production split is not hypothesis acceptance'],'deliverableSHA256':deliverables}
(O/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(O/'deliverable-manifest.json').write_text(json.dumps({**deliverables,'audit.json':sha(O/'audit.json')},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('AUDIT PASS',result['strictShotLineupMatches'],len(manifest['sources']),flush=True)

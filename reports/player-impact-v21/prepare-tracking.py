"""Audit tracked activity; do not turn touches or speed into unmeasured skill grades."""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v21');seasons=['2022-23','2023-24','2024-25','2025-26']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def table(doc,name=None):
 sets=doc['data']['resultSets'];sets=sets if isinstance(sets,list) else [sets]
 t=next(s for s in sets if not name or s['name']==name)
 return [dict(zip(t['headers'],r)) for r in t['rowSet']]
summary=[]
for season in seasons:
 output=root/f'{season}-tracking.json'
 if output.exists():raise RuntimeError('Preserve tracked input artifact')
 files={k:root/f'raw/{season}/{k}.json' for k in ['Passing','Possessions','SpeedDistance']}
 files['pairs']=root/f'raw/{season}/passing-pairs-league.json'
 files['hustle']=Path(f'reports/defense-tenth/step4-t2/raw/{season}/0-hustle.json')
 bundle=Path(f'reports/defense-tenth/step4-t0/{season}/bundle.json');files['bundle']=bundle
 official=defaultdict(Counter);names={}
 for t in read(bundle)['league']['teams']:
  for p in t['roster']:official[p['playerId']].update(p['observed']);names[p['playerId']]=p['name']
 maps={k:{p['PLAYER_ID']:p for p in table(read(files[k]))} for k in ['Passing','Possessions','SpeedDistance','hustle']}
 for k in maps:assert len(maps[k])==len(table(read(files[k]))),'Global table must not duplicate actors'
 made=defaultdict(Counter);received=defaultdict(Counter);pairs={};mirror={};excluded_self=[];nonpartition=[];fields=['PASS','AST','FGM','FGA','FG2M','FG2A','FG3M','FG3A']
 for r in table(read(files['pairs']),'PassesMade'):
  key=(r['TEAM_ID'],r['PLAYER_ID'],r['PASS_TEAMMATE_PLAYER_ID']);assert key not in pairs
  if key[1]==key[2]:excluded_self.append(r);continue
  assert 0<=r['AST']<=r['FGM']<=r['FGA'] and r['PASS']>=0
  if r['FGA']>r['PASS']:nonpartition.append(r)
  assert r['FG2A']+r['FG3A']==r['FGA'] and r['FG2M']+r['FG3M']==r['FGM']
  pairs[key]=r;made[key[1]].update({k:r[k] for k in fields});received[key[2]].update({k:r[k] for k in fields})
 for r in table(read(files['pairs']),'PassesReceived'):
  key=(r['TEAM_ID'],r['PASS_TEAMMATE_PLAYER_ID'],r['PLAYER_ID']);assert key not in mirror
  if key[1]!=key[2]:mirror[key]=r
 mirror_issues=[dict(team=k[0],passer=k[1],receiver=k[2],fields=[f for f in fields if r[f]!=mirror.get(k,{}).get(f)]) for k,r in pairs.items() if any(r[f]!=mirror.get(k,{}).get(f) for f in fields)]
 total=sum(official.values(),Counter());pm=sum(made.values(),Counter());pr=sum(received.values(),Counter())
 assert pm==pr
 priors={'passMadePerMinute':pm['PASS']/total['MIN'],'passReceivedPerMinute':pr['PASS']/total['MIN'],
  'passedFgaMadePerMinute':pm['FGA']/total['MIN'],'passedFgaReceivedPerMinute':pr['FGA']/total['MIN'],
  'officialAssistGivenPassedMake':pm['AST']/pm['FGM']}
 cards={};issues=[]
 for pid,o in official.items():
  m=made[pid];r=received[pid];minutes=o['MIN']
  activity={k:(n+60*priors[k])/(minutes+60) for k,n in [('passMadePerMinute',m['PASS']),('passReceivedPerMinute',r['PASS']),('passedFgaMadePerMinute',m['FGA']),('passedFgaReceivedPerMinute',r['FGA'])]}
  # This is a conditional official-credit frequency AFTER a made passed shot,
  # not the probability that an arbitrary pass leads to a field goal.
  activity['officialAssistGivenPassedMake']=(m['AST']+50*priors['officialAssistGivenPassedMake'])/(m['FGM']+50)
  passing=maps['Passing'].get(pid);poss=maps['Possessions'].get(pid);speed=maps['SpeedDistance'].get(pid);hustle=maps['hustle'].get(pid)
  discrepancies={'pairASTMinusOfficialAST':m['AST']-o['AST'],'pairPASSMinusPassingPASS':m['PASS']-passing['PASSES_MADE'] if passing else None,
   'derivedReceivedPASSMinusPassingReceivedPASS':r['PASS']-passing['PASSES_RECEIVED'] if passing else None,'receivedFgaAboveOfficial':max(0,r['FGA']-o['FGA'])}
  if any(v for v in discrepancies.values()):issues.append({'playerId':pid,**discrepancies})
  cards[str(pid)]={'name':names[pid],'minutes':minutes,'made':dict(m),'received':dict(r),'activity':activity,
   'passing':passing,'touches':poss,'movement':speed,'hustle':hustle,'discrepancies':discrepancies,
   'missing':[k for k,x in [('passing',passing),('touches',poss),('movement',speed),('hustle',hustle)] if x is None]}
 coverage={'season':season,'officialPlayers':len(official),'pairRows':len(pairs),'sourceActorCounts':{k:len(v) for k,v in maps.items()},'pairMirrorIssues':len(mirror_issues),
  'pairAST':pm['AST'],'officialAST':total['AST'],'pairFGA':pm['FGA'],'officialFGA':total['FGA'],'passedFgaReceiverOverages':sum(p['discrepancies']['receivedFgaAboveOfficial']>0 for p in cards.values()),
  'passingCountDiscrepancyPlayers':len(issues),'excludedSelfPairRows':len(excluded_self),'pairFgaExceedsPassRows':len(nonpartition)}
 doc={'season':season,'design':__doc__,'coverage':coverage,'priors':priors,'priorMinutes':60,'assistCreditPriorMadeFgs':50,
  'definitions':{'passFGA':'All tracked field-goal attempts after a pass, broader than potential assists; FGM does not equal official AST. Never treat either as the other.',
   'activity':'Successful passing and passed-shot activity, with same60-minute activity prior as terminal role; official assist credit given a made passed shot uses50-made prior. No per-player simulation residuals or OVR ranks.',
   'movement':'Observed average movement during offense/defense, not top speed or measured off-ball separation ability.',
   'screening':'Successful screens linked to made FG, no denominator of all screen attempts; productivity, not a measured success rate.',
   'unknownSkills':'offBall,screen,handle,breakDbl are not inferred from activity counts. Keep the difference between measured activity and unknown skill explicit.'},
  'cards':cards,'mirrorIssues':mirror_issues,'excludedSelfPairs':excluded_self,'nonpartitionPairRows':nonpartition,'discrepancies':issues,'sources':{str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files.values()},'codeSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 output.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8');summary.append(coverage);print(json.dumps(coverage),flush=True)
(root/'tracking-coverage.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

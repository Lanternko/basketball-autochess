"""Reference-context opportunities and measured contest coverage, no rank fit."""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-impact-v3');ROOT.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');roles=read(f'reports/player-impact-v1/{season}-cards.json')['cards'];risk=read(f'reports/player-impact-v2/{season}-risk.json')['cards']
 totals=Counter();observed=defaultdict(Counter)
 for t in b['league']['teams']:
  for p in t['roster']:
   q={k:p['observed'][k] for k in ['MIN','FGM','FGA']};totals.update(q);observed[str(p['playerId'])].update(q)
 priorFG=totals['FGM']/totals['FGA'];cards={}
 # Tracking 6-ft attempts are a contest exposure proxy, not all paint shots.
 f=f'reports/defense-tenth/step4-t2/raw/{season}/0-rim.json';raw=read(f)['data']['resultSets'][0];dfga=Counter()
 for values in raw['rowSet']:
  row=dict(zip(raw['headers'],values));dfga[str(row['CLOSE_DEF_PERSON_ID'])]+=row['FGA_LT_06']
 leagueContestRate=sum(dfga.values())/totals['MIN']
 # A lineup's measured share normalizes across all five defenders. Using the
 # same universe for numerator/denominator avoids pretending 6-ft == paint.
 for pid,q in observed.items():
  m=roles[pid];fg=(q['FGM']+100*priorFG)/(q['FGA']+100)
  cards[pid]={'selfOpportunityRate':m['selfMakesPerMinute']/fg,'receiveOpportunityRate':m['assistedMakesPerMinute']/fg,
   'passOpportunityRate':m['assistsPerMinute']/priorFG,'passStolenPerMinute':risk[pid]['passStolenPerMinute'],
   'referenceMakeProbability':fg,'contestExposurePerMinute':(dfga[pid]+240*leagueContestRate)/(q['MIN']+240)}
 doc={'season':season,'design':'Frozen source FG% converts made-production priors to opportunity weights; does not divide by counterfactual FG%, so shooting/creation improvements retain value. Self/received attempt split is a proxy, not measured assisted misses. Passing uses one shared league FG conversion prior. Contest coverage uses official 6-ft tracked attempts/min with 240-minute prior. No on/off/ranking or named-player fitting.',
 'leagueFG':priorFG,'leagueContestRate':leagueContestRate,'cards':cards,'trackingSource':{'file':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()}}
 (ROOT/f'{season}-cards.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
 print(season,len(cards),flush=True)

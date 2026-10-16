import json
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-impact-v4');ROOT.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');old=read(f'reports/player-impact-v3/{season}-cards.json');roles=read(f'reports/player-impact-v1/{season}-cards.json')['cards'];risk=read(f'reports/player-impact-v2/{season}-risk.json')['cards'];obs=defaultdict(Counter)
 for t in b['league']['teams']:
  for p in t['roster']:obs[str(p['playerId'])].update({k:p['observed'][k] for k in ['MIN','FGM','FGA','FTA','TOV','AST']})
 total=sum(obs.values(),Counter());leagueFG=total['FGM']/total['FGA'];leagueFgaSurvival=total['FGA']/(total['FGA']+.44*total['FTA']+total['TOV'])
 cards={}
 for pid,o in obs.items():
  m=roles[pid];fg=(o['FGM']+100*leagueFG)/(o['FGA']+100)
  # Explicit FGA/terminal-use denominator: observed FG% is not make/touch.
  survival=(o['FGA']+100*leagueFgaSurvival)/(o['FGA']+.44*o['FTA']+o['TOV']+100)
  q=fg*survival
  cards[pid]={**old['cards'][pid],'selfOpportunityRate':m['selfMakesPerMinute']/q,
   'receiveOpportunityRate':m['assistedMakesPerMinute']/q,'passOpportunityRate':m['assistsPerMinute']/(leagueFG*leagueFgaSurvival),
   'referenceMakePerUse':q,'referenceFgaSurvival':survival}
 doc={'season':season,'cards':cards,'leagueFG':leagueFG,'leagueFgaSurvival':leagueFgaSurvival,
 'design':'Observed FG% denominator corrected for FTA/turnover terminal uses. All source-context factors frozen across counterfactual lineups. Passing matrix balances creator row demands and receiver column demands with structural zero self-pass. No player-specific fitted offsets, no rank/on-off fit. Assisted-miss split still estimated.'}
 (ROOT/f'{season}-cards.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
 print(season,len(cards),flush=True)

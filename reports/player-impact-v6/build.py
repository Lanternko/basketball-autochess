import json
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v6');root.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 b=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');old=read(f'reports/player-impact-v5/{season}-cards.json');risks=read(f'reports/player-impact-v2/{season}-risk.json')['cards'];roles=read(f'reports/player-impact-v1/{season}-cards.json')['cards'];obs=defaultdict(Counter)
 for t in b['league']['teams']:
  for p in t['roster']:obs[str(p['playerId'])].update({k:p['observed'][k] for k in ['MIN','FGA','FTA','TOV','AST']})
 total=sum(obs.values(),Counter());pb=sum(sum(m.get('putbackProxyCounts',{}).get(z+'A',0) for z in ['long','mid','short']) for m in old['cards'].values())
 passStolen=sum(v['passStolen'] for v in risks.values());prior=(total['FGA']-pb+.44*total['FTA']+total['TOV']-passStolen)/total['MIN'];fg=read(f'reports/player-impact-v4/{season}-cards.json')
 for pid,m in old['cards'].items():
  o=obs[pid];pbA=m.get('putbackProxyCounts',{}).get('shortA',0);lost=risks[pid]['passStolen']
  terminal=(max(0,o['FGA']-pbA)+.44*o['FTA']+max(0,o['TOV']-lost)+60*prior)/(o['MIN']+60)
  assisted=min(1,roles[pid]['assistedMakeShare']/max(.01,1-roles[pid]['putbackMakeShare']))
  m['terminalOpportunityRate']=terminal;m['receiveOpportunityRate']=terminal*assisted;m['selfOpportunityRate']=terminal*(1-assisted)
  m['passOpportunityRate']=((o['AST']+60*total['AST']/total['MIN'])/(o['MIN']+60))/(fg['leagueFG']*fg['leagueFgaSurvival'])
 old['design']='Direct official fresh FGA + .44 FTA + non-pass-stolen TOV per minute, 60-minute common-rate prior. Joint creator/receiver distribution preserves each player terminal demand, excludes immediate putback attempts (separate OREB path), forbids self assists, and reduces assisted opportunities when creator supply is inadequate. No named-player offsets or fitting to OVR/on-off.'
 (root/f'{season}-cards.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['input.mjs','worker.mjs','run.mjs','score.py','ovr-input.mjs','ovr-worker.mjs','ovr-run.mjs','verify.mjs']:
 s=Path('reports/player-impact-v5',name).read_text(encoding='utf-8').replace('player-impact-v5','player-impact-v6').replace('observed-fresh-zone-foul-5','conserved-terminal-opportunities-6').replace('observed-profiles-natural-role-ovr-5','conserved-terminal-natural-role-ovr-6').replace('profile-flow','terminal-flow').replace('profile-contests','terminal-contests')
 if name=='ovr-input.mjs':s=s.replace('"selfOpportunityRate",','"terminalOpportunityRate","selfOpportunityRate",')
 (root/name).write_text(s,encoding='utf-8')
s=Path('reports/player-impact-v5/engine.mjs').read_text(encoding='utf-8').replace('player-impact-v5','player-impact-v6').replace('profile-flow','terminal-flow').replace('profile-contests','terminal-contests')
(root/'engine.mjs').write_text(s,encoding='utf-8')

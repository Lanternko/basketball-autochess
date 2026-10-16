"""Observe putback allocation; never tune parameters from these residuals."""
import json
from pathlib import Path

root=Path('reports/player-impact-v23')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
protocol=read(root/'validation-protocol.json')
out={}
for season in protocol['seasons']:
 source=read(f'reports/player-impact-v22/{season}-putback-events.json')
 actual=source['cards'];choice=read(root/f'{season}-choice-rates.json')
 cell={'actual':source['totals'],'versions':{}}
 for version in ['22','23']:
  audits=[read(f'reports/player-impact-v{version}/runs/{season}-rotation-space-strict-{seed}.json')['putbackAudit'] for seed in protocol['seeds']]
  mean=lambda k:sum(a[k] for a in audits)/len(audits)
  fga=mean('fga');players=[]
  for pid,p in actual.items():
   predicted=sum(a['players'].get(pid,{}).get('fga',0) for a in audits)/len(audits)
   players.append({'playerId':int(pid),'actual':p['attempts'],'predicted':predicted,'error':predicted-p['attempts']})
  weights=sum(p['attempts'] for p in actual.values())
  cell['versions'][version]={'fga':fga,'fgm':mean('fgm'),'sampledFG':mean('fgm')/fga,'expectedFG':mean('expectedMakes')/fga,'allPlayersCountMAE':sum(abs(p['error']) for p in players)/len(players),'attemptWeightedCountMAE':sum(abs(p['error'])*actual[str(p['playerId'])]['attempts'] for p in players)/weights,'players':players}
 cell['selectedPlayers']={pid:{'actual':actual[str(pid)],'sourceChoice':choice['cards'][str(pid)],**{v:next(p for p in cell['versions'][v]['players'] if p['playerId']==pid) for v in ['22','23']}} for pid in [1628983,1629029,203999,201939,1629674] if str(pid) in actual}
 out[season]=cell
 print(season,{v:{k:round(x,5) for k,x in c.items() if k!='players'} for v,c in cell['versions'].items()},flush=True)
(root/'putback-fit-audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')

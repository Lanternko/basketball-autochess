"""Describe putback selection opportunities; do not mistake FGA/OREB for branch probability."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v23');root.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def seconds(s):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',s);return int(m[1] or 0)*60+float(m[2])
for season in ['2022-23','2023-24','2024-25','2025-26']:
 target=root/f'{season}-putback-choices.json'
 if target.exists():raise RuntimeError('Preserve source choice audit')
 sf=Path(f'reports/player-impact-v22/{season}-putback-events.json');source=read(sf);valid={g['id']:g for g in source['games']};mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json'
 totals=Counter();cards=defaultdict(Counter);games=[]
 for spec in read(mf)['sources']:
  if spec['id'] not in valid:continue
  actions=read(spec['file'])['data']['game']['actions'];miss=None;pending=None;rows=[];hits={e['index']:e for e in valid[spec['id']]['events']};joined=0
  for index,e in enumerate(actions):
   kind=e.get('actionType');sub=e.get('subType');pid=e.get('personId')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    if index in hits:
     assert pending is not None and pending['playerId']==pid
     pending['recordedFastPutback']=1;pending['made']=hits[index]['made'];joined+=1
    pending=None;miss='fieldGoal' if e.get('shotResult')=='Missed' else None
   elif kind=='freethrow':pending=None;miss='freeThrow' if e.get('shotResult')=='Missed' else None
   elif kind=='rebound' and sub=='offensive' and pid and 'team' not in e.get('qualifiers',[]):
    pending=None
    if miss=='fieldGoal':
     pending={'index':index,'playerId':pid,'teamId':e['teamId'],'recordedFastPutback':0,'made':0,'clockSeconds':seconds(e['clock'])};rows.append(pending)
   elif kind in ['turnover','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None;miss=None
  assert joined==len(hits)
  for r in rows:
   c=cards[r['playerId']];c['fgReboundOpportunities']+=1;c['recordedFastPutbacks']+=r['recordedFastPutback'];c['fastMakes']+=r['made']
   if r['clockSeconds']<=.3:
    c['engineTooLateRebounds']+=1;c['fastShotsAfterTooLateRebounds']+=r['recordedFastPutback']
   totals.update({'fgReboundOpportunities':1,'recordedFastPutbacks':r['recordedFastPutback'],'fastMakes':r['made'],'engineTooLateRebounds':int(r['clockSeconds']<=.3),'fastShotsAfterTooLateRebounds':r['recordedFastPutback']*int(r['clockSeconds']<=.3)})
  games.append({'id':spec['id'],'fold':int(spec['id'])%5,'rows':rows})
 assert totals['recordedFastPutbacks']==source['totals']['fieldGoalAttempts']
 for pid,c in cards.items():assert c['recordedFastPutbacks']<=c['fgReboundOpportunities']
 for pid in source['cards']:cards.setdefault(int(pid),Counter())
 out={'season':season,'design':'Strict same PBP definition as v22. Denominator individual offensive rebounds following missed FGs; numerator recorded same-player short FGA within 0-3 seconds. This is recorded-FGA incidence, NOT a direct branch-selection probability: foul misses, player TOV, nonshooting contacts, clock expiry can occur after choosing to put back. Survival correction and finite-horizon eligibility must be resolved before runtime use. No simulation output/rank/ON-OFF fit.','totals':dict(totals),'cards':{pid:dict(c) for pid,c in cards.items()},'games':games,'sourceHash':hashlib.sha256(sf.read_bytes()).hexdigest(),'codeHash':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 target.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,dict(totals),flush=True)

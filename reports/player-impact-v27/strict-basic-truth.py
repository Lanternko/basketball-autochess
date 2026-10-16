"""Individual PBP counts on exactly the strict replay game IDs; preserve discrepancies."""
import json,hashlib,sys
from pathlib import Path
from collections import Counter,defaultdict
root=Path('reports/player-impact-v27');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
keys=['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','oreb','dreb','stl','blk','tov']
for season in sys.argv[1:] or ['2025-26']:
 target=root/f'{season}-strict-basic-truth.json';assert not target.exists(),'Preserve source truth'
 tf=f'reports/player-impact-v1/{season}-on-court-truth.json';truth=read(tf);valid=set(truth['gameIds']);players={p['playerId']:p for p in truth['players']};counts=defaultdict(Counter)
 mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json';hashes={f:sha(f) for f in [str(Path(__file__)),tf,mf,'reports/player-impact-v26/validation-protocol.json']};totals=Counter();games=[]
 for spec in read(mf)['sources']:
  if spec['id'] not in valid:continue
  hashes[spec['file']]=sha(spec['file']);actions=read(spec['file'])['data']['game']['actions'];cg=defaultdict(Counter)
  def add(pid,k,n=1):
   assert pid in players,(spec['id'],pid,k)
   cg[pid][k]+=n;totals[k]+=n
  for e in actions:
   kind=e.get('actionType');pid=e.get('personId');made=e.get('shotResult')=='Made'
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    add(pid,'fga');add(pid,'fgm',int(made))
    if kind=='3pt':add(pid,'fg3a');add(pid,'fg3m',int(made))
    if made:
     add(pid,'pts',3 if kind=='3pt' else 2)
     if e.get('assistPersonId'):add(e['assistPersonId'],'ast')
    if e.get('blockPersonId'):assert not made;add(e['blockPersonId'],'blk')
   elif kind=='freethrow':
    add(pid,'fta');add(pid,'ftm',int(made));add(pid,'pts',int(made))
   elif kind=='turnover':
    if pid:add(pid,'tov')
    else:totals['teamOnlyTov']+=1
    if e.get('stealPersonId'):add(e['stealPersonId'],'stl')
   elif kind=='rebound' and pid and 'team' not in e.get('qualifiers',[]):
    assert e.get('subType') in ['offensive','defensive']
    add(pid,'oreb' if e['subType']=='offensive' else 'dreb')
  for pid,c in cg.items():counts[pid].update(c)
  games.append({'id':spec['id'],'players':{pid:dict(c) for pid,c in cg.items()}})
 dreb=read(f'reports/player-impact-v24/{season}-dreb-rates.json')['cards'];hashes[f'reports/player-impact-v24/{season}-dreb-rates.json']=sha(f'reports/player-impact-v24/{season}-dreb-rates.json')
 for pid,p in players.items():
  c=counts[pid]
  for k in ['fga','fgm','fg3a','fg3m']:assert c[k]==p['own'].get(k,0),(season,pid,k,c[k],p['own'].get(k,0))
  assert c['dreb']==dreb[str(pid)]['sourceDreb'],(season,pid,'dreb')
  assert c['pts']==2*c['fgm']+c['fg3m']+c['ftm']
 assert len(games)==truth['strictGames']
 out={'season':season,'design':'Individual PBP FGA/FGM/3P/FT/PTS/AST/OREB/DREB/STL/BLK/TOV on exact strict source games. Team-only TOV kept separate, rebound team qualifiers excluded. Every individual FG ledger matches independent on-court source truth; every individual DREB matches v24 risk-set truth. Floor minutes use strict stints. PTS versus official selected-game box checked separately by replay scorer; raw PBP counts not silently corrected. No runtime use or fitted skill.', 'totals':dict(totals),'players':[{'playerId':pid,'name':p['name'],'seconds':p['on'].get('seconds',0),'stats':{k:counts[pid][k] for k in keys}} for pid,p in players.items()],'games':games,'hashes':hashes}
 target.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,'players',len(players),'games',len(games),'totals',dict(totals),flush=True)

import json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-impact-v42')
keys=['fga','fgm','longA','longM','midA','midM','shortA','shortM']
for season in json.loads((ROOT/'protocol.json').read_text(encoding='utf-8'))['seasons']:
 prior=json.loads(Path(f'reports/player-impact-v1/{season}-on-court-truth.json').read_text(encoding='utf-8'));valid=set(prior['gameIds']);old={p['playerId']:p for p in prior['players']}
 filename=Path('reports/defense-b1/stints.jsonl') if season=='2025-26' else Path(f'reports/defense-seventh/{season}/stints/stints.jsonl')
 games=defaultdict(list)
 for line in filename.open(encoding='utf-8'):
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:games[s['id']].append(s)
 players=defaultdict(lambda:{'on':Counter(),'off':Counter(),'onSeconds':0.,'offSeconds':0.});total=Counter()
 for gid,stints in games.items():
  counts=defaultdict(Counter);active=defaultdict(set);seconds=defaultdict(float);gameOn=defaultdict(Counter);gameSeconds=0.
  for s in stints:
   gameSeconds+=s['seconds']
   for t in s['teams']:
    tid=t['teamId'];active[tid].update(t['players']);c={k:t['opponent'][k] for k in keys};counts[tid].update(c);total.update(c)
    assert c['fga']==c['longA']+c['midA']+c['shortA'] and c['fgm']==c['longM']+c['midM']+c['shortM']
    for pid in t['players']:gameOn[pid].update(c);seconds[pid]+=s['seconds']
  for tid,ids in active.items():
   for pid in ids:
    p=players[pid];p['on'].update(gameOn[pid]);p['off'].update({k:counts[tid][k]-gameOn[pid][k] for k in keys});p['onSeconds']+=seconds[pid];p['offSeconds']+=gameSeconds-seconds[pid]
 assert set(games)==valid
 for pid,p in players.items():
  assert abs(p['onSeconds']-old[pid]['on'].get('seconds',0))<1e-6,(season,pid)
  for a,b in [('fga','opp_fga'),('fgm','opp_fgm'),('longA','opp_fg3a'),('longM','opp_fg3m')]:
   assert p['on'][a]==old[pid]['on'].get(b,0),(season,pid,a)
   assert p['off'][a]==old[pid]['off'].get(b,0),(season,pid,a,'off')
 for k in keys:assert sum(p['on'][k] for p in players.values())==5*total[k]
 out={'season':season,'games':len(games),'gameIds':sorted(games),'total':dict(total),'players':[{'playerId':pid,'name':old[pid]['name'],**p} for pid,p in players.items()],'sourceSHA256':hashlib.sha256(filename.read_bytes()).hexdigest(),'priorTruthSHA256':hashlib.sha256(Path(f'reports/player-impact-v1/{season}-on-court-truth.json').read_bytes()).hexdigest(),'definition':'All recorded FGA including putbacks. short = restricted and non-RA paint 2PT; long = all 3PT; mid = non-paint 2PT. FGA per48 defensive minutes, not a possession count or causal willingness.'}
 (ROOT/f'{season}-defense-truth.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8');print(json.dumps({'season':season,'games':len(games),'players':len(players),'fga':total['fga'],'verifiedPriorTruth':True}),flush=True)

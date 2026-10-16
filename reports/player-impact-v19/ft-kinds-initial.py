import json,hashlib,sys
from pathlib import Path
from collections import defaultdict,Counter
root=Path('reports/player-impact-v19');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);m=read(('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json');totals=Counter();players=defaultdict(Counter);games={};hashes={};ambiguous=[]
 for spec in m['sources']:
  if spec['id'] not in valid:continue
  a=read(spec['file'])['data']['game']['actions'];fouls=defaultdict(list)
  for e in a:
   if e.get('actionType')=='foul':fouls[(e.get('period'),e.get('clock'))].append(e)
  game=defaultdict(Counter)
  for e in a:
   if e.get('actionType')=='freethrow' and e.get('shotResult') in ['Made','Missed']:
    pid=e.get('personId');qs=e.get('qualifiers',[])
    if not pid:continue
    candidates=[f for f in fouls[(e.get('period'),e.get('clock'))] if f.get('foulDrawnPersonId')==pid and f.get('teamId')!=e.get('teamId')]
    shooting=[f for f in candidates if f.get('descriptor')=='shooting']
    if 'technical' in qs or 'Technical' in e.get('description',''):kind='technical'
    elif shooting and len({f.get('descriptor') for f in candidates})==1:kind='shooting'
    elif not shooting and candidates:kind='nonshooting'
    else:kind='unresolved'
    totals[kind]+=1;totals['fta']+=1;players[pid][kind]+=1;players[pid]['fta']+=1;game[str(pid)][kind]+=1;game[str(pid)]['fta']+=1
    if kind=='unresolved' and len(ambiguous)<12:ambiguous.append({'id':spec['id'],'ft':{k:e.get(k) for k in ['period','clock','actionNumber','personId','qualifiers','subType','description']},'candidates':[{k:f.get(k) for k in ['actionNumber','subType','descriptor','foulDrawnPersonId','qualifiers']} for f in candidates]})
   elif e.get('isFieldGoal') and e.get('actionType') in ['2pt','3pt']:
    players[e['personId']]['fga']+=1;game[str(e['personId'])]['fga']+=1;totals['fga']+=1
  games[spec['id']]={pid:dict(v) for pid,v in game.items()};hashes[spec['file']]=hashlib.sha256(Path(spec['file']).read_bytes()).hexdigest()
 out={'season':season,'design':'Strict PBP FT audit. Shooting foul matched by period/clock/drawn player; technical qualifier overrides. Mixed/missing foul linkage remains unresolved, never assumed shooting. Count every Made/Missed FT action; source event counts not yet reconciled to official box totals. No model inputs modified.','totals':dict(totals),'players':{str(pid):dict(v) for pid,v in players.items()},'games':games,'unresolvedExamples':ambiguous,'sources':hashes}
 (root/f'{season}-ft-kinds-initial.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8');print(season,dict(totals),flush=True)

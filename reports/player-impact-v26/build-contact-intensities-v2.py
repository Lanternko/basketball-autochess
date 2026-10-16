"""Source counts/exposure for a joint ordinary-contact and terminal-intensity model."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict

root=Path('reports/player-impact-v26');root.mkdir(exist_ok=True)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def seconds(value):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',value);assert m;return int(m[1] or 0)*60+float(m[2])

for season in ['2022-23','2023-24','2024-25','2025-26']:
 target=root/f'{season}-contact-intensities.json'
 if target.exists():
  print(season,'existing source preserved',flush=True);continue
 cf=f'reports/player-impact-v25/{season}-contact-policy.json';old=read(cf);valid={g['id']:g for g in old['games']}
 tf=f'reports/player-impact-v1/{season}-on-court-truth.json';truth=read(tf)
 sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl'
 mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json'
 bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');fixtures={g['id']:g for g in bundle['league']['schedule']}
 stints=defaultdict(list)
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  s=json.loads(line)
  if s['id'] in valid and s['seconds']>=0:stints[s['id']].append(s)
 games=[];totals=Counter();cards=defaultdict(Counter);hashes={f:sha(f) for f in [cf,sf,mf,tf,str(Path(__file__))]}
 for spec in read(mf)['sources']:
  if spec['id'] not in valid:continue
  gid=spec['id'];fixture=fixtures[gid];actions=read(spec['file'])['data']['game']['actions'];hashes[spec['file']]=sha(spec['file']);ps=defaultdict(Counter);counts=Counter();unassigned=0
  for s in stints[gid]:
   for t in s['teams']:
    for pid in t['players']:ps[pid]['minutes']+=s['seconds']/60
  for e in valid[gid]['rows']:
   if e['group']=='ordinary':ps[e['choice'][0]]['contacts']+=1;counts['contacts']+=1
  shots=Counter((e.get('period'),e.get('clock'),e.get('personId')) for e in actions if e.get('isFieldGoal') and e.get('actionType') in ['2pt','3pt']);home=away=0
  for e in actions:
   typ=e.get('actionType');kind=None;pid=e.get('personId');offense=None
   if e.get('isFieldGoal') and typ in ['2pt','3pt']:kind='fga';offense=e['teamId']
   elif typ=='turnover':kind='tov';offense=e['teamId']
   elif typ=='foul' and e.get('descriptor')=='shooting':
    pid=e.get('foulDrawnPersonId');assert pid
    if not shots[(e.get('period'),e.get('clock'),pid)]:kind='unrecordedShootingFouls';offense=e.get('possession')
   if kind:
    assert offense in [fixture['homeId'],fixture['awayId']]
    lead=home-away if offense==fixture['homeId'] else away-home;secs=seconds(e['clock']);policy=e['period']>=4 and .3<secs<=27 and 0<lead<=6
    if not policy:
     counts[kind]+=1
     if pid:ps[pid]['terminal']+=1
     else:assert kind=='tov';unassigned+=1
   for key in ['scoreHome','scoreAway']:
    value=e.get(key)
    if value is not None and str(value).strip():
     value=float(value);assert value>=0 and value.is_integer()
     if key=='scoreHome':home=int(value)
     else:away=int(value)
  expected=valid[gid]['counts'].get('ordinary',{})
  for key in ['fga','tov','unrecordedShootingFouls']:assert counts[key]==expected.get(key,0),(gid,key)
  assert counts['contacts']==expected.get('nonshootingContact',0)
  assert sum(p['terminal'] for p in ps.values())+unassigned==sum(counts[k] for k in ['fga','tov','unrecordedShootingFouls'])
  for pid,c in ps.items():assert str(pid) in old['players'];cards[pid].update(c)
  totals.update(counts);totals['unassignedTerminal']+=unassigned
  games.append({'id':gid,'fold':int(gid)%5,'players':{pid:dict(c) for pid,c in ps.items()},'unassignedTerminal':unassigned})
 assert totals['contacts']==old['groups']['ordinary']['nonshootingContact']
 for p in truth['players']:
  assert abs(cards[p['playerId']]['minutes']-p['on'].get('seconds',0)/60)<1e-5,(season,p['playerId'],cards[p['playerId']]['minutes'],p['on'].get('seconds',0)/60)
 for pid in old['players']:cards.setdefault(int(pid),Counter())
 total_minutes=sum(c['minutes'] for c in cards.values());totals['playerMinutes']=total_minutes
 out={'season':season,'design':'Joint ordinary contact victim counts C and ordinary terminal counts N (FGA+TOV+unrecorded shooting foul; all FGA including putbacks) with strict same-game floor minutes M. Same pre-action source policy split as v25. All contact victims known. Person-unassigned TOV retained separately with team-minute exposure. Goal: test whether sum individual C/min and N/min can represent lineup-dependent event intensity instead of a common league contact probability. Source production/style, not causal foul-drawing skill. No runtime changes or simulation residual fit. Minutes include full strict floor exposure; ordinary-state time is not separately identified, so rates are descriptive token intensities and must be validated in the engine.','totals':dict(totals),'cards':{pid:dict(c) for pid,c in cards.items()},'players':old['players'],'games':games,'hashes':hashes}
 target.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,dict(totals),flush=True)

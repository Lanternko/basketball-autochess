"""Audit ordinary vs engine-policy endgame contacts and actual drawn-player risk sets."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict

root=Path('reports/player-impact-v25');root.mkdir(exist_ok=True)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def seconds(value):
 m=re.fullmatch(r'PT(?:(\d+)M)?([\d.]+)S',value);assert m;return int(m[1] or 0)*60+float(m[2])

for season in ['2022-23','2023-24','2024-25','2025-26']:
 target=root/f'{season}-contact-policy.json'
 if target.exists():raise RuntimeError('Preserve source audit')
 tf=f'reports/player-impact-v1/{season}-on-court-truth.json';valid=set(read(tf)['gameIds'])
 mf=('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json'
 sf='reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl'
 bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json');fixtures={g['id']:g for g in bundle['league']['schedule']}
 players={p['playerId']:p['name'] for t in bundle['league']['teams'] for p in t['roster']}
 stints=defaultdict(list)
 for line in Path(sf).read_text(encoding='utf-8').splitlines():
  row=json.loads(line)
  if row['id'] in valid:stints[row['id']].append(row)
 games=[];totals=Counter();groups=defaultdict(Counter);ftgroups=defaultdict(Counter);issues=[];hashes={f:sha(f) for f in [tf,mf,sf,str(Path(__file__))]}
 for spec in read(mf)['sources']:
  if spec['id'] not in valid:continue
  fixture=fixtures[spec['id']];actions=read(spec['file'])['data']['game']['actions'];hashes[spec['file']]=sha(spec['file'])
  shots=Counter((e.get('period'),e.get('clock'),e.get('personId')) for e in actions if e.get('isFieldGoal') and e.get('actionType') in ['2pt','3pt'])
  fouls=defaultdict(list);policies={};rows=[];gc=defaultdict(Counter);home=away=0
  for index,e in enumerate(actions):
   typ=e.get('actionType');desc=e.get('descriptor');sub=e.get('subType');kind=None;offense=None
   if e.get('isFieldGoal') and typ in ['2pt','3pt']:kind='fga';offense=e['teamId']
   elif typ=='turnover':kind='tov';offense=e['teamId']
   elif typ=='foul':
    fouls[(e.get('period'),e.get('clock'))].append((index,e))
    if desc=='shooting':
     pid=e.get('foulDrawnPersonId');assert pid,'Missing source drawn shooting player'
     matches=shots[(e.get('period'),e.get('clock'),pid)]
     kind='unrecordedShootingFouls' if not matches else 'recordedShootingFouls';offense=e.get('possession')
     if matches>1:totals['multipleShotMatches']+=1
    elif sub=='personal' and e.get('possession') and e.get('teamId')!=e['possession']:kind='nonshootingContact';offense=e['possession']
   if kind:
    if offense not in [fixture['homeId'],fixture['awayId']]:raise RuntimeError(('Missing terminal offense',spec['id'],index,kind,e))
    secs=seconds(e['clock']);lead=home-away if offense==fixture['homeId'] else away-home
    policy=e['period']>=4 and .3<secs<=27 and 0<lead<=6;group='policyEndgame' if policy else 'ordinary'
    totals[kind]+=1;groups[group][kind]+=1;gc[group][kind]+=1;policies[index]=group
    if kind=='nonshootingContact':
     pid=e.get('foulDrawnPersonId')
     if not pid:groups[group]['missingDrawn']+=1;gc[group]['missingDrawn']+=1
     else:
      matches=[s for s in stints[spec['id']] if s['startIndex']<=index<s['endIndex']]
      if len(matches)!=1:issues.append({'id':spec['id'],'index':index,'reason':'stint cardinality','matches':len(matches)})
      else:
       own=next(t['players'] for t in matches[0]['teams'] if t['teamId']==offense)
       if pid not in own:issues.append({'id':spec['id'],'index':index,'reason':'drawn recipient outside lineup','playerId':pid})
       else:
        assert len(own)==5 and len(set(own))==5 and all(p in players for p in own)
        rows.append({'index':index,'group':group,'choice':[pid,*own]});groups[group]['mappedDrawn']+=1;gc[group]['mappedDrawn']+=1
   for key in ['scoreHome','scoreAway']:
    value=e.get(key)
    if value is not None and str(value).strip():
     value=float(value);assert value>=0 and value.is_integer()
     if key=='scoreHome':home=int(value)
     else:away=int(value)
  for e in actions:
   if e.get('actionType')!='freethrow' or e.get('shotResult') not in ['Made','Missed'] or not e.get('personId'):continue
   pid=e['personId'];candidates=[(i,f) for i,f in fouls[(e.get('period'),e.get('clock'))] if f.get('foulDrawnPersonId')==pid and f.get('teamId')!=e.get('teamId')]
   shooting=[f for _,f in candidates if f.get('descriptor')=='shooting']
   if 'technical' in e.get('qualifiers',[]) or 'technical' in e.get('description','').lower():kind='technical'
   elif shooting and len({f.get('descriptor') for _,f in candidates})==1:kind='shooting'
   elif not shooting and candidates:kind='nonshooting'
   else:kind='unresolved'
   contact_groups={policies.get(i,'outsidePersonalContactScope') for i,_ in candidates};group=next(iter(contact_groups)) if len(contact_groups)==1 else 'unresolvedContactGroup'
   ftgroups[group][kind]+=1
  games.append({'id':spec['id'],'fold':int(spec['id'])%5,'counts':{k:dict(v) for k,v in gc.items()},'rows':rows})
 old=read(f'reports/player-impact-v19/{season}-foul-contact-audit.json')['counts']
 for k in ['fga','tov','unrecordedShootingFouls','recordedShootingFouls']:assert totals[k]==old[k],(k,totals[k],old[k])
 assert totals['nonshootingContact']==old['defensiveNonshootingPersonalFouls']
 assert not issues,issues[:10]
 rate=lambda c:c['nonshootingContact']/(c['nonshootingContact']+c['fga']+c['tov']+c['unrecordedShootingFouls'])
 out={'season':season,'design':'Match archived v19 contact scope exactly, then partition using the current engine intentional-foul policy: period>=4, 0.3<clock<=27 seconds, offensive pre-action lead1..6. Pre-action scores updated sequentially, not post-make scores. This is policy eligibility, not a claim actual fouls were intentional. Ordinary contact recipient rows use actual drawn player and own five; unknown drawn IDs retained in rate, excluded from recipient fit. No simulation output or rank fit. FT categories exactly v19 proxy; contact groups outside personal scope/unresolved retained.','counts':dict(totals),'groups':{k:dict(v) for k,v in groups.items()},'contactRates':{k:rate(c) for k,c in groups.items()},'ftGroups':{k:dict(v) for k,v in ftgroups.items()},'players':players,'games':games,'issues':issues,'hashes':hashes}
 target.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8');print(season,'groups',out['groups'],'rates',out['contactRates'],'FTgroups',out['ftGroups'],flush=True)

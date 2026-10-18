import json,hashlib
from pathlib import Path
from collections import Counter
root=Path('reports/player-impact-v19');read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
for season in ['2022-23','2023-24','2024-25','2025-26']:
 m=read(('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')+'/manifest.json');valid=set(read(f'reports/player-impact-v1/{season}-on-court-truth.json')['gameIds']);c=Counter();detail=Counter()
 for spec in m['sources']:
  if spec['id'] not in valid:continue
  for e in read(spec['file'])['data']['game']['actions']:
   typ=e.get('actionType')
   if e.get('isFieldGoal') and typ in ['2pt','3pt']:c['fga']+=1
   elif typ=='turnover':c['tov']+=1
   elif typ=='foul':
    desc=e.get('descriptor','');sub=e.get('subType','');detail[(sub,desc)]+=1
    if desc=='shooting':c['shootingFouls']+=1
    elif sub=='personal' and e.get('possession') and e.get('teamId')!=e['possession']:c['defensiveNonshootingPersonalFouls']+=1
    elif sub=='technical':c['technicalFouls']+=1
 ft=read(root/f'{season}-ft-kinds.json')['totals'];terminal=c['fga']+c['tov']+c['shootingFouls'];n=c['defensiveNonshootingPersonalFouls'];rate=n/(n+terminal)
 out={'season':season,'counts':dict(c),'shootingAndFgaMayOverlap':True,'design':'Source contact-frequency diagnostic only. Denominator FGA+TOV+shooting foul records includes overlap on and-one; not a validated terminal count. Personal fouls by non-possession team and non-shooting descriptor counted as defensive nonshooting contacts. No model option changed.','roughNonshootingContactRate':rate,'ftKinds':ft,'foulSubtypes':[{'subType':k[0],'descriptor':k[1],'count':v} for k,v in detail.most_common()],'sourceFTKindsSHA256':hashlib.sha256((root/f'{season}-ft-kinds.json').read_bytes()).hexdigest()}
 (root/f'{season}-foul-contact-audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(season,'nonshootContacts',n,'roughRate',round(rate,5),'sourceOtherFTA',ft.get('nonshooting',0)+ft.get('technical',0),'shootingFTA',ft['shooting'],flush=True)

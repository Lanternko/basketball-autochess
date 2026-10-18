import json,re,datetime,hashlib
from pathlib import Path
import pdfplumber
D=Path('reports/defense-tenth/step3-a')
for s in ['2023-24','2024-25']:
 roster=json.loads((D/f'opening-{s}.json').read_text(encoding='utf-8'))['teams']
 names={}
 for t in roster:
  name=t['name']
  for suffix in ['Hawks','Celtics','Nets','Hornets','Bulls','Cavaliers','Mavericks','Nuggets','Pistons','Warriors','Rockets','Pacers','Clippers','Lakers','Grizzlies','Heat','Bucks','Timberwolves','Pelicans','Knicks','Thunder','Magic','76ers','Suns','TrailBlazers','Trail Blazers','Kings','Spurs','Raptors','Jazz','Wizards']:
   if name.endswith(' '+suffix):name=name[:-(len(suffix)+1)]
  names[name]=t['id']
 names['L.A. Lakers']=1610612747;names['LA Clippers']=1610612746
 for wrong in ['LA','Los Angeles']:names.pop(wrong,None)
 fixtures=[]
 with pdfplumber.open(D/f'opening-schedule-{s}.pdf') as f:
  for page in f.pages:
   for line in page.extract_text().splitlines():
    m=re.match(r'(?:\d+\s+)?\w+\.\s+(\d+/\d+/\d+)\s+(.+?)\s+\d+:\d+\s+[AP]M',line)
    if not m:continue
    raw=m[2].strip();candidates=[(a,b) for a in names for b in names if raw==a+' '+b or raw==a+' at '+b or raw==a+' vs '+b]
    assert len(candidates)==1,(s,line,candidates)
    away,home=candidates[0];date=datetime.datetime.strptime(m[1],'%m/%d/%y').strftime('%Y-%m-%d')
    fixtures.append({'id':f'opening-fixed-{len(fixtures):04}','date':date,'homeId':names[home],'awayId':names[away],'neutral':False})
  f.pages[0].to_image(resolution=70).save(D/f'opening-schedule-{s}-page0.png')
 assert len(fixtures)==1200,(s,len(fixtures))
 assert all(sum(t['id'] in [g['homeId'],g['awayId']] for g in fixtures)==80 for t in roster)
 ids=[t['id'] for t in sorted(roster,key=lambda t:t['name'])]
 dates=['2023-12-04','2023-12-08'] if s=='2023-24' else ['2024-12-11','2024-12-15']
 for rnd,date in enumerate(dates):
  order=ids if rnd==0 else ids[1:]+ids[:1]
  for i in range(0,30,2):fixtures.append({'id':f'opening-tbd-{rnd}-{i//2}','date':date,'homeId':order[i],'awayId':order[i+1],'neutral':False,'assumedTBD':True})
 fixtures.sort(key=lambda g:(g['date'],g['id']))
 assert all(sum(t['id'] in [g['homeId'],g['awayId']] for g in fixtures)==82 for t in roster)
 (D/f'opening-schedule-{s}.json').write_text(json.dumps({'published':'2023-08-17' if s=='2023-24' else '2024-08-15','fixedGames':1200,'assumedTBDGames':30,'schedule':fixtures,'PDFHash':hashlib.sha256((D/f'opening-schedule-{s}.pdf').read_bytes()).hexdigest(),'rule':'Alphabetical team-city order; pair0 consecutive, pair1 rotate left1. No Cup results; final excluded.'},indent=2)+'\n',encoding='utf-8')
 print(s,len(fixtures))

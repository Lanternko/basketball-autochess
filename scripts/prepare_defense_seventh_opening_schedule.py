"""Parse only the schedule PDF dated August14,2025. TBD is not future data."""
from pathlib import Path
import json,re,datetime,pdfplumber,hashlib
R=Path(__file__).resolve().parents[1];O=R/'data/defense-seventh/preseason-2025-26'
rosters=json.loads((O/'opening-rosters.json').read_text(encoding='utf-8'));teams=rosters['teams']
def team(s):
 s={'L.A. Lakers':'Los Angeles Lakers'}.get(s.strip(),s.strip())
 a=[t for t in teams if s in t['name']];assert len(a)==1,(s,a);return a[0]['id']
games=[]
with pdfplumber.open(O/'opening-schedule.pdf') as pdf:
 for page in pdf.pages:
  for line in page.extract_text().splitlines():
   m=re.match(r'\w+\.\s+(\d+/\d+/\d+)\s+(.+?)\s+(at|vs)\s+(.+?)\s+\d+:\d+\s+[AP]M',line)
   if not m:continue
   date=datetime.datetime.strptime(m[1],'%m/%d/%y').strftime('%Y-%m-%d');a,b=team(m[2]),team(m[4]);home,away=(b,a) if m[3]=='at' else (a,b)
   games.append({'id':f'preseason-fixed-{len(games):04}','date':date,'homeId':home,'awayId':away,'neutralSite':m[3]=='vs'})
counts={t['id']:sum(t['id'] in [g['homeId'],g['awayId']] for g in games) for t in teams};assert len(games)==1200 and set(counts.values())=={80},(len(games),counts)
# Two unknown Cup-week games: fixed cyclic pairings, independent of strengths,
# results or future Cup qualification. Reverse the home/away for the second.
ids=[t['id'] for t in sorted(teams,key=lambda t:t['name'])]
for round,date in enumerate(['2025-12-11','2025-12-15']):
 order=ids if round==0 else ids[1:]+ids[:1]
 for i in range(0,30,2):games.append({'id':f'preseason-tbd-{round}-{i//2}','date':date,'homeId':order[i],'awayId':order[i+1],'neutralSite':False,'assumedTBD':True})
games.sort(key=lambda g:(g['date'],g['id']))
assert all(sum(t['id'] in [g['homeId'],g['awayId']] for g in games)==82 for t in teams)
out={'published':'2025-08-14','fixedGames':1200,'assumedTBDGames':30,'schedule':games,'hash':hashlib.sha256((O/'opening-schedule.pdf').read_bytes()).hexdigest(),'rule':'1200 announced fixtures plus two fixed cyclic-pairing Cup-week fixtures per team; no actual Cup results, later opponents or postponements. NBA Cup final is excluded from regular-season statistics.'}
(O/'opening-schedule.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(len(games),counts)

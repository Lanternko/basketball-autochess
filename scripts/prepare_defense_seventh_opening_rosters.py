"""Extract the dated opening roster document, never a live roster page.
Name/ID/position/body joins are identity only; future statistics are discarded.
Run with the bundled Python PDF runtime.
"""
from pathlib import Path
from functools import lru_cache
import json,re,unicodedata,pdfplumber,hashlib
R=Path(__file__).resolve().parents[1];O=R/'data/defense-seventh/preseason-2025-26'
def read(f):return json.loads((R/f).read_text(encoding='utf-8'))
league=read('data/season-league.json');previous=read('data/defense-seventh/2024-25/league.json')
def normal(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();s=re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s);return re.sub('[^a-z]','',s)
aliases={'camjohnson':'cameronjohnson','ronholland':'ronaldholland','pjwashington':'pjwashington','paulreed':'paulreed'}
known={}
for t in [*previous['teams'],*league['teams']]:
 for p in t['roster']:known[normal(p['name'])]=p
for p in [{'playerId':1642850,'name':'Thomas Sorber','pos':'C','heightInches':81,'bodyWeight':263},{'playerId':1630284,'name':'Kevon Harris','pos':'SG','heightInches':77,'bodyWeight':216},{'playerId':1642365,'name':'Nikola Durisic','pos':'SF','heightInches':80,'bodyWeight':218}]:known[normal(p['name'])]=p
for p in [{'playerId':1642947,'name':'Eli Ndiaye','pos':'C','heightInches':82,'bodyWeight':209},{'playerId':1642926,'name':'Tamar Bates','pos':'SG','heightInches':76,'bodyWeight':195},{'playerId':1642893,'name':'Alex Toohey','pos':'SF','heightInches':80,'bodyWeight':223}]:known[normal(p['name'])]=p
# Previous official logs sometimes abbreviate names; current identity catalog
# supplies the full name but none of its measured capabilities.
groups=[(0,240,555,['Atlanta','Boston','Brooklyn','Charlotte','Chicago']),(1,60,390,['Cleveland','Dallas','Denver','Detroit','Golden State']),(1,395,752,['Houston','Indiana','LA Clippers','Los Angeles Lakers','Memphis']),(2,72,407,['Miami','Milwaukee','Minnesota','New Orleans','New York']),(2,416,752,['Oklahoma City','Orlando','Philadelphia','Phoenix','Portland']),(3,84,460,['Sacramento','San Antonio','Toronto','Utah','Washington'])]
teams=[];unmatched=[]
with pdfplumber.open(O/'opening-rosters.pdf') as pdf:
 for pg,top,bottom,names in groups:
  rows={}
  for w in pdf.pages[pg].extract_words():
   if top<w['top']<bottom:rows.setdefault(round(w['top']),[]).append(w)
  players=[[] for _ in range(5)];inactive=False
  for y,words in sorted(rows.items()):
   line=' '.join(w['text'] for w in words)
   if 'INACTIVE/TWO-WAY' in line:inactive=True;continue
   if y<=top+3 or line.startswith('* Indicates') or line=='# # #':continue
   if line.isupper():continue
   words.sort(key=lambda w:w['x0']);centers=[85,187,302,418,525] if pg==1 and top>350 else [99,218,328,428,527]
   @lru_cache(None)
   def partition(j,col):
    if col==5:return (0,[]) if j==len(words) else (1e9,[])
    best=(1e9,[])
    for n in range(min(6,len(words)-j)+1):
     phrase=words[j:j+n];name=' '.join(w['text'] for w in phrase).lstrip('*');key=normal(name)
     cost=0 if not n else ((0 if aliases.get(key,key) in known else 25)+abs((phrase[0]['x0']+phrase[-1]['x1'])/2-centers[col])/20)
     tail,parts=partition(j+n,col+1)
     if cost+tail<best[0]:best=(cost+tail,[[w['text'] for w in phrase]]+parts)
    return best
   _,cols=partition(0,0)
   for col,parts in enumerate(cols):
    if not parts:continue
    name=' '.join(parts);two=name.startswith('*');name=name.lstrip('*');key=normal(name);p=known.get(aliases.get(key,key))
    if not p:unmatched.append({'team':names[col],'name':name,'inactive':inactive,'twoWay':two});continue
    players[col].append({'playerId':p['playerId'],'name':name,'pos':p['pos'],'courtPosition':p.get('courtPosition',p['pos']),'heightInches':p.get('heightInches',78),'bodyWeight':p.get('bodyWeight',220),'inactiveAtPublication':inactive and not two,'twoWay':two})
  for name,ps in zip(names,players):
   match=[t for t in league['teams'] if name.lower() in t['name'].lower() or (name=='LA Clippers' and 'Clippers' in t['name'])]
   assert len(match)==1,(name,match)
   teams.append({'id':match[0]['id'],'name':match[0]['name'],'roster':ps})
result={'published':'2025-10-20','teams':teams,'unmatched':unmatched,'PDFHash':hashlib.sha256((O/'opening-rosters.pdf').read_bytes()).hexdigest(),'identityOnly':True,'identityWhitelist':['playerId','name','pos','courtPosition','heightInches','bodyWeight'],'definition':'Roster membership and inactive/two-way flags from dated NBA release. Identity join only; no 2025-26 statistics, minutes, availability or transactions used.'}
(O/'opening-rosters.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'teams':len(teams),'matched':sum(len(t['roster']) for t in teams),'unmatched':unmatched},ensure_ascii=False))

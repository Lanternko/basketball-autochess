import json,re,unicodedata,hashlib
from pathlib import Path
from functools import lru_cache
import pdfplumber
from html import unescape
D=Path('reports/defense-tenth/step3-a')
def normal(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 return re.sub('[^a-z]','',re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s))
known={}; teamids={}
for s in ['2022-23','2023-24','2024-25','2025-26']:
 l=json.loads(Path('data/season-league.json' if s=='2025-26' else f'data/defense-seventh/{s}/league.json').read_text(encoding='utf-8'))
 for t in l['teams']:
  teamids[t['name']]=t['id']
  for p in t['roster']:known[normal(p['name'])]={'playerId':p['playerId'],'name':p['name']}
aliases={'camjohnson':'cameronjohnson','chislivingston':'chrislivingston','natewilliams':'jeenathanwilliams','kenyonmartin':'kjmartin','kenyonmartinjr':'kjmartin','ronholland':'ronaldholland','kennethlofton':'kennethloftonjr','nickeilalexanderwalker':'nickeilalexanderwalker'}
aliases.update(ishmailwainright='ishwainright',aleksandarvezenkov='sashavezenkov',tywashington='tytywashington')
def identity(name):
 key=normal(name);k=aliases.get(key,key);p=known.get(key) or known.get(k)
 if not p:
  # Identity label only; unresolved entrants receive the preregistered prior.
  p={'playerId':-int(hashlib.sha256(key.encode()).hexdigest()[:8],16),'name':name,'unresolvedIdentity':True}
 return p.copy()
def tid(name):
 name=name.replace('TrailBlazers','Trail Blazers')
 if name=='LA Clippers' or name=='Los Angeles Clippers':return 1610612746
 m=[v for k,v in teamids.items() if name.lower() in k.lower()]
 assert len(set(m))==1,(name,m)
 return m[0]
groups=[(0,224,488,['Atlanta','Boston','Brooklyn','Charlotte','Chicago']),(0,488,780,['Cleveland','Dallas','Denver','Detroit','Golden State']),(1,64,363,['Houston','Indiana','LA Clippers','Los Angeles Lakers','Memphis']),(1,363,780,['Miami','Milwaukee','Minnesota','New Orleans','New York']),(2,76,352,['Oklahoma City','Orlando','Philadelphia','Phoenix','Portland']),(2,352,780,['Sacramento','San Antonio','Toronto','Utah','Washington'])]
teams=[]
with pdfplumber.open(D/'opening-2023-24.pdf') as pdf:
 for page,top,bottom,names in groups:
  rows={}
  for w in pdf.pages[page].extract_words():
   if top+5<w['top']<bottom-3:rows.setdefault(round(w['top']),[]).append(w)
  ps=[[] for _ in names];inactive=False
  for y,ws in sorted(rows.items()):
   line=' '.join(w['text'] for w in ws)
   if 'INACTIVE/TWO-WAY' in line:inactive=True;continue
   if line.startswith('* Indicates') or line=='# # #' or 'PAGE ' in line:continue
   if 'Indicates players' in line:continue
   ws.sort(key=lambda w:w['x0']);starts=[36,144,252,360,468]
   @lru_cache(None)
   def split(j,col):
    if col==5:return (0,[]) if j==len(ws) else (1e9,[])
    best=(1e9,[])
    for n in range(min(5,len(ws)-j)+1):
     z=ws[j:j+n];name=' '.join(w['text'] for w in z).lstrip('*');key=aliases.get(normal(name),normal(name))
     if n and abs(z[0]['x0']-starts[col])>3:continue
     if n and any(abs(w['x0']-x)<3 for w in z[1:] for x in starts[col+1:]):continue
     if not n and j<len(ws) and abs(ws[j]['x0']-starts[col])<3:continue
     cost=0 if not n else (0 if key in known or normal(name) in known else 5)+abs(z[0]['x0']-starts[col])/2
     v,parts=split(j+n,col+1)
     if cost+v<best[0]:best=(cost+v,[name]+parts)
    return best
   _,parts=split(0,0)
   for col,name in enumerate(parts):
    if not name:continue
    # Recover the star from the original token sequence.
    star=any(w['text'].startswith('*') and abs(w['x0']-starts[col])<8 for w in ws)
    q=identity(name);q.update(twoWay=star,inactiveAtPublication=inactive and not star)
    ps[col].append(q)
  for name,players in zip(names,ps):teams.append({'id':tid(name),'name':name,'roster':players})
(D/'opening-2023-24.json').write_text(json.dumps({'season':'2023-24','published':'2023-10-23','teams':teams,'identityOnly':True,'source':'NBA dated release reproduced by Tucson/AP'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html=(D/'opening-2024-25.html').read_text(encoding='utf-8');teams=[]
clean=lambda s:unescape(re.sub('<[^>]+>','',s)).strip()
for block in re.finditer(r'<h2\b[^>]*>(.*?)</h2>(.*?)(?=<h2\b|$)',html,re.S):
 name=clean(block[1])
 try:id=tid(name)
 except:continue
 ps=[];inactive=False
 body=block[2];lists=list(re.finditer(r'<ul\b[^>]*>.*?</ul>',body,re.S))[:2]
 if lists:body=body[:lists[-1].end()]
 inactive_at=body.lower().find('inactivos')
 for li in re.finditer(r'<li\b[^>]*>(.*?)</li>',body,re.S):
  raw=clean(li[1]);star=raw.startswith('*');q=identity(raw.lstrip('*').strip());q.update(twoWay=star,inactiveAtPublication=inactive_at>=0 and li.start()>inactive_at and not star);ps.append(q)
 if ps:teams.append({'id':id,'name':name,'roster':ps})
(D/'opening-2024-25.json').write_text(json.dumps({'season':'2024-25','published':'2024-10-22','teams':teams,'identityOnly':True,'source':'Dated Gigantes reproduction of NBA opening release'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for s in ['2023-24','2024-25']:
 x=json.loads((D/f'opening-{s}.json').read_text(encoding='utf-8'));assert len(x['teams'])==30
 for t in x['teams']:assert 12<=len(t['roster'])<=19,(s,t)
 print(s,len(x['teams']),sum(len(t['roster']) for t in x['teams']),[p['name'] for t in x['teams'] for p in t['roster'] if p.get('unresolvedIdentity')])

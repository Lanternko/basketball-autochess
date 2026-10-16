"""Archive factual rank fields only, not article prose or images."""
import json,re,urllib.request
from pathlib import Path
from html.parser import HTMLParser
class Text(HTMLParser):
    def __init__(self):super().__init__();self.text=[];self.skip=0;self.links=[]
    def handle_starttag(self,t,a):
        if t in ('script','style'):self.skip+=1
        if t=='a':self.links.extend(v for k,v in a if k=='href')
    def handle_endtag(self,t):
        if t in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip:self.text.append(d)
url='https://sports.yahoo.com/article/ranking-consensus-top-100-players-111631517.html'
p=Text();p.feed(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read().decode())
text=' '.join(' '.join(p.text).split())
parts=re.split(r'(?<!\d)(\d{1,3})\. ([^()]{2,70}) \(([^)]+)\)',text)
rows=[]
for i in range(1,len(parts)-3,4):
    n,name,team,chunk=parts[i:i+4]
    ranks={a:int(b) for a,b in re.findall(r'(ESPN\.com|The Ringer|SI\.com|HoopsHype) rank: No\. (\d+)',chunk)}
    if len(ranks)>=1:rows.append({'publishedConsensusRank':int(n),'name':name,'team':team,'ranks':ranks})
rows=list({r['name']:r for r in reversed(rows)}.values());rows.sort(key=lambda r:r['publishedConsensusRank'])
# This one heading omits the parenthesized team used by the other headings.
if not any(r['publishedConsensusRank']==87 for r in rows):
    chunk=re.search(r"87\. De'Andre Hunter(.*?)(?=88\. Aaron Nesmith)",text).group(1)
    ranks={a:int(b) for a,b in re.findall(r'(ESPN\.com|The Ringer|SI\.com|HoopsHype) rank: No\. (\d+)',chunk)}
    assert ranks=={'HoopsHype':75,'The Ringer':82,'SI.com':87}
    rows.append({'publishedConsensusRank':87,'name':"De'Andre Hunter",'team':None,'ranks':ranks})
rows.sort(key=lambda r:r['publishedConsensusRank'])
assert len(rows)==100,len(rows)
d={'source':url,'published':'2025-10-18','selectedMedia':['ESPN.com','The Ringer','HoopsHype'],'players':rows,
   'links':[x for x in p.links if any(k in x for k in ['espn.com/nba/story','theringer.com','hoopshype.com/story'])]}
Path('reports/model-evolution-20261016/media-ranks.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved factual rank fields for',len(rows),'players; 3-outlet means recomputed separately.')

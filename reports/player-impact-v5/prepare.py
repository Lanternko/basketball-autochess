"""Observed fresh-shot zone profiles, preserving explicit OREB putback path."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-impact-v5');ROOT.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
hashes={}
def seconds(s):
 m=re.match(r'PT(?:(\d+)M)?([\d.]+)S',s);return int(m[1] or 0)*60+float(m[2])
for season in ['2022-23','2023-24','2024-25','2025-26']:
 old=read(f'reports/player-impact-v4/{season}-cards.json');base=Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}');manifest=read(base/'manifest.json');shots=defaultdict(Counter);putbacks=defaultdict(Counter)
 for spec in manifest['sources']:
  f=Path(spec['file']);hashes[str(f).replace('\\','/')]=hashlib.sha256(f.read_bytes()).hexdigest();pending=None
  for e in read(f)['data']['game']['actions']:
   kind=e.get('actionType');sub=e.get('subType');pid=str(e.get('personId'))
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    z='long' if kind=='3pt' else 'mid' if e.get('area')=='Mid-Range' else 'short';hit=e.get('shotResult')=='Made'
    pb=pending and pid==str(pending['personId']) and e.get('teamId')==pending['teamId'] and e.get('period')==pending['period'] and z=='short' and 0<=seconds(pending['clock'])-seconds(e['clock'])<=3
    (putbacks if pb else shots)[pid].update({z+'A':1,z+'M':int(hit)});pending=None
   elif kind=='rebound' and sub=='offensive' and e.get('personId') and 'team' not in e.get('qualifiers',[]):pending=e
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None
 total=sum(shots.values(),Counter());prior={z:total[z+'A']/sum(total[k+'A'] for k in ['long','mid','short']) for z in ['long','mid','short']};cards={}
 for pid,m in old['cards'].items():
  s=shots[pid];a=sum(s[z+'A'] for z in prior)
  # A small 20-FGA prior keeps unobserved/very small samples usable while
  # preserving a real non-shooter's zero-three profile once it is observed.
  zone={z:(s[z+'A']+20*prior[z])/(a+20) for z in prior}
  if a>=100 and not s['longA']:
   zone['long']=0;d=zone['mid']+zone['short'];zone['mid']/=d;zone['short']/=d
  cards[pid]={**m,'freshZone':zone,'freshShotCounts':dict(s),'putbackProxyCounts':dict(putbacks[pid])}
 (ROOT/f'{season}-cards.json').write_text(json.dumps({'season':season,'cards':cards,'zonePrior':prior,'design':'Fixed source-context opportunity priors with balanced passing; measured fresh-shot zone distribution, immediate OREB shots excluded to avoid double counting. 20-FGA zone prior. Zero threes retained for >=100 fresh FGA non-shooters. Same-season reconstruction, not out-of-sample.'},ensure_ascii=False,indent=2),encoding='utf-8')
 print(season,len(cards),flush=True)
(ROOT/'source-hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')

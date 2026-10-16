"""Aggregate immutable T0 outputs. No games are rerun."""
import json
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;T0=R/'reports/defense-tenth/step4-t0'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def table(p):
 t=read(p)['data']['resultSets'][0];return [dict(zip(t['headers'],r)) for r in t['rowSet']]
cases=read(O/'cases.json');out=[]
def boxposs(a):return a['fga']-a['oreb']+a['tov']+.44*a['fta']
def simstats(a,own):
 def rat(n,d,k=100):return k*a[n]/a[d] if a[d] else None
 poss=(boxposs(a)+boxposs(own))/2
 return {'paintShare':rat('rima','fga'),'paintFG':rat('rimm','rima'),'threeShare':rat('fg3a','fga'),'threeFG':rat('fg3m','fg3a'),'defProxy':100*a['pts']/poss,'forcedTOVpct':100*a['tov']/poss,'FTR':rat('fta','fga',1),'efg':100*(a['fgm']+.5*a['fg3m'])/a['fga']}
for s in sorted({c['season'] for c in cases}):
 selected={c['teamId']:c for c in cases if c['season']==s};sim={}
 for version in ['pure','v3']:
  counts=defaultdict(lambda:defaultdict(float));own=defaultdict(lambda:defaultdict(float))
  for seed in range(20261012,20261032):
   run=read(T0/'runs'/f'{s}-{version}-{seed}.json')
   for t in run['teams']:
    if t['id'] not in selected:continue
    for k,v in t['opponent'].items():counts[t['id']][k]+=v
    for k,v in t['stats'].items():own[t['id']][k]+=v
  for tid,c in selected.items():
   v=simstats(counts[tid],own[tid]);v['DREBpct']=100*own[tid]['dreb']/(own[tid]['dreb']+counts[tid]['oreb']);sim.setdefault(tid,{})[version]=v
 base=R/('data/season-source' if s=='2025-26' else f'data/defense-seventh/{s}')
 logs=table(base/'team-games.json');bygame=defaultdict(list)
 for t in logs:bygame[t['GAME_ID']].append(t)
 for tid,c in selected.items():
  opp=defaultdict(float);own=defaultdict(float)
  for rows in bygame.values():
   t=next((r for r in rows if r['TEAM_ID']==tid),None)
   if t is None:continue
   other=next(r for r in rows if r['TEAM_ID']!=tid)
   for k in ['PTS','FGM','FGA','FG3A','FG3M','FTA','OREB','DREB','TOV']:opp[k.lower()]+=other[k];own[k.lower()]+=t[k]
  poss=(boxposs(opp)+boxposs(own))/2
  real={'defProxy':100*opp['pts']/poss,'threeShare':100*opp['fg3a']/opp['fga'],'threeFG':100*opp['fg3m']/opp['fg3a'],'forcedTOVpct':100*opp['tov']/poss,'FTR':opp['fta']/opp['fga'],'efg':100*(opp['fgm']+.5*opp['fg3m'])/opp['fga'],'DREBpct':100*own['dreb']/(own['dreb']+opp['oreb'])}
  out.append({'season':s,'team':c['team'],'fullSeason':{'real':real,**sim[tid]},'strictPbpPaintReference':c['observed'],'limitation':'simulated paint counts cover 1230 games; real paint counts cover strict games only; no matched-game paint comparison available in saved T0 output'})
 print('CACHED',s,flush=True)
(O/'cached-factors.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

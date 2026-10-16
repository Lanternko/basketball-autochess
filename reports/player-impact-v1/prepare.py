"""Measured shot creation and strict on-court truth; no name or rank targets."""
import json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('reports/player-impact-v1');ROOT.mkdir(exist_ok=True)
SEASONS=['2022-23','2023-24','2024-25','2025-26']
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
hashes={}
def source(p):
 p=Path(p);hashes[str(p).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest();return read(p)
def save(f,x):(ROOT/f).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
pbp=source('reports/defense-tenth/step4-t2b/overall-pbp-counts.json')
for season in SEASONS:
 b=source(f'reports/defense-tenth/step4-t0/{season}/bundle.json');players=defaultdict(Counter);names={}
 for t in b['league']['teams']:
  for p in t['roster']:
   names[p['playerId']]=p['name'];players[p['playerId']].update({k:p['observed'][k] for k in ['MIN','FGM','AST','FGA','FTA','TOV']})
 made=defaultdict(Counter)
 for x in pbp:
  if x['season']==season:made[x['player']].update({'fgm':x['m'],'assisted':x['am'],'fga':x['a']})
 sf=Path('reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints')
 audit=source(sf/'defensive-samples.json')
 excluded={x if isinstance(x,str) else x['id'] for k in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'] for x in audit[k]}
 valid=set()
 with (sf/'real-games.jsonl').open(encoding='utf-8') as f:
  for line in f:
   g=json.loads(line)
   if g['id'] not in excluded and g['lineupsValid'] and g['pointsValid'] and not g['anomalies']:valid.add(g['id'])
 assert len(valid)==audit['strictUsableGames']
 # Putback made production already comes from OREB opportunities in the engine.
 # Exclude that production from fresh possession self-creation priors.
 base=Path('data/defense-a-source' if season=='2025-26' else f'data/defense-seventh/{season}')
 manifest=source(base/'manifest.json');putbacks=Counter();strict_own=defaultdict(Counter)
 for spec in manifest['sources']:
  raw=source(spec['file']);actions=raw['data']['game']['actions'];pending=None
  for e in actions:
   clock=e.get('clock','');period=e.get('period');kind=e.get('actionType');sub=e.get('subType');pid=e.get('personId');team=e.get('teamId')
   if kind in ['2pt','3pt'] and e.get('isFieldGoal'):
    hit=e.get('shotResult')=='Made'
    if spec['id'] in valid:strict_own[pid].update({'fga':1,'fgm':int(hit),'fg3a':int(kind=='3pt'),'fg3m':int(hit and kind=='3pt')})
    if pending and hit and not e.get('assistPersonId') and pid==pending['personId'] and team==pending['teamId'] and period==pending['period']:
     def seconds(s):
      import re
      m=re.match(r'PT(?:(\d+)M)?([\d.]+)S',s);return int(m[1] or 0)*60+float(m[2])
     dt=seconds(pending['clock'])-seconds(clock)
     if 0<=dt<=3 and kind=='2pt' and e.get('area')!='Mid-Range':putbacks[pid]+=1
    pending=None
   elif kind=='rebound' and sub=='offensive' and pid and not any('team'==q for q in e.get('qualifiers',[])):
    pending=e
   elif kind in ['turnover','freethrow','foul','period','jumpball'] or kind=='rebound' and sub=='defensive':pending=None
 total_m=sum(v['fgm'] for v in made.values());q_prior=sum(v['assisted'] for v in made.values())/total_m
 totals=sum(players.values(),Counter());rate_prior={k:totals[k]/totals['MIN'] for k in ['FGM','AST','FGA','FTA','TOV']}
 pb_prior=sum(putbacks.values())/total_m
 cards={}
 for pid,p in players.items():
  c=made[pid];q=(c['assisted']+50*q_prior)/(c['fgm']+50);pb=min(1-q,(putbacks[pid]+50*pb_prior)/(c['fgm']+50))
  fgm_rate=(p['FGM']+240*rate_prior['FGM'])/(p['MIN']+240)
  cards[str(pid)]={'name':names[pid],'minutes':p['MIN'],'selfMakesPerMinute':fgm_rate*max(0,1-q-pb),
   'assistedMakesPerMinute':fgm_rate*q,'assistsPerMinute':(p['AST']+240*rate_prior['AST'])/(p['MIN']+240),
   'assistedMakeShare':q,'putbackMakeShare':pb,'pbpMakes':c['fgm'],'pbpAssistedMakes':c['assisted'],'putbackProxyMakes':putbacks[pid]}
 # Stint "opponent" counts are from the other team's offense. Own DREB is
 # stored specially there, so only use the unambiguous FG fields here.
 onc=defaultdict(Counter);games={};teamgames={};joined=Counter()
 f=sf/'stints.jsonl';hashes[str(f).replace('\\','/')]=hashlib.sha256(f.read_bytes()).hexdigest()
 with f.open(encoding='utf-8') as stream:
  for line in stream:
   st=json.loads(line)
   if st['id'] not in valid:continue
   g=games.setdefault(st['id'],{'teams':{},'players':defaultdict(set)})
   for i,t in enumerate(st['teams']):
    other=st['teams'][1-i];own=other['opponent'];opp=t['opponent'];tid=t['teamId']
    gt=g['teams'].setdefault(tid,Counter());gt.update({'seconds':st['seconds'],'fga':own['fga'],'fgm':own['fgm'],'fg3a':own['longA'],'fg3m':own['longM'],'opp_fga':opp['fga'],'opp_fgm':opp['fgm'],'opp_fg3a':opp['longA'],'opp_fg3m':opp['longM']})
    for pid in t['players']:
     g['players'][tid].add(pid);onc[pid].update({'seconds':st['seconds'],'fga':own['fga'],'fgm':own['fgm'],'fg3a':own['longA'],'fg3m':own['longM'],'opp_fga':opp['fga'],'opp_fgm':opp['fgm'],'opp_fg3a':opp['longA'],'opp_fg3m':opp['longM']})
 for g in games.values():
  for tid,ids in g['players'].items():
   for pid in ids:
    joined[pid]+=1
    for k,v in g['teams'][tid].items():onc[pid]['game_'+k]+=v
 rows=[]
 for pid,p in players.items():
  on=onc[pid];own=strict_own[pid];off={k:on['game_'+k]-on[k] for k in ['seconds','fga','fgm','fg3a','fg3m','opp_fga','opp_fgm','opp_fg3a','opp_fg3m']};mates={k:on[k]-own[k] for k in ['fga','fgm','fg3a','fg3m']}
  assert all(v>=0 for v in off.values()) and all(v>=0 for v in mates.values()),pid
  pct=lambda c,k,a:100*c[k]/c[a] if c[a] else None
  rows.append({'playerId':pid,'name':names[pid],'strictGamesPlayed':joined[pid],'on':dict(on),'off':off,'own':dict(own),'teammates':mates,'metrics':{
   'onTeamFG':pct(on,'fgm','fga'),'onTeam3P':pct(on,'fg3m','fg3a'),'onTeammateFG':pct(mates,'fgm','fga'),'onTeammate3P':pct(mates,'fg3m','fg3a'),
   'offTeamFG':pct(off,'fgm','fga'),'offTeam3P':pct(off,'fg3m','fg3a'),'onOpponentFG':pct(on,'opp_fgm','opp_fga'),'onOpponent3P':pct(on,'opp_fg3m','opp_fg3a')}})
 save(f'{season}-cards.json',{'season':season,'method':'Fresh self-made FG production and assisted FG production priors; assisted-make share is not assisted-attempt probability. 50 made-FG prior and 240-minute event-rate shrinkage, fixed before simulation. Same-season inputs, no player-name offsets or fitted OVR targets.','cards':cards,'leagueAssistedMakeShare':q_prior})
 save(f'{season}-on-court-truth.json',{'season':season,'strictGames':len(valid),'gameIds':sorted(valid),'definitions':'On-court team FG includes own shots; teammate FG excludes own shots. OFF uses only the same team-games in which this player actually played. No causal interpretation of raw on/off. Full-game strict lineup reconstruction and counter checks inherited, no box-minute fitting.','players':rows})
 print(season,'cards',len(cards),'strict games',len(valid),'on-court rows',len(rows),flush=True)
save('source-hashes.json',hashes)

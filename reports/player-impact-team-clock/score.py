"""Reclassify saved, exactly parity-verified counters in memory; never reroll games."""
import json,importlib.util,csv,hashlib
from pathlib import Path
ROOT=Path('reports/player-impact-team-clock')
spec=importlib.util.spec_from_file_location('box','reports/player-box-audit/experiment/score.py');box=importlib.util.module_from_spec(spec);spec.loader.exec_module(box)
oldread=box.read
def read(p):
 p=Path(p)
 if not p.exists() and p.parent==Path('reports/player-impact-v6/runs'):
  stem,seed=p.stem.rsplit('-',1);p=p.with_name(stem+'-full-'+seed+'.json')
 r=oldread(p)
 if p.parent==Path('reports/player-impact-v6/runs'):
  for team in r['teams']:
   for player in team['players']:
    s=player['stats'];clock=s['clockTov'];s['tov']-=clock;s['deadTov']-=clock;s['clockTov']=0
    assert s['tov']>=0 and s['deadTov']>=0
   assert abs(sum(p['stats']['tov'] for p in team['players'])+team['stats']['clockTov']-team['stats']['tov'])<1e-8
 return r
box.read=read
protocol=oldread('reports/player-impact-validation/confirmation-protocol.json');cells=[]
for season in protocol['seasons']:
 c=box.score(season,'terminal-flow',protocol['seeds'],Path('reports/player-impact-v6'));cells.append(c)
 print(season,'individual TOV36 MAE',c['summary']['ALL']['tov36']['mae'],'guard bias',c['summary']['G']['tov36']['bias'],flush=True)
out={'design':'Twenty-seed frozen terminal-flow counters with only player clockTov removed from individual tov/deadTov. Actual engine change is separately exact-parity verified over 240 games. Team scores, minutes and all other player counters unchanged. Same-season reconstruction, not prediction.', 'cells':cells}
(ROOT/'scores.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
keys=list(cells[0]['players'][0]['metrics'])
with (ROOT/'all-players-20-seeds.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['season','playerId','name','position','roleGroup','minutes','predictedMinutes','minuteError','primarySample']+[k+'_'+z for k in keys for z in ['actual','predicted','error']]+[k+'_total_'+z for k in box.COUNTS for z in ['actual','predicted','error']];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for c in cells:
  for p in c['players']:
   row={k:p[k] for k in fields[:7] if k in p};row.update(season=c['season'],primarySample=p['minutes']>=500,minuteError=p['predictedMinutes']-p['minutes'])
   for k,q in p['metrics'].items():
    if q:row.update({k+'_actual':q['actual'],k+'_predicted':q['predicted'],k+'_error':q['predicted']-q['actual']})
   for k in box.COUNTS:
    q=p['metrics'][k+'36']
    if q:
     actual=q['actual']*p['minutes']/36;predicted=q['predicted']*p['predictedMinutes']/36
     row.update({k+'_total_actual':actual,k+'_total_predicted':predicted,k+'_total_error':predicted-actual})
   w.writerow(row)
verification=oldread(ROOT/'verification.json');assert verification['games']==240 and verification['scoreAndTeamStatsExactParity'] and verification['otherPlayerStatsExactParity']
files=['src/individual_team_accounting.js',str(ROOT/'engine.mjs'),str(ROOT/'season-source.mjs')]
status={'version':'team-only-clock-1','enabled':True,'changesGameOutcomes':False,'verification':verification,'hashes':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}}
(ROOT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')

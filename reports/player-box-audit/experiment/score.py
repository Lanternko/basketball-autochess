"""Score mechanism interventions against matching archived seeds, never ratings."""
import json, sys, csv
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT=Path('reports/player-box-audit')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
baseline=read(ROOT/'baseline.json')
COUNTS=['pts','ast','tov','stl','blk','oreb','dreb','fga','fg3a','fta']
RATES={'fgPct':('fgm','fga',100),'threePct':('fg3m','fg3a',100),'ftPct':('ftm','fta',50)}

def metric(rows,key,group='ALL'):
    rs=[p for p in rows if p['minutes']>=500 and p['metrics'].get(key) is not None and (group=='ALL' or p['roleGroup']==group)]
    if not rs:return None
    w=np.array([p['minutes'] for p in rs]);w=w/w.sum()
    a=np.array([p['metrics'][key]['actual'] for p in rs]);b=np.array([p['metrics'][key]['predicted'] for p in rs]);e=b-a
    am=np.sum(w*a);bm=np.sum(w*b);den=np.sqrt(np.sum(w*(a-am)**2)*np.sum(w*(b-bm)**2))
    return dict(players=len(rs),actual=float(am),predicted=float(bm),bias=float(w@e),mae=float(w@abs(e)),rmse=float(np.sqrt(w@(e*e))),correlation=float(w@((a-am)*(b-bm))/den) if den else None)

def score(season,version,seeds,folder):
    base=next(s for s in baseline['seasons'] if s['season']==season)
    truth=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')['league']['teams']
    sums=defaultdict(lambda:defaultdict(float));teams=defaultdict(lambda:defaultdict(float));matches=[]
    for seed in seeds:
      path=(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/{season}-split-{seed}.json' if version=='control' else folder/f'runs/{season}-{version}-{seed}.json')
      run=read(path);assert len(run['matches'])==1230
      matches.append(run['matches'])
      for t in run['teams']:
        assert t['games']==82
        for k in ['pts','oreb','dreb','fgm','fga','fg3m','fg3a','stl','ast','tov']:teams[t['id']][k]+=t['stats'][k]/len(seeds)
        for k in ['pts','oreb','dreb']:teams[t['id']]['opp_'+k]+=t['opponent'][k]/len(seeds)
        teams[t['id']]['wins']+=t['wins']/len(seeds)
        for p in t['players']:
          for k,v in p['stats'].items():
            if isinstance(v,(int,float)):sums[p['playerId']][k]+=v/len(seeds)
    rows=[]
    for p in base['players']:
      sim=sums[p['playerId']];sm=sim['seconds']/60;m={}
      for k in COUNTS:m[k+'36']={'actual':p['metrics'][k+'36']['actual'],'predicted':36*sim[k]/sm} if sm and p['metrics'][k+'36'] else None
      for k,(made,att,threshold) in RATES.items():m[k]={'actual':p['metrics'][k]['actual'],'predicted':100*sim[made]/sim[att]} if p['metrics'].get(k) and sim[att] else None
      uses=sim['fga']+.44*sim['fta']+sim['tov']
      m['tovPer100Uses']={'actual':p['metrics']['tovPer100Uses']['actual'],'predicted':100*sim['tov']/uses} if uses and p['metrics'].get('tovPer100Uses') else None
      rows.append({**{k:p[k] for k in ['playerId','name','minutes','roleGroup','position']},'predictedMinutes':sm,'metrics':m})
    keys=list(rows[0]['metrics']);summary={g:{k:metric(rows,k,g) for k in keys} for g in ['ALL','G','F','C']}
    target=read('reports/defense-tenth/step4-rebounds-turnover-time/seed-arrays.json')[season]
    net=np.array([(teams[tid]['pts']-teams[tid]['opp_pts'])/82-target['truth']['net'][i] for i,tid in enumerate(target['ids'])]);net-=net.mean()
    wins=np.array([teams[tid]['wins']-target['truth']['wins'][i] for i,tid in enumerate(target['ids'])])
    total={k:sum(t[k] for t in teams.values()) for k in teams[next(iter(teams))]}
    tm={'netRMSE':float(np.sqrt(np.mean(net**2))),'winsMAE':float(abs(wins).mean()),'ptsPerGame':total['pts']/2460,'astPerGame':total['ast']/2460,'tovPerGame':total['tov']/2460,'threePct':100*total['fg3m']/total['fg3a']}
    return dict(season=season,version=version,seeds=seeds,summary=summary,teamMetrics=tm,players=rows)

def main():
    folder=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'experiment'
    p=read(folder/'protocol.json');versions=['control']+p['variants'];cells=[]
    for season in p['seasons']:
      for v in versions:
        c=score(season,v,p['seeds'],folder);cells.append(c)
        print(season,v,'ALL',*[f'{k}={c["summary"]["ALL"][k]["mae"]:.3f}' for k in ['pts36','ast36','oreb36','stl36','blk36','threePct']], 'Gbias',*[f'{k}={c["summary"]["G"][k]["bias"]:+.3f}' for k in ['pts36','ast36']], 'team',c['teamMetrics'],flush=True)
    (folder/'scores.json').write_text(json.dumps({'comparison':'Matching-seed same-season diagnostic; no player ratings changed','cells':cells},ensure_ascii=False,indent=2),encoding='utf-8')
    with (folder/'players.csv').open('w',newline='',encoding='utf-8-sig') as f:
      fields=['season','version','playerId','name','minutes','predictedMinutes','roleGroup','position']+list(cells[0]['players'][0]['metrics'])
      w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
      for c in cells:
        for r in c['players']:w.writerow({'season':c['season'],'version':c['version'],**{k:v for k,v in r.items() if k!='metrics'},**{k:json.dumps(v) for k,v in r['metrics'].items()}})

if __name__=='__main__':main()

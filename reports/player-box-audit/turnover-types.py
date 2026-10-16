"""Recover offensive turnover subtypes from the engine's exact partitions."""
import json
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('reports/player-box-audit');read=lambda f:json.loads(Path(f).read_text(encoding='utf-8'))
baseline=next(s for s in read(ROOT/'baseline.json')['seasons'] if s['season']=='2025-26')
pbp=read(ROOT/'pbp-truth.json');real={p['playerId']:p for p in pbp['players']};sim=defaultdict(Counter)
seeds=range(20261012,20261032)
for seed in seeds:
    run=read(f'reports/defense-tenth/step4-rebounds-turnover-time/runs/2025-26-split-{seed}.json')
    for t in run['teams']:
      for p in t['players']:
        q=p['stats'];handleLive=q['touchTov']-q['deadTov']+q['clockTov'];passLive=q['liveTov']-handleLive
        assert handleLive>=0 and passLive>=0
        for k,v in dict(minutes=q['seconds']/60,tov=q['tov'],liveTov=q['liveTov'],passStolenAgainst=passLive,handleStolenAgainst=handleLive,
                        passTov=passLive+q['passOutTov'],handleTov=handleLive+q['handlingOutTov'],assignedClockTov=q['clockTov']).items():sim[p['playerId']][k]+=v/len(seeds)
keys=['tov','liveTov','passStolenAgainst','handleStolenAgainst','passTov','handleTov']
rows=[]
for p in baseline['players']:
    s=sim[p['playerId']];r=real[p['playerId']]
    rows.append({**{k:p[k] for k in ['playerId','name','roleGroup','minutes']},'pbpMinutes':r['matchedMinutes'],'simulationMinutes':s['minutes'],
                 'metrics':{k:{'actual':r['per36'].get(k,0),'predicted':36*s[k]/s['minutes']} for k in keys} if r['matchedMinutes'] and s['minutes'] else {},
                 'assignedClockTov36':36*s['assignedClockTov']/s['minutes'] if s['minutes'] else None})
summary={}
for g in ['ALL','G','F','C']:
    rs=[p for p in rows if p['minutes']>=500 and p['metrics'] and (g=='ALL' or p['roleGroup']==g)];w=sum(p['minutes'] for p in rs)
    summary[g]={}
    for k in keys:
      a=sum(p['minutes']*p['metrics'][k]['actual'] for p in rs)/w;b=sum(p['minutes']*p['metrics'][k]['predicted'] for p in rs)/w
      summary[g][k]={'actual':a,'predicted':b,'bias':b-a,'mae':sum(p['minutes']*abs(p['metrics'][k]['predicted']-p['metrics'][k]['actual']) for p in rs)/w}
result={'method':'Offensive lost-ball live = touchTov-deadTov+clockTov; pass stolen against = liveTov-lost-ball live. Checks exact nonnegative partitions. Do not mistake defensive passSteals for offensive pass turnovers.',
        'limits':f'Truth PBP covers {pbp["games"]}/1230 games; simulation covers 1230. Each uses its own minutes, traded stints merged; this is a coverage-qualified subtype diagnosis, not perfectly matched game evaluation. Clock turnovers are currently assigned to a player in simulation; official PBP team turnovers excluded from individual truth.',
        'summary':summary,'players':rows}
(ROOT/'turnover-types.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))

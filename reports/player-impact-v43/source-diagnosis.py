"""Expected FG on the exact recorded shots, not simulation or causal impact."""
import json, hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit

ROOT=Path('reports/player-impact-v43')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
fit=read('reports/player-impact-v41/fit.json')
out=[]
for season in read(ROOT/'protocol.json')['seasons']:
    data=read(f'reports/player-impact-v40/{season}-fga-data.json')
    full=next(s for s in fit['seasons'] if s['season']==season)
    ids=full['playerIds']; index={p:i for i,p in enumerate(ids)}
    # Off means the same games in which this player actually appeared.
    eligible=defaultdict(set)
    for gid,fold,minutes in data['minutes']:
        for pid,m in minutes:
            if m>0: eligible[gid].add(pid)
    game_teams=defaultdict(lambda:defaultdict(set))
    stintpath=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
    for line in stintpath.read_text(encoding='utf-8').splitlines():
        s=json.loads(line)
        if s['id'] not in eligible:continue
        for t in s['teams']:game_teams[s['id']][t['teamId']].update(t['players'])
    sides={gid:list(teams.values()) for gid,teams in game_teams.items()}
    assert all(len(g)==2 and not(g[0]&g[1]) for g in sides.values())
    sums=defaultdict(lambda:defaultdict(lambda:np.zeros(3)))
    held={}
    for fold in range(5):
        held[fold]={}
        for z,sigma in fit['selectedSigmaByZone'].items():
            # Selected full fits live in v40 or v41 depending on sigma.
            name=f'{season}-sigma{sigma:g}-fold{fold}.json'
            paths=[Path('reports/player-impact-v41/fits')/name,Path('reports/player-impact-v40/fits')/name]
            path=next(p for p in paths if p.exists()) if season=='2025-26' else None
            if path:
                f=read(path);assert f['playerIds']==ids
                held[fold][z]=next(b for b in f['zones'] if b['zone']==z)
    for gid,fold,zi,shooter,own,defenders,n,m in data['rows']:
        z=data['zones'][zi];b=next(b for b in full['zones'] if b['zone']==z)
        def expected(b):
            eta=b['intercept']+b['shooterLogits'][index[shooter]]+sum(b['defenderLogits'][index[p]] for p in defenders)
            return n*float(expit(eta))
        expected_full=expected(b)
        expected_held=expected(held[fold][z]) if z in held[fold] else np.nan
        team=next(g for g in sides[gid] if defenders[0] in g)
        for pid in team & eligible[gid]:
            arm='on' if pid in defenders else 'off'
            sums[pid][z+':'+arm]+=np.array([n,m,expected_full])
            sums[pid][z+':'+arm+':held']+=np.array([n,m,expected_held])
    rows=[]
    for p in data['players']:
        metrics={}
        for z in data['zones']:
            a=sums[p['playerId']][z+':on'];b=sums[p['playerId']][z+':off']
            ah=sums[p['playerId']][z+':on:held'];bh=sums[p['playerId']][z+':off:held']
            if min(a[0],b[0])<100:continue
            metrics[z]={'onAttempts':int(a[0]),'offAttempts':int(b[0]),'actualOn':100*a[1]/a[0], 'expectedOn':100*a[2]/a[0], 'actualDelta':100*(a[1]/a[0]-b[1]/b[0]),'expectedDelta':100*(a[2]/a[0]-b[2]/b[0]),'heldoutOn':100*ah[2]/ah[0] if np.isfinite(ah[2]) else None,'heldoutDelta':100*(ah[2]/ah[0]-bh[2]/bh[0]) if np.isfinite(ah[2]+bh[2]) else None}
        rows.append({**p,'metrics':metrics})
    out.append({'season':season,'players':rows})
    print(json.dumps({'season':season,'focus':[p for p in rows if p['name'] in ['Victor Wembanyama','Mitchell Robinson','Stephen Curry','Cade Cunningham']]},ensure_ascii=True))
result={'definition':'Fresh recorded FGA only; exact source shots and lineups; off restricted to same games played. Expected values are probabilistic, no random sampling. Heldout available for target season. Descriptive on/off, not causal attribution.','seasons':out}
(ROOT/'source-diagnosis.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

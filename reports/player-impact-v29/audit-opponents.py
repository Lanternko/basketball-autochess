"""Actual-five opponent starter exposure: role context, not opponent ability."""
import collections
import hashlib
import json
from pathlib import Path

ROOT=Path('reports/player-impact-v29')
hashes={}
def read(path):
    path=Path(path);raw=path.read_bytes();hashes[path.as_posix()]=hashlib.sha256(raw).hexdigest()
    return json.loads(raw)

seasons=[]
for season in ['2022-23','2023-24','2024-25','2025-26']:
    bundle=read(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
    truth=read(f'reports/player-impact-v1/{season}-on-court-truth.json')
    valid=set(truth['gameIds'])
    games={g['id']:g for g in bundle['exposure']['games']}
    path=Path('reports/defense-b1/stints.jsonl' if season=='2025-26' else f'reports/defense-seventh/{season}/stints/stints.jsonl')
    hashes[path.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    totals=collections.defaultdict(lambda:dict(seconds=0.,opposingStarterSeconds=0.,ownStarterGameSeconds=0.))
    seen=set();stints=0
    with path.open(encoding='utf-8') as file:
        for line in file:
            s=json.loads(line)
            if s['id'] not in valid or s['seconds']<=0:continue
            assert len(s['teams'])==2
            exposure={t['teamId']:{p['playerId']:p for p in t['players']} for t in games[s['id']]['teams']}
            for side,team in enumerate(s['teams']):
                other=s['teams'][1-side];opp=exposure[other['teamId']]
                assert len(team['players'])==len(set(team['players']))==5
                n=sum(bool(opp[pid]['starter']) for pid in other['players'])
                assert 0<=n<=5
                for pid in team['players']:
                    r=totals[pid];r['seconds']+=s['seconds']
                    r['opposingStarterSeconds']+=s['seconds']*n
                    r['ownStarterGameSeconds']+=s['seconds']*bool(exposure[team['teamId']][pid]['starter'])
            seen.add(s['id']);stints+=1
    assert seen==valid
    for row in truth['players']:
        pid=row['playerId'];actual=row['on'].get('seconds',0)
        if 'seconds' not in row['on']:
            assert not any(row['on'].values()), row
        assert abs(totals[pid]['seconds']-actual)<1e-5,(season,pid,actual,totals[pid]['seconds'])
    rows=[dict(playerId=pid,**r,opposingStarterFraction=r['opposingStarterSeconds']/(5*r['seconds']),
        ownStarterGameFraction=r['ownStarterGameSeconds']/r['seconds']) for pid,r in totals.items() if r['seconds']>0]
    seasons.append(dict(season=season,games=len(valid),stints=stints,players=rows))
    print(json.dumps(dict(season=season,games=len(valid),players=len(rows))),flush=True)
out=ROOT/'opponent-role-exposure.json'
assert not out.exists()
out.write_text(json.dumps(dict(design='Actual strict-source opposing five, seconds-weighted fraction of opponents who started that same game. A role/exposure descriptor only; starters are not automatically better than reserves. This is not an opponent strength estimate or a correction for lineup quality. All on-floor seconds independently match prior strict source truth.',seasons=seasons,hashes=hashes)),encoding='utf-8')

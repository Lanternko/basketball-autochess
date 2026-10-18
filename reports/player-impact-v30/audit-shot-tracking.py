"""Audit newly fetched official tracking shot modalities without converting them into skill grades."""
import collections
import hashlib
import json
from pathlib import Path
ROOT=Path('reports/player-impact-v30')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
seasons=[];hashes={}
for season in ['2022-23','2023-24','2024-25','2025-26']:
    observed=collections.defaultdict(collections.Counter);names={}
    bundle=Path(f'reports/defense-tenth/step4-t0/{season}/bundle.json')
    hashes[bundle.as_posix()]=hashlib.sha256(bundle.read_bytes()).hexdigest()
    for team in read(bundle)['league']['teams']:
        for p in team['roster']:observed[p['playerId']].update(p['observed']);names[p['playerId']]=p['name']
    tables={};totals={};issues=[]
    for mode in ['Drives','CatchShoot','PullUpShot']:
        file=ROOT/f'raw/{season}/{mode}.json';doc=read(file);t=doc['data']['resultSets']
        t=t[0] if isinstance(t,list) else t
        rows=[dict(zip(t['headers'],r)) for r in t['rowSet']]
        assert len(rows)==len({r['PLAYER_ID'] for r in rows})==len(observed)
        assert set(r['PLAYER_ID'] for r in rows)==set(observed)
        tables[mode]={r['PLAYER_ID']:r for r in rows}
        hashes[file.as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
        for r in rows:
            pid=r['PLAYER_ID'];o=observed[pid]
            if mode=='Drives':
                assert 0<=r['DRIVE_FGM']<=r['DRIVE_FGA'] and 0<=r['DRIVE_FTM']<=r['DRIVE_FTA']
                residual=r['DRIVE_PTS']-2*r['DRIVE_FGM']-r['DRIVE_FTM']
                if residual:
                    issues.append(dict(playerId=pid,mode=mode,trackingPointsResidual=residual,
                        note='Reported tracking points are not exactly decomposed by these FG/FT fields; retain source, do not force identity or use as box-score points.'))
                fields={'FGA':r['DRIVE_FGA'],'FTA':r['DRIVE_FTA']}
            else:
                prefix='CATCH_SHOOT' if mode=='CatchShoot' else 'PULL_UP'
                assert 0<=r[prefix+'_FGM']<=r[prefix+'_FGA']
                m3,a3=r[prefix+'_FG3M'],r[prefix+'_FG3A']
                fields={'FGA':r[prefix+'_FGA']}
                if m3 is None or a3 is None:
                    assert m3 is a3 is None
                    issues.append(dict(playerId=pid,mode=mode,nullThreeSubtype=True,
                        note='Keep source null subtype counts; do not invent a measured zero-attempt percentage. Totals of available numeric values exclude these fields.'))
                    assert 2*r[prefix+'_FGM']<=r[prefix+'_PTS']<=3*r[prefix+'_FGM']
                else:
                    assert 0<=m3<=a3<=r[prefix+'_FGA'] and m3<=r[prefix+'_FGM']
                    assert 0<=r[prefix+'_FGM']-m3<=r[prefix+'_FGA']-a3
                    assert r[prefix+'_PTS']==2*r[prefix+'_FGM']+m3
                    fields['FG3A']=a3
            if r['GP']!=o['GP'] or abs(r['MIN']-o['MIN'])>1 or any(n>o[k] for k,n in fields.items()):
                issues.append(dict(playerId=pid,mode=mode,gpDifference=r['GP']-o['GP'],minuteDifference=r['MIN']-o['MIN'],
                    attemptOverages={k:n-o[k] for k,n in fields.items() if n>o[k]}))
        totals[mode]={k:dict(knownSum=sum(r[k] for r in rows if r[k] is not None),nullRows=sum(r[k] is None for r in rows)) for k in rows[0] if k.startswith(('DRIVE_','CATCH_SHOOT_','PULL_UP_')) and not k.endswith('PCT')}
    cards=[]
    for pid,o in observed.items():
        card=dict(playerId=pid,name=names[pid],officialMinutes=o['MIN'],officialFGA=o['FGA'],officialFG3A=o['FG3A'],
            drives=tables['Drives'][pid],catchShoot=tables['CatchShoot'][pid],pullUp=tables['PullUpShot'][pid])
        cards.append(card)
    seasons.append(dict(season=season,players=cards,totals=totals,scopeIssues=issues))
    print(json.dumps(dict(season=season,players=len(cards),scopeIssues=len(issues))),flush=True)
out=dict(design=__doc__,definitions='Drive activity is not driving skill; catch-and-shoot and pull-up accuracy are conditional modes, not pure off-ball/handle skill. Do not add drive FGA to catch/pull FGA: these are not mutually exclusive categories. Other shot modes and different official event classifications remain. All source values retained; no runtime input change in v30.',seasons=seasons,hashes=hashes)
p=ROOT/'shot-tracking-audit.json';assert not p.exists();p.write_text(json.dumps(out),encoding='utf-8')

"""Verify frozen v27 source, transport, pooled scores and report scope."""
import csv, hashlib, json, math, subprocess
from collections import Counter, defaultdict
from pathlib import Path

root=Path('reports/player-impact-v27')
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
checked={}
def hashes(x):
    for p,h in x['hashes'].items():
        if p not in checked: checked[p]=sha(p)
        assert checked[p]==h, ('source changed',p)
def close(a,b):
    assert math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-10),(a,b)

hashes(read('reports/player-impact-v26/validation-protocol.json'))
eligible=states=0
for season in ['2022-23','2023-24','2024-25','2025-26']:
    a=read(root/f'{season}-source-fga-audit.json');hashes(a)
    sums=defaultdict(Counter);ids=set();nr=0
    for g in a['games']:
        assert g['id'] not in ids;ids.add(g['id'])
        for row in g['rows']:
            nr+=1;assert len(set(row['own']))==len(set(row['opponent']))==5
            assert not set(row['own']) & set(row['opponent'])
            n=sum(row['observed'])
            for key in ['observed','expectedRaw','expectedSurvival']:
                assert len(row[key])==5 and all(x>=0 and math.isfinite(x) for x in row[key])
                close(sum(row[key]),n)
                for pid,x in zip(row['own'],row[key]):sums[pid][key]+=x
    t=a['totals'];assert nr==t['states'] and len(ids)==t['games']
    assert t['fga']==t['eligibleFresh']+t['putback']+t['excludedLateOrEndgame']
    assert sum(p['actual'] for p in a['players'])==t['eligibleFresh']
    for p in a['players']:
        for key,out in [('observed','actual'),('expectedRaw','expectedRaw'),('expectedSurvival','expectedSurvival')]:close(sums[p['playerId']][key],p[out])
    eligible+=t['eligibleFresh'];states+=nr
assert (eligible,states)==(739550,223615)

truth=read(root/'2025-26-strict-basic-truth.json');hashes(truth)
players={p['playerId']:p for p in truth['players']};assert len(players)==582
ontruth=read('reports/player-impact-v1/2025-26-on-court-truth.json');on={p['playerId']:p for p in ontruth['players']}
dreb=read('reports/player-impact-v24/2025-26-dreb-rates.json')['cards']
gameids={g['id'] for g in truth['games']};assert gameids==set(ontruth['gameIds']) and len(gameids)==1188
sums=defaultdict(Counter)
for g in truth['games']:
    for pid,stats in g['players'].items():sums[int(pid)].update(stats)
for pid,p in players.items():
    for k,n in p['stats'].items():assert sums[pid][k]==n
    for k in ['fga','fgm','fg3a','fg3m']:assert p['stats'][k]==on[pid]['own'].get(k,0)
    assert p['stats']['dreb']==dreb[str(pid)]['sourceDreb']
    assert p['stats']['pts']==2*p['stats']['fgm']+p['stats']['fg3m']+p['stats']['ftm']
    close(p['seconds'],on[pid]['on'].get('seconds',0))
for k,n in truth['totals'].items():
    if k!='teamOnlyTov':assert sum(p['stats'][k] for p in players.values())==n

seeds=[20261012,20261013,20261014];versions=['heuristic','synthetic','observed']
runs=[read(root/f'rotation-replay-v2-2025-26-{s}.json') for s in seeds]
pooled={v:defaultdict(Counter) for v in versions};onc={v:defaultdict(lambda:defaultdict(Counter)) for v in versions}
for seed,r in zip(seeds,runs):
    hashes(r);assert r['seed']==seed and r['games']==1188 and r['limit']==0
    assert r['actual']==runs[0]['actual'];assert set(r['variants'])==set(versions)
    for v,x in r['variants'].items():
        assert {m['id'] for m in x['matches']}==gameids and len(x['matches'])==1188
        assert x['ties']==sum(m['tie'] for m in x['matches'])
        assert all(m['gameSeconds']==2880+300*(m['periods']-4) for m in x['matches'])
        assert {p['playerId'] for p in x['players']}==set(players)
        for p in x['players']:
            pid=p['playerId'];s=p['stats'];pooled[v][pid].update(s)
            assert s['pts']==2*s['fgm']+s['fg3m']+s['ftm'] and s['tov']==s['liveTov']+s['deadTov']
            if v!='heuristic':assert abs(s['seconds']-players[pid]['seconds'])<.011
        close(sum(p['stats']['seconds'] for p in x['players']),10*sum(m['gameSeconds'] for m in x['matches']))
        for p in x['onCourt']['players']:
            pid=p['playerId']
            for group,c in p.items():
                if isinstance(c,dict):onc[v][pid][group].update(c)
            for k in ['fga','fgm','fg3a','fg3m']:
                assert p['on'][k]==p['own'][k]+p['teammates'][k]
                assert p['sameGame'][k]==p['on'][k]+p['off'][k]
        for k in ['fga','fgm','fg3a','fg3m']:
            total=sum(p['stats'][k] for p in x['players'])
            for group,mult in [('own',1),('on',5),('teammates',4)]:assert sum(p[group][k] for p in x['onCourt']['players'])==mult*total

probe=read(root/'rotation-current-2025-26-20261012-probe-2.json');fixed=read(root/'rotation-replay-v2-2025-26-20261012-probe-2.json')
for x in [probe,fixed]:hashes(x);assert x['games']==2
for k in ['actual','variants']:assert probe[k]==fixed[k]
assert any(m['periods']>4 for m in probe['variants']['observed']['matches'])
for name in ['default-parity-v2.json','engine-default-parity.json']:
    x=read(root/name);hashes(x);assert x['games']==96 and x['defaultV26ExactParity']
test=subprocess.run(['node','test/rotation_plan_refresh.js'],text=True,capture_output=True,check=True)
assert 'currentFiveTransportConserved: true' in test.stdout

scores=read(root/'rotation-replay-v2-scores-3-seeds.json');assert scores['seeds']==seeds
configs={'onTeamFG':('on','fgm','fga'),'onTeam3P':('on','fg3m','fg3a'),'onTeammateFG':('teammates','fgm','fga'),'onTeammate3P':('teammates','fg3m','fg3a'),'offTeamFG':('off','fgm','fga'),'offTeam3P':('off','fg3m','fg3a'),'onOpponentFG':('on','opp_fgm','opp_fga'),'onOpponent3P':('on','opp_fg3m','opp_fg3a')}
with (root/'rotation-replay-v2-all-players-3-seeds.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);rows=list(reader);assert len(reader.fieldnames)==135
assert len(rows)==1746;flat={(r['version'],int(r['playerId'])):r for r in rows};assert len(flat)==1746
for v in versions:
    assert len(scores['versions'][v]['players'])==582
    for p in scores['versions'][v]['players']:
        pid=p['playerId'];f=flat[v,pid];q=pooled[v][pid];t=players[pid]['stats'];M=players[pid]['seconds']/60;N=q['seconds']/60
        close(float(f['actualMinutes']),M);close(float(f['simulatedMinutes']),N/3)
        for k in t:
            close(float(f[k+'Total_actual']),t[k]);close(float(f[k+'Total_predicted']),q[k]/3)
        for key,m in p['metrics'].items():
            if key.endswith('36'):
                k=key[:-2];a=t['oreb']+t['dreb'] if k=='reb' else t[k];b=q['oreb']+q['dreb'] if k=='reb' else q[k]
                av=36*a/M if M else None;pv=36*b/N if N else None;primary=M>=500
            elif key in ['fgPct','threePct']:
                mk,ak=('fgm','fga') if key=='fgPct' else ('fg3m','fg3a');av=100*t[mk]/t[ak] if t[ak] else None;pv=100*q[mk]/q[ak] if q[ak] else None;primary=M>=500 and t[ak]>=100
            elif key in configs:
                g,mk,ak=configs[key];a=on[pid][g];b=onc[v][pid][g];av=100*a.get(mk,0)/a[ak] if a.get(ak,0) else None;pv=100*b[mk]/b[ak] if b[ak] else None;primary=M>=500 and a.get(ak,0)>=100
                close(float(f[key+'_actualAttempts']),a.get(ak,0));close(float(f[key+'_predictedAttempts']),b[ak]/3)
            else:
                left,right=('onTeamFG','offTeamFG') if key=='teamFGOnOff' else ('onTeam3P','offTeam3P');a=p['metrics'][left];b=p['metrics'][right]
                av=a['actual']-b['actual'] if a['actual'] is not None and b['actual'] is not None else None;pv=a['predicted']-b['predicted'] if a['predicted'] is not None and b['predicted'] is not None else None;primary=a['primary'] and b['primary']
            for col,n in [('actual',av),('predicted',pv),('error',pv-av if av is not None and pv is not None else None)]:
                if n is None:assert m[col] is None and f[key+'_'+col]==''
                else:close(m[col],n);close(float(f[key+'_'+col]),n)
            assert m['primary']==primary and f[key+'_primary']==str(primary)
    for key,s in scores['versions'][v]['summary'].items():
        ps=[p for p in scores['versions'][v]['players'] if p['metrics'][key]['primary'] and p['metrics'][key]['error'] is not None]
        assert s['players']==len(ps);close(s['minuteWeightedMAE'],sum(p['actualMinutes']*abs(p['metrics'][key]['error']) for p in ps)/sum(p['actualMinutes'] for p in ps))
diffs=scores['sourcePbpVersusOfficialBoxPointDiscrepancies'];assert len(diffs)==2 and all(abs(p['pbpPoints']-p['boxPoints'])==1 for p in diffs)
status=read(root/'status.json');assert not status['officialModelAdopted'] and not status['goalComplete'] and not status['ovrFullRankingThisVersion']
assert status['rotationReplayGames']==10692 and status['ovrLastCompleteVersion']==24
superseded=read(root/'superseded.json');assert 'v2' in json.dumps(superseded)
artifacts=[p for p in root.iterdir() if p.is_file() and p.name!='verification.json']+[Path('test/rotation_plan_refresh.js')]
out={'passed':True,'sourceHashFiles':len(checked),'sourceEligibleFga':eligible,'sourceFivePlayerStates':states,'replayGames':10692,'players':582,'csvRows':1746,'csvColumns':135,'currentEngineEqualsCorrectedReplayProbe':True,'defaultV26ParityGames':96,'currentFiveTest':test.stdout.strip(),'allMetricsRecomputed':True,'scope':'Historical exposure diagnostic only; no ordinary-season win-gate result, new OVR or model adoption.','hashes':{str(p).replace('\\','/'):sha(p) for p in artifacts}}
(root/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='hashes'},ensure_ascii=False,indent=2))

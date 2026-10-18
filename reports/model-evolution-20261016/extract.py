"""Compare archived models only. No simulator edits or regenerated historical outputs."""
import json, hashlib, math, unicodedata
from pathlib import Path

ROOT=Path('reports/model-evolution-20261016')
SEASON='2025-26'
VERSIONS=[14,17,19,20,21,22,23,24,25,26,28,30,31,34,35,36,37,39,41]
SEEDS=[20261012,20261013,20261014]
hashes={}
def read(p):
    p=Path(p);b=p.read_bytes();hashes[p.as_posix()]=hashlib.sha256(b).hexdigest()
    return json.loads(b.decode('utf-8-sig'))
def mean(a):return sum(a)/len(a)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum() and not unicodedata.combining(c))

media=read(ROOT/'media-ranks.json')
eligible=[dict(r,average=sum(r['ranks'].get(m,101) for m in media['selectedMedia'])/3) for r in media['players']]
eligible.sort(key=lambda r:(r['average'],r['name']))
top=eligible[:10]
rankings={n:read(f'reports/player-impact-v{n}/all-{SEASON}/ranking.json') for n in [13,14,24]}
ovr=[]
for i,p in enumerate(top,1):
    ranks={}
    for n,d in rankings.items():
        matches=[r for r in d['players'] if norm(r['name'])==norm(p['name'])]
        assert len(matches)==1,(p['name'],n)
        r=matches[0];ranks[str(n)]={'rank':r['rank'],'winRate':r['winRate'],'games':r['games'],'ci95':r['ci95']}
    media_rank=1+sum(r['average']<p['average'] for r in eligible)
    ovr.append({'name':p['name'],'mediaRank':media_rank,'mediaAverage':p['average'],'mediaRanks':{m:p['ranks'][m] for m in media['selectedMedia']},'models':ranks})

personal={};team={};on_court={};team_checks=[]
cells={}
for n in VERSIONS:
    d=read(f'reports/player-impact-v{n}/scores.json')
    c=next(c for c in d['cells'] if c['season']==SEASON and c['version']=='rotation-space')
    assert c['seeds']==SEEDS
    cells[n]=c
    personal[str(n)]={k:v['mae'] for k,v in c['summary']['ALL'].items()}
    on_court[str(n)]={k:v['mae'] for k,v in c['onCourtSummary']['ALL'].items()}
    controls=[c for c in d['cells'] if c['season']==SEASON and c['version']=='control']
    if controls:
        ctl=controls[0]
        current={k:v['mae'] for k,v in ctl['summary']['ALL'].items()}
        # v41 corrects the individual clock-TOV control evaluation. Always use that latest recount.
        if n==41:personal['control']=current;on_court['control']={k:v['mae'] for k,v in ctl['onCourtSummary']['ALL'].items()}

audit=read('reports/player-impact-diagnostics/team-error-v39/audit.json')
truth={r['teamId']:r for r in audit['rows'] if r['season']==SEASON and r['version']=='control'}
assert len(truth)==30
def metrics(pred):
    e={k:[] for k in ['winsMAE','netRMSE','pts','ast','oreb','dreb','reb','stl','blk','tov','fgPct','threePct','ftPct']}
    for tid,row in truth.items():
        a=row['stats']['own']['actual'];o=row['stats']['opp']['actual'];p=pred[tid];s=p['stats'];opp=p['opponent'];g=82
        e['winsMAE'].append(abs(p['wins']-row['actualWins']))
        e['netRMSE'].append(((s['pts']-opp['pts'])/g-(a['pts']-o['pts'])/g)**2)
        for k in ['pts','ast','oreb','dreb','stl','blk','tov']:e[k].append(abs(s[k]-a[k])/g)
        e['reb'].append(abs(s['oreb']+s['dreb']-a['oreb']-a['dreb'])/g)
        for k,num,den in [('fgPct','fgm','fga'),('threePct','fg3m','fg3a'),('ftPct','ftm','fta')]:
            e[k].append(100*abs(s[num]/s[den]-a[num]/a[den]))
    return {k:math.sqrt(mean(v)) if k=='netRMSE' else mean(v) for k,v in e.items()}
team['control']=metrics({tid:{'wins':r['predictedWins'],'stats':r['stats']['own']['predicted'],'opponent':r['stats']['opp']['predicted']} for tid,r in truth.items()})
for n in VERSIONS:
    manifest=read(f'reports/player-impact-v{n}/validation-manifest.json')
    jobs=[j for j in manifest['jobs'] if j['season']==SEASON and j.get('version')=='rotation-space' and not j.get('strict')]
    assert sorted(j['seed'] for j in jobs)==SEEDS
    runs=[read(j['file']) for j in jobs]
    for j in jobs:assert hashes[j['file']]==j['sha256']
    pred={}
    for tid in truth:
        rr=[next(t for t in d['teams'] if t['id']==tid) for d in runs]
        assert all(t['games']==82 for t in rr)
        pred[tid]={'wins':mean([r['wins'] for r in rr]),**{side:{k:mean([r[side][k] for r in rr]) for k in rr[0][side]} for side in ['stats','opponent']}}
    team[str(n)]=metrics(pred)
    for key in ['winsMAE','netRMSE']:
        delta=abs(team[str(n)][key]-cells[n]['teamMetrics'][key]);team_checks.append({'version':n,'metric':key,'difference':delta})
        assert delta<1e-9,(n,key,delta)

# All individual versions use the same actual-minute weighting and the same >=500 MIN cohort.
for n,c in cells.items():
    assert c['summary']['ALL']['pts36']['players']==378
    assert abs(c['summary']['ALL']['pts36']['actual']-cells[14]['summary']['ALL']['pts36']['actual'])<1e-12

out={'season':SEASON,'versions':VERSIONS,'seeds':SEEDS,'players':378,'teams':30,
     'media':{'source':media['source'],'published':media['published'],'outlets':media['selectedMedia'],'missingRank':101,'top10':ovr},
     'personal':personal,'team':team,'onCourt':on_court,
     'missingFullOVR':list(range(25,42)),
     'notes':{'personal':'Actual MIN >=500; actual-minute-weighted MAE; per36 counts; shooting errors in percentage points. v41 control includes corrected clock-TOV evaluation.',
              'team':'30 teams; average three seed totals per team before error; 82 games; box-score actuals reused from verified team-error-v39 audit. Counts per game; shooting percentage points; wins full-season wins; net points/game RMSE.',
              'ovr':'Complete 582-player point ranks only. v13/v14: 600 short games/player; v24: 2400. Experiments, not adopted. Different sampling precision and protocols; no newer all-league ranks.',
              'inference':'In-sample season reconstruction, not blind future-season prediction. Lines join measured checkpoints only; unmeasured versions have no observation.'}}
(ROOT/'chart-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'verification.json').write_text(json.dumps({'passed':True,'season':SEASON,'versions':VERSIONS,'teamScoreboardChecks':team_checks,'sourceSHA256':hashes},indent=2),encoding='utf-8')
print('PASS',len(VERSIONS),'versions;',len(ovr),'media top players;',len(hashes),'source hashes; max team scoreboard delta',max(c['difference'] for c in team_checks))
for x in ovr:print(x['mediaRank'],x['name'],round(x['mediaAverage'],3),{n:r['rank'] for n,r in x['models'].items()})
for key in ['winsMAE','netRMSE','pts','ast','reb','fgPct','threePct']:
    print('TEAM',key,'control',team['control'][key],'v24',team['24'][key],'v41',team['41'][key])

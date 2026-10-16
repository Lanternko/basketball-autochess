import json,hashlib
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
cfg=read(O/'named-pairs-supplement.json')
assert hashlib.sha256((O/'named-pairs-supplement.json').read_bytes()).hexdigest()==(O/'named-pairs-supplement.sha256').read_text().split()[0]
data=read(R/'reports/defense-tenth/step4-t2/players.json');cases=read(O/'cases.json')
def blank():return dict.fromkeys(['points','fga','shortA','shortM','longA','longM','fta','poss','seconds'],0.)
def metrics(a):
    def rat(n,d,k=1):return k*a[n]/a[d] if a[d] else None
    return {'defRtg':rat('points','poss',100),'paintShare':rat('shortA','fga',100),'paintFG':rat('shortM','shortA',100),'threeShare':rat('longA','fga',100),'threeFG':rat('longM','longA',100),'FTR':rat('fta','fga'),'poss':a['poss'],'minutes':a['seconds']/60}
pairs=[];league=[]
for season,S in data.items():
    sf=R/('reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints')
    au=read(sf/'defensive-samples.json');excluded={g if isinstance(g,str) else g['id'] for k in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'] for g in au[k]}
    valid=set()
    for line in (sf/'real-games.jsonl').open(encoding='utf8'):
        g=json.loads(line)
        if g['id'] not in excluded and g['lineupsValid'] and g['pointsValid'] and not g['anomalies']:valid.add(g['id'])
    specs=[]
    for spec in cfg['pairs']:
        if spec['season']!=season:continue
        tid=next(tid for tid,t in S['teams'].items() if t['name']==spec['team'])
        pids=[next(int(pid) for pid,p in S['players'].items() if p['name']==name and tid in p['teams']) for name in spec['players']]
        specs.append((spec,tid,pids))
    bins=defaultdict(blank);totals=defaultdict(blank)
    for line in (sf/'stints.jsonl').open(encoding='utf8'):
        st=json.loads(line)
        if st['id'] not in valid:continue
        for t in st['teams']:
            tid=str(t['teamId']);keys=[('total',tid)]
            for spec,team,pids in specs:
                if tid==team:keys.append(('pair',team,sum((1<<i)*(pid in t['players']) for i,pid in enumerate(pids))))
            for key in keys:
                a=totals[tid] if key[0]=='total' else bins[key[1:]]
                for k in a:a[k]+=st['seconds'] if k=='seconds' else t['defensivePossessions'] if k=='poss' else t['opponent'].get(k,0)
    pooled=blank()
    for a in totals.values():
        for k in pooled:pooled[k]+=a[k]
    league.append({'season':season,'pooled':metrics(pooled),'teams':{S['teams'][tid]['name']:metrics(a) for tid,a in totals.items()}})
    for spec,tid,pids in specs:
        b=read(R/f'reports/defense-tenth/step4-t0/{season}/bundle.json')
        cc={p['playerId']:p for team in b['league']['teams'] for p in team['roster']}
        for state in range(4):pairs.append({'season':season,'team':spec['team'],'pair':spec['players'],'present':[spec['players'][i] for i in range(2) if state&(1<<i)],'stats':metrics(bins[tid,state]),'sufficient':bins[tid,state]['poss']>=500,'playerCards':[{'name':S['players'][str(pid)]['name'],'card':{k:cc[pid].get(k) for k in ['heightInches','help','onBall','rebound']},'metrics':S['players'][str(pid)]['teams'][tid]['metrics'],'minutes':S['players'][str(pid)]['teams'][tid]['minutes']} for pid in pids]})
    print(season,len(valid),flush=True)
save('named-pairs.json',pairs);save('league-reference.json',league)

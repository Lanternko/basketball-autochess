"""T2 observations only. Never imports or runs the simulator or fits cards."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json, hashlib, ast
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import rankdata

R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
OLD=R/'reports/defense-tenth/step4-t2'; T0=R/'reports/defense-tenth/step4-t0'
def read(f):return json.loads(Path(f).read_text(encoding='utf8'))
def save(f,x):(O/f).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
protocol=read(O/'protocol.json')
assert sha(O/'protocol.json')==(O/'protocol.sha256').read_text().split()[0]
data=read(OLD/'players.json'); analysis=read(T0/'analysis.json')
def table(f):
    if not Path(f).exists():return []
    x=read(f)['data']['resultSets'];t=x[0] if isinstance(x,list) else x
    return [dict(zip(t['headers'],v)) for v in t['rowSet']]
def ratio(a,b,k=1):return k*a/b if b>0 else None
metricnames=['load','highUsageShare','diversity','effectivePositions','guardShare','forwardShare','centerShare']
new={};cards={};signals={};coverage=[];issues=[]
for season,S in data.items():
    bundle=read(T0/season/'bundle.json');signals[season]=bundle['options']['defenseSignals']
    cards[season]={str(p['playerId']):p for t in bundle['league']['teams'] for p in t['roster']}
    raw=OLD/'raw'/season
    position={str(x['CLOSE_DEF_PERSON_ID']):x['PLAYER_POSITION'] for x in table(raw/'0-rim.json')}
    usage={str(x['PLAYER_ID']):x['USG_PCT']*100 if x['USG_PCT']<=1 else x['USG_PCT'] for x in table(raw/'0-advanced.json') if x.get('USG_PCT') is not None}
    new[season]={}
    for tid in [0]+sorted({int(tid) for x in S['players'].values() for tid in x['teams']}):
        groups=defaultdict(lambda:dict(mass=0.,knownPosition=0.,knownUsage=0.,usage=0.,high=0.,pos=defaultdict(float),five=defaultdict(float)))
        f=raw/f'{tid}-matchups.json'
        if not f.exists():
            issues.append({'season':season,'team':tid,'reason':'no prior team-filtered matchup file'});continue
        for row in table(f):
            pid=str(row['DEF_PLAYER_ID']);opid=str(row['OFF_PLAYER_ID']);x=S['players'].get(pid);w=row['PARTIAL_POSS']
            if not x or w<=0:continue
            if tid and (str(tid) not in x['teams'] or row['GP']>x['teams'][str(tid)]['GP']):continue
            z=groups[pid];z['mass']+=w
            pos=position.get(opid,'');parts=[a for a in pos.split('-') if a in ['G','F','C']]
            if parts:
                z['knownPosition']+=w
                for a in parts:z['pos'][a]+=w/len(parts)
            if opid in usage:z['knownUsage']+=w;z['usage']+=w*usage[opid];z['high']+=w*(usage[opid]>=25)
            if opid in cards[season]:z['five'][cards[season][opid]['courtPosition']]+=w
        for pid,z in groups.items():
            pp={k:ratio(z['pos'][k],z['knownPosition']) for k in ['G','F','C']}
            h=-sum(v*np.log(v) for v in pp.values() if v is not None and v>0)
            metrics={'load':ratio(z['usage'],z['knownUsage']),'highUsageShare':ratio(z['high'],z['knownUsage'],100),'diversity':float(h/np.log(3)) if z['knownPosition'] else None,'effectivePositions':float(np.exp(h)) if z['knownPosition'] else None,**dict(zip(['guardShare','forwardShare','centerShare'],[100*pp[k] if pp[k] is not None else None for k in ['G','F','C']]))}
            result={'metrics':metrics,'mass':z['mass'],'positionCoverage':ratio(z['knownPosition'],z['mass']),'usageCoverage':ratio(z['knownUsage'],z['mass']),'officialPosition':position.get(pid),'positions':pp,'fivePositionProxy':{k:ratio(v,sum(z['five'].values()),100) for k,v in z['five'].items()},'breadth10pct':sum(v is not None and v>=.1 for v in pp.values())}
            key=(pid,str(tid))
            new[season][key]=result
        if tid==0:
            mass=sum(z['mass'] for z in groups.values());coverage.append({'season':season,'players':len(groups),'partialPoss':mass,'positionCoverage':ratio(sum(z['knownPosition'] for z in groups.values()),mass),'usageCoverage':ratio(sum(z['knownUsage'] for z in groups.values()),mass)})
    # Use the season total for a non-mover, exactly as the earlier T2 audit.
    for pid,x in S['players'].items():
        if len(x['teams'])==1 and (pid,'0') in new[season]:new[season][pid,next(iter(x['teams']))]=new[season][pid,'0']
    print('MATCHUPS',season,len(new[season]),flush=True)
save('matchup-player-data.json',{s:{pid+':'+tid:x for (pid,tid),x in v.items()} for s,v in new.items()})
save('matchup-coverage.json',{'coverage':coverage,'missingFilters':issues})

# Reuse the exact registered cluster estimator from the old immutable script,
# extracting only pure functions, never executing its top-level read/write code.
tree=ast.parse((OLD/'analyze.py').read_text(encoding='utf8'))
functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['corr','evaluate']],type_ignores=[])
p={'uncertainty':{'rng':protocol['portability']['rng']}}
exec(compile(functions,'old-T2-pure-statistics','exec'),globals())
adj=[];within=[]
def eligible(v):return v is not None and v['mass']>=1000 and v['positionCoverage']>=.95 and v['usageCoverage']>=.95
seasons=protocol['seasons']
for a,b in zip(seasons[:-1],seasons[1:]):
    A=data[a]['players'];B=data[b]['players']
    for pid in sorted(set(A)&set(B)):
        x,y=A[pid],B[pid]
        if min(x['minutes'],y['minutes'])<500 or min(x['dominantShare'],y['dominantShare'])<.6:continue
        u,v=new[a].get((pid,'0')),new[b].get((pid,'0'))
        if not (eligible(u) and eligible(v)):continue
        for metric in metricnames:adj.append({'metric':metric,'group':'same' if x['dominantTeam']==y['dominantTeam'] else 'moved','period':a+'→'+b,'id':int(pid),'teams':[x['dominantTeam'],y['dominantTeam']],'x':u['metrics'][metric],'y':v['metrics'][metric]})
for row in read(OLD/'move-samples.json')['audit']:
    if row['reason']:continue
    s=row['season'];pid=str(row['id']);x=data[s]['players'][pid]
    ts=sorted([v for v in x['teams'].values() if v['minutes']>=300],key=lambda t:min(t['dates']))
    if len(ts)<2:continue
    a,b=ts[0],ts[-1];u,v=new[s].get((pid,str(a['id']))),new[s].get((pid,str(b['id'])))
    if not (eligible(u) and eligible(v)):continue
    for metric in metricnames:within.append({'metric':metric,'group':'seasonMove','period':s,'id':int(pid),'teams':[a['id'],b['id']],'x':u['metrics'][metric],'y':v['metrics'][metric],'officialTradeParticipant':row['officialTradeParticipant']})
correlations=[]
for metric in metricnames:
    for group in ['same','moved','seasonMove','officialTradeParticipant']:
        source=adj if group in ['same','moved'] else within
        rr=[r for r in source if r['metric']==metric and (r['group']==group or group=='officialTradeParticipant' and r['officialTradeParticipant'])]
        correlations.append({'metric':metric,'group':group,**evaluate(rr,metric+group)})
    team=[]
    for s,S in data.items():
        for tid,t in S['teams'].items():
            pp=[(x,new[s].get((pid,tid))) for pid,x in S['players'].items() if tid in x['teams']]
            total=sum(x['teams'][tid]['minutes'] for x,v in pp);usable=[(x,v) for x,v in pp if eligible(v)]
            used=sum(x['teams'][tid]['minutes'] for x,v in usable)
            if used<.8*total:continue
            pred=sum(x['teams'][tid]['minutes']*v['metrics'][metric] for x,v in usable)/used
            team.append({'id':int(tid),'teams':[int(tid)],'period':s,'x':pred,'y':-t['defRtg']})
    correlations.append({'metric':metric,'group':'team',**evaluate(team,metric+'team',True)})
    print('BOOTSTRAP',metric,flush=True)
save('matchup-correlations.json',correlations)

keys=['points','fga','fgm','shortA','shortM','longA','longM','fta','dreb','oreb','tov']
def blank():return {k:0. for k in keys+['poss','seconds','stints']}
def add(a,t,sec,own_dreb):
    for k in keys:a[k]+=own_dreb if k=='dreb' else t['opponent'].get(k,0)
    a['poss']+=t['defensivePossessions'];a['seconds']+=sec;a['stints']+=1
def stats(a):
    return {'defRtg':ratio(a['points'],a['poss'],100),'paintShare':ratio(a['shortA'],a['fga'],100),'paintFG':ratio(a['shortM'],a['shortA'],100),'threeShare':ratio(a['longA'],a['fga'],100),'threeFG':ratio(a['longM'],a['longA'],100),'DREBpct':ratio(a['dreb'],a['dreb']+a['oreb'],100),'FTR':ratio(a['fta'],a['fga']),'poss':a['poss'],'minutes':a['seconds']/60,'stints':a['stints']}
caseout=[];lineupout=[];sources={};validation=[]
for s,S in data.items():
    caseids={tid:t['name'] for tid,t in S['teams'].items() if t['name'] in protocol['cases'].get(s,[])}
    sf=R/('reports/defense-b1' if s=='2025-26' else f'reports/defense-seventh/{s}/stints')
    audit=read(sf/'defensive-samples.json')
    excluded={g if isinstance(g,str) else g['id'] for k in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'] for g in audit[k]}
    valid=set()
    with (sf/'real-games.jsonl').open(encoding='utf8') as f:
        for line in f:
            g=json.loads(line)
            if g['id'] not in excluded and g['lineupsValid'] and g['pointsValid'] and not g['anomalies']:valid.add(g['id'])
    assert len(valid)==S['strictGames']==audit['strictUsableGames']
    totals=defaultdict(blank);bins=defaultdict(blank);exposure=defaultdict(float);stintcount=0
    def rim(pid):
        x=S['players'].get(str(pid));c=cards[s].get(str(pid),{})
        return c.get('heightInches',0)>=82 and x is not None and (x['metrics'].get('BLK36') or 0)>=1 and x['samples'].get('rimFGA',0)>=100 and (x['metrics'].get('rimSuppression') or 0)>0
    with (sf/'stints.jsonl').open(encoding='utf8') as f:
        for line in f:
            st=json.loads(line)
            if st['id'] not in valid:continue
            stintcount+=1
            for t in st['teams']:
                own_dreb=next(z['opponent'].get('dreb',0) for z in st['teams'] if z['teamId']!=t['teamId'])
                tid=str(t['teamId']);add(totals[tid],t,st['seconds'],own_dreb)
                for pid in t['players']:exposure[tid,str(pid)]+=t['defensivePossessions']
                if tid in caseids:
                    for kind,count in [('rimProtector',sum(rim(pid) for pid in t['players'])),('sizeOnly',sum(cards[s].get(str(pid),{}).get('heightInches',0)>=82 for pid in t['players']))]:add(bins[tid,kind,min(2,count)],t,st['seconds'],own_dreb)
    sources[s]={'strictGames':len(valid),'strictStints':stintcount,'stintsSHA':sha(sf/'stints.jsonl'),'auditSHA':sha(sf/'defensive-samples.json')}
    for tid,a in totals.items():
        assert abs(stats(a)['defRtg']-S['teams'][tid]['strictDefRtg'])<1e-8
        assert abs(sum(v for (t,pid),v in exposure.items() if t==tid)-5*a['poss'])<1e-6
    validation.append({'season':s,'strictGames':len(valid),'ratingAndFiveExposureChecks':'pass'})
    for tid,name in caseids.items():
        base=stats(totals[tid])
        for kind in ['rimProtector','sizeOnly']:
            for b in range(3):
                a=bins[tid,kind,b];v=stats(a)
                lineupout.append({'season':s,'team':name,'type':kind,'count':b,'stats':v,'deltaFromTeam':{k:v[k]-base[k] if v[k] is not None and base[k] is not None else None for k in ['defRtg','paintShare','paintFG','threeShare','threeFG','DREBpct','FTR']},'sufficient':a['poss']>=500,'raw':a})
        players=sorted([(pid,x) for pid,x in S['players'].items() if tid in x['teams']],key=lambda z:z[1]['teams'][tid]['minutes'],reverse=True)[:10]
        tableout=[]
        sig=signals[s];decomp={k:0. for k in sig['centers']}
        for pid,x in players:
            c=cards[s].get(pid,{});t=x['teams'][tid];v=new[s].get((pid,tid));eta={k:sig['values'].get(pid,{}).get(k,0)-sig['centers'][k] for k in sig['centers']}
            credit={k:eta[k]*exposure[tid,pid]/(5*totals[tid]['poss']) for k in eta}
            for k,val in credit.items():decomp[k]+=val
            tableout.append({'id':int(pid),'name':x['name'],'minutes':t['minutes'],'card':{k:c.get(k) for k in ['onBall','help','rebound','physique','heightInches','courtPosition']},'metrics':t['metrics'],'samples':t['samples'],'matchups':v,'rimProtector':rim(pid),'centeredSignal':eta,'exposureWeightedSignalContribution':credit,'inSample':True})
        allcredit={k:sum((sig['values'].get(pid,{}).get(k,0)-sig['centers'][k])*v/(5*totals[tid]['poss']) for (team,pid),v in exposure.items() if team==tid) for k in sig['centers']}
        t0={c['version']:next(t for t in c['teams'] if str(t['id'])==tid) for c in analysis['cells'] if c['season']==s}
        caseout.append({'season':s,'team':name,'teamId':int(tid),'observed':base,'T0':{ver:{k:t[k] for k in ['net','netRank','O','D','netError']} for ver,t in t0.items()},'actualNet':t0['pure']['actual']['net'],'actualNetRank':t0['pure']['actualNetRank'],'players':tableout,'allPlayersMeanSignal':allcredit,'top10MeanSignal':decomp,'rimProtectors':[x['name'] for pid,x in S['players'].items() if tid in x['teams'] and rim(pid)]})
    print('STINTS',s,len(valid),stintcount,flush=True)
save('cases.json',caseout);save('lineup-observations.json',lineupout);save('stint-audit.json',{'sources':sources,'validation':validation})
# Exact guard/forward/center peer percentiles, full-season individual observations.
peer=[]
for case in caseout:
    s=case['season']
    for player in case['players']:
        v=player['matchups']
        if not v:continue
        pos=v['officialPosition'];own=v['metrics']['load']
        rr=[n['metrics']['load'] for (pid,tid),n in new[s].items() if tid=='0' and n['officialPosition']==pos and data[s]['players'][pid]['minutes']>=500 and eligible(n)]
        player['burdenPeerPercentile']=100*sum(a<=own for a in rr)/len(rr) if rr and own is not None else None
        player['burdenPeerN']=len(rr)
save('cases.json',caseout)
print('DONE',len(caseout),'cases',flush=True)

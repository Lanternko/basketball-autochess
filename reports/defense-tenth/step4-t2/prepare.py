"""Observed defense diagnostics only; never fits a card or imports the simulator."""
import json, hashlib, sys
from pathlib import Path
from collections import defaultdict,Counter
R=Path(__file__).resolve().parents[3]
O=R/'reports/defense-tenth/step4-t2'
def read(p): return json.loads((R/p).read_text(encoding='utf-8'))
def save(name,x): (O/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def table(p):
    d=read(p)['data']; t=d['resultSets'][0] if isinstance(d['resultSets'],list) else d['resultSets']
    return [dict(zip(t['headers'],r)) for r in t['rowSet']]
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
p=read('reports/defense-tenth/step4-t2/protocol.json')
assert sha('reports/defense-tenth/step4-t2/protocol.json')==(O/'protocol.sha256').read_text().split()[0]
for file,h in p['inputHashes'].items(): assert sha(file)==h,file
keys=['points','fga','shortA','longA','dreb','oreb','tov','fta','fgm','shortM','longM']
def blank(): return dict.fromkeys(keys+['poss','seconds'],0.)
def add(a,b):
    for k in a: a[k]+=b.get(k,0) or 0
def delta(a,b): return {k:a[k]-b[k] for k in a}
def ratio(a,b,scale=1.): return scale*a/b if b>0 else None
def onmetrics(on,off,team):
    rg=ratio(on['points'],on['poss'],100); offrg=ratio(off['points'],off['poss'],100); tr=ratio(team['points'],team['poss'],100)
    return {'onDefRtg':-rg if rg is not None else None,'onOffDef':offrg-rg if rg is not None and offrg is not None else None,
      'teamCenteredOn':tr-rg if tr is not None and rg is not None else None,
      'onOffRimShare':100*(off['shortA']/off['fga']-on['shortA']/on['fga']) if off['fga']>0 and on['fga']>0 else None,
      'onOffThreeShare':100*(off['longA']/off['fga']-on['longA']/on['fga']) if off['fga']>0 and on['fga']>0 else None,
      'offDefRtg':-offrg if offrg is not None else None}
seasons={}
for season in p['seasons']:
    data='data/season-source' if season=='2025-26' else f'data/defense-seventh/{season}'
    stint='reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints'
    strict=read(stint+'/defensive-samples.json')
    excluded_ids={g if isinstance(g,str) else g['id'] for key in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'] for g in strict[key]}
    logs=table(data+'/player-games.json'); boxes=table(data+'/team-games.json')
    players={}; gameplayers=defaultdict(list); teamrows=defaultdict(list)
    official_gp=Counter((r['PLAYER_ID'],r['TEAM_ID']) for r in logs)
    for r in boxes: teamrows[r['TEAM_ID']].append(r)
    for r in logs:
        if not r['MIN'] or r['MIN']<=0: continue
        pid=r['PLAYER_ID']; tid=r['TEAM_ID']; x=players.setdefault(pid,{'id':pid,'name':r['PLAYER_NAME'],'minutes':0.,'teams':{},'box':dict.fromkeys(['FGM','FGA','FG3M','FG3A','STL','BLK','DREB','PF'],0.)})
        x['minutes']+=r['MIN']; t=x['teams'].setdefault(tid,{'id':tid,'minutes':0.,'GP':0,'dates':[],'box':dict.fromkeys(x['box'],0.),'on':blank(),'matchedTeam':blank(),'allTeam':blank(),'metrics':{},'samples':{}})
        t['minutes']+=r['MIN'];t['GP']+=1;t['dates'].append(r['GAME_DATE'][:10]);gameplayers[r['GAME_ID'],tid].append(pid)
        for k in x['box']: x['box'][k]+=r.get(k,0) or 0;t['box'][k]+=r.get(k,0) or 0
    # GP includes appearances rounded to MIN=0 in the official game log.
    for pid,x in players.items():
        for tid,t in x['teams'].items():t['GP']=official_gp[pid,tid]
    valid=set(); exclusions=[]; gameinfo={}
    with (R/stint/'real-games.jsonl').open(encoding='utf-8') as f:
        for line in f:
            g=json.loads(line)
            if g['id'] not in excluded_ids and g['lineupsValid'] and g['pointsValid'] and not g['anomalies']:
                valid.add(g['id']);gameinfo[g['id']]={'ids':g['ids'],'score':g['score']}
            else: exclusions.append({'id':g['id'],'lineupsValid':g['lineupsValid'],'pointsValid':g['pointsValid'],'anomalies':g['anomalies'],'authoritativeExclusion':g['id'] in excluded_ids})
    assert len(valid)==strict['strictUsableGames'],(season,len(valid),strict['strictUsableGames'])
    gt=defaultdict(blank); ons=defaultdict(blank); teamtotal=defaultdict(blank); onplayers=defaultdict(set);stints=0
    with (R/stint/'stints.jsonl').open(encoding='utf-8') as f:
        for line in f:
            s=json.loads(line)
            if s['id'] not in valid: continue
            stints+=1
            for t in s['teams']:
                assert len(t['players'])==len(set(t['players']))==5
                vals={k:t['opponent'].get(k,0) for k in keys}; vals.update(poss=t['defensivePossessions'],seconds=s['seconds'])
                tid=t['teamId'];add(gt[s['id'],tid],vals);add(teamtotal[tid],vals)
                for pid in t['players']:
                    add(ons[pid,tid],vals);onplayers[s['id'],tid].add(pid)
    scoreissues=[]
    for gid,g in gameinfo.items():
        for i,tid in enumerate(g['ids']):
            if abs(gt[gid,tid]['points']-g['score'][1-i])>1e-6: scoreissues.append({'id':gid,'team':tid,'opponentStintPoints':gt[gid,tid]['points'],'box':g['score'][1-i]})
    assert not scoreissues,scoreissues[:3]
    # Game logs round very short appearances to MIN=0. Valid reconstructed
    # court presence is the played-game indicator, not the rounded MIN field.
    for (gid,tid),pids in onplayers.items():
        for pid in pids:
            if pid in players and tid in players[pid]['teams']:add(players[pid]['teams'][tid]['matchedTeam'],gt[gid,tid])
    paired=defaultdict(list)
    for row in boxes: paired[row['GAME_ID']].append(row)
    ratings={}
    for tid,rs in teamrows.items():
        ownposs=oppposs=allowed=0.
        for r in rs:
            opp=next(z for z in paired[r['GAME_ID']] if z['TEAM_ID']!=tid)
            ownposs+=r['FGA']-r['OREB']+r['TOV']+.44*r['FTA'];oppposs+=opp['FGA']-opp['OREB']+opp['TOV']+.44*opp['FTA'];allowed+=opp['PTS']
        ratings[tid]={'id':tid,'name':rs[0]['TEAM_NAME'],'defRtg':100*allowed/((ownposs+oppposs)/2),'strictDefRtg':ratio(teamtotal[tid]['points'],teamtotal[tid]['poss'],100),'games':len(rs),'strictGames':sum((gid,tid) in gt for gid in valid)}
    for pid,x in players.items():
        dominant=max(x['teams'].values(),key=lambda t:t['minutes']);x['dominantTeam']=dominant['id'];x['dominantShare']=dominant['minutes']/x['minutes']
        x['metrics']={};x['samples']={}
        for tid,t in x['teams'].items():
            t['on']=ons[pid,tid];t['allTeam']=teamtotal[tid];t['off']=delta(t['matchedTeam'],t['on'])
            assert min(t['off'].values())>=-1e-6,(season,pid,tid,t['off'])
            t['metrics']=onmetrics(t['on'],t['off'],t['allTeam']);t['samples']={'onPoss':t['on']['poss'],'offPoss':t['off']['poss']}
            for k in ['STL','BLK','DREB','PF']: t['metrics'][k+'36']=t['box'][k]/t['minutes']*36
        x['metrics'].update(dominant['metrics']);x['samples'].update(dominant['samples'])
    seasons[season]={'players':players,'teams':ratings,'strictGames':len(valid),'strictStints':stints,'exclusions':exclusions}
    print('STINTS',season,len(valid),stints,'players',len(players),flush=True)
save('onoff.json',seasons)
if '--stints-only' in sys.argv: sys.exit(0)

manifest=read('reports/defense-tenth/step4-t2/fetch-manifest.json')
source_index={(s['season'],s['team'],s['kind']):s for s in manifest['sources']}
audit={'rejectedRows':[],'missingOpponents':[],'splitReconciliations':[],'duplicateRowsMerged':[]}; inventory=[]
metricNames=['rimSuppression','threeSuppression','onDefRtg','onOffDef','teamCenteredOn','onOffRimShare','onOffThreeShare','matchupSuppression','usageWeightedMatchupSuppression','defensiveLoad','CONTESTED_SHOTS_2PT36','CONTESTED_SHOTS_3PT36','DEFLECTIONS36','DEF_BOXOUTS36','CHARGES_DRAWN36','officialDefRtg','STL36','BLK36','DREB36','PF36']
for season,S in seasons.items():
    players=S['players']; usg={}
    def raw(team,kind):
        src=source_index.get((season,team,kind))
        if not src: return []
        assert sha(src['file'])==src['sha256']
        rows=table(src['file'])
        # NBA returns two global rows for some traded players (e.g. Bridges
        # 2022-23); retain all counts, never keep the last row as full-season.
        if kind in ['rim','three']:
            grouped=defaultdict(list)
            for row in rows:grouped[row['CLOSE_DEF_PERSON_ID']].append(row)
            rows=[]
            for pid,rr in grouped.items():
                if len(rr)==1:rows.append(rr[0]);continue
                row=rr[0].copy();ak,mk,fk,nk=('FGA_LT_06','FGM_LT_06','LT_06_PCT','NS_LT_06_PCT') if kind=='rim' else ('FG3A','FG3M','FG3_PCT','NS_FG3_PCT')
                attempts=sum(r[ak] for r in rr);row[ak]=attempts;row[mk]=sum(r[mk] for r in rr);row[fk]=row[mk]/attempts if attempts else 0;row[nk]=sum(r[nk]*r[ak] for r in rr)/attempts if attempts else 0
                for key in ['GP','G']:row[key]=sum(r.get(key,0) for r in rr)
                rows.append(row);audit['duplicateRowsMerged'].append({'season':season,'team':team,'kind':kind,'id':pid,'rows':len(rr),'attempts':attempts})
        return rows
    for r in raw(0,'advanced'):
        if r.get('USG_PCT') is not None: usg[r['PLAYER_ID']]=r['USG_PCT']*100 if r['USG_PCT']<=1 else r['USG_PCT']
    for team in sorted({s['team'] for s in manifest['sources'] if s['season']==season}):
        for kind in ['rim','three','hustle','advanced']:
            for r in raw(team,kind):
                pid=r.get('PLAYER_ID',r.get('CLOSE_DEF_PERSON_ID')); x=players.get(pid)
                if x is None: continue
                t=x['teams'].get(team) if team else x
                if t is None: audit['rejectedRows'].append({'season':season,'team':team,'kind':kind,'id':pid,'reason':'not in team logs'});continue
                if team and (r.get('GP',r.get('G',0))>t['GP']): audit['rejectedRows'].append({'season':season,'team':team,'kind':kind,'id':pid,'reason':'filtered GP exceeds franchise GP'});continue
                m=t['metrics'];n=t['samples']
                if kind=='rim':
                    a=r.get('FGA_LT_06',r.get('D_FGA',0));fg=r.get('LT_06_PCT',r.get('D_FG_PCT'));ns=r.get('NS_LT_06_PCT',r.get('NORMAL_FG_PCT'))
                    m['rimSuppression']=100*(ns-fg) if fg is not None and ns is not None and a>0 else None;n['rimFGA']=a
                elif kind=='three':
                    a=r.get('FG3A',r.get('D_FGA',0));fg=r.get('FG3_PCT',r.get('D_FG_PCT'));ns=r.get('NS_FG3_PCT',r.get('NORMAL_FG_PCT'))
                    m['threeSuppression']=100*(ns-fg) if fg is not None and ns is not None and a>0 else None;n['threeFGA']=a
                elif kind=='advanced': m['officialDefRtg']=-r['DEF_RATING'] if r.get('DEF_RATING') is not None else None
                else:
                    for k in p['metrics']['hustle']: m[k+'36']=36*r[k]/t['minutes'] if r.get(k) is not None else None
                    n['hustleGP']=r.get('G');n['hustleMIN']=r.get('MIN')
        matchup=defaultdict(lambda:dict.fromkeys(['fga','diff','wFGA','wDiff','partial','load','missingUsageFGA'],0.))
        for r in raw(team,'matchups'):
            pid=r['DEF_PLAYER_ID'];opid=r['OFF_PLAYER_ID'];x=players.get(pid);opp=players.get(opid)
            if x is None or opp is None: continue
            t=x['teams'].get(team) if team else x
            if t is None or (team and r['GP']>t['GP']): audit['rejectedRows'].append({'season':season,'team':team,'kind':'matchups','id':pid,'reason':'pair GP/ownership inconsistent'});continue
            b=opp['box']; fg2=ratio(b['FGM']-b['FG3M'],b['FGA']-b['FG3A']);fg3=ratio(b['FG3M'],b['FG3A']);a=r['MATCHUP_FGA'];a3=r['MATCHUP_FG3A']
            if (a-a3>0 and fg2 is None) or (a3>0 and fg3 is None): continue
            expected=(a-a3)*(fg2 or 0)+a3*(fg3 or 0);d=expected-r['MATCHUP_FGM'];v=matchup[pid];v['fga']+=a;v['diff']+=d
            if opid in usg:
                v['wFGA']+=a*usg[opid];v['wDiff']+=d*usg[opid];v['partial']+=r['PARTIAL_POSS'];v['load']+=r['PARTIAL_POSS']*usg[opid]
            else: v['missingUsageFGA']+=a
        for pid,v in matchup.items():
            t=players[pid]['teams'][team] if team else players[pid];t['metrics'].update(matchupSuppression=ratio(v['diff'],v['fga'],100),usageWeightedMatchupSuppression=ratio(v['wDiff'],v['wFGA'],100),defensiveLoad=ratio(v['load'],v['partial']))
            t['samples'].update(matchupFGA=v['fga'],matchupPartialPoss=v['partial'],usageMissingFGA=v['missingUsageFGA'])
    for pid,x in players.items():
        for metric in metricNames:
            if metric not in x['metrics']: x['metrics'][metric]=None
        # Box controls for the season-wide row use total individual counts.
        for k in ['STL','BLK','DREB','PF']:x['metrics'][k+'36']=36*x['box'][k]/x['minutes']
        for team,t in x['teams'].items():
            # A never-moved player is exactly the full-season endpoint sample.
            if len(x['teams'])==1:
                for k in metricNames:
                    if k not in ['onDefRtg','onOffDef','teamCenteredOn','onOffRimShare','onOffThreeShare']: t['metrics'][k]=x['metrics'].get(k)
                t['samples'].update({k:v for k,v in x['samples'].items() if k not in ['onPoss','offPoss']})
    # Reconcile filtered counts on all moved players; TEAM_ID can be last team even when filtered.
    for pid,x in players.items():
        if len(x['teams'])<2:continue
        for sample in ['rimFGA','threeFGA','matchupFGA']:
            vals=[t['samples'].get(sample) for t in x['teams'].values()];total=x['samples'].get(sample)
            if total is not None and all(v is not None for v in vals):
                diff=sum(vals)-total;audit['splitReconciliations'].append({'season':season,'id':pid,'sample':sample,'global':total,'teamSum':sum(vals),'difference':diff})
                if abs(diff)>1e-6:
                    for t in x['teams'].values():
                        for k in {'rimFGA':['rimSuppression'],'threeFGA':['threeSuppression'],'matchupFGA':['matchupSuppression','usageWeightedMatchupSuppression','defensiveLoad']}[sample]:t['metrics'][k]=None
                    audit['rejectedRows'].append({'season':season,'id':pid,'kind':sample,'reason':'split counts do not sum to global'})
    for metric in metricNames:
        usable=[x for x in players.values() if x['metrics'].get(metric) is not None]
        rotation=[x for x in players.values() if x['minutes']>=500]
        inventory.append({'season':season,'metric':metric,'players':len(usable),'totalPlayers':len(players),'playerCoverage':len(usable)/len(players),'minuteCoverage':sum(x['minutes'] for x in usable)/sum(x['minutes'] for x in players.values()),'rotationPlayers':sum(x['metrics'].get(metric) is not None for x in rotation),'totalRotationPlayers':len(rotation)})
    print('METRICS',season,'players',len(players),flush=True)
save('players.json',seasons);save('inventory.json',{'metrics':inventory,'fetch':{'jobs':manifest['jobs'],'success':len(manifest['sources']),'failures':manifest['failures']},'strictGames':{s:S['strictGames'] for s,S in seasons.items()}});save('endpoint-audit.json',audit)

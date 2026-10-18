import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json, re, hashlib, unicodedata
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from scipy.stats import rankdata
R=Path(__file__).resolve().parents[3]; O=R/'reports/defense-tenth/step4-t2'
def read(p):return json.loads((O/p).read_text(encoding='utf-8'))
def save(p,x):(O/p).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
p=read('protocol.json');data=read('players.json');inv=read('inventory.json')
metrics=sorted({r['metric'] for r in inv['metrics']})
def sufficient(x,metric,move=False):
    m=x['metrics'].get(metric); s=x['samples']
    if m is None or not np.isfinite(m):return False
    if metric=='rimSuppression':return s.get('rimFGA',0)>=(50 if move else 100)
    if metric=='threeSuppression':return s.get('threeFGA',0)>=(40 if move else 75)
    if metric in ['matchupSuppression','usageWeightedMatchupSuppression','defensiveLoad']:return s.get('matchupFGA',0)>=(50 if move else 100)
    if metric in ['onDefRtg','onOffDef','teamCenteredOn','onOffRimShare','onOffThreeShare']:
        return s.get('onPoss',0)>=(300 if move else 1000) and s.get('offPoss',0)>=(300 if move else 1000)
    return True
def corr(x,y,w=None):
    w=np.ones(len(x)) if w is None else w;sw=w.sum()
    if sw<=0:return None
    mx=np.dot(w,x)/sw;my=np.dot(w,y)/sw;xx=np.dot(w,(x-mx)**2);yy=np.dot(w,(y-my)**2)
    return float(np.dot(w,(x-mx)*(y-my))/np.sqrt(xx*yy)) if xx>1e-15 and yy>1e-15 else None
def evaluate(rows,tag,teamonly=False):
    n=len(rows)
    if n<10:return {'n':n,'players':len({r['id'] for r in rows}),'pearson':None,'spearman':None,'ci95':None,'reason':'fewer than 10 pairs'}
    counts=Counter(r['period'] for r in rows)
    x=np.array([r['x'] for r in rows],float);y=np.array([r['y'] for r in rows],float)
    # Equal transition/season weight and within-transition centering.
    if len(counts)>1:
        for period in counts:
            mask=np.array([r['period']==period for r in rows]);x[mask]-=x[mask].mean();y[mask]-=y[mask].mean()
    base=np.array([1/counts[r['period']] for r in rows])
    point=corr(x,y,base);rankcorr=corr(rankdata(x),rankdata(y),base)
    ids=sorted({r['id'] for r in rows});ix={v:i for i,v in enumerate(ids)};pi=np.array([ix[r['id']] for r in rows]);teams=sorted({t for r in rows for t in r['teams']});ti={v:i for i,v in enumerate(teams)}
    t0=np.array([ti[r['teams'][0]] for r in rows]);t1=np.array([ti[r['teams'][-1]] for r in rows]);rng=np.random.default_rng(p['uncertainty']['rng']^int(hashlib.sha256(tag.encode()).hexdigest()[:8],16));values=[]
    for start in range(0,20000,500):
        b=min(500,20000-start);tc=rng.multinomial(len(teams),np.ones(len(teams))/len(teams),size=b);w=(tc[:,t0]+tc[:,t1])/2
        if not teamonly:pc=rng.multinomial(len(ids),np.ones(len(ids))/len(ids),size=b);w=w*pc[:,pi]
        w=w*base;vx=np.zeros(b);vy=np.zeros(b);cov=np.zeros(b);good=np.ones(b,dtype=bool)
        # Recenter and renormalize each period inside every resample. A
        # franchise draw must not accidentally change season weighting.
        for period in counts:
            mask=np.array([r['period']==period for r in rows]);ww=w[:,mask];xx=x[mask];yy=y[mask];sw=ww.sum(axis=1);safe=np.maximum(sw,1e-100)
            mx=ww@xx/safe;my=ww@yy/safe;vx+=ww@(xx*xx)/safe-mx*mx;vy+=ww@(yy*yy)/safe-my*my;cov+=ww@(xx*yy)/safe-mx*my;good&=sw>0
        good&=(vx>1e-12)&(vy>1e-12);values.extend((cov[good]/np.sqrt(vx[good]*vy[good])).tolist())
    ci=np.quantile(values,[.025,.975]).tolist() if values else None
    return {'n':n,'players':len(ids),'franchises':len(teams),'pearson':point,'spearman':rankcorr,'ci95':ci,'validBootstrap':len(values),'label':'descriptive association, not portability proof'}
adj=[];eligibility=[]
for before,after in zip(p['seasons'][:-1],p['seasons'][1:]):
    A=data[before]['players'];B=data[after]['players']; eligible=[];excluded=[]
    for pid in sorted(set(A)&set(B)):
        a=A[pid];b=B[pid]
        reason='less than 500 minutes' if min(a['minutes'],b['minutes'])<500 else 'dominant franchise below 60%' if min(a['dominantShare'],b['dominantShare'])<.6 else None
        if reason:excluded.append({'id':int(pid),'name':a['name'],'reason':reason});continue
        group='same' if a['dominantTeam']==b['dominantTeam'] else 'moved';eligible.append({'id':int(pid),'name':a['name'],'group':group,'before':before,'after':after,'teams':[a['dominantTeam'],b['dominantTeam']]})
        for metric in metrics:
            if sufficient(a,metric) and sufficient(b,metric):adj.append({'metric':metric,'group':group,'period':before+'→'+after,'id':int(pid),'teams':[a['dominantTeam'],b['dominantTeam']],'x':a['metrics'][metric],'y':b['metrics'][metric]})
    eligibility.append({'before':before,'after':after,'eligible':eligible,'excluded':excluded})

def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
trade_sources=read('trade-sources.json');trade_index={};trade_evidence=[]
for src in trade_sources['sources']:
    html=(R/src['file']).read_text(encoding='utf-8');j=json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',html,re.S).group(1));art=j['props']['pageProps']['article'];body=art['contentFiltered'];text=norm(art['contentText']);ids={int(v) for v in re.findall(r'/player/(\d+)',body)}
    trade_index[src['season']]={'ids':ids,'text':text}
moves=[]; move_audit=[]
for season,S in data.items():
    for pid,x in S['players'].items():
        ts=sorted(x['teams'].values(),key=lambda t:min(t['dates']))
        if len(ts)<2:continue
        reason='overlapping/returned chronology' if any(max(ts[i]['dates'])>=min(ts[i+1]['dates']) for i in range(len(ts)-1)) else None
        eligible=[t for t in ts if t['minutes']>=300]
        if len(eligible)<2:reason=reason or 'fewer than two franchises with 300 minutes'
        confirmed=False; match=None
        if season in trade_index and len(ts)==2:
            tr=trade_index[season];name=norm(x['name']);confirmed=int(pid) in tr['ids'] or (' '+name+' ') in (' '+tr['text']+' ');match='player link ID' if int(pid) in tr['ids'] else 'exact normalized full name' if confirmed else None
        move_audit.append({'season':season,'id':int(pid),'name':x['name'],'teams':[t['id'] for t in ts],'minutes':[t['minutes'] for t in ts],'reason':reason,'officialTradeParticipant':confirmed,'verification':match})
        if reason:continue
        a,b=eligible[0],eligible[-1]
        for metric in metrics:
            if sufficient(a,metric,True) and sufficient(b,metric,True):moves.append({'metric':metric,'group':'seasonMove','period':season,'id':int(pid),'teams':[a['id'],b['id']],'x':a['metrics'][metric],'y':b['metrics'][metric],'officialTradeParticipant':confirmed})
save('move-samples.json',{'rows':moves,'audit':move_audit,'limitation':'Confirmed article-list participation subset; not a full transaction-history identification of the first→last leg.'})
save('adjacent-samples.json',{'rows':adj,'eligibility':eligibility})
results=[]
periods=sorted({r['period'] for r in adj})
for metric in metrics:
    for group in ['same','moved']:
        for period in periods+['pooled']:
            rows=[r for r in adj if r['metric']==metric and r['group']==group and (period=='pooled' or r['period']==period)]
            results.append({'metric':metric,'comparison':'adjacent','group':group,'period':period,**evaluate(rows,metric+group+period)})
    for group in ['seasonMove','officialTradeParticipant']:
        for period in p['seasons']+['pooled']:
            rows=[r for r in moves if r['metric']==metric and (group=='seasonMove' or r['officialTradeParticipant']) and (period=='pooled' or r['period']==period)]
            results.append({'metric':metric,'comparison':'withinSeason','group':group,'period':period,**evaluate(rows,metric+group+period)})
    print('CORRELATIONS',metric,flush=True)
save('correlations.json',results)
team_results=[];team_predictions=[]
for metric in metrics:
    rows=[];contexts=[]
    for season,S in data.items():
        for tid,team in S['teams'].items():
            tid=int(tid);ps=[x['teams'][str(tid)] for x in S['players'].values() if str(tid) in x['teams']]
            total=sum(t['minutes'] for t in ps);obs=[t for t in ps if sufficient(t,metric)]
            covered=sum(t['minutes'] for t in obs)
            if covered<.8*total or not obs:continue
            x=sum(t['minutes']*t['metrics'][metric] for t in obs)/covered
            row={'metric':metric,'period':season,'id':tid,'teams':[tid,tid],'x':x,'y':-team['defRtg'],'minuteCoverage':covered/total};rows.append(row);team_predictions.append(row)
        for pid,x in S['players'].items():
            if x['minutes']>=500 and x['dominantShare']>=.6 and sufficient(x,metric) and x['metrics'].get('offDefRtg') is not None and x['samples'].get('offPoss',0)>=1000:
                contexts.append({'period':season,'id':int(pid),'teams':[x['dominantTeam'],x['dominantTeam']],'x':x['metrics'][metric],'y':x['metrics']['offDefRtg']})
    for period in p['seasons']+['pooled']:
        rr=[r for r in rows if period=='pooled' or r['period']==period];cc=[r for r in contexts if period=='pooled' or r['period']==period]
        team_results.append({'metric':metric,'period':period,'kind':'teamDefRtg',**evaluate(rr,'team'+metric+period,True)})
        team_results.append({'metric':metric,'period':period,'kind':'matchedOffContext',**evaluate(cc,'off'+metric+period)})
save('team-correlations.json',{'results':team_results,'predictions':team_predictions})
print('DONE',len(results),len(team_results),flush=True)

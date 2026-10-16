"""Offline, game-grouped binomial/Poisson ridge with simultaneous offense/defense.
No team indicator and no win/OVR input. Only later lineup exposures used at test.
"""
import json, hashlib, time
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.special import expit
from scipy.optimize import minimize
R=Path(__file__).resolve().parents[1];out=R/'reports/defense-third';out.mkdir(exist_ok=True)
def read(f): return json.loads((R/f).read_text(encoding='utf-8'))
def table(f):
    d=read(f)['data'];t=d['resultSets'][0];return [dict(zip(t['headers'],r)) for r in t['rowSet']]
league=read('data/season-league.json');cards={p['playerId']:p for t in league['teams'] for p in t['roster']}
pids=sorted(cards);pi={p:i for i,p in enumerate(pids)};P=len(pids)
game_map={g['id']:g for g in league['schedule']};order={};counter={t['id']:0 for t in league['teams']}
for g in sorted(league['schedule'],key=lambda g:(g['date'],g['id'])):
    for t in (g['homeId'],g['awayId']):counter[t]+=1;order[g['id'],t]=counter[t]
prep=read('reports/defense-b1/defensive-samples.json')
def ids(a): return {x if isinstance(x,str) else x['id'] for x in a}
exclude=ids(prep['lineupFailed'])|ids(prep['uncertainPossessionGames'])|ids(prep['counterMismatchGames'])|ids(prep['missingPbp'])
strict=set(game_map)-exclude
assert len(strict)==1188,(len(strict),list(exclude)[:4])
rows=[]
with (R/'reports/defense-b1/stints.jsonl').open(encoding='utf-8') as f:
    for line in f:
        s=json.loads(line)
        if s['id'] not in strict:continue
        for j,t in enumerate(s['teams']):
            rows.append(dict(id=s['id'],team=t['teamId'],defense=t['players'],offense=s['teams'][1-j]['players'],n=t['defensivePossessionEnds'],**t['opponent']))
N=len(rows);game_ids=np.array([r['id'] for r in rows]);team_ids=np.array([r['team'] for r in rows]);
train_games={g for g in strict if all(order[g,t]<=41 for t in (game_map[g]['homeId'],game_map[g]['awayId']))}
train=np.array([g in train_games for g in game_ids]);test=np.array([order[r['id'],r['team']]>41 for r in rows]);assert not set(game_ids[train])&set(game_ids[test])
ii=[];jj=[]
for k,r in enumerate(rows):
    ii.extend([k]*10);jj.extend([pi[p] for p in r['offense']]+[P+pi[p] for p in r['defense']])
X=sparse.csr_matrix((np.full(len(ii),.2),(ii,jj)),shape=(N,2*P))
boxes=table('data/season-source/player-games.json');teams=table('data/season-source/team-games.json');poss={(r['GAME_ID'],r['TEAM_ID']):r['FGA']-r['OREB']+r['TOV']+.44*r['FTA'] for r in teams}
positions=['PG','SG','SF','PF','C']
tracking_manifest=read('data/defense-third-source/manifest.json');assert len(tracking_manifest['sources'])==60 and not tracking_manifest['failures']
tracking={}
curves={'long':[(0,.120),(40,.085),(55,.040),(70,.003),(85,-.038),(99,-.076),(120,-.100),(150,-.120)],'short':[(0,.150),(40,.105),(55,.050),(70,.004),(85,-.048),(99,-.095),(120,-.125),(150,-.150)]}
for src in tracking_manifest['sources']:
    g41=next(g for g in league['schedule'] if g['id'] in game_map and (g['homeId']==src['teamId'] or g['awayId']==src['teamId']) and order[g['id'],src['teamId']]==41)
    assert g41['date']==src['date']
    for t in table(src['file']):
        assert t['GP']<=41
        attempts=t.get('D_FGA',t.get('FG3A' if src['zone']=='long' else 'FGA_LT_06',0));diff=t.get('PCT_PLUSMINUS',t.get('PLUSMINUS',0))
        points=curves[src['zone']];effect=diff*attempts/(attempts+200)
        attr=float(np.clip(np.interp(effect,[y for x,y in points][::-1],[x for x,y in points][::-1]),40,99)) if attempts>0 else 70
        tracking[src['teamId'],t['CLOSE_DEF_PERSON_ID'],src['zone']]=attr
tracking_rows=np.array([[np.mean([tracking.get((r['team'],p,z),70)-70 for p in r['defense']])/20 for z in ['long','short']] for r in rows])
def features(allowed):
    totals=np.zeros((P,5))
    for b in boxes:
        if b['GAME_ID'] not in allowed:continue
        i=pi[b['PLAYER_ID']];n=b['MIN']/48*poss.get((b['GAME_ID'],b['TEAM_ID']),100)
        totals[i]+=np.array([n,b['STL'],b['BLK'],b['DREB'],b['PF']])
    mean=totals[:,1:].sum(axis=0)/totals[:,0].sum();rates=(totals[:,1:]+200*mean)/(totals[:,0,None]+200)
    Z=(rates-mean)/(np.std(rates,axis=0)+1e-9)
    pos=np.array([[float(cards[p]['pos']==x) for x in positions] for p in pids]);F=np.column_stack((Z,pos))
    B=sparse.block_diag((sparse.csr_matrix(F),sparse.csr_matrix(F))).toarray()
    prior=np.column_stack((np.ones(N),X@B))
    # Same current-card recipe, rebuilt from each team's pre41 tracking endpoint.
    current=np.column_stack((np.ones(N),X[:,:P]@F,tracking_rows))
    return prior,current,totals
outcomes={
 'shortFG':('shortM','shortA','binomial'),'midFG':('midM','midA','binomial'),'threeFG':('longM','longA','binomial'),
 'shortShare':('shortA','fga','binomial'),'midShare':('midA','fga','binomial'),'threeShare':('longA','fga','binomial'),
 'liveTOV':('liveTov','n','binomial'),'DREB':('dreb',None,'binomial'),'FTA':('fta','n','poisson')}
def arrays(spec):
    y=np.array([r[spec[0]] for r in rows],float)
    n=np.array([r[spec[1]] if spec[1] else r['dreb']+r['oreb'] for r in rows],float)
    # FT substitutions create instantaneous lineups with no possession ends.
    # Model their count with a separate learned intercept and one stint exposure.
    if spec[2]=='poisson':n=np.where(n>0,n,1)
    return y,n
def fit(A,y,n,mask,family,penalty,offset=None):
    mask=mask&(n>0);a=A[mask];yy=y[mask];nn=n[mask];off=np.zeros(mask.sum()) if offset is None else offset[mask]
    weights=np.full(A.shape[1],penalty);weights[0]=0 if not sparse.issparse(A) else penalty
    def fg(b):
        eta=np.clip(a@b+off,-18,18)
        if family=='binomial':mu=nn*expit(eta);loss=np.sum(nn*np.logaddexp(0,eta)-yy*eta)
        else:mu=nn*np.exp(eta);loss=np.sum(mu-yy*eta)
        return (loss+.5*np.dot(weights*b,b))/len(yy),np.asarray(a.T@(mu-yy)+weights*b).ravel()/len(yy)
    z=np.zeros(A.shape[1]);res=minimize(fg,z,jac=True,method='L-BFGS-B',options={'maxiter':180,'ftol':1e-9,'gtol':2e-6})
    if not np.isfinite(res.fun):raise ValueError('nonfinite fit')
    return res.x,dict(success=bool(res.success),iterations=int(res.nit),gradient=float(np.max(np.abs(res.jac))))
def loss(eta,y,n,mask,family):
    m=mask&(n>0);e=np.clip(eta[m],-18,18)
    return float(np.sum(n[m]*np.logaddexp(0,e)-y[m]*e) if family=='binomial' else np.sum(n[m]*np.exp(e)-y[m]*e))
fold={g:int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%3 for g in train_games}
fold_inputs=[]
for f in range(3):
    allowed={g for g in train_games if fold[g]!=f};a,c,_=features(allowed)
    fold_inputs.append((np.array([g in allowed for g in game_ids]),train&np.array([fold.get(g,-1)==f for g in game_ids]),a,c))
A,C,totals=features(train_games);preds={'current':{},'prior':{},'new':{}};cv={};coeff={};diagnostics={};lambdas=[1,3,10,30,100,300,1000,3000]
start=time.time()
for name,spec in outcomes.items():
    y,n=arrays(spec);family=spec[2];scores={l:0. for l in lambdas}
    dead=np.array([r['n']==0 for r in rows],float)
    for tm,vm,a,c in fold_inputs:
        if family=='poisson':a=np.column_stack((a,dead))
        beta,_=fit(a,y,n,tm,family,3);offset=a@beta
        for l in lambdas:
            residual,_=fit(X,y,n,tm,family,l,offset);scores[l]+=loss(offset+X@residual,y,n,vm,family)
    selected=min(scores,key=scores.get);outcomeA=np.column_stack((A,dead)) if family=='poisson' else A;outcomeC=np.column_stack((C,dead)) if family=='poisson' else C
    prior,d1=fit(outcomeA,y,n,train,family,3);offset=outcomeA@prior
    residual,d2=fit(X,y,n,train,family,selected,offset);current,d3=fit(outcomeC,y,n,train,family,3)
    for method,eta in [('current',outcomeC@current),('prior',offset),('new',offset+X@residual)]:preds[method][name]=expit(eta) if family=='binomial' else np.exp(np.clip(eta,-18,18))
    cv[name]={'selected':selected,'negativeLogLikelihood':scores,'folds':3};coeff[name]={'prior':prior.tolist(),'offenseResidual':residual[:P].tolist(),'defenseResidual':residual[P:].tolist()}
    diagnostics[name]={'prior':d1,'residual':d2,'current':d3,'zeroExposureDroppedY':float(y[train&(n==0)].sum()),'trainY':float(y[train].sum()),'testZeroExposureY':float(y[test&(n==0)].sum()),'zeroPossessionY':float(y[train&(dead==1)].sum())}
    print(name,selected,round(time.time()-start,1),flush=True)
# Normalize three separately modeled shot shares to a coherent simplex.
for method in preds:
    total=sum(preds[method][z+'Share'] for z in ['short','mid','three'])
    for z in ['short','mid','three']:preds[method][z+'Share']/=total
metric_names=['opp2','opp3','liveTOVRate','DREBRate','FTR','shortShare','midShare','threeShare','shortFG','midFG']
game_rows={m:[] for m in ['observed',*preds]}
for g in sorted(set(game_ids[test])):
    for tid in (game_map[g]['homeId'],game_map[g]['awayId']):
        idx=np.flatnonzero(test&(game_ids==g)&(team_ids==tid))
        if not len(idx):continue
        sums=lambda k:sum(rows[i][k] for i in idx)
        den=[sums('shortA')+sums('midA'),sums('longA'),sums('n'),sums('dreb')+sums('oreb'),sums('fga'),sums('fga'),sums('fga'),sums('fga'),sums('shortA'),sums('midA')]
        num=[sums('shortM')+sums('midM'),sums('longM'),sums('liveTov'),sums('dreb'),sums('fta'),sums('shortA'),sums('midA'),sums('longA'),sums('shortM'),sums('midM')]
        game_rows['observed'].append({'id':g,'team':tid,'num':num,'den':den})
        for method,p in preds.items():
            predicted=[]
            for k in metric_names:
                if k=='opp2':
                    share=p['shortShare'][idx]+p['midShare'][idx]
                    rate=(p['shortShare'][idx]*p['shortFG'][idx]+p['midShare'][idx]*p['midFG'][idx])/share
                    val=sum(rate*np.array([rows[i]['shortA']+rows[i]['midA'] for i in idx]))
                elif k in ['opp3','shortFG','midFG']:
                    z='three' if k=='opp3' else k[:-2];attempt='longA' if z=='three' else z+'A';val=sum(p[z+'FG'][idx]*np.array([rows[i][attempt] for i in idx]))
                elif k in ['liveTOVRate','FTR']:val=sum(p['liveTOV' if k=='liveTOVRate' else 'FTA'][idx]*np.array([rows[i]['n'] if k=='liveTOVRate' else max(1,rows[i]['n']) for i in idx]))
                elif k=='DREBRate':val=sum(p['DREB'][idx]*np.array([rows[i]['dreb']+rows[i]['oreb'] for i in idx]))
                else:val=sum(p[k][idx]*np.array([rows[i]['fga'] for i in idx]))
                predicted.append(float(val))
            game_rows[method].append({'id':g,'team':tid,'num':predicted,'den':den})
team_order=sorted(counter)
def team_values(method,weights=None):
    num=np.zeros((30,len(metric_names)));den=num.copy()
    for r in game_rows[method]:
        w=1 if weights is None else weights.get(r['id'],0);j=team_order.index(r['team']);num[j]+=w*np.array(r['num']);den[j]+=w*np.array(r['den'])
    return num/np.maximum(den,1e-9),num.sum(axis=0)/np.maximum(den.sum(axis=0),1e-9)
def score(a,b,ca,cb):
    return {'correlation':float(np.corrcoef(a,b)[0,1]),'sdRatio':float(np.std(b)/np.std(a)), 'centeredRMSE':float(np.sqrt(np.mean(((a-ca)-(b-cb))**2))), 'centeredMAE':float(np.mean(np.abs((a-ca)-(b-cb)))),'bias':float(cb-ca)}
truth,truth_center=team_values('observed');metrics={}
for method in preds:
    values,center=team_values(method);metrics[method]={k:score(truth[:,i],values[:,i],truth_center[i],center[i]) for i,k in enumerate(metric_names)}
boot={k:[] for k in metric_names};rng=np.random.default_rng(20261103);gids=sorted(set(game_ids[test]))
for b in range(500):
    sampled=rng.choice(gids,len(gids),replace=True);unique,counts=np.unique(sampled,return_counts=True);weights=dict(zip(unique,counts))
    a,ca=team_values('observed',weights);old,co=team_values('current',weights);new,cn=team_values('new',weights)
    for i,k in enumerate(metric_names):boot[k].append(score(a[:,i],new[:,i],ca[i],cn[i])['centeredRMSE']-score(a[:,i],old[:,i],ca[i],co[i])['centeredRMSE'])
paired={k:{'rmseNewMinusCurrent':metrics['new'][k]['centeredRMSE']-metrics['current'][k]['centeredRMSE'],'ci95':np.quantile(boot[k],[.025,.975]).tolist()} for k in metric_names}
result={'strictGames':1188,'stintSideRows':N,'trainGames':len(train_games),'testGames':len(gids),'trainSideRows':int(train.sum()),'testSideRows':int(test.sum()),
 'method':'Binomial GLM for FG, zone shares, live TOV and DREB; Poisson FTA with two exposure strata: actual possession ends for positive rows; one instantaneous-stint exposure plus separate learned intercept for zero-end rows (including FT substitutions). All FTA labels retained. Offense five and defense five simultaneous sparse player effects (averaged1/5). Ridge residuals around learned box+position prior; fixed200-possession feature smoothing. Three game-grouped folds select residual precision from1/3/10/30/100/300/1000/3000. Three zone probabilities renormalized. FTA is a conditional stint-count model, not yet a foul-moment causal attribution.',
 'split':'Chronological schedule date+ID, individual team game index <=41. Training requires BOTH teams in first41, excluding crossover games to avoid same-game train/test leakage. Test uses each defender team index >41, only true later lineups and opportunity weights; no later outcomes fitted.',
 'currentSignalLimitation':'Current signal rebuilt with the frozen individual tracking recipe (difference*attempts/(attempts+200), inverse curve bounded40..99, missing70) using each team first41 cutoff. DateTo accepted in API parameters, GP<=41 checked, every returned player matched to a pre-cutoff official player game on that team. GLM mapping fitted only on train. This compares signal information under a common offline response model, not engine probabilities or an engine-integrated validation.',
 'prior':'Player box STL/BLK/DREB/PF per estimated exposed possession, plus position; no team IDs in design. Players absent from train have population rate/position prior, zero residual.',
 'uncertainty':'Paired test-game bootstrap 500; fitted models held fixed, no refit. Conditional held-out uncertainty, not estimation uncertainty.',
 'metricUnits':'Rates are fractions. FTR=FTA/FGA. Forced live turnovers per actual possession ends; not total turnover rate. DREB uses player DREB/(player DREB+opponent player OREB).',
 'metrics':metrics,'paired':paired,'cv':cv,'fitDiagnostics':diagnostics,'players':pids,'trainPlayerExposure':totals[:,0].tolist(),'teamTestGames':{str(t):len({r['id'] for r in game_rows['observed'] if r['team']==t}) for t in team_order},
 'trainTeamGames':{str(t):sum(g in train_games and t in (game_map[g]['homeId'],game_map[g]['awayId']) for g in train_games) for t in team_order},
 'runtime':{'numpy':np.__version__},
 'sources':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in ['reports/defense-b1/stints.jsonl','reports/defense-b1/defensive-samples.json','data/season-source/player-games.json','data/season-source/team-games.json','data/season-league.json','data/defense-third-source/manifest.json','scripts/estimate_defense_third.py']}}
(out/'offline-model.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(out/'offline-coefficients.json').write_text(json.dumps({'players':pids,'coefficients':coeff,'engineIntegrated':False},ensure_ascii=False)+'\n',encoding='utf-8')
(out/'offline-predictions.json').write_text(json.dumps(game_rows,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# B1 離線時間切分估計','','嚴格1188場；訓練要求兩隊都在各自前41場，測試依防守球隊後41場。',result['currentSignalLimitation'],'','| 指標 | 現行訊號 相關 / SD比 / RMSE | 只用先驗 | 新模型 | 新−現行 RMSE 95%區間 |','|---|---:|---:|---:|---:|']
for k in metric_names:
    cells=[' / '.join(f"{metrics[m][k][v]:.4f}" for v in ['correlation','sdRatio','centeredRMSE']) for m in preds]
    md.append('| '+k+' | '+' | '.join(cells)+' | '+str([round(v,4) for v in paired[k]['ci95']])+' |')
md+=['',f'訓練 {len(train_games)} 場；測試 {len(gids)} 場，各隊有效後半場數詳見 JSON。未接引擎。',result['method'],result['uncertainty'],'']
(out/'offline-model.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'trainGames':len(train_games),'testGames':len(gids),'metrics':metrics,'paired':paired}),flush=True)

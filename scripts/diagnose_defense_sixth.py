"""Read-only capability diagnosis. Heldout outcomes below NEVER make cards."""
from defense_sixth_data import *
from scipy.special import ndtr
d=Data(41);print('Loaded strict stints',len(d.rows),flush=True)
phase={}
for name,test in [('train',False),('post',True)]:
 phase[name]=[]
 for t in d.league['teams']:
  rows=[b for b in d.team if b['TEAM_ID']==t['id'] and (d.order[b['GAME_ID'],t['id']]>41)==test];opp=[d.tb[b['GAME_ID'],next(i for i in [d.gmap[b['GAME_ID']]['homeId'],d.gmap[b['GAME_ID']]['awayId']] if i!=t['id'])] for b in rows];poss=sum((b['FGA']-b['OREB']+b['TOV']+.44*b['FTA']+o['FGA']-o['OREB']+o['TOV']+.44*o['FTA'])/2 for b,o in zip(rows,opp));phase[name].append(dict(id=t['id'],net=sum(b['PLUS_MINUS'] for b in rows)/len(rows),offense=sum(b['PTS'] for b in rows)/poss*100,defense=sum(b['PTS'] for b in opp)/poss*100))
aggregate=[]
for t in d.league['teams']:
 ps=[p for p in d.cards['players'] if p['teamId']==t['id']];w=np.array([p['minutes'] for p in ps]);aggregate.append(dict(id=t['id'],offense=float(w@np.array([p['offense'] for p in ps])/w.sum()),defense=float(w@np.array([p['defenseAllowed'] for p in ps])/w.sum())))
aggMetrics={key:metrics([r[key] for r in phase['train']],[r[key] for r in aggregate]) for key in ['offense','defense']}
print('Card sum',aggMetrics,flush=True)
# Post-only regularized residuals control all ten players. Diagnosis, not input.
b,cv=choose(d,d.test);print('Controlled post diagnostic',cv,flush=True)
effects=np.column_stack((100*d.leaguePPP*b[1:1+d.P],100*d.leaguePPP*b[1+d.P:]));exposure=np.asarray(d.X[d.test,:d.P].T@d.n[d.test]).ravel();groups=[]
for lo,hi in [(0,100),(100,400),(400,800),(800,1200),(1200,10000)]:
 m=(d.minutes>=lo)&(d.minutes<hi)&(exposure>0);w=exposure[m];groups.append(dict(trainMinutes=[lo,hi],players=int(m.sum()),postDefensivePossessions=float(w.sum()*5),offenseObservedMinusCard=float(w@effects[m,0]/w.sum()),defenseAllowedObservedMinusCard=float(w@effects[m,1]/w.sum()),netObservedMinusCard=float(w@(effects[m,0]-effects[m,1])/w.sum())))
# Raw on-court rates for requested top-ten later-minute players, with controlled residuals separately.
details={}
for tid in [1610612758,1610612765,1610612754,1610612749]:
 later={}
 for r in d.box:
  if r['TEAM_ID']==tid and d.order[r['GAME_ID'],tid]>41:later[r['PLAYER_ID']]=later.get(r['PLAYER_ID'],0)+r['MIN']
 details[str(tid)]=[]
 for pid,minutes in sorted(later.items(),key=lambda z:-z[1])[:10]:
  i=d.pi[pid];p=d.bycard.get((tid,pid),d.cv[pid]);own=np.array([r['team']==tid and pid in r['offense'] for r in d.rows])&d.test;opp=np.array([r['opponent']==tid and pid in r['defense'] and d.order[r['id'],tid]>41 for r in d.rows]);on=d.y[own].sum()/d.n[own].sum()*100 if d.n[own].sum() else 0;allowed=d.y[opp].sum()/d.n[opp].sum()*100 if d.n[opp].sum() else 0
  raw=p['raw'];lg=d.cards['reference'];a=p['attributes'];curves=d.cards['curves'];shots={}
  # Raw before shrink exists only where the training box has the outcome.
  for z,m,n in [('long','FG3M','FG3A'),('ft','FTM','FTA')]:
   rawrate=raw.get(m,0)/raw[n] if raw.get(n,0)>0 else None;curve=curves[z];postrate=float(np.interp(a[z],[q[0] for q in curve],[q[1] for q in curve]));shots[z]=dict(attempts=raw.get(n,0),rawRate=rawrate,shrunkRate=postrate)
  details[str(tid)].append(dict(id=pid,name=p['name'],trainMinutes=float(d.minutes[i]),inTeamTrainMinutes=p['minutes'],postMinutes=minutes,cardOffense=p['offense'],cardDefenseAllowed=p['defenseAllowed'],postOnCourtOffense=float(on),postOnCourtDefense=float(allowed),postOnCourtNet=float(on-allowed),controlledOffenseMinusCard=float(effects[i,0]),controlledDefenseAllowedMinusCard=float(effects[i,1]),shotShrinkage=shots))
result=dict(phaseTruth=phase,weightedCardValues=aggregate,aggregateMetrics=aggMetrics,minuteGroups=groups,controlledPostCV=cv,fourTeams=details,zeroExposurePointsDropped=d.zeroY,shrinkage={'shooting':'100 recorded attempts at league training shooting mean, then inverse curve. Missing players get league mean; nonshooting skills often70.','defense':'Box/position prior + game-CV player ridge; signal centered at training league.','warning':'Analytic EV is an additive diagnostic proxy, not full game PPP. Post coefficients diagnosed here are never engine inputs; sparse low-minute residuals remain regularized and correlated.'})
save('diagnosis.json',result)
print('WROTE diagnosis.json',flush=True)

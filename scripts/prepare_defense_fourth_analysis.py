import json, math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];out=R/'reports/defense-fourth'
read=lambda p:json.loads((R/p).read_text(encoding='utf-8'))
league=read('data/season-league.json');ids=[t['id'] for t in league['teams']];ix={t:i for i,t in enumerate(ids)}
games=league['schedule'];X=np.zeros((len(games),31));m=np.array([g['observed']['homeScore']-g['observed']['awayScore'] for g in games])
for i,g in enumerate(games):X[i,ix[g['homeId']]]=1;X[i,ix[g['awayId']]]=-1;X[i,30]=0 if g['neutral'] else 1
b=np.linalg.lstsq(X,m,rcond=None)[0];mu=X@b;res=m-mu;res-=res.mean();res*=math.sqrt(len(games)/(len(games)-30))
expected_net=np.zeros(30);expected_wins=np.zeros(30)
for j,g in enumerate(games):
    h,a=ix[g['homeId']],ix[g['awayId']];expected_net[h]+=mu[j]/82;expected_net[a]-=mu[j]/82
    p=np.mean(res>-mu[j]);expected_wins[h]+=p;expected_wins[a]+=1-p
rng=np.random.default_rng(20261032);results=[]
for _ in range(5000):
    margin=mu+rng.choice(res,len(games),replace=True)+rng.uniform(-.001,.001,len(games));net=np.zeros(30);wins=np.zeros(30)
    for j,g in enumerate(games):
        h,a=ix[g['homeId']],ix[g['awayId']];net[h]+=margin[j]/82;net[a]-=margin[j]/82;wins[h]+=margin[j]>0;wins[a]+=margin[j]<0
    results.append([np.sqrt(np.mean((net-expected_net)**2)),np.mean(abs(wins-expected_wins)),np.sqrt(np.mean((wins-expected_wins)**2))])
v=np.array(results)
noise={'method':'Diagnostic oracle approximation: least-squares team strength plus common home effect fitted to observed margins; centered empirical game residuals with 1230/(1230-30) variance correction, 5000 independent resampled seasons on actual schedule. Team IDs used only to estimate diagnostic latent strengths, never simulation probability inputs. Fixed strengths/independent games assumed; oracle knows these strengths. Not an information-theoretic lower bound and no parameter-estimation uncertainty included.',
 'games':len(games),'residualSD':float(np.std(res)),'commonHomeMargin':float(b[-1]),'netRMSE':float(v[:,0].mean()),'winMAE':float(v[:,1].mean()),'winRMSE':float(v[:,2].mean()),'seasonRealization95':dict(zip(['netRMSE','winMAE','winRMSE'],np.quantile(v,[.025,.975],axis=0).T.tolist())),
 'sensitivity':'Net floor approximately proportional to residual SD; +/-10% residual SD implies +/-10% net floor. Real schedules/availability and changing strength violate stationarity; observed one-season team means are not exact latent targets.'}
(out/'noise-floor.json').write_text(json.dumps(noise,indent=2)+'\n',encoding='utf-8')
cells={};overall=[0.,0.]
with (R/'reports/defense-b1/real-games.jsonl').open(encoding='utf-8') as f:
    for line in f:
        g=json.loads(line)
        if not g['lineupsValid'] or not g['pointsValid']:continue
        for p in g['possessions']:
            if p['period']>4 or p['seconds']<=0:continue
            remaining=(4-p['period'])*720+p['start'];timebin=next(i for i,x in enumerate([2160,1440,720,360,120,0]) if remaining>=x)
            leadbin=next(i for i,x in enumerate([5,9,19,999]) if abs(p['lead'])<=x)
            c=cells.setdefault(f'{timebin}:{leadbin}',[0.,0.]);c[0]+=p['starterSeconds'];c[1]+=5*p['seconds'];overall[0]+=p['starterSeconds'];overall[1]+=5*p['seconds']
global_share=overall[0]/overall[1]
rotation={'remainingEdges':[2160,1440,720,360,120,0],'absoluteLeadEdges':[5,9,19,999],'overallStarterShare':global_share,'cells':{k:{'rawShare':v[0]/v[1],'seconds':v[1]/5,'share':(v[0]+600*5*global_share)/(v[1]+600*5)} for k,v in cells.items()},'method':'League pooled starter player-seconds / all player-seconds, 6 remaining-time by4 absolute-lead cells, 600 possession-seconds shrinkage to overall league share. No team curve. Independent rotation utility switch; eligible official starters retained from original roster indices0..4.'}
(out/'rotation-curve.json').write_text(json.dumps(rotation,indent=2)+'\n',encoding='utf-8')
print(json.dumps(noise,indent=2))

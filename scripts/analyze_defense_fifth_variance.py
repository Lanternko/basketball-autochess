"""Identical observational decomposition for real PBP and v3 diagnostics."""
import json,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'reports/defense-fifth'
read=lambda f:json.loads((R/f).read_text(encoding='utf-8'))
l=read('data/season-league.json');ids=[t['id'] for t in l['teams']];pi={t:i for i,t in enumerate(ids)}
d=read('data/season-source/team-games.json')['data']['resultSets'][0];logs=[dict(zip(d['headers'],r)) for r in d['rowSet']];lookup={(r['GAME_ID'],r['TEAM_ID']):r for r in logs}
def leadbin(x):return '<=-20' if x<=-20 else '-19..-10' if x<=-10 else '-9..-6' if x<=-6 else '-5..5' if x<=5 else '6..9' if x<=9 else '10..19' if x<=19 else '>=20'
real=[]
with (R/'reports/defense-b1/real-games.jsonl').open(encoding='utf-8') as f:
 for line in f:
  g=json.loads(line)
  if not g['pointsValid']:continue
  cells={};N=[0,0];points=[0,0];S=[0,0]
  for p in g['possessions']:
   if p['period']>4:continue
   s=p['side'];N[s]+=1;points[s]+=p['points'];S[s]+=p['points'];S[1-s]+=p['opponentPoints'];remaining=(4-p['period'])*720+p['start'];time=next(i for i,x in enumerate([2160,1440,720,360,120,0]) if remaining>=x);b=leadbin(p['lead']);c=cells.setdefault((s,time,b),dict(side=s,time=time,lead=b,n=0,points=0,duration=0));c['n']+=1;c['points']+=p['points'];c['duration']+=p['duration']
  box=[{k:lookup[g['id'],t][k.upper()] for k in ['fgm','fga','fta','fg3m','fg3a']} for t in g['ids']]
  real.append(dict(id=g['id'],ids=g['ids'],N=N,points=points,S=S,q3=g['q3'],box=box,cells=list(cells.values())))
def analyze(games):
 totals={t:np.zeros(4) for t in ids}
 for g in games:
  for s,t in enumerate(g['ids']):totals[t]+=np.array([g['points'][s],g['N'][s],g['points'][1-s],g['N'][1-s]])
 league=sum(v[0] for v in totals.values())/sum(v[1] for v in totals.values());rates={t:(v[0]/v[1],v[2]/v[3]) for t,v in totals.items()};cells={}
 for g in games:
  for c in g['cells']:
   s=c['side'];key=str(c['time'])+':'+c['lead'];r=cells.setdefault(key,dict(time=c['time'],lead=c['lead'],n=0,points=0,duration=0,expectedPoints=0));r['n']+=c['n'];r['points']+=c['points'];r['duration']+=c['duration'];r['expectedPoints']+=c['n']*(rates[g['ids'][s]][0]+rates[g['ids'][1-s]][1]-league)
 for c in cells.values():c.update(ppp=c['points']/c['n'],controlledPPP=(c['points']-c['expectedPoints'])/c['n']+league,pppResidual=(c['points']-c['expectedPoints'])/c['n'],durationMean=c['duration']/c['n'])
 N=np.array([np.mean(g['N']) for g in games]);X=np.zeros((len(games),30))
 for j,g in enumerate(games):
  for t in g['ids']:X[j,pi[t]]+=.5
 b=np.linalg.lstsq(X,N,rcond=None)[0];fit=X@b;res=N-fit;v=float(np.var(N));vf=float(np.var(fit));vr=float(np.var(res));noise=vr*29/max(1,len(games)-30)
 fga=np.array([[x['fgm']/max(1,x['fga']) for x in g['box']] for g in games]);fta=np.array([[x['fta'] for x in g['box']] for g in games]);teammean={t:{key:np.mean([values[j,s] for j,g in enumerate(games) for s,q in enumerate(g['ids']) if q==t]) for key,values in [('fg',fga),('fta',fta)]} for t in ids}
 fgadj=fga-np.array([[teammean[t]['fg'] for t in g['ids']] for g in games]);ftadj=fta-np.array([[teammean[t]['fta'] for t in g['ids']] for g in games]);corr=lambda a:float(np.corrcoef(a.T)[0,1])
 return dict(games=len(games),meanPairPossessions=float(N.mean()),pairPossessionVariance=v,teamPaceFitVariance=vf,sameGameRemainderVariance=vr,teamPaceRawShare=vf/v,teamPaceNoiseCorrectedVariance=max(0,vf-noise),teamPaceNoiseCorrectedShare=max(0,vf-noise)/v,fgCorrelation=corr(fga),ftaCorrelation=corr(fta),teamCenteredFGCorrelation=corr(fgadj),teamCenteredFTACorrelation=corr(ftadj),cells=cells)
truth=analyze(real);manifest=read('reports/defense-fifth/v3-diagnostic-seeds.json');runs=[read(f['file']) for f in manifest['files']];sim=[analyze(r['diagnosticGames']) for r in runs];scalar=[k for k in truth if k!='cells'];rng=np.random.default_rng(20261203);summary={}
for k in scalar:
 a=np.array([s[k] for s in sim]);samples=a[rng.integers(0,20,(2000,20))].mean(axis=1);summary[k]={'real':truth[k],'v3':float(a.mean()),'v3Mean95':np.quantile(samples,[.025,.975]).tolist()}
cells={key:{'real':c,'v3':{k:float(np.mean([s['cells'].get(key,{}).get(k,np.nan) for s in sim])) for k in ['n','ppp','controlledPPP','pppResidual','durationMean']}} for key,c in truth['cells'].items()}
out={'summary':summary,'cells':cells,'timeRemainingEdges':[2160,1440,720,360,120,0],'method':'Regulation actual possessions, common real/sim aggregation. PPP adjusted for own offense and opponent allowance = team PPP + opponent allowed PPP - league PPP. Team IDs used for observational adjustment only. Pair pace OLS uses half-weight sum of two team intercepts; fitted variance + residual variance equals total. Raw and degrees-of-freedom noise-corrected shares reported. Box FG/FTA correlations include OT in both real/sim (regulation count analysis does not); additionally centered by team mean. No engine parameter learned.','varianceGate':read('reports/defense-fifth/simple-baselines.json')['varianceScenarios'],'implemented2c':False,'reason':'Main heldout fixed-margin ideal SD scenario gain <0.3 winMAE; user2a requires measurement only. Full-season potential is larger but not the primary adoption evidence.','sources':{'reports/defense-b1/real-games.jsonl':hashlib.sha256((R/'reports/defense-b1/real-games.jsonl').read_bytes()).hexdigest(),'reports/defense-fifth/v3-diagnostic-seeds.json':hashlib.sha256((R/'reports/defense-fifth/v3-diagnostic-seeds.json').read_bytes()).hexdigest()}}
(O/'variance-measurements.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary),flush=True)

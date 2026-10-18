"""Descriptive absence sensitivity. No rating or engine modification."""
import json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'reports/defense-fifth';read=lambda f:json.loads((R/f).read_text(encoding='utf-8'))
def table(f):
 d=read(f)['data']['resultSets'][0];return [dict(zip(d['headers'],r)) for r in d['rowSet']]
l=read('data/season-league.json');ids=[t['id'] for t in l['teams']];pi={t:i for i,t in enumerate(ids)};logs=table('data/season-source/team-games.json');by={(r['GAME_ID'],r['TEAM_ID']):r for r in logs};players=table('data/season-source/player-games.json');dates={};owners={}
for r in players:
 key=(r['TEAM_ID'],r['PLAYER_ID']);dates.setdefault(key,[]).append(r['GAME_DATE'][:10]);owners.setdefault(r['PLAYER_ID'],set()).add(r['TEAM_ID'])
cores={t['id']:[p for p in t['roster'] if p['observed']['GP']>=10 and p['seasonMinutesPerGame']>=15] for t in l['teams']};fixtures=l['schedule'];absence={}
for g in fixtures:
 for side,t in enumerate([g['homeId'],g['awayId']]):
  eligible=[p for p in cores[t] if len(owners.get(p['playerId'],[]))<=1 or min(dates[t,p['playerId']])<=g['date']<=max(dates[t,p['playerId']])];active=set(g['homePlayerIds' if side==0 else 'awayPlayerIds']);den=sum(p['seasonMinutesPerGame'] for p in eligible);absence[g['id'],t]=sum(p['seasonMinutesPerGame'] for p in eligible if p['playerId'] not in active)/max(1,den)
rows=[(g,s,t,[g['homeId'],g['awayId']][1-s]) for g in fixtures for s,t in enumerate([g['homeId'],g['awayId']])];X=np.zeros((len(rows),64));actual=np.zeros((len(rows),2))
for j,(g,s,t,o) in enumerate(rows):
 X[j,pi[t]]=1;X[j,30+pi[o]]=1;X[j,60:]=[absence[g['id'],t],absence[g['id'],o],1 if s==0 and not g['neutral'] else -1 if not g['neutral'] else 0,j/len(rows)];actual[j]=[by[g['id'],t]['PTS'],by[g['id'],o]['PTS']]
manifest=read('reports/defense-fourth/final-normalized-seeds.json');runs=[read(f['file']) for f in manifest['files']];Y=[]
for r in runs:
 match={g['id']:g for g in r['matches']};Y.append(np.array([[match[g['id']]['scoreA' if s==0 else 'scoreB'],match[g['id']]['scoreB' if s==0 else 'scoreA']] for g,s,t,o in rows])-actual)
Y=np.array(Y);pinv=np.linalg.pinv(X);betas=np.array([pinv@y for y in Y]);avg=Y.mean(axis=0);beta=betas.mean(axis=0);res=avg-X@beta;bread=np.linalg.pinv(X.T@X);clusters=[]
for j in range(0,len(rows),2):clusters.append(X[j:j+2].T@res[j:j+2])
adjust=len(fixtures)/(len(fixtures)-1)*(len(rows)-1)/(len(rows)-np.linalg.matrix_rank(X));rng=np.random.default_rng(20261204);samples=betas[rng.integers(0,20,(2000,20))].mean(axis=1);effect={}
for c,name in enumerate(['offenseError','defenseAllowedError']):
 meat=sum(np.outer(u[:,c],u[:,c]) for u in clusters);vc=adjust*bread@meat@bread;se=float(np.sqrt(max(0,vc[60,60])));b=float(beta[60,c]);effect[name]={'per10pctAbsence':b*.1,'gameCluster95':[(b-1.96*se)*.1,(b+1.96*se)*.1],'engineSeed95':np.quantile(samples[:,60,c]*.1,[.025,.975]).tolist()}
bucket=[]
netbeta=float(beta[60,0]-beta[60,1]);netmeat=sum(np.outer(u[:,0]-u[:,1],u[:,0]-u[:,1]) for u in clusters);netvc=adjust*bread@netmeat@bread;netse=float(np.sqrt(max(0,netvc[60,60])));effect['netError']={'per10pctAbsence':netbeta*.1,'gameCluster95':[(netbeta-1.96*netse)*.1,(netbeta+1.96*netse)*.1],'engineSeed95':np.quantile((samples[:,60,0]-samples[:,60,1])*.1,[.025,.975]).tolist()}
for lo,hi in [(0,.1),(.1,.2),(.2,.3),(.3,.5),(.5,1.01)]:
 ix=[j for j,(g,s,t,o) in enumerate(rows) if lo<=absence[g['id'],t]<hi];bucket.append({'from':lo,'to':hi,'teamGames':len(ix),'meanAbsence':float(np.mean([X[j,60] for j in ix])) if ix else None,'offenseError':float(avg[ix,0].mean()) if ix else None,'defenseAllowedError':float(avg[ix,1].mean()) if ix else None})
teamExamples={}
for t in l['teams']:
 ix=[j for j,r in enumerate(rows) if r[2]==t['id']];a=np.array([X[j,60] for j in ix]);teamExamples[t['name']]={'meanAbsence':float(a.mean()),'offenseError':float(avg[ix,0].mean()),'defenseAllowedError':float(avg[ix,1].mean()),'core':[{'player':p['name'],'GP':p['observed']['GP'],'MPG':p['seasonMinutesPerGame']} for p in cores[t['id']]]}
out={'effects':effect,'buckets':bucket,'teams':teamExamples,'definition':'Core GP>=10, MPG>=15, continuous MPG weights; eligible single-team core throughout season. Multi-team players limited to observed first/last in-team dates to reduce trade-as-absence confounding. Actual active roster determines absence, not realized game minutes. Player and game IDs used only diagnostic joins. Team + opponent fixed effects, common home and linear time adjustment; two team rows clustered by fixture. Coefficients describe error association, not causal injury effects. Full-season MPG is diagnostic weighting only and never input to future engine. Positive offense error slope means simulated offense falls too little with own absence; negative allowed-error slope means defense worsens too little.'}
(O/'absence-diagnosis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(effect),flush=True)

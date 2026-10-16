import json,pathlib,numpy as np
r=pathlib.Path('reports/defense-tenth/step4-rebounds-turnover-time');load=lambda f:json.loads(pathlib.Path(f).read_text(encoding='utf8'));p=load(r/'protocol.json');a=load(r/'analysis.json');out={}
for s in p['seasons']:
 truth=next(x for x in a['cells'] if x['season']==s and x['version']=='split');teams=truth['teams'];ids=[x['id'] for x in teams];actual=np.array([x['net'] for x in teams]);wins=np.array([x['wins'] for x in teams]);target=truth['target'];out[s]={}
 for v in ['calibrated','rawsplit','split']:
  folder='reports/defense-tenth/step4-rebounds-clock' if v=='calibrated' else str(r);runs=[load(f'{folder}/runs/{s}-{v}-{seed}.json') for seed in p['diagnosticSeeds']]
  net=np.array([[(next(t for t in z['teams'] if t['id']==id)['stats']['pts']-next(t for t in z['teams'] if t['id']==id)['opponent']['pts'])/82 for id in ids] for z in runs]).mean(0)
  w=np.array([[next(t for t in z['teams'] if t['id']==id)['wins'] for id in ids] for z in runs]).mean(0);e=net-actual;e-=e.mean()
  sums={k:sum(t['stats'].get(k,0) for z in runs for t in z['teams']) for k in ['fga','fgm','fg3a','fg3m','fta','ftm','oreb','dreb','tov','stl','poss','pts','liveTov','deadTov','clockTov']};n=2460*len(runs);poss=(sums['fga']-sums['oreb']+sums['tov']+.44*sums['fta'])/n
  out[s][v]={'netRMSE':float(np.sqrt(np.mean(e*e))),'winsMAE':float(np.mean(abs(w-wins))),'possessionsBias':poss-target['possessionsProxy'],'efficiencyBias':sums['pts']/n/poss*100-target['offensiveRatingProxy'],'countsPerGame':{k:x/n for k,x in sums.items()},'FGpct':100*sums['fgm']/sums['fga'],'threePct':100*sums['fg3m']/sums['fg3a']}
pooled={v:{'netRMSE':float(np.sqrt(np.mean([out[s][v]['netRMSE']**2 for s in p['seasons']]))),'winsMAE':float(np.mean([out[s][v]['winsMAE'] for s in p['seasons']])),'possessionsBias':float(np.mean([out[s][v]['possessionsBias'] for s in p['seasons']])),'efficiencyBias':float(np.mean([out[s][v]['efficiencyBias'] for s in p['seasons']]))} for v in ['calibrated','rawsplit','split']}
(r/'attribution-analysis.json').write_text(json.dumps({'label':'three-seed descriptive attribution only; all seasons seen','seasons':out,'pooled':pooled},indent=2)+'\n');print(json.dumps(pooled,indent=2))

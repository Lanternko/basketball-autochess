"""Versioned forks; never overwrite a prior experiment."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
(R/'reports/defense-fourth/runs').mkdir(parents=True,exist_ok=True)
for name in ['game','season','pool']:
    source=(R/f'src/defense_third_{name}.js').read_text(encoding='utf-8')
    source=source.replace('defense_third_','defense_fourth_').replace('simulateDefenseThirdGame','simulateDefenseFourthGame').replace('runThirdJobs','runFourthJobs')
    if name=='season':source=source.replace("./defense_fourth_minutes.js","./defense_third_minutes.js")
    if name=='pool':source=source.replace('Math.min(4,availableParallelism())','Math.min(6,availableParallelism())')
    target=R/f'src/defense_fourth_{name}.js'
    if not target.exists():target.write_text(source,encoding='utf-8')
s=(R/'scripts/estimate_defense_third.py').read_text(encoding='utf-8')
s=s.replace('import json, hashlib, time','import json, hashlib, time, os')
s=s.replace("out=R/'reports/defense-third'","mode=os.environ.get('DEFENSE_FOURTH_FIT','pre41');out=R/('reports/defense-fourth/model-'+mode)")
s=s.replace('out.mkdir(exist_ok=True)','out.mkdir(exist_ok=True,parents=True)')
s=s.replace("train=np.array([g in train_games", "if mode=='full':train_games=set(strict)\ntrain=np.array([g in train_games")
s=s.replace('assert not set(game_ids[train])&set(game_ids[test])',"assert mode=='full' or not set(game_ids[train])&set(game_ids[test])")
# Export the complete player effect, including its learned box/position prior.
insert='''
mean=totals[:,1:].sum(axis=0)/totals[:,0].sum()
rates=(totals[:,1:]+200*mean)/(totals[:,0,None]+200)
F=np.column_stack(((rates-mean)/(np.std(rates,axis=0)+1e-9),np.array([[float(cards[p]['pos']==x) for x in positions] for p in pids])))
effects={};centers={}
for name,spec in outcomes.items():
    b=coeff[name];v=F@np.array(b['prior'][10:19])+np.array(b['defenseResidual']);effects[name]=v.tolist()
    row_effect=np.array([np.mean([v[pi[p]] for p in r['defense']]) for r in rows])
    _,n=arrays(spec);w=n*train
    centers[name]=float(np.sum(w*row_effect)/w.sum())
(out/'engine-signals.json').write_text(json.dumps({'mode':mode,'players':pids,'effects':effects,'centers':centers,'features':F.tolist(),'trainGames':sorted(train_games),'selectedLambda':{k:v['selected'] for k,v in cv.items()},'definition':'Centered mean of five defense player coefficients, including box/position prior; no offense residual injected; count-model FTA used only as relative log hazard.'},ensure_ascii=False)+'\\n',encoding='utf-8')
'''
s=s.replace('# Normalize three separately modeled shot shares',insert+'\n# Normalize three separately modeled shot shares')
s=s.replace("'scripts/estimate_defense_third.py'","'scripts/estimate_defense_fourth.py'")
(R/'scripts/estimate_defense_fourth.py').write_text(s,encoding='utf-8')

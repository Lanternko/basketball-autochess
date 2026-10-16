"""Common heldout-lineup aggregation; no simulation and no holdout model fitting."""
import os,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
k=int(sys.argv[1]);os.environ['DEFENSE_SEVENTH_CONFIG']=f'reports/defense-seventh/2025-26/calendar-{k}/config.json'
from defense_seventh_data import Data,metrics,np
d=Data(k);root=R/'reports/defense-eighth/a/coverage';rules=json.loads((root/'rules.json').read_text());teamids=sorted({r['team'] for r in d.rows});models={}
def load(f):return json.loads(f.read_text(encoding='utf-8'))
def aggregate(rate):
 values=[]
 for tid in teamids:
  own=np.array([r['team']==tid for r in d.rows])&d.test;opp=np.array([r['opponent']==tid for r in d.rows])&d.test
  values.append(100*(np.sum(d.n[own]*rate[own])/d.n[own].sum()-np.sum(d.n[opp]*rate[opp])/d.n[opp].sum()))
 return np.array(values)
actual=aggregate(d.y/d.n)
for name,dir in [('full',R/f'reports/defense-seventh/2025-26/calendar-{k}')]+[(f'mask-{s}',root/f'mask-{s}/calendar-{k}') for s in rules['maskSeeds']]:
 m=load(dir/'ability-model-forward.json');idx={p:i for i,p in enumerate(m['players'])};order=[idx[p] for p in d.pids];z=m['models']['role']
 o=np.array(z['priorOffense'])+np.array(z['offenseResidual']);df=np.array(z['priorDefenseAllowed'])+np.array(z['defenseResidual']);eta=z['intercept']+d.X@np.r_[o[order],df[order]]
 joint=aggregate(np.exp(np.clip(eta,-8,8)))
 vdir=root/f'full/calendar-{k}' if name=='full' else dir;raw=load(vdir/'deployed-card-values.json');pv={p['id']:p for p in raw['players']}
 o=np.array([pv[p]['offense'] for p in d.pids]);df=np.array([pv[p]['defenseAllowed'] for p in d.pids]);mins=np.array(m['minutes'])[order];oc=mins@o/max(1,mins.sum());dc=mins@df/max(1,mins.sum())
 deployed=aggregate(m['leaguePPP']+(d.X[:,:d.P]@(o-oc)+d.X[:,d.P:]@(df-dc))/100)
 models[name]={'trainingGames':len(m['trainGames']),'ridge':z['CV']['selected'],'joint':metrics(actual,joint),'deployedLinear':metrics(actual,deployed),'teamValues':[{'id':tid,'actual':float(a),'joint':float(j),'deployedLinear':float(v)} for tid,a,j,v in zip(teamids,actual,joint,deployed)],'trainGames':m['trainGames']}
for name,m in models.items():
 if name=='full':continue
 m['delta']={method:{key:m[method][key]-models['full'][method][key] for key in m[method]} for method in ['joint','deployedLinear']}
result={'cutoff':k,'date':d.gmap[max(d.trainids,key=lambda g:(d.gmap[g]['date'],g))]['date'],'models':models,'heldoutStrictGames':len(set(d.gids[d.test])),'heldoutTeamRows':int(d.test.sum()),'method':'Same original strict heldout stint rows for all masks; observed scoring and all predicted rates aggregated to offense minus defense points per100 observed possession ends. joint includes full fitted defense residual (offline likelihood diagnostic); deployedLinear uses actual projected v4 card analytic isolated-player values, with full defense residual OFF. Neither equals engine-season net forecast. No postcut fitting, no league recalibration and no game simulation. Only three masks, not a sampling confidence interval.'}
(root/f'diagnosis-{k}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({key:{m:v[m] for m in ['joint','deployedLinear']} for key,v in models.items()}),flush=True)

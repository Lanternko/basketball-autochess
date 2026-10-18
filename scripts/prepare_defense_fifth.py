"""Make independent versioned fifth-batch forks and rolling-cutoff tooling."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'reports/defense-fifth';O.mkdir(exist_ok=True);(O/'runs').mkdir(exist_ok=True)
for name in ['game','season','pool']:
 s=(R/f'src/defense_fourth_{name}.js').read_text(encoding='utf-8')
 if name=='game':s=s.replace('simulateDefenseFourthGame','simulateDefenseFifthGame')
 if name=='season':
  s=s.replace("'./defense_fourth_game.js'","'./defense_fifth_game.js'").replace('simulateDefenseFourthGame','simulateDefenseFifthGame')
  s=s.replace('post41=false,baseline=null','post41=false,cutoff=41,baseline=null').replace(']<=41',']<=cutoff')
  s=s.replace('normal.push(n);',"n.box=[game.statA,game.statB].map(s=>({fga:s.fga,fgm:s.fgm,fg3a:s.fg3a,fg3m:s.fg3m,fta:s.fta}));normal.push(n);")
  s=s.replace('analysis:analysis?{...analysis,records:undefined}:null',"analysis:analysis?{...analysis,records:undefined}:null,diagnosticGames:normal.map(n=>({id:n.id,ids:n.ids,box:n.box,regulationScore:n.regulationScore,q3:n.q3,possessions:n.possessions.map(p=>({side:p.side,period:p.period,start:p.start,lead:p.lead,points:p.points,opponentPoints:p.opponentPoints,duration:p.duration,state:p.state}))}))")
 if name=='pool':s=s.replace('runFourthJobs','runFifthJobs').replace('defense_fourth_worker','defense_fifth_worker')
 f=R/f'src/defense_fifth_{name}.js'
 if not f.exists():f.write_text(s,encoding='utf-8')
f=R/'scripts/estimate_defense_fifth.py'
if not f.exists():
 s=(R/'scripts/estimate_defense_fourth.py').read_text(encoding='utf-8')
 s=s.replace("mode=os.environ.get('DEFENSE_FOURTH_FIT','pre41');out=R/('reports/defense-fourth/model-'+mode)","cutoff=int(os.environ.get('DEFENSE_FIFTH_CUTOFF','41'));mode='pre'+str(cutoff);out=R/('reports/defense-fifth/model-'+mode)")
 s=s.replace('<=41','<=cutoff').replace('>41','>cutoff').replace('==41','==cutoff').replace("read('data/defense-third-source/manifest.json')","read('data/defense-third-source/manifest.json' if cutoff==41 else 'data/defense-fifth-source/pre'+str(cutoff)+'/manifest.json')")
 s=s.replace("'scripts/estimate_defense_fourth.py'","'scripts/estimate_defense_fifth.py'")
 f.write_text(s,encoding='utf-8')
f=R/'scripts/build_defense_fifth_holdout.js'
if not f.exists():
 s=(R/'scripts/build_defense_fourth_holdout.js').read_text(encoding='utf-8')
 s=s.replace("const league=read", "const cutoff=Number(process.argv[2]??41);\nconst league=read",1)
 s=s.replace("'reports/defense-fourth/model-pre41/engine-signals.json'","'reports/defense-fifth/model-pre'+cutoff+'/engine-signals.json'")
 s=s.replace("'data/defense-third-source/manifest.json'","(cutoff===41?'data/defense-third-source/manifest.json':'data/defense-fifth-source/pre'+cutoff+'/manifest.json')")
 s=s.replace("'reports/defense-fourth/pre41-league.json'","'reports/defense-fifth/pre'+cutoff+'-league.json'")
 s=s.replace("const means=read('reports/defense-fourth/foul-profile-means.json')","const means={}")
 s=s.replace('means.pre41=',"means['pre'+cutoff]=").replace("'reports/defense-fourth/foul-profile-means.json'","'reports/defense-fifth/pre'+cutoff+'-foul-means.json'")
 f.write_text(s,encoding='utf-8')
f=R/'scripts/fetch_defense_fifth_tracking.js'
if not f.exists():
 s=(R/'scripts/fetch_defense_third_tracking.js').read_text(encoding='utf-8')
 s=s.replace("const directory='data/defense-third-source'","const cutoff=Number(process.argv[2]??25);const directory='data/defense-fifth-source/pre'+cutoff")
 s=s.replace('===41','===cutoff').replace('>41','>cutoff').replace("'-pre41.json'","'-pre'+cutoff+'.json'")
 f.write_text(s,encoding='utf-8')
selection=json.loads((R/'reports/defense-fourth/final-selection.json').read_text(encoding='utf-8'))
files=['src/defense_fourth_game.js','src/defense_fourth_effects.js','src/defense_fourth_jobs.js','src/defense_fourth_season.js','reports/defense-fourth/final-selection.json','reports/defense-fourth/normalization-full.json','reports/defense-fourth/normalization-pre41.json','reports/defense-fourth/final-normalized-seeds.json','reports/defense-fourth/holdout-normalized-seeds.json']
snapshot={'name':'nba-defense-v3','parent':'final-normalized','fullLabel':'final-normalized','holdoutLabel':'holdout-normalized','seedRange':[20261012,20261031],'options':selection['finalOptions'],'sources':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in files}}
if not (O/'v3-frozen.json').exists():(O/'v3-frozen.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan={'seeds':list(range(20261012,20261032)),'cutoffs':[25,41,55],'mainCutoff':41,'bootstrap':2000,'varianceImplementationGate':0.3,'acceptance':'Heldout winMAE paired95 below v3, netRMSE no significant increase; residualSD, win slope and Q3/Q4 relation move toward observed. Calibration slope true-on-predicted near1 replaces SD ratio near1 outside training. No parameters selected from heldout accuracy; switches may be rejected. Simple shrink and Pythagorean exponent use only training. Cutoff41 frozen; other rolling endpoints rebuilt on same-cutoff data.'}
if not (O/'analysis-plan.json').exists():(O/'analysis-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
print('fifth forks, v3 snapshot and analysis plan ready')

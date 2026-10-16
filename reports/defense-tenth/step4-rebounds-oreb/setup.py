"""Create an isolated OREB acquisition experiment and register before producing cards."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

R = Path('reports/defense-tenth/step4-rebounds-oreb')
OLD = Path('reports/defense-tenth/step4-rebounds')
SEASONS = ['2022-23', '2023-24', '2024-25', '2025-26']
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
write = lambda p, s: p.write_text(s, encoding='utf-8')
if (R/'protocol.json').exists():
    raise SystemExit('Already registered; setup must not overwrite the experiment.')
R.mkdir(parents=True, exist_ok=True)

for name in ['run.mjs','worker.mjs','adapter.mjs','calibrate.mjs','analyze.mjs','bootstrap.py','player-diagnostic.mjs']:
    s = (OLD/name).read_text(encoding='utf-8')
    s = s.replace('step4-rebounds/', 'step4-rebounds-oreb/').replace("step4-rebounds'", "step4-rebounds-oreb'")
    s = s.replace('individualDrebCard','individualOrebCard').replace('individualDreb','individualOreb')
    s = s.replace("['pooled','dreb']", "['pooled','oreb']").replace("['T0','pooled','dreb']", "['T0','pooled','oreb']")
    s = s.replace("==='dreb'", "==='oreb'").replace("('dreb','pooled')", "('oreb','pooled')").replace("('dreb','T0')", "('oreb','T0')").replace('drebMinuspooled','orebMinuspooled')
    if name == 'run.mjs':
        s = s.replace("['pooled','oreb']", "['oreb']")
    if name == 'calibrate.mjs':
        s = s.replace("['pooled','oreb']", "['oreb']")
    if name in ['analyze.mjs','player-diagnostic.mjs']:
        s = s.replace('`${root}/runs/${season}-${version}-${seed}.json`', "(version==='pooled'?`reports/defense-tenth/step4-rebounds/runs/${season}-pooled-${seed}.json`:`${root}/runs/${season}-${version}-${seed}.json`)")
    if name == 'analyze.mjs':
        s = s.replace("'dreb','drtg','ortg'", "'dreb','oreb','drtg','ortg'")
        s = s.replace('dreb:100*s.dreb/(s.dreb+op.oreb),', 'dreb:100*s.dreb/(s.dreb+op.oreb),oreb:100*s.oreb/(s.oreb+op.dreb),')
        s = s.replace("k==='drtg'?", "k==='oreb'?100*t.stats.oreb/(t.stats.oreb+t.opponent.dreb):k==='drtg'?")
        s = s.replace('predictedDreb:x.dreb[i],', 'predictedDreb:x.dreb[i],predictedOreb:x.oreb[i],actualOreb:y.oreb[i],')
        s = s.replace('DREB_RMSE:rms(', "OREB_MAE:mean(center(x.oreb.map((v,i)=>v-y.oreb[i])).map(Math.abs)),OREB_RMSE:rms(center(x.oreb.map((v,i)=>v-y.oreb[i]))),OREB_RawMAE:mean(x.oreb.map((v,i)=>Math.abs(v-y.oreb[i]))),OREB_Correlation:corr(x.oreb,y.oreb),OREB_SDRatio:rms(center(x.oreb))/rms(center(y.oreb)),DREB_RMSE:rms(")
    if name == 'bootstrap.py':
        s = s.replace("'DREB_RMSE':", "'OREB_MAE':abs(centered(a['oreb']-y['oreb'])).mean((-1,-2)),'OREB_RMSE':rms(centered(a['oreb']-y['oreb'])),'OREB_RawMAE':abs(a['oreb']-y['oreb']).mean((-1,-2)),'OREB_Correlation':corr(a['oreb'],y['oreb']),'OREB_SDRatio':rms(centered(a['oreb']))/rms(centered(y['oreb'])),'DREB_RMSE':")
    if name == 'player-diagnostic.mjs':
        s = s.replace('dreb','oreb').replace('Dreb','Oreb').replace('OREB_CARD_UNUSED','OREB_CARD_UNUSED')
        # dreb strings were not renamed elsewhere; this file intentionally measures OREB only.
    write(R/name, s)

write(R/'model.mjs', """import {offensiveReboundProbability,DEFAULT_OREB_SHARE,opportunityReboundWeights} from '../../../src/rebound_block_model.js';
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const logit=p=>Math.log(p/(1-p));
export const sigmoid=x=>1/(1+Math.exp(-x));
const neutral=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70}));
export function reboundChance(offense,defense,{zone,shooterIndex,oldChance,options}){
 let p=oldChance;
 if(options.individualOrebCard){
  const share=clamp(offense.reduce((s,p)=>s+p.individualOreb.share,0),.01,.95);
  const defend=offensiveReboundProbability(neutral,defense,{zone,shooterIndex:-1});
  p=sigmoid(logit(share)+logit(defend)-logit(DEFAULT_OREB_SHARE));
 }
 return clamp(sigmoid(logit(p)+(options.leagueOrbLogit??0)),.05,.60);
}
// Recipient allocation deliberately unchanged: this batch tests acquisition only.
export function reboundWeights(lineup,settings){return opportunityReboundWeights(lineup,settings);}
""")

write(R/'prepare.mjs', """import fs from 'node:fs';
import {read,table,hash} from '../../../scripts/defense_io.js';
import {verify,root} from './run.mjs';
verify();const p=read(root+'/protocol.json');
const sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,clip=(v,a,b)=>Math.max(a,Math.min(b,v));
for(const [f,h]of Object.entries(p.inputHashes))if(hash(f)!==h)throw Error('Changed input '+f);
const coverage=[];
for(const season of p.seasons){
 const base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`,logs=table(base+'/player-games.json'),adv=table(`reports/defense-tenth/step4-t2/raw/${season}/0-advanced.json`),b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`);
 const raw=new Map();for(const r of logs){const x=raw.get(r.PLAYER_ID)??{id:r.PLAYER_ID,name:r.PLAYER_NAME,minutes:0,oreb:0};x.minutes+=r.MIN??0;x.oreb+=r.OREB??0;raw.set(r.PLAYER_ID,x);}
 const aMap=new Map();for(const a of adv){if(aMap.has(a.PLAYER_ID))throw Error('Duplicate advanced player '+a.PLAYER_ID);aMap.set(a.PLAYER_ID,a);}
 const valid=[...raw.values()].map(r=>({...r,share:aMap.get(r.id)?.OREB_PCT})).filter(r=>r.oreb>0&&r.share>0&&r.share<1&&r.minutes>0).map(r=>({...r,n:r.oreb/r.share})),fit=valid.filter(r=>r.minutes>=500);
 const mu=sum(fit.map(r=>r.oreb))/sum(fit.map(r=>r.n)),avg=mean(fit.map(r=>r.share)),variance=mean(fit.map(r=>(r.share-avg)**2)),noise=mean(fit.map(r=>mu*(1-mu)/r.n)),kappa=clip(mu*(1-mu)/Math.max(variance-noise,1e-6)-1,1,10000),opportunitiesPerMinute=sum(valid.map(r=>r.n))/sum(valid.map(r=>r.minutes));
 const players={},ids=new Set(b.league.teams.flatMap(t=>t.roster.map(p=>p.playerId))),missing=[];
 for(const id of ids){const r=raw.get(id),a=aMap.get(id),rate=a?.OREB_PCT;let n=0,share=mu,flag=null;if(r&&Number.isFinite(rate)&&rate>=0&&rate<1){n=r.oreb>0&&rate>0?r.oreb/rate:r.minutes*opportunitiesPerMinute;share=(r.oreb+kappa*mu)/(n+kappa);}else{flag='Missing official OREB_PCT; pooled individual prior';missing.push(id);}players[id]={id,name:r?.name,share,rawShare:rate??null,oreb:r?.oreb??null,minutes:r?.minutes??0,opportunities:n,flag};}
 const allMinutes=sum([...raw.values()].map(r=>r.minutes));fs.mkdirSync(root+'/'+season,{recursive:true});fs.writeFileSync(root+'/'+season+'/cards.json',JSON.stringify({season,mu,kappa,variance,noise,fitPlayers:fit.length,opportunitiesPerMinute,players,missing},null,2)+'\\n');coverage.push({season,players:ids.size,missing,minuteCoverage:sum([...raw.values()].filter(r=>ids.has(r.id)&&!missing.includes(r.id)).map(r=>r.minutes))/allMinutes,mu,kappa,fitPlayers:fit.length});
}
fs.writeFileSync(root+'/coverage.json',JSON.stringify(coverage,null,2)+'\\n');console.log(JSON.stringify(coverage));
""")

write(R/'parity.mjs', """import fs from 'node:fs';import assert from 'node:assert/strict';
import {read} from '../../../scripts/defense_io.js';import {pool,job,root,verify} from './run.mjs';
import {reboundChance,reboundWeights} from './model.mjs';import {opportunityReboundWeights} from '../../../src/rebound_block_model.js';
verify();const p=read(root+'/protocol.json'),results=[];
for(const season of p.seasons){const r=(await pool([job(season,'off',p.seeds[0])],{workers:1,quiet:true}))[0].result,old=read(`reports/defense-tenth/step4-t0/runs/${season}-pure-${p.seeds[0]}.json`);assert.deepEqual(r.matches,old.matches);assert.deepEqual(r.teams,old.teams);results.push({season,games:r.matches.length,teamPlayerStatsIdentical:true});console.log('PARITY',season,r.matches.length);}
const base=['PG','SG','SF','PF','C'].map(pos=>({pos,rebound:70,physique:70,individualOreb:{share:.05}})),settings={zone:'short',shooterIndex:2,oldChance:.26,options:{individualOrebCard:true,leagueOrbLogit:0}},strong=base.map(p=>({...p,individualOreb:{share:.2}}));
const v=reboundChance(base,base,settings);assert(reboundChance(strong,base,settings)>v);assert(reboundChance(strong,base,settings)<=.60);assert(Math.abs(reboundChance([...base].reverse(),base,settings)-v)<1e-12);assert.deepEqual(reboundWeights(base,{side:'offense',zone:'short',shooterIndex:2},settings.options),opportunityReboundWeights(base,{side:'offense',zone:'short',shooterIndex:2}));assert.equal(reboundChance(base,base,{...settings,options:{individualOrebCard:false}}),.26);
fs.writeFileSync(root+'/parity.json',JSON.stringify({results,invariants:['stronger own OREB increases team acquisition','five high rates remain one bounded Bernoulli outcome','offensive permutation invariant','recipient allocation identical','OFF probability unchanged']},null,2)+'\\n');
""")

protected={str(f).replace('\\','/'):digest(f) for top in ['src','scripts','reports/defense-tenth'] for f in Path(top).rglob('*') if f.is_file() and R not in f.parents and '__pycache__' not in str(f)}
write(R/'protected-before.json',json.dumps(protected,indent=2)+'\n')
inputs={}
for season in SEASONS:
    base='data/season-source' if season=='2025-26' else f'data/defense-seventh/{season}'
    for f in [f'{base}/player-games.json',f'{base}/team-games.json',f'reports/defense-tenth/step4-t2/raw/{season}/0-advanced.json',f'reports/defense-tenth/step4-t0/{season}/bundle.json']:
        inputs[f]=digest(Path(f))
    if season!='2025-26':
        f=f'reports/defense-tenth/step4-t0/{season}/calibration-v3.json';inputs[f]=digest(Path(f))
code={str(f).replace('\\','/'):digest(f) for f in R.iterdir() if f.suffix in ['.py','.mjs']}
protocol={
 'version':'pure-oreb-acquisition-1','registeredUTC':datetime.now(timezone.utc).isoformat(),
 'interpretation':'已看過答案；四季全季同季重現；只估計球隊取得進攻籃板，不宣稱換隊或跨季預測增益。',
 'seasons':SEASONS,'seeds':list(range(20261012,20261032)),
 'base':'T0 v3 cards, five stint signals OFF, no defenseSignals map, observed appearances and game minute soft targets. Frozen files never rewritten.',
 'inputs':'Only individual own OREB counts, official OREB_PCT, MIN. Season-pooled player IDs only join data; no team outcomes or stint outcomes as inputs.',
 'cardRule':{'N':'positive OREB / positive official OREB_PCT; zero OREB uses individual MIN times pooled opportunities/minute','fit':'players with MIN >=500 and positive valid share','mu':'sum OREB / sum N','kappa':'clip(mu*(1-mu)/max(population rate variance - mean(mu*(1-mu)/N),1e-6)-1,1,10000)','posterior':'(OREB+kappa*mu)/(N+kappa)','missing':'pooled individual prior, flagged'},
 'mechanism':{'switch':'individualOrebCard','chance':'sigmoid(logit(clip(sum five posterior shares,.01,.95)) + logit(old neutral attack vs current defense, shooterIndex=-1) - logit(DEFAULT_OREB_SHARE) + leagueOrbLogit), clipped .05..60','scope':'field goal player-board branch only; FT/team-board branches unchanged','allocation':'old recipient weights unchanged','counting':'one Bernoulli team decision and one recipient per effective miss; subsequent rebound needs a new miss','limitations':'OREB% embeds observed roles/team context. Replaces offense position, physique and landing effects only in acquisition; recipient effects retained. No invented boxout or physical bonus.'},
 'calibration':{'seeds':[20260101,20260102,20260103],'iterations':6,'tolerances':{'efficiency':.12,'possessions':.15,'orebShare':.0005},'rule':'Same frozen pooled control procedure, last evaluated iteration; league shot-logit, pace, OREB-logit only. No team net/rank/wins or TOV calibration. Reuse existing pooled baseline results and calibration.'},
 'uncertainty':{'bootstrap':20000,'seed':20261014,'unit':'franchise plus simulation seed paired across seasons; within-season centering and equal season weights'},
 'primary':['OREB centered MAE percentage points','OREB centered RMSE percentage points'],
 'secondary':['OREB correlation/SD ratio/raw MAE','DREB centered RMSE','net centered RMSE/Spearman','wins MAE','individual minute-weighted OREB36 MAE','league efficiency/possessions/FG/3P/TOV/minutes'],
 'decision':'OREB improves only if pooled comparison upper joint95 below zero for both centered MAE and RMSE. Retain independent candidate; do not promote T0 if net RMSE, wins MAE or DREB RMSE show significant deterioration. Existing baselines unchanged regardless.',
 'expectation':'Likely stronger team differentiation than old total-rebound/body/position signal (old OREB correlation ~0.24); no numeric effect promised. Individual allocation unchanged may remain a bottleneck.',
 'inputHashes':inputs,'codeHashes':code,'protectedManifestSHA':digest(R/'protected-before.json')}
write(R/'protocol.json',json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
sha=digest(R/'protocol.json');write(R/'protocol.sha256',sha+'  protocol.json\n')
print(json.dumps({'registeredUTC':protocol['registeredUTC'],'sha256':sha,'protectedFiles':len(protected),'newCodeFiles':len(code)}))

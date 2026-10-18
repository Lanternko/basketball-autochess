import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path('reports/defense-tenth/step4-rebounds-allocation');O=Path('reports/defense-tenth/step4-rebounds-oreb')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda n,s:(R/n).write_text(s,encoding='utf-8')
if (R/'protocol.json').exists():raise SystemExit('Already registered; no overwrites')
R.mkdir(parents=True,exist_ok=True)
for name in ['run.mjs','worker.mjs','adapter.mjs','analyze.mjs','bootstrap.py','player-diagnostic.mjs']:
 s=(O/name).read_text(encoding='utf-8').replace('step4-rebounds-oreb','step4-rebounds-allocation')
 if name=='run.mjs':
  s=s.replace("['oreb']","['allocation']").replace('read(`${root}/${s}/calibration-${v}.json`).selected',"read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected")
 if name=='worker.mjs':
  s=s.replace("b.options.individualOrebCard=j.version==='oreb';","b.options.individualOrebCard=true;b.options.individualOrebAllocation=j.version==='allocation';")
  s=s.replace("read(root+'/'+j.season+'/cards.json')","read('reports/defense-tenth/step4-rebounds-oreb/'+j.season+'/cards.json')")
  s=s.replace(' const run=j.native?'," const trace={fgOreb:0,ftOreb:0,dreb:0,expectedOldPutback:0,expectedNewPutback:0,selectedPutbackProbability:0};\n b.options.allocationObserver=x=>{if(!x.offensive){trace.dreb++;return;}if(x.freeThrow){trace.ftOreb++;return;}trace.fgOreb++;trace.expectedOldPutback+=x.oldExpected;trace.expectedNewPutback+=x.newExpected;trace.selectedPutbackProbability+=x.selectedExpected;};\n const run=j.native?")
  s=s.replace(' if(j.file)'," delete r.options.allocationObserver;r.allocationTrace=trace;\n if(j.file)")
 if name=='adapter.mjs':
  s=s.replace("shooterIndex:offensive?slot:-1},opt)","shooterIndex:offensive?slot:-1,freeThrow},opt)")
  anchor="  g=`import {reboundChance,reboundWeights}"
  insertion="""  const ret='    return {end:!offensive,dead:false,putback:offensive && !freeThrow && rng()<M.putbackRate(ls[side][index],M.helpDefense(ds))?player:null};';
  if(g.split(ret).length!==2)throw Error('Putback trace anchor drift');
  g=g.replace(ret,`    if(opt.allocationObserver){const cfg={zone,side:'offense',shooterIndex:slot,freeThrow};const ow=opportunityReboundWeights(os,cfg),nw=reboundWeights(os,cfg,{individualOrebAllocation:true}),h=M.helpDefense(ds);opt.allocationObserver({offensive,freeThrow,oldExpected:ow.reduce((s,w,i)=>s+w*M.putbackRate(os[i],h),0),newExpected:nw.reduce((s,w,i)=>s+w*M.putbackRate(os[i],h),0),selectedExpected:offensive?M.putbackRate(ls[side][index],h):0});}\\n${ret}`);
"""
  assert anchor in s;s=s.replace(anchor,insertion+anchor)
 if name in ['analyze.mjs','player-diagnostic.mjs']:
  s=s.replace("['T0','pooled','oreb']","['acquisition','allocation']")
  old="version==='T0'?`reports/defense-tenth/step4-t0/runs/${season}-pure-${seed}.json`:(version==='pooled'?`reports/defense-tenth/step4-rebounds/runs/${season}-pooled-${seed}.json`:`${root}/runs/${season}-${version}-${seed}.json`)"
  assert old in s;s=s.replace(old,"version==='acquisition'?`reports/defense-tenth/step4-rebounds-oreb/runs/${season}-oreb-${seed}.json`:`${root}/runs/${season}-${version}-${seed}.json`")
 if name=='bootstrap.py':
  s=s.replace("['T0','pooled','oreb']","['acquisition','allocation']").replace("[('oreb','pooled'),('oreb','T0'),('pooled','T0')]","[('allocation','acquisition')]").replace('orebMinuspooled','allocationMinusacquisition')
 write(name,s)
write('model.mjs',"""import {opportunityReboundWeights} from '../../../src/rebound_block_model.js';
export {reboundChance,logit,sigmoid} from '../step4-rebounds-oreb/model.mjs';
export function reboundWeights(lineup,settings,options={}){
 if(!options.individualOrebAllocation||settings.side!=='offense'||settings.freeThrow)return opportunityReboundWeights(lineup,settings);
 const shares=lineup.map(p=>p.individualOreb?.share);
 if(shares.some(x=>!Number.isFinite(x)||x<0))throw Error('Invalid individual OREB share');
 const sum=shares.reduce((s,x)=>s+x,0);if(!(sum>0))throw Error('Zero OREB share sum');
 return shares.map(x=>x/sum);
}
""")
write('parity.mjs',"""import fs from 'node:fs';import assert from 'node:assert/strict';
import {root,verify,job,pool} from './run.mjs';import {read} from '../../../scripts/defense_io.js';
import {reboundChance,reboundWeights} from './model.mjs';import {reboundChance as oldChance} from '../step4-rebounds-oreb/model.mjs';import {opportunityReboundWeights} from '../../../src/rebound_block_model.js';
verify();const p=read(root+'/protocol.json'),results=[];
for(const s of p.seasons){const c=read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected,r=(await pool([job(s,'acquisition',p.seeds[0],c)],{workers:1,quiet:true}))[0].result,o=read(`reports/defense-tenth/step4-rebounds-oreb/runs/${s}-oreb-${p.seeds[0]}.json`);assert.deepEqual(r.matches,o.matches);assert.deepEqual(r.teams,o.teams);results.push({season:s,games:1230,identical:true,trace:r.allocationTrace});console.log('PARITY',s,1230);}
const lineup=['PG','SG','SF','PF','C'].map((pos,i)=>({pos,physique:70,rebound:70,individualOreb:{share:[.001,.01,.03,.06,.15][i]}})),options={individualOrebAllocation:true,individualOrebCard:true,leagueOrbLogit:.27};
for(const zone of ['short','mid','long']){
 for(const side of ['offense','defense'])for(const freeThrow of [true,false]){const s={zone,side,freeThrow,shooterIndex:2},w=reboundWeights(lineup,s,options);assert(Math.abs(w.reduce((s,x)=>s+x,0)-1)<1e-12);if(side==='defense'||freeThrow)assert.deepEqual(w,opportunityReboundWeights(lineup,s));}
 const s={zone,oldChance:.26,shooterIndex:2,options};assert.equal(reboundChance(lineup,lineup,s),oldChance(lineup,lineup,s));
}
assert(reboundWeights(lineup,{zone:'short',side:'offense',freeThrow:false},options)[0]<.06);
const swapped=lineup.map(p=>({...p,courtPosition:'PG'}));assert.deepEqual(reboundWeights(lineup,{side:'offense'},options),reboundWeights(swapped,{side:'offense'},options));
fs.writeFileSync(root+'/parity.json',JSON.stringify({results,invariants:['OFF exact full-season parity','acquisition function re-exported byte-identically','FT and DREB allocation unchanged','one normalized recipient distribution','no PG/C penalty or uniform floor on FG OREB allocation']},null,2)+'\\n');
""")
protected={str(f).replace('\\','/'):sha(f) for top in ['src','scripts','reports/defense-tenth'] for f in Path(top).rglob('*') if f.is_file() and R not in f.parents and '__pycache__' not in str(f)}
write('protected-before.json',json.dumps(protected,indent=2)+'\n')
p={'version':'pure-oreb-allocation-1','registeredUTC':datetime.now(timezone.utc).isoformat(),'label':'已看過答案；四季全季當季重現，不是換隊／跨季盲測','seasons':['2022-23','2023-24','2024-25','2025-26'],'seeds':list(range(20261012,20261032)),
 'base':'pure-oreb-acquisition-1 frozen cards, individualOrebCard ON, five stint signals OFF/no-map, observed appearances and game soft minute targets',
 'mechanism':{'switch':'individualOrebAllocation','formula':'FG player offensive rebound recipient weight = individual posterior OREB share / sum five shares. No .30 uniform floor, no additional body/slot/zone multiplier. Prior shrinkage already in frozen share.','scope':'FG player OREB recipient only; FT, DREB, team-board and putback formulas unchanged','acquisition':'re-export previous function unchanged','constants':'reuse prior season-specific calibration exactly; NO recalibration, even if selected recipient changes downstream scores/clock/lineups','trace':'non-random observer of old/new conditional expected putback probability; OFF-parity first seed each season supplies fixed-path diagnostic'},
 'primary':'Observed-minute-weighted player OREB36 MAE: seed-mean OREB / seed-mean simulated MIN, aggregated across traded teams per player. Cohort actual MIN>0 and both versions mean simulated MIN>0, exclusions reported.',
 'secondary':['player OREB36 weighted RMSE','team OREB MAE/RMSE/correlation','DREB RMSE','net RMSE/ranking/SD ratio','wins MAE','FG/3P/TOV/efficiency/possessions/minutes','fixed-path expected putback probability'],
 'uncertainty':{'bootstrap':20000,'seed':20261014,'unit':'franchise plus seed paired across seasons. Player cluster assigned to season team with most observed minutes (ties ascending team ID); traded players aggregated before scoring. Equal season weights; no independent player bootstrap.'},
 'decision':'Player allocation improves only if four-season paired joint95 upper MAE difference <0. Retain candidate only if no significant deterioration in team OREB RMSE, DREB RMSE, net RMSE, wins MAE; each season absolute efficiency and possession proxy bias <=.5. Failures kept, no after-result retuning or extra calibration. No frozen baseline replacement.',
 'expectation':'Likely reduces low-OREB guard overallocation caused by 6% minimum recipient share; may increase big-man putback opportunities and drift efficiency. No numerical improvement target promised.',
 'codeHashes':{str(f).replace('\\','/'):sha(f) for f in R.iterdir() if f.suffix in ['.py','.mjs']},'protectedManifestSHA':sha(R/'protected-before.json')}
write('protocol.json',json.dumps(p,ensure_ascii=False,indent=2)+'\n');h=sha(R/'protocol.json');write('protocol.sha256',h+'  protocol.json\n');print(json.dumps({'SHA256':h,'registeredUTC':p['registeredUTC'],'protectedFiles':len(protected)}))

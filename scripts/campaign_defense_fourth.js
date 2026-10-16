import fs from 'node:fs';
import {runLabel,loadRuns} from './run_defense_fourth.js';
import {comparison,prepareRuns,summarize} from '../src/defense_fourth_scoreboard.js';
const root='reports/defense-fourth';
const plan={seeds:[20261012,20261031],bootstrap:2000,groupOrder:['neutralContests','reboundSignal','rimSignal','liveSignal','zoneSignal','foulSignal'],
 gate:'Sequential group versus last accepted combination: reject if paired95% CI netRMSE or winMAE increase excludes0, or netSDRatio decreases excludes0 (ratio<1). Correlation, slope and residual SD are reported, not optimized. No strength coefficient tuned from validation outcomes.',
 rotation:'League starter/time/lead curve; rotation utility gain60 fixed in engine units. No score-accuracy tuning. Accept for final only if netRMSE not significantly worse versus signals and winMAE not significantly worse; curve diagnostics separately reported.',
 verdict:'Full82 success: netRMSE and winMAE lower95%CI excludes0 versus frozenv1, netSDRatio no significant decrease. Partial: at least one of netRMSE,winMAE,or SD-goal (team SD ratio distance1/residualSD distance14.027) significantly improves, none of three goals significantly worsens. All seed intervals conditional on fixed actual season; six adaptive group tests unadjusted, so heldout confirmation essential.',
 heldout:'Both old and final cards rebuilt strictly disjoint574 first41 games. Conditional actual post41 active players/starters, train-MPG minutes. Both v1old and v2old controls, plus final. No hyperparameters selected on post41 outcomes.'};
fs.writeFileSync(root+'/analysis-plan.json',JSON.stringify(plan,null,2)+'\n');
let accepted={},current='v2',currentRuns=loadRuns('v2');const results=[];
for(const [i,flag] of plan.groupOrder.entries()){
  const options={...accepted,[flag]:true},label='b1-'+(i+1)+'-'+flag;
  const runs=await runLabel(label,options),delta=comparison(runs,currentRuns);
  const reasons=[];for(const k of ['netRMSE','winMAE'])if(delta[k].ci95[0]>0)reasons.push(k+' significantly worse');if(delta.netSDRatio.ci95[1]<0)reasons.push('netSDRatio significantly worse');
  const keep=!reasons.length;results.push({label,flag,previous:current,options,accepted:keep,reasons,incremental:delta});
  if(keep){accepted=options;current=label;currentRuns=runs;}
  fs.writeFileSync(root+'/signal-sequence.json',JSON.stringify({accepted,current,results},null,2)+'\n');console.log('GATE',label,keep,reasons);
}
const allSignals=current;const rotationOnly=await runLabel('rotation-only',{scoreRotation:true});
const combined=await runLabel('rotation-signals',{...accepted,scoreRotation:true}),delta=comparison(combined,currentRuns);
const useRotation=delta.netRMSE.ci95[0]<=0&&delta.winMAE.ci95[0]<=0;
const finalLabel=useRotation?'rotation-signals':allSignals,finalOptions={...accepted,...(useRotation?{scoreRotation:true}:{})};
fs.writeFileSync(root+'/final-selection.json',JSON.stringify({allSignals,signalOptions:accepted,rotationAccepted:useRotation,rotationDelta:delta,finalLabel,finalOptions,interpretation:'Selected by preregistered sequential gates; seed95 intervals do not account for adaptive testing.'},null,2)+'\n');
await runLabel('holdout-v1',{}, {post41:true,oldSignal:true});
await runLabel('holdout-v2',{}, {post41:true});
await runLabel('holdout-final',finalOptions,{post41:true});
const test=loadRuns('holdout-final');for(const old of ['holdout-v1','holdout-v2']){
  const paired=comparison(test,loadRuns(old),true);fs.writeFileSync(root+'/paired-'+old+'.json',JSON.stringify(paired,null,2)+'\n');console.log('HOLDOUT',old,JSON.stringify(paired));
}

import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import {defenseProbabilities,pressureSignal} from '../../src/defense_probability.js';
import {positionalOvrInput} from '../player-impact-validation/positional-input.mjs';
import {attachCreationContext,measuredContext} from '../../src/measured_creation_context.js';
import {opportunityPlan} from '../player-impact-v11/model.mjs';
for(const season of process.argv.slice(2)){
 const x=await positionalOvrInput(season),file=`reports/player-impact-v13/${season}-contexts.json`,ref=JSON.parse(fs.readFileSync(file)).contextReference;
 attachCreationContext(x.profiles,ref);for(const t of x.opponents)attachCreationContext(t.roster,ref);
 const plan=opportunityPlan(x.profiles,undefined,1,'supply-creation');let num=0,den=0;
 for(const t of x.opponents)for(let i=0;i<5;i++){
  const p=x.profiles[i],ds=t.roster,ctx=measuredContext(x.profiles,i),weights=x.profiles.map((_,j)=>j===i?plan.rows[i].weight*plan.rows[i].shoot:plan.rows[j].receivers[i]),total=weights.reduce((s,q)=>s+q,0);
  const rate=p.offenseMeasurement.attempts/p.offenseMeasurement.minutes*p.shotProfile.threeRate;
  for(let j=0;j<5;j++)if(weights[j]>0){
   const options={assist:i===j?null:x.profiles[j].pass,contextScale:x.options.contextScale,contextShortScale:x.options.contextShortScale,turnoverMode:x.options.turnoverMode,turnoverScale:x.options.turnoverScale,pressureAttribute:pressureSignal(ds,x.options.stealPriorRate).attribute};
   const q=scale=>defenseProbabilities(p,ctx,ds[i],M.helpDefense(ds),70,70,M.teamPhysique(ds),{...options,contextLongScale:scale});
   const w=rate*weights[j]/total;num+=w*(q(1).make.long-q(0).make.long);den+=w;
  }
 }
 const out={season,fullCenter:num/den,design:'Only synthetic positional mean70 profiles: common long-context increment versus zero, weighted by fixed profile 3PA rate and model-implied created-shot mix over the fixed thirty-opponent benchmark. Prevents changing context from granting every synthetic teammate a uniform league-level FG boost. Actual player rates use their own frozen source contexts. No actual on/off outcomes or OVR ranks used.',contextSourceSHA256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')};
 fs.writeFileSync(`reports/player-impact-v13/${season}-synthetic-center.json`,JSON.stringify(out,null,2));console.log(JSON.stringify(out));
}

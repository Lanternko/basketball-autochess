import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {verifyC} from './run_defense_eighth_c_versions.js';
import {buildSeventh} from './build_defense_seventh_cards.js';
import {runSeventh,loadSeventh} from './run_defense_seventh.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {mean} from '../src/statistical_summary.js';
const root='reports/defense-eighth/c',p=verifyC(),season=process.argv[2],ks=process.argv[3]?[Number(process.argv[3])]:p.cutoffs;
if(![...p.developmentSeasons,...p.blindSeasons].includes(season))throw Error('Unknown season');
const variance=xs=>{const mu=mean(xs);return mean(xs.map(x=>(x-mu)**2));},cov=(xs,ys)=>{const a=mean(xs),b=mean(ys);return mean(xs.map((x,i)=>(x-a)*(ys[i]-b)));};
for(const k of ks){
 verifyC();const cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,c=read(cf),truth=calendarTruth(c),baseLabel=season+'-calendar-'+k+'-v4',mf=read(`reports/defense-seventh/${baseLabel}-seeds.json`),control=mf.files.slice(0,3).map(f=>read(f.file)),net=summarizeFifth(control,0,[0,1,2],truth).teams.map(t=>t.net),allVariance=variance(net),ablations={},deltas={};
 for(const name of Object.keys(p.diagnostics.ablation.components)){
  const dir=`${root}/ablation/${season}/calendar-${k}/${name}`,label=`${season}-eighth-c-ablation-${k}-${name}`;fs.mkdirSync(dir,{recursive:true});
  let cardFile=mf.extra.cardFile,options={};
  if(['offensePrior','offenseResidual'].includes(name)){
   if(!fs.existsSync(dir+`/pre${k}-ablation-league.json`)){
    const model=read(c.root+'/ability-model-forward.json'),weights=model.minutes,mu=model.models.role.priorOffense.reduce((s,x,i)=>s+x*weights[i],0)/weights.reduce((s,x)=>s+x,0);
    if(name==='offensePrior')model.models.role.priorOffense=model.models.role.priorOffense.map(()=>mu);else model.models.role.offenseResidual=model.models.role.offenseResidual.map(()=>0);
    for(const file of ['bundle.json','card-values.json'])fs.copyFileSync(c.root+'/'+file,dir+'/'+file);fs.writeFileSync(dir+'/ability-model-forward.json',JSON.stringify(model)+'\n');fs.writeFileSync(dir+'/config.json',JSON.stringify({...c,root:dir},null,2)+'\n');buildSeventh(k,{label:'ablation',configFile:dir+'/config.json'});
   }cardFile=dir+`/pre${k}-ablation-league.json`;
  }else if(name==='defenseSignals')options={reboundSignal:false,rimSignal:false,liveSignal:false,zoneSignal:false,foulSignal:false};
  else if(name==='minutes'){
   const file=dir+'/uniform-minute-league.json';if(!fs.existsSync(file)){const league=read(mf.extra.cardFile);for(const t of league.teams)for(const player of t.roster)player.seasonMinutesPerGame=20;fs.writeFileSync(file,JSON.stringify(league)+'\n');}cardFile=file;
  }
  if(!fs.existsSync(`reports/defense-seventh/${label}-seeds.json`))await runSeventh(label,{...mf.extra,cardFile,options},p.diagnostics.ablation.seeds);
  const runs=loadSeventh(label),pred=summarizeFifth(runs,0,[0,1,2],truth).teams.map(t=>t.net),delta=net.map((x,i)=>x-pred[i]),v=variance(pred);deltas[name]=delta;
  ablations[name]={net:pred,variance:v,varianceReduction:allVariance-v,marginalShare:(allVariance-v)/allVariance,netChangeRMS:Math.sqrt(mean(delta.map(x=>x*x))),covarianceContribution:cov(net,delta)/allVariance,manifest:`reports/defense-seventh/${label}-seeds.json`,cardHash:hash(cardFile),options};
 }
 const remainder=net.map((x,i)=>x-Object.values(deltas).reduce((s,ds)=>s+ds[i],0)),covarianceRemainder= cov(net,remainder)/allVariance;
 const output={label:'事後探索，不作驗收',season,k,seeds:p.diagnostics.ablation.seeds,allVariance,controlNet:net,ablations,covarianceRemainder,covarianceSum:Object.values(ablations).reduce((s,x)=>s+x.covarianceContribution,0)+covarianceRemainder,calibration:mf.extra.calibration,interpretation:'Leave-one-component-off marginal variance changes are not additive causal shares. The covariance bookkeeping plus remainder sums to1 by algebra; remainder includes interactions and three-seed noise. Defense switch disables the shortFG deployment channel too, including the role-defense projection stored in that channel; card projection itself is retained. The C0 phrase saying that embedded role-defense effect was excluded is a semantic error, not a change to registered switches.',sourceConfigHash:hash(cf),preregHash:hash(root+'/prereg-supplement.json')};
 const out=`${root}/ablation/${season}/calendar-${k}`;fs.mkdirSync(out,{recursive:true});fs.writeFileSync(out+'/diagnostic.json',JSON.stringify(output,null,2)+'\n');console.log('C ABLATION',season,k,JSON.stringify({variance:allVariance,marginal:Object.fromEntries(Object.entries(ablations).map(([n,a])=>[n,a.marginalShare])),covarianceRemainder}));
}

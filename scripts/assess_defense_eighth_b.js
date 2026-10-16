import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {jointBlindPair,jointBlindEnvelope,combinedMetric} from '../src/defense_eighth_blind_evaluation.js';
import {bLabel} from './run_defense_eighth_b_point.js';
const root='reports/defense-eighth/b',rules=read(root+'/development-rules.json'),selection=read(root+'/selection.json'),a=read('reports/defense-eighth/a/analysis.json'),result={developmentOnly:true,seasons:{},combined:{},jointBootstrap:rules.blindEvaluation.jointBootstrap,sources:{}};
const datasets={};
for(const season of rules.developmentSeasons){result.seasons[season]={};datasets[season]={};for(const k of rules.cutoffs){
 const cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,c=read(cf),truth=calendarTruth(c),versions={},ds={};
 for(const v of ['v3','v4','v5']){
  const label=v==='v5'?bLabel(season,k,selection.cutoffs[k].c):`${season}-calendar-${k}-${v}`,mf=`reports/defense-seventh/${label}-seeds.json`,runs=loadSeventh(label),summary=summarizeFifth(runs,0,runs.map((_,i)=>i),truth);
  versions[v]=summary;ds[v]=runs.map(run=>summarizeFifth([run],0,[0],truth).teams.map(t=>({id:t.id,net:t.net,wins:t.wins,observed:{net:t.observed.net,wins:t.observed.wins}})));result.sources[mf]=hash(mf);
 }
 for(const v of ['simple','shrink']){const model=a.seasons[season][k].models[v];versions[v]={metrics:model.metrics,teams:model.teams};const rows=model.teams.map(t=>({id:t.id,net:t.net,wins:t.wins,observed:{net:t.actualNet,wins:t.actualWins}}));ds[v]=Array.from({length:20},()=>rows);}
 const v5Manifest=`reports/defense-seventh/${bLabel(season,k,selection.cutoffs[k].c)}-seeds.json`,extra=read(v5Manifest).extra,v5Dir=extra.bundle.slice(0,-'/bundle.json'.length),inputFiles=[cf,extra.bundle,extra.cardFile,v5Dir+'/ability-model-forward.json',v5Dir+'/calibration-v5.json'];
 const p={};for(const v of ['v3','v4','simple','shrink'])p['v5-minus-'+v]=jointBlindPair([ds],'v5',v);p['v5-minus-stronger']=jointBlindEnvelope([ds],'v5');
 result.seasons[season][k]={date:c.date,versions,pairs:p,v5Manifest,v5Dir,inputHashes:Object.fromEntries(inputFiles.map(p=>[p,hash(p)]))};datasets[season][k]=ds;
 console.log('B ASSESS',season,k,JSON.stringify({v5:versions.v5.metrics,net:p['v5-minus-v4'].netRMSE,wins:p['v5-minus-v4'].winMAE}));
}}
for(const k of rules.cutoffs){const groups=rules.developmentSeasons.map(s=>datasets[s][k]),seeds=Array.from({length:20},(_,i)=>i),teams=Array.from({length:30},(_,i)=>i),versions=Object.fromEntries(['v3','v4','v5','simple','shrink'].map(v=>[v,combinedMetric(groups,v,seeds,teams)])),pairs={};for(const v of ['v3','v4','simple','shrink'])pairs['v5-minus-'+v]=jointBlindPair(groups,'v5',v);pairs['v5-minus-stronger']=jointBlindEnvelope(groups,'v5');result.combined[k]={versions,pairs,targetSimpleSlope:selection.cutoffs[k].targetSimpleSlope,actualV5Slope:versions.v5.calibrationSlope,achievedGap:versions.v5.calibrationSlope-selection.cutoffs[k].targetSimpleSlope};}
result.sources[root+'/selection.json']=hash(root+'/selection.json');fs.writeFileSync(root+'/assessment.json',JSON.stringify(result,null,2)+'\n');

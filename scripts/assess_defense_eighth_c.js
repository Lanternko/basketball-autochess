import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {verifyC} from './run_defense_eighth_c_versions.js';
import {cConfig,cManifest,cSimple,loadCSeeds,realCResidual} from './defense_eighth_c_data.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
import {prepareCGroup,combinedC,bootstrapC,confirmationC} from '../src/defense_eighth_c_statistics.js';
const root='reports/defense-eighth/c',p=verifyC(),quality=read(root+'/quality.json'),seasons=[...p.developmentSeasons,...p.blindSeasons],versions=['v1','v3-signals-off','v3','v4','v5'],result={stage:'C',assessedAt:new Date().toISOString(),preregHash:hash(root+'/prereg-supplement.json'),v5FreezeHash:p.v5FreezeHash,seasons:{},groups:{},confirmations:{},exploration:{label:'事後探索，不作驗收',oracle:{}},sources:{}};
const precompute=process.argv[2]==='--precompute',cutoffs=precompute?[Number(process.argv[3])]:p.cutoffs;if(cutoffs.some(k=>!p.cutoffs.includes(k)))throw Error('Unregistered cutoff');
const datasets={};
for(const s of seasons){result.seasons[s]={};datasets[s]={};result.exploration.oracle[s]={};for(const k of cutoffs){
 const cf=cConfig(s,k),c=read(cf),truth=calendarTruth(c),data=Object.fromEntries(versions.map(v=>[v,loadCSeeds(cManifest(s,k,v),truth,result.sources)])),simple=cSimple(c,truth);data.simple=simple.simple;data.shrink=simple.shrink;
 const calibrated=(rs,m)=>rs.map(rows=>{const mu=rows.reduce((sum,r)=>sum+r.net,0)/rows.length;return rows.map(r=>({id:r.id,name:r.name,net:m*(r.net-mu),wins:null,observed:r.observed}));});
 data.v4cal=calibrated(data.v4,p.outputCalibration.m4[k]);data.simplecal=calibrated(data.simple,p.outputCalibration.ms[k]);const g=prepareCGroup(data),point=combinedC([g]);
 datasets[s][k]=g;result.seasons[s][k]={date:c.date,trainingGames:c.trainGames.length,allTrainingGames:c.allTrainGames.length,teamGP:c.teamGP,versions:point,simpleTraining:simple.training,realResidual:await realCResidual(c),quality:quality.seasons[s].strictCoverage};
 result.exploration.oracle[s][k]={v4:point.v4.calibrationSlope,simple:point.simple.calibrationSlope,ratio:point.v4.calibrationSlope/point.simple.calibrationSlope,m4:p.outputCalibration.m4[k],ms:p.outputCalibration.ms[k]};for(const file of [cf,c.leagueFile,c.paths['data/season-source/team-games.json'],c.realGames])if(!result.sources[file])result.sources[file]=hash(file);console.log('C POINT',s,k,JSON.stringify(Object.fromEntries(['v3','v4','v5','simple','v4cal','simplecal'].map(v=>[v,point[v].netRMSE]))));
}}
const groupDefinitions={four:seasons,blind:p.blindSeasons};
const insufficient=seasons.filter(s=>quality.seasons[s].coverageInsufficient);result.coverageInsufficientSeasons=insufficient;
if(insufficient.length){groupDefinitions.fourExcludingLowCoverage=seasons.filter(s=>!insufficient.includes(s));groupDefinitions.blindExcludingLowCoverage=p.blindSeasons.filter(s=>!insufficient.includes(s));}
for(const [name,ss]of Object.entries(groupDefinitions)){
 result.groups[name]={seasons:ss,cutoffs:{},interpretation:name.startsWith('blind')?'Only registered blind-two group determines C4; exclusion sensitivity is separate.':'Contains development seasons that participated in selection; descriptive primary table, not an independent validation.'};
 if(!ss.length){result.groups[name].unavailable='No season remains above coverage threshold';continue;}
 for(const k of cutoffs){const groups=ss.map(s=>datasets[s][k]),cache=`${root}/bootstrap-${name}-${k}.json`,inputHashes={prereg:result.preregHash,code:hash('src/defense_eighth_c_statistics.js'),loader:hash('scripts/defense_eighth_c_data.js'),assessmentCode:hash('scripts/assess_defense_eighth_c.js'),truth:Object.fromEntries(ss.flatMap(s=>{const cf=cConfig(s,k),c=read(cf);return [cf,c.leagueFile,c.paths['data/season-source/team-games.json'],c.realGames];}).map(f=>[f,result.sources[f]])),manifests:Object.fromEntries(ss.flatMap(s=>versions.map(v=>cManifest(s,k,v))).map(f=>[f,hash(f)]))},signature=JSON.stringify(inputHashes);
  let cell;if(fs.existsSync(cache)&&JSON.stringify(read(cache).inputHashes)===signature)cell=read(cache);else{cell={...bootstrapC(groups,p.comparisons,{B:p.evaluation.bootstrap.replicates,rngSeed:p.evaluation.bootstrap.rngSeed}),inputHashes};fs.writeFileSync(cache,JSON.stringify(cell,null,2)+'\n');}
  result.groups[name].cutoffs[k]=cell;console.log('C JOINT',name,k,JSON.stringify(Object.fromEntries(p.comparisons.map(c=>[c.id,cell.pairs[c.id].verdict]))));
 }
}
if(!precompute){
for(const c of p.comparisons)result.confirmations[c.id]={improvement:confirmationC(result.groups.blind.cutoffs,c,'improvement'),worsening:confirmationC(result.groups.blind.cutoffs,c,'worsening')};
result.sources[root+'/quality.json']=hash(root+'/quality.json');result.sources['src/defense_eighth_c_statistics.js']=hash('src/defense_eighth_c_statistics.js');result.sources['scripts/defense_eighth_c_data.js']=hash('scripts/defense_eighth_c_data.js');
fs.writeFileSync(root+'/assessment.json',JSON.stringify(result,null,2)+'\n');console.log('C ASSESS COMPLETE',JSON.stringify(result.confirmations));
}else console.log('C bootstrap cache complete; final assessment withheld until all cutoffs finish');

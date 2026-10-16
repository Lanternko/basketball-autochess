import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read,hash} from './defense_io.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {runSeventh} from './run_defense_seventh.js';
const root='reports/defense-eighth/a',season='2024-25';fs.mkdirSync(root,{recursive:true});
const rules={stage:'A5',writtenAt:new Date().toISOString(),versions:['v1','v3-signals-off'],cutoffs:[25,41,55],seeds:Array.from({length:20},(_,i)=>20261012+i),definition:'v1 uses frozen v1 event mechanisms with training-only rebuilt old cards and season MPG. v3-signals-off retains all v3 event accounting/timing/foul/turnover mechanisms and disables only learned DREB/rim/liveTOV/zone/FTA signals. Both use the frozen seven-batch pooled training calibration algorithm (3 seeds, at most5 iterations), initial pace1; no net/win tuning. Pure signal attribution is v3 versus signals-off; v3 versus v1 also changes accounting/events/timing and is not a pure defense signal attribution.'};
const ruleFile=root+'/control-rules.json';if(!fs.existsSync(ruleFile))fs.writeFileSync(ruleFile,JSON.stringify(rules,null,2)+'\n');
for(const k of rules.cutoffs)for(const version of rules.versions){
 const original=read(`reports/defense-seventh/${season}/calendar-${k}/config.json`),dir=`${root}/${season}/calendar-${k}-${version}`;fs.mkdirSync(dir,{recursive:true});
 const base=read(original.root+'/bundle.json'),options=version==='v1'?{...NBA_DEFENSE_V1,pace:1,seasonMinuteTargets:true,stealPriorRate:base.league.priorRate}:{...base.options,reboundSignal:false,rimSignal:false,liveSignal:false,zoneSignal:false,foulSignal:false};
 const bundle={...base,options},config={...original,root:dir,leagueOutput:original.leagueOutput};fs.writeFileSync(dir+'/bundle.json',JSON.stringify(bundle)+'\n');fs.writeFileSync(dir+'/config.json',JSON.stringify(config,null,2)+'\n');
 if(!fs.existsSync(dir+'/calibration-'+version+'.json')){
  let s=fs.readFileSync('scripts/calibrate_defense_seventh_bundle.js','utf8');
  s=s.replace("const configFile=process.argv[2],version=process.argv[3]??'v4'","const configFile=process.argv[2],version=process.argv[3]").replace("label=c.season+'-calendar-'+c.k+'-'+version","label=c.season+'-eighth-a-calendar-'+c.k+'-'+version");
  // The v1 legacy mechanism cannot respond to new foul/category/clock moment
  // knobs. Keep these iterations/audit targets visible; do not add new mechanics.
  const script='scripts/.eighth-a-control-calibration.js';fs.writeFileSync(script,s);execFileSync(process.execPath,[script,dir+'/config.json',version],{stdio:'inherit'});
 }
 const label=`${season}-eighth-a-calendar-${k}-${version}`,cal=read(dir+'/calibration-'+version+'.json');
 if(!fs.existsSync(`reports/defense-seventh/${label}-seeds.json`))await runSeventh(label,{bundle:dir+'/bundle.json',cutoff:k,calendarDate:original.date,cardFile:original.leagueOutput,neutralContests:false,calibration:cal.selected});
 fs.writeFileSync(dir+'/provenance.json',JSON.stringify({config:hash(dir+'/config.json'),bundle:hash(dir+'/bundle.json'),cards:hash(original.leagueOutput),calibrator:hash('scripts/calibrate_defense_seventh_bundle.js'),rules:hash(ruleFile)},null,2)+'\n');
}

import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read} from './defense_io.js';
import {buildSeventh} from './build_defense_seventh_cards.js';
import {runSeventh} from './run_defense_seventh.js';
const season=process.argv[2],ks=process.argv[3]?[Number(process.argv[3])]:[25,41,55];
function node(file,args=[]){execFileSync(process.execPath,[file,...args],{stdio:'inherit'});}
for(const k of ks){
 const root=`reports/defense-seventh/${season}/calendar-${k}`,configFile=root+'/config.json';if(!fs.existsSync(configFile))node('scripts/prepare_defense_seventh_calendar.js',[season,String(k)]);
 if(!fs.existsSync(root+'/tracking/manifest.json'))node('scripts/fetch_defense_seventh_tracking.js',[configFile]);
 if(!fs.existsSync(root+'/factors/engine-signals.json'))execFileSync('python',['scripts/estimate_defense_seventh_factors.py',configFile,'random'],{stdio:'inherit'});
 if(!fs.existsSync(root+'/bundle.json')){node('scripts/build_defense_seventh_base.js',[configFile]);node('scripts/build_defense_seventh_bundle.js',[configFile]);}
 if(!fs.existsSync(root+'/ability-model-forward.json'))execFileSync('python',['scripts/estimate_defense_seventh.py',String(k),'forward'],{env:{...process.env,DEFENSE_SEVENTH_CONFIG:configFile},stdio:'inherit'});
 if(!fs.existsSync(root+`/pre${k}-v4-league.json`))buildSeventh(k,{label:'v4',configFile});
 const c=read(configFile);
 for(const version of ['v3','v4']){
  if(!fs.existsSync(root+'/calibration-'+version+'.json'))node('scripts/calibrate_defense_seventh_bundle.js',[configFile,version]);
  const label=season+'-calendar-'+k+'-'+version;
  if(!fs.existsSync('reports/defense-seventh/'+label+'-seeds.json'))await runSeventh(label,{bundle:root+'/bundle.json',cutoff:k,calendarDate:c.date,cardFile:version==='v4'?`${root}/pre${k}-v4-league.json`:c.leagueOutput,neutralContests:version==='v4',calibration:read(root+'/calibration-'+version+'.json').selected});
 }
}

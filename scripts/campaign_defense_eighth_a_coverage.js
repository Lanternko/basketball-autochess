import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read} from './defense_io.js';
import {buildSeventh} from './build_defense_seventh_cards.js';
const root='reports/defense-eighth/a/coverage';
function node(file,args=[]){execFileSync(process.execPath,[file,...args],{stdio:'inherit'});}
if(!fs.existsSync(root+'/rules.json'))node('scripts/prepare_defense_eighth_a_coverage.js');
for(const seed of read(root+'/rules.json').maskSeeds)for(const k of [25,41,55]){
 const dir=`${root}/mask-${seed}/calendar-${k}`,file=dir+'/config.json';
 if(!fs.existsSync(dir+'/factors/engine-signals.json'))execFileSync('python',['scripts/estimate_defense_eighth_a_coverage_factors.py',file,'random'],{stdio:'inherit'});
 if(!fs.existsSync(dir+'/bundle.json')){node('scripts/build_defense_seventh_base.js',[file]);node('scripts/build_defense_seventh_bundle.js',[file]);}
 if(!fs.existsSync(dir+'/ability-model-forward.json'))execFileSync('python',['scripts/estimate_defense_seventh.py',String(k),'forward'],{env:{...process.env,DEFENSE_SEVENTH_CONFIG:file},stdio:'inherit'});
 if(!fs.existsSync(dir+`/pre${k}-v4-league.json`))buildSeventh(k,{label:'v4',configFile:file});
 console.log('COVERAGE DONE',seed,k);
}

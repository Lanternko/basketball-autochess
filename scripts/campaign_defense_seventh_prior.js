import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read,hash} from './defense_io.js';
import {buildSeventh} from './build_defense_seventh_cards.js';
import {runSeventh} from './run_defense_seventh.js';
const out='reports/defense-seventh/prior';fs.mkdirSync(out,{recursive:true});
if(!fs.existsSync('reports/defense-seventh/2024-25-calendar-assessment.json'))throw Error('Blind assessment must finish first');
if(!fs.existsSync(out+'/rules.json'))fs.writeFileSync(out+'/rules.json',JSON.stringify({createdAt:new Date().toISOString(),pseudoPlayerPossessions:200,previousSeason:'2024-25',currentSeason:'2025-26',method:'Previous full-season centered joint player effects as prior offset. Mix with fold-rebuilt current box/position/MPG prior using n/(n+200), n=training MIN/48*100. Three forward folds choose current residual ridge. Prior affects joint likelihood; full defense residual deployment off. Current past-only league constants recalibrated by frozen v4 rule. No heldout selection of prior strength. No prior B1 factor replacement in this experiment.',frozenV4:hash('reports/defense-seventh/v4-freeze.json')},null,2)+'\n');
for(const k of [25,41,55]){
 const old=`reports/defense-seventh/2025-26/calendar-${k}`,root=`${out}/calendar-${k}`,file=root+'/config.json';fs.mkdirSync(root,{recursive:true});
 if(!fs.existsSync(file)){const c=read(old+'/config.json');c.root=root;c.leagueOutput=root+'/v3-league.json';c.foulMeansOutput=root+'/foul-means.json';for(const [key,v]of Object.entries(c.paths))if(v===old+'/card-values.json')c.paths[key]=root+'/card-values.json';fs.writeFileSync(file,JSON.stringify(c,null,2)+'\n');for(const f of ['bundle.json','card-values.json','v3-league.json'])fs.copyFileSync(old+'/'+f,root+'/'+f);}
 if(!fs.existsSync(root+'/ability-model-forward.json'))execFileSync('python',['scripts/estimate_defense_seventh_prior.py',String(k)],{env:{...process.env,DEFENSE_SEVENTH_CONFIG:file},stdio:'inherit'});
 if(!fs.existsSync(root+`/pre${k}-v4-league.json`))buildSeventh(k,{label:'v4',configFile:file});
 if(!fs.existsSync(root+'/calibration-v4.json'))execFileSync(process.execPath,['scripts/calibrate_defense_seventh_bundle.js',file,'v4'],{stdio:'inherit'});
 const c=read(file),label='2025-26-calendar-'+k+'-prior';if(!fs.existsSync('reports/defense-seventh/'+label+'-seeds.json'))await runSeventh(label,{bundle:root+'/bundle.json',cutoff:k,calendarDate:c.date,cardFile:root+`/pre${k}-v4-league.json`,neutralContests:true,calibration:read(root+'/calibration-v4.json').selected});
}

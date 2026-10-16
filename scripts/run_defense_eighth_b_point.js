import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read,hash} from './defense_io.js';
import {buildV5} from './build_defense_eighth_v5_cards.js';
import {runSeventh} from './run_defense_seventh.js';
export const bLabel=(season,k,c)=>`${season}-eighth-b-calendar-${k}-c${c.toFixed(6).replace('.','p')}`;
export async function runBPoint(season,k,c){
 const label=bLabel(season,k,c),dir=`reports/defense-eighth/b/${season}/calendar-${k}/c${c.toFixed(6).replace('.','p')}`,cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,original=read(cf);
 if(!fs.existsSync(dir+`/pre${k}-v5-league.json`))await buildV5(cf,c,{output:dir});
 if(!fs.existsSync(dir+'/calibration-v5.json')){
  let s=fs.readFileSync('scripts/calibrate_defense_seventh_bundle.js','utf8');s=s.replace("label=c.season+'-calendar-'+c.k+'-'+version",`label=${JSON.stringify(label)}`).replace("version==='v4'?`${c.root}/pre${c.k}-v4-league.json`:c.leagueOutput","`${c.root}/pre${c.k}-v5-league.json`").replace("neutralContests:version==='v4'","neutralContests:true");
  const file=`scripts/.eighth-b-calibration-${label}.js`;fs.writeFileSync(file,s);execFileSync(process.execPath,[file,dir+'/config.json','v5'],{stdio:'inherit'});
 }
 const extra={bundle:dir+'/bundle.json',cutoff:k,calendarDate:original.date,cardFile:dir+`/pre${k}-v5-league.json`,neutralContests:true,calibration:read(dir+'/calibration-v5.json').selected};
 if(!fs.existsSync(`reports/defense-seventh/${label}-seeds.json`))await runSeventh(label,extra);
 fs.writeFileSync(dir+'/provenance.json',JSON.stringify({season,k,c,sourceConfig:hash(cf),sourceModel:hash(original.root+'/ability-model-forward.json'),frozenProjection:hash('scripts/build_defense_seventh_cards.js'),frozenCalibration:hash('scripts/calibrate_defense_seventh_bundle.js'),rules:hash('reports/defense-eighth/b/development-rules.json')},null,2)+'\n');
 return {label,dir,c};
}
if(process.argv[1]?.endsWith('run_defense_eighth_b_point.js'))await runBPoint(process.argv[2],Number(process.argv[3]),Number(process.argv[4]));

import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {read,hash} from './defense_io.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {runSeventh} from './run_defense_seventh.js';
import {buildV5} from './build_defense_eighth_v5_cards.js';
const root='reports/defense-eighth/c';
export function verifyC(){const p=read(root+'/prereg-supplement.json');if(hash(root+'/prereg-supplement.json')!==fs.readFileSync(root+'/prereg-supplement.sha256','utf8').split(/\s/)[0])throw Error('C0 changed');if(hash('reports/defense-eighth/b/v5-freeze.json')!==p.v5FreezeHash)throw Error('v5 freeze changed');for(const [f,h]of Object.entries(p.frozenSources))if(hash(f)!==h)throw Error('Frozen source changed '+f);return p;}
export const cLabel=(season,k,v)=>`${season}-eighth-c-calendar-${k}-${v}`;
export async function runCVersion(season,k,version){
 const p=verifyC(),cf=`reports/defense-seventh/${season}/calendar-${k}/config.json`,original=read(cf),dir=`${root}/${season}/calendar-${k}/${version}`,label=cLabel(season,k,version);fs.mkdirSync(dir,{recursive:true});
 const c=read('reports/defense-eighth/b/v5-freeze.json').c[k];let cardFile,neutral;
 if(version==='v5'){
  if(!fs.existsSync(dir+`/pre${k}-v5-league.json`))await buildV5(cf,c,{output:dir});cardFile=dir+`/pre${k}-v5-league.json`;neutral=true;
 }else{
  if(!['v1','v3-signals-off'].includes(version))throw Error('Unexpected version');
  const base=read(original.root+'/bundle.json'),options=version==='v1'?{...NBA_DEFENSE_V1,pace:1,seasonMinuteTargets:true,stealPriorRate:base.league.priorRate}:{...base.options,reboundSignal:false,rimSignal:false,liveSignal:false,zoneSignal:false,foulSignal:false};
  if(!fs.existsSync(dir+'/bundle.json'))fs.writeFileSync(dir+'/bundle.json',JSON.stringify({...base,options})+'\n');
  if(!fs.existsSync(dir+'/config.json'))fs.writeFileSync(dir+'/config.json',JSON.stringify({...original,root:dir},null,2)+'\n');cardFile=original.leagueOutput;neutral=false;
 }
 if(!fs.existsSync(dir+'/calibration-'+version+'.json')){
  let s=fs.readFileSync('scripts/calibrate_defense_seventh_bundle.js','utf8');s=s.replace("label=c.season+'-calendar-'+c.k+'-'+version",`label=${JSON.stringify(label)}`);
  if(version==='v5')s=s.replace("version==='v4'?`${c.root}/pre${c.k}-v4-league.json`:c.leagueOutput","`${c.root}/pre${c.k}-v5-league.json`").replace("neutralContests:version==='v4'","neutralContests:true");
  const file=`scripts/.eighth-c-calibration-${label}.js`;fs.writeFileSync(file,s);execFileSync(process.execPath,[file,dir+'/config.json',version],{stdio:'inherit'});
 }
 if(!fs.existsSync(`reports/defense-seventh/${label}-seeds.json`))await runSeventh(label,{bundle:dir+'/bundle.json',cutoff:k,calendarDate:original.date,cardFile,neutralContests:neutral,calibration:read(dir+'/calibration-'+version+'.json').selected},p.seeds);
 fs.writeFileSync(dir+'/execution-provenance.json',JSON.stringify({version,season,k,c:version==='v5'?c:null,preregHash:hash(root+'/prereg-supplement.json'),v5Freeze:p.v5FreezeHash,frozenCalibrator:hash('scripts/calibrate_defense_seventh_bundle.js'),sourceConfig:hash(cf),cardHash:hash(cardFile),bundleHash:hash(dir+'/bundle.json'),adapterHash:hash('scripts/run_defense_eighth_c_versions.js')},null,2)+'\n');
 return label;
}
if(process.argv[1]?.endsWith('run_defense_eighth_c_versions.js'))await runCVersion(process.argv[2],Number(process.argv[3]),process.argv[4]);

import {execFileSync} from 'node:child_process';
import {verifyC,runCVersion} from './run_defense_eighth_c_versions.js';
const p=verifyC(),season=process.argv[2],ks=process.argv[3]?[Number(process.argv[3])]:p.cutoffs;
if(!p.blindSeasons.includes(season))throw Error('Not a registered blind season');
for(const k of ks){verifyC();execFileSync(process.execPath,['scripts/campaign_defense_seventh_calendar.js',season,String(k)],{stdio:'inherit'});for(const v of ['v1','v3-signals-off','v5'])await runCVersion(season,k,v);console.log('C CELL COMPLETE',season,k);}

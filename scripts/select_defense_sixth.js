import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSixth} from './run_defense_sixth.js';
import {compareFifth} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-sixth';
const roleDifference=compareFifth(loadSixth('role-offense-41'),loadSixth('offense-41'),41);
const role=read(root+'/model-pre41.json').trainingSelectRole&&!['netRMSE','winMAE'].some(k=>roleDifference[k].ci95[0]>0),cardVersion=role?'role-offense':'offense';
let neutral=false,neutralTests={};
if(process.argv.includes('--neutral')){
 for(const k of [25,41,55])neutralTests[k]=compareFifth(loadSixth(cardVersion+'-neutral-'+k),loadSixth(cardVersion+'-'+k),k);
 neutral=!Object.values(neutralTests).some(p=>['netRMSE','winMAE'].some(k=>p[k].ci95[0]>0))&&Object.values(neutralTests).some(p=>['netRMSE','winMAE'].some(k=>p[k].ci95[1]<0));
}
const selection={baseline:'nba-defense-v3',cardVersion,neutral,clock:false,netResidual:false,roleDifference,neutralTests,policy:read('scripts/defense_sixth_selection_policy.json')};
fs.writeFileSync(root+'/selection.json',JSON.stringify(selection,null,2)+'\n');console.log('SELECT',cardVersion,neutral);

import fs from 'node:fs';
import {runSixth} from './run_defense_sixth.js';
const phase=process.argv[2]??'initial';
let jobs=phase==='initial'?['role','offense','role-offense'].map(v=>({label:v+'-41',cutoff:41,cardVersion:v})):phase==='net'?[{label:'role-offense-net-41',cutoff:41,cardVersion:'role-offense-net'}]:[];
if(phase==='rolling'){const v=process.argv[3];jobs=[25,55].map(k=>({label:v+'-'+k,cutoff:k,cardVersion:v}));}
if(phase==='neutral'){const v=process.argv[3];jobs=[25,41,55].map(k=>({label:v+'-neutral-'+k,cutoff:k,cardVersion:v,options:{neutralContests:true}}));}
for(const {label,...job} of jobs)if(!fs.existsSync('reports/defense-sixth/'+label+'-seeds.json'))await runSixth(label,job);

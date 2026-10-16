import fs from 'node:fs';
import {read} from './defense_io.js';
import {runSixth} from './run_defense_sixth.js';
const variant=read('reports/defense-sixth/selection.json').cardVersion;
const jobs=[... [25,55].map(k=>({label:variant+'-'+k,cutoff:k,cardVersion:variant})),...[25,41,55].map(k=>({label:variant+'-neutral-'+k,cutoff:k,cardVersion:variant,options:{neutralContests:true}}))];
for(const {label,...job} of jobs)if(!fs.existsSync('reports/defense-sixth/'+label+'-seeds.json'))await runSixth(label,job);

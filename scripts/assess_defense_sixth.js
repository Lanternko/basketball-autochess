import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSixth} from './run_defense_sixth.js';
import {summarizeFifth,compareFifth,prepare} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-sixth';
export const baseRuns=k=>read((k===41?'reports/defense-fourth/holdout-normalized':'reports/defense-fifth/v3-'+k)+'-seeds.json').files.map(f=>read(f.file));
export function assess(label,k){const a=loadSixth(label),b=baseRuns(k);return {label,cutoff:k,summary:summarizeFifth(a,k),paired:compareFifth(a,b,k)};}
if(process.argv[1]?.endsWith('assess_defense_sixth.js')){const results={};for(const label of process.argv.slice(2)){const k=Number(label.split('-').at(-1));results[label]=assess(label,k);}
fs.writeFileSync(root+'/assessment.json',JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(Object.fromEntries(Object.entries(results).map(([k,r])=>[k,{metrics:r.summary.metrics,net:r.paired.netRMSE,wins:r.paired.winMAE}]))));}

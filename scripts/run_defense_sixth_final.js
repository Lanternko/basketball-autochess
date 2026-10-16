import fs from 'node:fs';
import {read} from './defense_io.js';
import {runSixth} from './run_defense_sixth.js';
const s=read('reports/defense-sixth/selection.json'),train=process.argv.includes('--train'),ks=train?[41]:[25,41,55];
for(const k of ks){const label=train?'train-ability'+(s.neutral?'-neutral':'')+'-41':s.cardVersion+(s.neutral?'-neutral':'')+'-'+k;
 if(!fs.existsSync('reports/defense-sixth/'+label+'-seeds.json'))await runSixth(label,{cutoff:k,phase:train?'train':'post',cardVersion:s.cardVersion,options:{neutralContests:s.neutral}});
}

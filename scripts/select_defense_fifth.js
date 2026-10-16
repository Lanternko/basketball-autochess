import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadFifth} from './run_defense_fifth.js';
import {compareFifth} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-fifth',v3=read('reports/defense-fourth/holdout-normalized-seeds.json').files.map(f=>read(f.file));
const policy={scope:'Fifth batch phase1 switches. Main chronological41 test, 20 paired seeds. Policy fixed before neutral and clock accuracy tables are read.',rule:'Keep a switch only if at least netRMSE or winMAE improves significantly, neither significantly worsens, and |true-on-predicted calibrationSlope -1| does not significantly worsen. This is selection among mechanisms, not parameter fitting. Rotation remains diagnostic only: variance gate <0.3 means no2c implementation; previous3c directional failure remains.',clock:'Clock forecasts only pre-cutoff league counts, no post-cutoff actual pace; residual forecast bias reported rather than tuned to zero.'};
// Used as a separate reproducible policy artifact, never changes prior batches.
const policyFile=root+'/selection-policy.json';if(!fs.existsSync(policyFile))fs.writeFileSync(policyFile,JSON.stringify(policy,null,2)+'\n');
if(process.argv.includes('--policy-only'))process.exit(0);
const candidates=['neutral-41','clock-41'],results=[];
for(const label of candidates){const paired=compareFifth(loadFifth(label),v3,41),improves=paired.netRMSE.ci95[1]<0||paired.winMAE.ci95[1]<0,worsens=paired.netRMSE.ci95[0]>0||paired.winMAE.ci95[0]>0||paired.calibrationError.ci95[0]>0;results.push({label,paired,accepted:improves&&!worsens});}
fs.writeFileSync(root+'/selection.json',JSON.stringify({policy,results,valid:results.filter(r=>r.accepted).map(r=>r.label),note:'If both individually survive, test combined once with20 paired seeds before final. No2c mechanism implemented.'},null,2)+'\n');console.log(JSON.stringify(results));

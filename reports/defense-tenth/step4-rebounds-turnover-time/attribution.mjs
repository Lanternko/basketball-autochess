import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {root,verify,pool,job} from './run.mjs';
verify();const p=read(root+'/protocol.json');
const jobs=p.seasons.flatMap(s=>p.diagnosticSeeds.map(seed=>({...job(s,'rawsplit',seed,read(`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`).selected),clockCalibration:read(`reports/defense-tenth/step4-rebounds-clock/${s}/calibration.json`).selected,diagnostic:true,file:`${root}/runs/${s}-rawsplit-${seed}.json`})));
fs.mkdirSync(root+'/runs',{recursive:true});await pool(jobs.filter(j=>!fs.existsSync(j.file)));
fs.writeFileSync(root+'/attribution-manifest.json',JSON.stringify({finishedUTC:new Date().toISOString(),files:jobs.map(j=>({...j,sha256:hash(j.file)}))},null,2)+'\n');

import fs from 'node:fs';
import {read} from './defense_io.js';
import {runFifth} from './run_defense_fifth.js';
for(const k of [41,25,55])if(!fs.existsSync('reports/defense-fifth/clock-'+k+'-seeds.json'))await runFifth('clock-'+k,{cutoff:k,options:read('reports/defense-fifth/clock-calibration-pre'+k+'.json').selected});

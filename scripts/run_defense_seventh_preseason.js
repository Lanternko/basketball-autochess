import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {runSeventh} from './run_defense_seventh.js';
const root='reports/defense-seventh/prior/preseason-0',label='2025-26-preseason-0',seeds=Array.from({length:20},(_,i)=>20261012+i),results=[],calibration=read('reports/defense-seventh/2024-25/calendar-82/calibration-v4.json').selected;let next=0;
await Promise.all(Array.from({length:5},async()=>{while(next<seeds.length){const seed=seeds[next++],tag=label+'-'+seed,file='reports/defense-seventh/'+tag+'-seeds.json';if(!fs.existsSync(file))await runSeventh(tag,{bundle:`${root}/bundle-seed${seed}.json`,cutoff:1,calendarDate:'2025-10-20',neutralContests:true,calibration},[seed]);results.push(...read(file).files);}}));results.sort((a,b)=>a.seed-b.seed);
fs.writeFileSync('reports/defense-seventh/'+label+'-seeds.json',JSON.stringify({label,truePreseason:true,files:results,sources:{rules:hash(root+'/rules.json'),runner:hash('scripts/run_defense_seventh_preseason.js')}},null,2)+'\n');

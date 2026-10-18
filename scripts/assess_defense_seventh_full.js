import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {compareFifth} from '../src/defense_fifth_scoreboard.js';
const old=read('reports/defense-fifth/closeout.json').full,load=l=>read(`reports/defense-fourth/${l}-seeds.json`).files.map(f=>read(f.file)),a=loadSeventh('full-candidate'),vsV3=compareFifth(a,load('final-normalized')),vsV1=compareFifth(a,load('v1'));
delete vsV3.residualSD;delete vsV1.residualSD;
fs.writeFileSync('reports/defense-seventh/full-comparison.json',JSON.stringify({v1:old.v1,v3:old.v3,candidate:read('reports/defense-seventh/full-reference.json').summary,vsV3,vsV1,referenceOnly:true},null,2)+'\n');console.log('Full reference paired comparisons saved');

import fs from 'node:fs';
import {collector,realEvent} from './collect.mjs';
import {read,hash} from '../../../scripts/defense_io.js';
const root='reports/defense-tenth/step4-rebounds-rim-calibration',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').trim())throw Error('Protocol changed');
const results={},missing=[];
for(const season of p.seasons){
 const schedule=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`).league.schedule;
 const rows=[];
 for(const [index,g] of schedule.entries()){
  const file=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+`/pbp/${g.id}.json`;
  if(!fs.existsSync(file)){missing.push({season,id:g.id,index});continue;}
  const a=read(file).data.game.actions,refs=new Map(a.map(e=>[e.actionNumber,e])),c=collector();
  for(const e of a)c.event(realEvent(e,refs));c.event({kind:'gameEnd'});
  rows.push({id:g.id,index,half:index<schedule.length/2?'train':'test',...c.finish()[0]});
 }
 results[season]=rows;
}
fs.writeFileSync(root+'/real.json',JSON.stringify({results,missing})+'\n');
console.log(JSON.stringify({games:Object.fromEntries(Object.entries(results).map(([s,a])=>[s,a.length])),missing}));

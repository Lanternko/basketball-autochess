import fs from 'node:fs';import {read} from '../../../scripts/defense_io.js';
import {realEvent} from '../step4-rebounds-rim-calibration/collect.mjs';
const root='reports/defense-tenth/step4-rebounds-clock-competing',p=read(root+'/protocol.json'),rows=[];
for(const season of p.seasons){
 const schedule=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`).league.schedule;
 for(const [index,g] of schedule.entries()){
 const path=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+`/pbp/${g.id}.json`;if(!fs.existsSync(path))continue;
 const actions=read(path).data.game.actions,refs=new Map(actions.map(e=>[e.actionNumber,e]));let pending=null;
 for(const e of actions){const x=realEvent(e,refs);
 if(x.kind==='clock'&&pending&&x.off===pending.off&&x.period===pending.period)rows.push({season,id:g.id,half:index<schedule.length/2?'train':'test',seconds:pending.time-x.time,periodRemaining:pending.time});
 if(['fg','ft','foul','reb','turnover','clock','period','gameEnd'].includes(x.kind))pending=null;
 if(x.kind==='reb'&&x.fgOreb)pending=x;
 }
 }
}
fs.writeFileSync(root+'/timing-real.json',JSON.stringify(rows)+'\n');console.log('Real post-OREB clock rows',rows.length);

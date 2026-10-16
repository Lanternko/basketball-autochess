import fs from 'node:fs';
import {read,table} from '../../../scripts/defense_io.js';
import {root,verify} from './run.mjs';
verify();const p=read(root+'/protocol.json'),out=[];
for(const season of p.seasons){const base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`,logs=table(base+'/player-games.json'),actual=new Map();
 for(const r of logs){const a=actual.get(r.PLAYER_ID)??{name:r.PLAYER_NAME,minutes:0,oreb:0};a.minutes+=r.MIN??0;a.oreb+=r.OREB??0;actual.set(r.PLAYER_ID,a);}
 for(const version of ['T0','pooled','oreb']){const simulated=new Map();for(const seed of p.seeds){const r=read(version==='T0'?`reports/defense-tenth/step4-t0/runs/${season}-pure-${seed}.json`:(version==='pooled'?`reports/defense-tenth/step4-rebounds/runs/${season}-pooled-${seed}.json`:`${root}/runs/${season}-${version}-${seed}.json`));for(const t of r.teams)for(const q of t.players){const a=simulated.get(q.playerId)??{minutes:0,oreb:0};a.minutes+=q.stats.seconds/60/p.seeds.length;a.oreb+=q.stats.oreb/p.seeds.length;simulated.set(q.playerId,a);}}
  const rows=[...actual].filter(([id,a])=>a.minutes>0&&simulated.get(id)?.minutes>0).map(([id,a])=>{const s=simulated.get(id);return{id,name:a.name,minutes:a.minutes,actualPer36:36*a.oreb/a.minutes,simulatedPer36:36*s.oreb/s.minutes,errorPer36:36*(s.oreb/s.minutes-a.oreb/a.minutes)};}),weight=rows.reduce((s,r)=>s+r.minutes,0),mae=rows.reduce((s,r)=>s+r.minutes*Math.abs(r.errorPer36),0)/weight;
  out.push({season,version,label:'事後探索；非採用判準；交易球員跨隊加總後比較，實際分鐘加權',minutesWeightedOreb36MAE:mae,players:rows.length,largestErrors:[...rows].filter(r=>r.minutes>=500).sort((a,b)=>Math.abs(b.errorPer36)-Math.abs(a.errorPer36)).slice(0,15)});
 }}
fs.writeFileSync(root+'/player-diagnostic.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out.map(({largestErrors,...s})=>s)));

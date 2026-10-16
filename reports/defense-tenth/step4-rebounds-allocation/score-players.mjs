import fs from 'node:fs';import {read,table} from '../../../scripts/defense_io.js';import {root,verify} from './run.mjs';
verify();const p=read(root+'/protocol.json'),arrays={},summary=[];
for(const season of p.seasons){
 const logs=table((season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`)+'/player-games.json'),actual=new Map();
 for(const r of logs){const a=actual.get(r.PLAYER_ID)??{id:r.PLAYER_ID,name:r.PLAYER_NAME,minutes:0,oreb:0,teams:{}};a.minutes+=r.MIN??0;a.oreb+=r.OREB??0;a.teams[r.TEAM_ID]=(a.teams[r.TEAM_ID]??0)+(r.MIN??0);actual.set(r.PLAYER_ID,a);}
 const versions={},ids=[...actual.keys()].sort((a,b)=>a-b);
 for(const version of ['acquisition','allocation']){
  const orebs=[],minutes=[];
  for(const seed of p.seeds){const r=read(version==='acquisition'?`reports/defense-tenth/step4-rebounds-oreb/runs/${season}-oreb-${seed}.json`:`${root}/runs/${season}-${version}-${seed}.json`),sim=new Map();
   for(const t of r.teams)for(const q of t.players){const a=sim.get(q.playerId)??{minutes:0,oreb:0};a.minutes+=q.stats.seconds/60;a.oreb+=q.stats.oreb;sim.set(q.playerId,a);}
   orebs.push(ids.map(id=>sim.get(id)?.oreb??0));minutes.push(ids.map(id=>sim.get(id)?.minutes??0));
  }versions[version]={orebs,minutes};
 }
 const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,cohort=ids.map((id,i)=>i).filter(i=>actual.get(ids[i]).minutes>0&&Object.values(versions).every(v=>mean(v.minutes.map(r=>r[i]))>0)),excluded=ids.filter((id,i)=>!cohort.includes(i));
 const truth=cohort.map(i=>{const a=actual.get(ids[i]),cluster=Object.keys(a.teams).map(Number).sort((x,y)=>a.teams[y]-a.teams[x]||x-y)[0];return {...a,cluster,actualPer36:36*a.oreb/a.minutes};});
 const d={truth,ids:read(`reports/defense-tenth/step4-t0/${season}/bundle.json`).league.teams.map(t=>t.id).sort((a,b)=>a-b),versions:{},excluded:excluded.map(id=>actual.get(id))};
 for(const [version,v]of Object.entries(versions)){
  d.versions[version]={orebs:v.orebs.map(r=>cohort.map(i=>r[i])),minutes:v.minutes.map(r=>cohort.map(i=>r[i]))};
  const rows=truth.map((a,i)=>{const q=d.versions[version],pred=36*mean(q.orebs.map(r=>r[i]))/mean(q.minutes.map(r=>r[i]));return {...a,predictedPer36:pred,error:pred-a.actualPer36};}),total=rows.reduce((s,a)=>s+a.minutes,0);
  summary.push({season,version,players:rows.length,excludedMinutes:d.excluded.reduce((s,a)=>s+a.minutes,0),MAE:rows.reduce((s,a)=>s+a.minutes*Math.abs(a.error),0)/total,RMSE:Math.sqrt(rows.reduce((s,a)=>s+a.minutes*a.error*a.error,0)/total),largestErrors:rows.filter(a=>a.minutes>=500).sort((a,b)=>Math.abs(b.error)-Math.abs(a.error)).slice(0,20),rows});
 }arrays[season]=d;
}
fs.writeFileSync(root+'/player-arrays.json',JSON.stringify(arrays)+'\n');fs.writeFileSync(root+'/player-analysis.json',JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary.map(({rows,largestErrors,...x})=>x)));

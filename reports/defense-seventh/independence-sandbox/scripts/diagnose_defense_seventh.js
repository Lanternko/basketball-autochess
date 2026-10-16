import fs from 'node:fs';
import {read,table} from './defense_io.js';
import {baseRuns} from './assess_defense_sixth.js';
import {loadSixth} from './run_defense_sixth.js';
const root='reports/defense-seventh';
const box=table('data/season-source/player-games.json'),league=read('data/season-league.json'),order={},counter={};
for(const g of league.schedule)for(const t of [g.homeId,g.awayId])order[g.id+'/'+t]=counter[t]=(counter[t]??0)+1;
const keys=['pts','fga','fgm','fg3a','fg3m','ast','oreb','dreb','seconds'];
export function playerErrors(runs,k,date=null){
 const real=new Map(),pred=new Map();
 const dates=new Map(league.schedule.map(g=>[g.id,g.date]));
 for(const b of box)if(date?dates.get(b.GAME_ID)>date:order[b.GAME_ID+'/'+b.TEAM_ID]>k){const r=real.get(b.PLAYER_ID)??{id:b.PLAYER_ID,name:b.PLAYER_NAME,games:0,MIN:0,PTS:0,FGA:0,FGM:0,FG3A:0,FG3M:0,AST:0,REB:0};r.games++;for(const z of ['MIN','PTS','FGA','FGM','FG3A','FG3M','AST','REB'])r[z]+=b[z]??0;real.set(b.PLAYER_ID,r);}
 for(const run of runs)for(const t of run.teams)for(const p of t.players){const r=pred.get(p.playerId)??Object.fromEntries(keys.map(z=>[z,0]));for(const z of keys)r[z]+=p.stats[z]/runs.length;pred.set(p.playerId,r);}
 const definitions={points:r=>r.PTS/r.games,attempts:r=>r.FGA/r.games,FG:r=>r.FGA?100*r.FGM/r.FGA:null,three:r=>r.FG3A?100*r.FG3M/r.FG3A:null,assists:r=>r.AST/r.games,rebounds:r=>r.REB/r.games};
 const players=[...real.values()].map(r=>{const p=pred.get(r.id)??{};const sim={...r,PTS:p.pts??0,FGA:p.fga??0,FGM:p.fgm??0,FG3A:p.fg3a??0,FG3M:p.fg3m??0,AST:p.ast??0,REB:(p.oreb??0)+(p.dreb??0)};return {id:r.id,name:r.name,minutes:r.MIN,games:r.games,actual:Object.fromEntries(Object.entries(definitions).map(([z,f])=>[z,f(r)])),predicted:Object.fromEntries(Object.entries(definitions).map(([z,f])=>[z,f(sim)])),simulatedMinutes:(p.seconds??0)/60};});
 return {definition:'Per observed appearance averages; trades pooled by player. MAE/RMSE/bias weighted by heldout actual minutes. FG/3FG in percentage points; zero-attempt ratios excluded separately. No per-minute rescaling of predicted counts.',metrics:Object.fromEntries(Object.keys(definitions).map(z=>{const ps=players.filter(p=>p.actual[z]!=null&&p.predicted[z]!=null),w=ps.reduce((s,p)=>s+p.minutes,0);return [z,{MAE:ps.reduce((s,p)=>s+p.minutes*Math.abs(p.predicted[z]-p.actual[z]),0)/w,RMSE:Math.sqrt(ps.reduce((s,p)=>s+p.minutes*(p.predicted[z]-p.actual[z])**2,0)/w),bias:ps.reduce((s,p)=>s+p.minutes*(p.predicted[z]-p.actual[z]),0)/w,n:ps.length}];})),players};
}
if(process.argv[1]?.endsWith('diagnose_defense_seventh.js')){
const result={cutoffs:{}};
for(const k of [25,41,55]){
 const projection=read(`reports/defense-sixth/pre${k}-role-offense-projection.json`).players;
 const unique=[...new Map(projection.map(p=>[p.id,p])).values()],minutes=unique.reduce((s,p)=>s+p.minutes,0);
 const bounds=unique.filter(p=>Object.values(p.attributes).some(a=>a<=1e-6||a>=120-1e-6));
 result.cutoffs[k]={v3:playerErrors(baseRuns(k),k),candidate:playerErrors(loadSixth(`role-offense-neutral-${k}`),k),projection:{minuteWeightedBias:unique.reduce((s,p)=>s+p.minutes*p.offenseProjectionError,0)/minutes,minuteWeightedMAE:unique.reduce((s,p)=>s+p.minutes*Math.abs(p.offenseProjectionError),0)/minutes,bounds:bounds.map(p=>({id:p.id,name:p.name,minutes:p.minutes,attributes:p.attributes,error:p.offenseProjectionError})),boundMinutesFraction:bounds.reduce((s,p)=>s+p.minutes,0)/minutes}};
}
fs.writeFileSync(root+'/initial-diagnosis.json',JSON.stringify(result,null,2)+'\n');
for(const [k,v] of Object.entries(result.cutoffs))console.log(k,JSON.stringify({v3:v.v3.metrics,candidate:v.candidate.metrics,projection:v.projection}));
}

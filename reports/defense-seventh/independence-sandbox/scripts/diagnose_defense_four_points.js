import fs from 'node:fs';
import readline from 'node:readline';
import {read,hash,loadDefenseInputs} from './defense_io.js';
import {simulateDefenseGame} from '../src/defense_game.js';
import {NBA_DEFENSE_V1} from '../src/defense_presets.js';
import {observedLineup} from '../src/minute_budget.js';
const real={four:0,threePlusOne:0,twoFTPlusFG:0,other:0},sim={four:0,threePlusOne:0,twoFTPlusFG:0,other:0};
for await(const line of readline.createInterface({input:fs.createReadStream('reports/defense-b1/real-games.jsonl'),crlfDelay:Infinity})){
  if(!line)continue;const g=JSON.parse(line),actions=read('data/defense-a-source/pbp/'+g.id+'.json').data.game.actions;
  for(const p of g.possessions.filter(p=>p.period<=4&&p.points===4)){real.four++;const rows=actions.slice(p.startIndex,p.endIndex+1).filter(e=>e.teamId===g.ids[p.side]),long=rows.some(e=>e.actionType==='3pt'&&e.shotResult==='Made'),ft=rows.filter(e=>e.actionType==='freethrow'&&e.shotResult==='Made').length;
    real[long&&ft===1?'threePlusOne':ft>=1&&rows.some(e=>e.actionType==='2pt'&&e.shotResult==='Made')?'twoFTPlusFG':'other']++;}
}
const inputs=loadDefenseInputs(),teams=new Map(inputs.league.teams.map(t=>[t.id,t])),boxes=new Map(inputs.exposure.games.map(g=>[g.id,g])),seed=20261012;
for(const [index,fixture] of inputs.league.schedule.entries()){
  const box=boxes.get(fixture.id),pair=[fixture.homeId,fixture.awayId].map((id,i)=>observedLineup(teams.get(id),fixture[i?'awayPlayerIds':'homePlayerIds'],box.teams.find(t=>t.teamId===id)));
  const game=simulateDefenseGame(...pair,{...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate,seed:(seed+Math.imul(index+1,7919))>>>0,replay:true});
  let current=null;const end=e=>{if(!current)return;const pts=e.score[current.off]-current.score[current.off];if(pts===4){sim.four++;sim[current.long&&current.ft===1?'threePlusOne':current.ft>0&&current.short?'twoFTPlusFG':'other']++;}current=null;};
  for(const e of game.events){if(e.type==='POSSESSION'){end(e);current=e.period<=4?{off:e.off,score:e.score,long:false,short:false,ft:0}:null;}if(current&&e.off===current.off){if(e.type==='FGM'){if(e.zone==='long')current.long=true;else current.short=true;}if(e.type==='FTM')current.ft++;}if(e.type==='PERIOD_END')end(e);}
}
const result={seed,realGames:1227,simGames:1230,real,simulation:sim,interpretation:'Event classification only, no engine change. Simulation on same frozen v1 roster/seed. Most four-point possessions from made three plus made and-one FT indicates a foul outcome-frequency issue despite globally aligned recorded FG%.',provenance:{sources:Object.fromEntries(['reports/defense-b1/real-games.jsonl','data/defense-a-source/manifest.json'].map(f=>[f,hash(f)])),code:Object.fromEntries(['scripts/diagnose_defense_four_points.js','src/defense_game.js','src/defense_probability.js'].map(f=>[f,hash(f)]))}};
fs.writeFileSync('reports/defense-b1/four-point-diagnosis.json',JSON.stringify(result,null,2)+'\n');console.log(result);

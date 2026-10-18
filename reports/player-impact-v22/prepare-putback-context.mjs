import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v21/input.mjs';
import {exposureDefenseProbabilities} from '../player-impact-v20/model.mjs';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {pressureSignal} from '../../src/defense_probability.js';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
const root='reports/player-impact-v22',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-putback-contexts.json`;if(fs.existsSync(output))throw Error('Preserve source contexts');
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const src=read(`${root}/${season}-putback-events.json`),valid=new Map(src.games.map(g=>[g.id,g])),games=new Map(),sums=new Map();
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;const rows=games.get(s.id)??[];rows.push(s);games.set(s.id,rows);}
 const mf=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',paths=new Map(read(mf).sources.map(s=>[s.id,s.file]));let count=0,strictSeconds=0;
 for(const[id,rows]of games){
  const energies=new Map(),events=valid.get(id).events,actions=events.length?read(paths.get(id)).data.game.actions:[],joined=new Set();let lastPeriod=1;
  rows.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  for(const s of rows){
   strictSeconds+=s.seconds*10;
   if(s.period>lastPeriod){for(const[k,e]of energies)energies.set(k,periodEnergyRecovery(e,s.period-lastPeriod));lastPeriod=s.period;}
   const active=s.teams.map(t=>{const ids=new Set(t.players),lineup=new Map();for(const[pid,p]of teams.get(t.teamId)){const key=t.teamId+':'+pid,e=energies.get(key)??1,step=rotationEnergyStep(e,s.seconds,ids.has(pid),p.stamina);energies.set(key,step.end);if(ids.has(pid))lineup.set(pid,M.applyStamina(p,1-step.mean));}return t.players.map(pid=>lineup.get(pid));});
   for(const e of events)if(s.startIndex<=e.index&&e.index<s.endIndex){
    if(joined.has(e.index))throw Error('Overlapping event source stints');joined.add(e.index);
    const side=s.teams.findIndex(t=>t.teamId===e.teamId),os=active[side],ds=active[1-side],i=os.findIndex(p=>p.playerId===e.playerId);if(i<0)throw Error('Putback actor outside lineup');
    const p=os[i],clock=actions[e.index].clock.match(/PT(?:(\d+)M)?([\d.]+)S/),secs=Number(clock[1]??0)*60+Number(clock[2]);
    const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
    const q=exposureDefenseProbabilities(p,measuredContext(os,i),ds[i],M.helpDefense(ds),tr(os),tr(ds),M.teamPhysique(ds),{assist:null,forced:secs<1.5,putback:true,contextScale:b.options.contextScale,contextLongScale:1,contextShortScale:b.options.contextShortScale,turnoverScale:b.options.turnoverScale,turnoverMode:b.options.turnoverMode,pressureAttribute:pressureSignal(ds,b.options.stealPriorRate).attribute},ds);
    const sum=sums.get(p.playerId)??{attempts:0,delta:0};sum.attempts++;sum.delta+=q.make.short-p.shootingMeasurement.sourceBase.short;sums.set(p.playerId,sum);count++;
   }
  }
  if(joined.size!==events.length)throw Error('Unmapped source putback events');
 }
 if(count!==src.totals.fieldGoalAttempts)throw Error('Source attempt coverage mismatch');
 const leagueDelta=[...sums.values()].reduce((s,p)=>s+p.delta,0)/count,priorAttempts=60*count/(strictSeconds/60);
 const players=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p]));
 const cards=Object.fromEntries([...players].map(([pid,p])=>{const s=sums.get(pid)??{attempts:0,delta:0};return[pid,{sourceBase:p.shootingMeasurement.sourceBase.short,context:(s.delta+priorAttempts*leagueDelta)/(s.attempts+priorAttempts),sourceAttempts:s.attempts,sourceDeltaSum:s.delta}];}));
 const out={season,design:'Source PB-only recorded-FGA weighted mean of uncentered model short make minus frozen source short curve. Uses actual opposing five, original measured creation context, tracked defensive exposure, source rotation mean energy and period recovery. Source makes never enter this context. Source miss linkage is a PBP proxy. 60-minute league PB-attempt prior. Fresh-shot contexts remain byte-for-byte frozen.',attempts:count,strictPlayerMinutes:strictSeconds/60,priorAttempts,leagueDelta,cards,hashes:Object.fromEntries([`${root}/prepare-putback-context.mjs`,`${root}/${season}-putback-events.json`,file,'reports/player-impact-v21/input.mjs','reports/player-impact-v20/model.mjs',`reports/player-impact-v20/${season}-contexts.json`].map(f=>[f,hash(f)]))};
 fs.writeFileSync(output,JSON.stringify(out,null,2));console.log(JSON.stringify({season,attempts:count,priorAttempts,leagueDelta}));
}

import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from './input.mjs';
import {impactEngine} from './audit-engine.mjs';
const root='reports/player-impact-v24',season='2025-26',seed=20261012,read=f=>JSON.parse(fs.readFileSync(f));
const b=loadInput(season),run=await impactEngine('rotation-space'),source=read(`reports/player-impact-v19/${season}-ft-kinds.json`),truth=read(`reports/player-impact-v1/${season}-on-court-truth.json`),valid=new Set(truth.gameIds);
b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=read(`reports/player-impact-v7/${season}-center.json`).fullCenter;
const players={},counts={},fouls={};let lastFoul=null;
const increment=(obj,key)=>obj[key]=(obj[key]??0)+1;
b.options.eventObserver=e=>{
 if(e.type==='FOUL'){lastFoul={kind:e.kind,period:e.period,clock:e.clock};increment(fouls,e.kind);}
 if(['FTM','FTX'].includes(e.type)){
  const kind=e.technical?'technical':lastFoul?.period===e.period&&lastFoul?.clock===e.clock?lastFoul.kind:'unresolved',p=players[e.playerId]??={};assert.ok(e.playerId);increment(counts,kind);increment(p,kind);increment(p,'fta');
 }
 if(['FGM','FGX'].includes(e.type)){const p=players[e.playerId]??={};increment(p,'fga');}
 if(e.type==='GAME_END'||e.type==='PERIOD_START')lastFoul=null;
};
const result=run(b.league,b.exposure,{seed,options:b.options,audit:false,replay:false,indices:b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[])});
const minutes=new Map(),names=new Map();for(const t of result.teams)for(const p of t.players){minutes.set(p.playerId,(minutes.get(p.playerId)??0)+p.stats.seconds/60);names.set(p.playerId,p.name);}
const rows=Object.entries(source.players).map(([pid,s])=>({playerId:Number(pid),name:names.get(Number(pid)),source:s,simulated:players[pid]??{},sourceMinutes:truth.players.find(p=>p.playerId===Number(pid))?.on.seconds/60,simulatedMinutes:minutes.get(Number(pid))??0}));
const original=read(`${root}/runs/${season}-rotation-space-strict-${seed}.json`);assert.deepEqual(result.matches,original.matches);assert.deepEqual(result.teams,original.teams);
assert.equal(result.teams.reduce((s,t)=>s+t.stats.fta,0),Object.values(counts).reduce((s,n)=>s+n,0));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),out={season,seed,games:result.matches.length,sourceCounts:source.totals,simulationCounts:counts,fouls,rows,passiveExactMatchAndTeamParity:true,hashes:Object.fromEntries(['audit-free-throws.mjs','audit-engine.mjs'].map(f=>[root+'/'+f,hash(root+'/'+f)]))};
fs.writeFileSync(root+'/free-throw-audit.json',JSON.stringify(out,null,2));console.log(JSON.stringify({season,games:out.games,source:source.totals,simulated:counts,selected:rows.filter(p=>[201939,203999,1628983,1629029,1629674].includes(p.playerId))}));

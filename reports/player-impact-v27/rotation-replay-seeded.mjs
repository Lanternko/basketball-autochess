// Closed historical-exposure diagnostic. Historical period count and rotations
// are fixed covariates; game wins are deliberately not an adoption metric.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../player-impact-v26/input.mjs';
import {impactEngine} from './replay-engine.mjs';
import {thirdLineup} from '../../src/defense_third_minutes.js';
import {minuteBudgetSchedule} from '../../src/minute_budget.js';
import {onCourtCollector} from '../player-impact-v1/on-court.mjs';
const root='reports/player-impact-v27',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const season=process.argv.find(x=>/^202\d-\d\d$/.test(x))??'2025-26',limit=Number(process.argv.find(x=>x.startsWith('--limit='))?.split('=')[1]??0),seed=Number(process.argv.find(x=>x.startsWith('--seed='))?.split('=')[1]??20261012);
const suffix=`${season}-${seed}${limit?'-probe-'+limit:''}`,file=`${root}/rotation-replay-${suffix}.json`;assert.ok(!fs.existsSync(file),'Preserve diagnostic result');
const b=loadInput(season),run=await impactEngine('rotation-space',{game:true}),teams=new Map(b.league.teams.map(t=>[t.id,t])),exposure=new Map(b.exposure.games.map(g=>[g.id,g]));
const valid=new Set(read(`reports/player-impact-v1/${season}-on-court-truth.json`).gameIds),sf=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,stints=new Map();
for(const line of fs.readFileSync(sf,'utf8').trim().split('\n')){const s=JSON.parse(line);if(valid.has(s.id)&&s.seconds>0){if(!stints.has(s.id))stints.set(s.id,[]);stints.get(s.id).push(s);}}
const inherited=read('reports/player-impact-v26/validation-protocol.json').hashes,hashes={...inherited,...Object.fromEntries([`${root}/rotation-replay-seeded.mjs`,`${root}/replay-engine.mjs`,'src/minute_budget.js','src/defense_third_minutes.js',sf].map(f=>[f,hash(f)]))};
const verify=()=>{for(const[f,h]of Object.entries(hashes))assert.equal(hash(f),h,`Source drift ${f}`);};verify();
const versions=['heuristic','synthetic','observed'],statsKeys=['pts','ast','oreb','dreb','stl','blk','tov','fga','fgm','fg3a','fg3m','fta','ftm','seconds','clockTov','liveTov','deadTov'];
const names=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p.name])),blank=()=>Object.fromEntries(statsKeys.map(k=>[k,0]));
const results=Object.fromEntries(versions.map(v=>[v,{players:new Map([...names].map(([id,name])=>[id,{playerId:id,name,stats:blank()}])),collector:onCourtCollector(),matches:[],ties:0}]));
const actual=new Map([...names].map(([id,name])=>[id,{playerId:id,name,seconds:0,points:0}]));let done=0;
for(const[index,fixture]of b.league.schedule.entries()){
 if(!valid.has(fixture.id))continue;if(limit&&done>=limit)break;
 const raw=stints.get(fixture.id);assert.ok(raw?.length);const periods=Math.max(...raw.map(s=>s.period)),duration=2880+(periods-4)*300;
 raw.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
 const observed=exposure.get(fixture.id),pair=[fixture.homeId,fixture.awayId].map((id,i)=>thirdLineup(teams.get(id),fixture[i?'awayPlayerIds':'homePlayerIds'],observed.teams.find(t=>t.teamId===id),b.options.seasonMinuteTargets));
 for(const t of pair)t.roster=t.roster.map(p=>({...p,injured:false}));
 const sourceSeconds=pair.map(t=>new Map(t.roster.map(p=>[p.playerId,0]))),schedules=pair.map(()=>[]);
 for(const s of raw){
  const offset=s.period<=4?(s.period-1)*720:2880+(s.period-5)*300,clock=s.period<=4?720:300,start=offset+clock-s.startClock,end=offset+clock-s.endClock;
  assert.ok(Math.abs(end-start-s.seconds)<1e-6);
  for(let side=0;side<2;side++){
   const t=s.teams.find(t=>t.teamId===pair[side].id),indices=t.players.map(pid=>pair[side].roster.findIndex(p=>p.playerId===pid));assert.ok(indices.every(i=>i>=0));assert.equal(new Set(indices).size,5);
   assert.ok(Math.abs(start-(schedules[side].at(-1)?.end??0))<1e-6,'Source rotation gap or overlap');
   schedules[side].push({start,end,lineup:indices});for(const pid of t.players)sourceSeconds[side].set(pid,sourceSeconds[side].get(pid)+s.seconds);
  }
 }
 for(let side=0;side<2;side++){
  assert.ok(Math.abs(schedules[side].at(-1).end-duration)<1e-6);
  for(const p of pair[side].roster){const row=actual.get(p.playerId);row.seconds+=sourceSeconds[side].get(p.playerId);row.points+=observed.teams.find(t=>t.teamId===pair[side].id).players.find(q=>q.playerId===p.playerId).points;}
 }
 const synthetic=pair.map((t,side)=>minuteBudgetSchedule(t.roster.map(p=>({...p,targetMinutes:sourceSeconds[side].get(p.playerId)/60})),duration));
 for(const version of versions){
  const result=results[version],options={...b.options,seed:(seed+Math.imul(index+1,7919))>>>0,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:read(`reports/player-impact-v7/${season}-center.json`).fullCenter,foulOut:99,sourcePeriods:periods,maxOvertimes:Math.max(20,periods-4),minuteMode:version==='heuristic'?'heuristic':'budget',onCourtObserver:e=>result.collector.event(e)};
  if(version!=='heuristic')options.sourceRotations=version==='observed'?schedules:synthetic;
  const g=run(...pair,options);assert.equal(g.gameSeconds,duration);assert.equal(g.periods,periods);assert.equal(g.complete,true);result.ties+=Number(g.tie);
  for(let side=0;side<2;side++){
   const tag=side?'B':'A',s=g['stat'+tag],ps=g['players'+tag];assert.equal(s.pts,g['score'+tag]);assert.equal(s.pts,2*s.fgm+s.fg3m+s.ftm);assert.ok(Math.abs(ps.reduce((n,p)=>n+p.seconds,0)-5*duration)<.011);
   for(const k of statsKeys){const teamOnly=['tov','clockTov','deadTov'].includes(k)?s.clockTov:0;assert.ok(Math.abs(ps.reduce((n,p)=>n+(p[k]??0),0)+teamOnly-s[k])<.011,`${version} ${fixture.id} ${k}`);}
   for(let i=0;i<ps.length;i++){
    const pid=pair[side].roster[i].playerId;if(version!=='heuristic')assert.ok(Math.abs(ps[i].seconds-sourceSeconds[side].get(pid))<.011,`Source player time ${version} ${fixture.id} ${pid}`);
    for(const k of statsKeys)result.players.get(pid).stats[k]+=ps[i][k]??0;
   }
  }
  assert.equal(g.statA.stl,g.statB.liveTov);assert.equal(g.statB.stl,g.statA.liveTov);
  result.matches.push({id:fixture.id,periods,gameSeconds:g.gameSeconds,scoreA:g.scoreA,scoreB:g.scoreB,tie:g.tie});
 }
 done++;if(done%200===0)console.log(JSON.stringify({season,games:done,variants:versions.length}));
}
assert.equal(done,limit||valid.size);verify();
const output={season,seed,scope:'Closed historical-exposure diagnostic only: observed period count for all variants, foulOut99, same available roster, same source-role inputs and random seed. Heuristic rotations vs synthetic exact individual minutes vs observed source five-player stints. Source and synthetic schedules may substitute at live clock boundaries; this changes joint teammates/opponents and energy histories, not just marginal minutes. Not prospective prediction, causal on/off, ordinary season wins or adoption evidence. Default engine exactly matches v26 without options.',limit,hashes,games:done,actual:[...actual.values()],variants:Object.fromEntries(versions.map(v=>{
 const r=results[v],onCourt=r.collector.finish();assert.equal(onCourt.games,done);return[v,{players:[...r.players.values()],matches:r.matches,ties:r.ties,onCourt}];
}))};
fs.writeFileSync(file,JSON.stringify(output));console.log(JSON.stringify({file,games:done,sourceMinutesExact:['synthetic','observed'],ties:Object.fromEntries(versions.map(v=>[v,results[v].ties]))}));

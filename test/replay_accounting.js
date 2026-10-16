import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {replayAccounting} from '../src/replay_accounting.js';
import {lineupForGame} from '../src/season_simulation.js';
import {simulateGame} from '../src/simulation_engine.js';

// A substitution at the same clock as a score must affect only later scores.
// Free throws after a substitution belong to the new on-court lineup.
const first=[0,1,2,3,4],reserve=[0,1,2,3,5];
const teams=[{roster:Array.from({length:6},(_,i)=>({playerId:i===0?1628983:i}))},
  {roster:Array.from({length:6},(_,i)=>({playerId:100+i}))}];
const event=(elapsed,score,lineup=first)=>({elapsed,score,lineups:[lineup,first]});
const fixture={complete:true,scoreA:5,scoreB:3,gameSeconds:30,
  playersA:[30,30,30,30,20,10].map(seconds=>({seconds})),playersB:[30,30,30,30,30,0].map(seconds=>({seconds})),
  events:[event(0,[0,0]),event(10,[2,0]),event(10,[2,0],reserve),event(20,[2,3],reserve),
    event(20,[2,3]),event(20,[3,3]),event(30,[5,3])]};
const accounted=replayAccounting(fixture,teams);
assert.deepEqual(accounted.players[0].map(p=>p.plusMinus),[2,2,2,2,5,-3]);
assert.deepEqual(accounted.players[1].map(p=>p.plusMinus),[-2,-2,-2,-2,-2,0]);
assert.equal(accounted.buckets[0][0].seconds,20);assert.equal(accounted.buckets[0][0].plusMinus,5);
assert.equal(accounted.buckets[0][1].seconds,10);assert.equal(accounted.buckets[0][1].plusMinus,-3);
assert.equal(accounted.shai[0].on.seconds,30);assert.equal(accounted.shai[1].off.seconds,30);
for (const bad of [
  {...fixture,complete:false},
  {...fixture,scoreA:6},
  {...fixture,gameSeconds:31},
  {...fixture,playersA:fixture.playersA.map((p,i)=>i===4?{seconds:21}:p)},
  {...fixture,events:[event(0,[0,0],[0,0,2,3,4]),...fixture.events.slice(1)]},
  {...fixture,events:[fixture.events[0],event(-1,[0,0]),...fixture.events.slice(1)]},
  {...fixture,events:[fixture.events[0],event(1,[-1,0]),...fixture.events.slice(1)]},
]) assert.throws(()=>replayAccounting(bad,teams));

const read=file=>JSON.parse(fs.readFileSync(new URL('../'+file,import.meta.url)));
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+file,import.meta.url))).digest('hex');
const league=read('data/season-league.json'),baseline=read('reports/nba-season-2025-26-seed20261012.json');
const allTeams=new Map(league.teams.map(t=>[t.id,t]));
const chosen=[0,baseline.matches.findIndex(g=>g.overtimes>0),league.schedule.findIndex(g=>g.neutral)];
for(const index of chosen){
  const f=league.schedule[index],pair=[lineupForGame(allTeams.get(f.homeId),f.homePlayerIds),lineupForGame(allTeams.get(f.awayId),f.awayPlayerIds)];
  const game=simulateGame(...pair,{mode:'timed',seed:baseline.matches[index].seed,replay:true});
  assert.equal(game.scoreA,baseline.matches[index].homeScore);assert.equal(game.scoreB,baseline.matches[index].awayScore);
  replayAccounting(game,pair);
}
const report=read('reports/season-diagnostics.json');
assert.equal(report.provenance.baselineReport,hash('reports/nba-season-2025-26-seed20261012.json'));
assert.equal(report.provenance.league,hash('data/season-league.json'));
for(const [file,h] of Object.entries(report.provenance.code))assert.equal(hash(file),h);
for(const [name,source] of Object.entries(report.provenance.diagnostics))assert.equal(hash('data/diagnostic-source/'+name+'.json'),source.sha256);
assert.equal(report.players.length,661);
for(const t of baseline.standings){
  const ps=report.players.filter(p=>p.teamId===t.id);
  assert.equal(ps.reduce((n,p)=>n+p.simulatedPlusMinus,0),5*(t.pointsFor-t.pointsAgainst));
  assert.ok(Math.abs(ps.reduce((n,p)=>n+p.simulatedMinutes,0)-t.stats.seconds/60)<.01);
}
const west=read('data/diagnostic-source/cup-west.json').data.boxScoreTraditional;
assert.equal(west.homeTeamId,1610612760);assert.equal(west.awayTeamId,1610612759);
assert.deepEqual(report.officialLocation.find(t=>t.id===1610612759),{id:1610612759,name:'San Antonio Spurs',home:40,road:41,neutral:1});
console.log('PASS substitution/free-throw attribution, invalid replay rejection, regulation/OT/neutral replays, 661 stint conservation and diagnostic fingerprints');

import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {validateSeason,lineupForGame,checkGameAccounting} from '../src/season_simulation.js';
import {simulateGame} from '../src/simulation_engine.js';
import {interpolate} from '../src/probability_model.js';
import {CURVE_DEF_3PT,CURVE_DEF_RIM} from '../src/constants.js';

const read=path=>JSON.parse(fs.readFileSync(new URL('../'+path,import.meta.url)));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const league=read('data/season-league.json');
assert.deepEqual(validateSeason(league),{teams:30,games:1230,teamGames:2460,neutralGames:5,playerCards:661,uniquePlayers:582});
for (const source of league.sources) assert.equal(sha(fs.readFileSync(new URL('../data/'+source.file,import.meta.url))),source.sha256);
assert.equal(league.sources.length,44);
for (const bad of [
  {...league,schedule:league.schedule.slice(1)},
  {...league,schedule:league.schedule.map((g,i)=>i===1?league.schedule[0]:g)},
  {...league,schedule:league.schedule.map((g,i)=>i?g:{...g,homePlayerIds:g.homePlayerIds.slice(0,4)})},
  {...league,schedule:league.schedule.map((g,i)=>i?g:{...g,neutral:!g.neutral})},
]) assert.throws(()=>validateSeason(bad));

// NBA sources use PLUSMINUS and zone-specific attempts. Missing fields must
// never silently produce a league of 99-rated defenders.
for (const [source,key,curve,attemptKey] of [
  ['defense-long','onBall',CURVE_DEF_3PT,'FG3A'],['defense-rim','help',CURVE_DEF_RIM,'FGA_LT_06']]) {
  const raw=read('data/benchmark-source/'+source+'.json').data.resultSets[0];
  const rows=new Map(raw.rowSet.map(r=>{const row=Object.fromEntries(raw.headers.map((h,i)=>[h,r[i]]));return[row.CLOSE_DEF_PERSON_ID,row];}));
  let checked=0;
  for (const p of league.teams.flatMap(t=>t.roster)) {
    const d=rows.get(p.playerId);
    if (!d||!d[attemptKey]) {assert.ok(p.missingMeasurements.includes(source));assert.equal(p[key],70);continue;}
    if (p[key]>40&&p[key]<99) {
      assert.ok(Math.abs(interpolate(p[key],curve)-d.PLUSMINUS*d[attemptKey]/(d[attemptKey]+200))<1e-12);
      checked++;
    }
  }
  assert.ok(checked>400,'Defenders must retain measured heterogeneity');
}
const bio=read('data/benchmark-source/bio.json').data.resultSets[0];
const missingWeight=new Set(bio.rowSet.filter(r=>!Number(r[bio.headers.indexOf('PLAYER_WEIGHT')])).map(r=>r[0]));
for (const p of league.teams.flatMap(t=>t.roster).filter(p=>missingWeight.has(p.playerId))) {
  assert.equal(p.physique,70);assert.ok(p.missingMeasurements.includes('body-weight'));
}

const team=league.teams[0],before=JSON.stringify(team);
for (const count of [5,6,team.roster.length]) {
  const lineup=lineupForGame(team,team.roster.slice(0,count).map(p=>p.playerId));
  assert.ok(Math.abs(lineup.roster.reduce((n,p)=>n+p.targetMinutes,0)-240)<1e-9);
  assert.ok(lineup.roster.every(p=>p.targetMinutes>=0&&p.targetMinutes<=48));
}
assert.equal(JSON.stringify(team),before);
assert.throws(()=>lineupForGame(team,[999,998,997,996,995]));
assert.throws(()=>checkGameAccounting({complete:false,winnerA:null}));

const teams=new Map(league.teams.map(t=>[t.id,t]));
const fixtures=[league.schedule[0],...league.schedule.filter(g=>g.neutral),league.schedule.at(-1)];
for (const fixture of fixtures) {
  const home=lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds);
  const away=lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds);
  const game=simulateGame(home,away,{mode:'timed',seed:777});
  checkGameAccounting(game);
  assert.deepEqual(game,simulateGame(home,away,{mode:'timed',seed:777}));
  assert.throws(()=>checkGameAccounting({...game,gameSeconds:game.gameSeconds+1}));
  assert.throws(()=>checkGameAccounting({...game,scoreA:game.scoreA+1}));
}

const reportPath=new URL('../reports/nba-season-2025-26-seed20261012.json',import.meta.url);
if (fs.existsSync(reportPath)) {
  const report=JSON.parse(fs.readFileSync(reportPath));
  assert.equal(report.provenance.leagueSha256,sha(fs.readFileSync(new URL('../data/season-league.json',import.meta.url))));
  for (const [file,hash] of Object.entries(report.provenance.codeHashes)) assert.equal(sha(fs.readFileSync(new URL('../'+file,import.meta.url))),hash);
  assert.equal(report.standings.length,30);
  assert.ok(report.standings.every(t=>t.games===82&&t.wins+t.losses===82&&t.homeGames+t.awayGames+t.neutralGames===82));
  assert.equal(report.standings.reduce((n,t)=>n+t.wins,0),1230);
  assert.equal(report.standings.reduce((n,t)=>n+t.losses,0),1230);
  const boxes=fs.readFileSync(new URL('../reports/nba-season-2025-26-seed20261012-games.jsonl',import.meta.url));
  assert.equal(sha(boxes),report.provenance.boxScoresSha256);
  const games=boxes.toString().trim().split('\n').map(line=>JSON.parse(line));
  assert.equal(games.length,1230);
  const eligibility=new Map();
  for (const game of games) for (const side of ['home','away']) for (const p of game[`${side}Players`]) {
    const key=game[`${side}Id`]+'/'+p.playerId;
    eligibility.set(key,(eligibility.get(key)??0)+1);
  }
  for (const t of league.teams) for (const p of t.roster) assert.equal(eligibility.get(t.id+'/'+p.playerId),p.observed.GP);
  for (const fixture of fixtures) {
    const index=league.schedule.indexOf(fixture),box=games[index];
    const home=lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds);
    const away=lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds);
    const game=simulateGame(home,away,{mode:'timed',seed:box.seed});
    assert.equal(box.id,fixture.id);assert.equal(game.scoreA,box.homeScore);assert.equal(game.scoreB,box.awayScore);
    assert.deepEqual(game.statA,box.homeStats);assert.deepEqual(game.statB,box.awayStats);
    assert.deepEqual(game.playersA.map((p,i)=>({playerId:home.roster[i].playerId,...p})),box.homePlayers);
  }
  console.log('PASS completed 1,230-game artifacts, observed stint availability, source/code hashes and sample full-game reconstruction');
}
console.log('PASS 30 teams / 582 players / 661 stints, neutral sites, defense fields, missing-data flags, rotation budgets, seeded accounting');

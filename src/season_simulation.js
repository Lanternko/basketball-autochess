import {simulateGame} from './simulation_engine.js';

export const SEASON_COUNT_KEYS = ['pts','fga','fgm','fg3a','fg3m','fta','ftm','oreb','dreb','ast','stl','blk','tov','pf','seconds','poss','passes'];
const blank = () => Object.fromEntries(SEASON_COUNT_KEYS.map(k=>[k,0]));
const assert = (ok, message) => {if (!ok) throw new Error(message);};

export function validateSeason(league) {
  assert(league.season==='2025-26', 'Expected 2025-26');
  assert(league.teams.length===30, 'Expected 30 teams');
  const teams = new Map(league.teams.map(t=>[t.id,t]));
  assert(teams.size===30, 'Duplicate team');
  const counts = new Map(league.teams.map(t=>[t.id,{home:0,away:0,neutral:0}]));
  for (const team of league.teams) {
    assert(team.roster.length>=5, `Incomplete roster: ${team.name}`);
    assert(new Set(team.roster.map(p=>p.playerId)).size===team.roster.length, 'Duplicate roster player');
    for (const p of team.roster) {
      for (const key of ['long','mid','short','drive','tovSkill','pass','ft','rebound','onBall','help','stamina','physique','offBall','screen','handle','breakDbl']) {
        assert(Number.isFinite(p[key])&&p[key]>=0&&p[key]<=150, `Invalid ${key}: ${p.name}`);
      }
      assert(Number.isFinite(p.seasonMinutesPerGame)&&p.seasonMinutesPerGame>0, `Invalid rotation weight: ${p.name}`);
    }
  }
  assert(league.schedule.length===1230, 'Expected 1,230 regular-season games');
  const ids = new Set(), playerDates = new Set();
  for (const game of league.schedule) {
    assert(/^00225\d{5}$/.test(game.id)&&!ids.has(game.id), 'Invalid or duplicate regular-season game ID');
    ids.add(game.id);
    assert(/^\d{4}-\d{2}-\d{2}$/.test(game.date), 'Invalid game date');
    assert(game.homeId!==game.awayId && teams.has(game.homeId)&&teams.has(game.awayId), 'Invalid opponents');
    assert(typeof game.neutral==='boolean', 'Missing neutral-site flag');
    for (const side of ['home','away']) {
      const team = teams.get(game[`${side}Id`]), players=game[`${side}PlayerIds`];
      assert(Array.isArray(players)&&players.length>=5&&new Set(players).size===players.length, 'Invalid participant list');
      for (const id of players) {
        assert(team.roster.some(p=>p.playerId===id), `Missing participant card: ${id}`);
        const key=`${game.date}/${id}`;
        assert(!playerDates.has(key), `Player appears for two teams on one date: ${id}`);
        playerDates.add(key);
      }
      counts.get(team.id)[game.neutral?'neutral':side]++;
    }
  }
  for (const [id,c] of counts) {
    assert(c.home+c.away+c.neutral===82, `Expected 82 appearances: ${id}`);
    assert(['home','away','neutral'].every(k=>c[k]===teams.get(id).locationExposure[k]), `Location exposure differs from source: ${id}`);
  }
  return {teams:30,games:1230,teamGames:2460,neutralGames:league.schedule.filter(g=>g.neutral).length,
    playerCards:league.teams.reduce((n,t)=>n+t.roster.length,0),
    uniquePlayers:new Set(league.teams.flatMap(t=>t.roster.map(p=>p.playerId))).size};
}

// Availability comes from observed appearances. Minutes use season averages,
// never this game's observed minutes or score. Caps preserve a 240-minute budget.
export function lineupForGame(team, playerIds) {
  const selected = new Set(playerIds);
  const players = team.roster.filter(p=>selected.has(p.playerId)).map(p=>({...p}));
  assert(players.length===selected.size&&players.length>=5, 'Incomplete game roster');
  players.sort((a,b)=>b.seasonMinutesPerGame-a.seasonMinutesPerGame||a.playerId-b.playerId);
  let low=0, high=240/Math.min(...players.map(p=>p.seasonMinutesPerGame));
  for (let i=0;i<80;i++) {
    const scale=(low+high)/2;
    if (players.reduce((n,p)=>n+Math.min(48,p.seasonMinutesPerGame*scale),0)<240) low=scale;
    else high=scale;
  }
  for (const p of players) p.targetMinutes=Math.min(48,p.seasonMinutesPerGame*(low+high)/2);
  const starters=players.slice(0,5).sort((a,b)=>a.heightInches-b.heightInches||b.pass-a.pass||a.playerId-b.playerId);
  starters.forEach((p,i)=>{p.pos=p.courtPosition=['PG','SG','SF','PF','C'][i];});
  return {...team,roster:[...starters,...players.slice(5)]};
}

export function checkGameAccounting(game) {
  assert(game.complete&&game.winnerA!==null&&game.scoreA!==game.scoreB, 'Unfinished game; refusing to assign a winner');
  assert(game.gameSeconds===2880+game.overtimes*300, 'Incorrect game duration');
  for (const side of ['A','B']) {
    const stat=game[`stat${side}`], players=game[`players${side}`];
    assert(stat.pts===game[`score${side}`], 'Score does not match points');
    assert(stat.pts===2*stat.fgm+stat.fg3m+stat.ftm, 'Scoring identity failed');
    assert(game.periodScores[side==='A'?0:1].reduce((n,x)=>n+x,0)===stat.pts, 'Period scores do not sum');
    for (const key of SEASON_COUNT_KEYS.filter(k=>k!=='poss')) {
      assert(Math.abs(players.reduce((n,p)=>n+p[key],0)-stat[key])<0.11, `Player/team accounting mismatch: ${key}`);
    }
    assert(Math.abs(stat.seconds-5*game.gameSeconds)<0.11, 'Five-player minute budget failed');
  }
}

export function simulateSeason(league, {seed=20261012, onGame=()=>{}, onProgress=()=>{}}={}) {
  const validation=validateSeason(league);
  assert(Number.isSafeInteger(seed)&&seed>=0&&seed<=0xffffffff, 'Invalid season seed');
  const teams=new Map(league.teams.map(t=>[t.id,t]));
  const totals=new Map(league.teams.map(t=>[t.id,{id:t.id,name:t.name,games:0,wins:0,losses:0,homeWins:0,awayWins:0,neutralWins:0,
    homeGames:0,awayGames:0,neutralGames:0,
    pointsFor:0,pointsAgainst:0,stats:blank(),players:t.roster.map(p=>({playerId:p.playerId,name:p.name,
      eligibleGames:0,games:0,stats:blank()}))}]));
  const matches=[];
  for (const [index,fixture] of league.schedule.entries()) {
    const home=lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds);
    const away=lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds);
    const gameSeed=(seed+Math.imul(index+1,7919))>>>0;
    const game=simulateGame(home,away,{mode:'timed',seed:gameSeed,replay:false});
    checkGameAccounting(game);
    for (const [side,team,won,location] of [['A',home,game.winnerA,'home'],['B',away,!game.winnerA,'away']]) {
      const row=totals.get(team.id), stat=game[`stat${side}`];
      row.games++; row.wins+=Number(won); row.losses+=Number(!won);
      const venue=fixture.neutral?'neutral':location;
      row[`${venue}Wins`]+=Number(won);row[`${venue}Games`]++;
      row.pointsFor+=stat.pts;row.pointsAgainst+=game[side==='A'?'scoreB':'scoreA'];
      for (const key of SEASON_COUNT_KEYS) row.stats[key]+=stat[key];
      game[`players${side}`].forEach((p,i)=>{
        const player=row.players.find(r=>r.playerId===team.roster[i].playerId);
        player.eligibleGames++;player.games+=Number(p.seconds>0);
        for (const key of SEASON_COUNT_KEYS) player.stats[key]+=p[key];
      });
    }
    const match={id:fixture.id,date:fixture.date,seed:gameSeed,homeId:home.id,awayId:away.id,neutral:fixture.neutral,
      homeScore:game.scoreA,awayScore:game.scoreB,overtimes:game.overtimes,
      seconds:game.gameSeconds,periodScores:game.periodScores};
    matches.push(match);
    onGame({...match,homeStats:game.statA,awayStats:game.statB,
      homePlayers:game.playersA.map((p,i)=>({playerId:home.roster[i].playerId,...p})),
      awayPlayers:game.playersB.map((p,i)=>({playerId:away.roster[i].playerId,...p}))});
    if ((index+1)%50===0||index===league.schedule.length-1) onProgress(index+1,league.schedule.length);
  }
  const standings=[...totals.values()].sort((a,b)=>b.wins-a.wins||
    (b.pointsFor-b.pointsAgainst)-(a.pointsFor-a.pointsAgainst)||a.id-b.id);
  assert(standings.every(t=>t.games===82&&t.wins+t.losses===82), 'Incomplete team season');
  assert(standings.reduce((n,t)=>n+t.wins,0)===1230&&standings.reduce((n,t)=>n+t.losses,0)===1230, 'League W/L conservation failed');
  assert(standings.reduce((n,t)=>n+t.pointsFor-t.pointsAgainst,0)===0, 'League points conservation failed');
  const players=new Map();
  for (const team of standings) for (const p of team.players) {
    if (!players.has(p.playerId)) players.set(p.playerId,{playerId:p.playerId,name:p.name,games:0,eligibleGames:0,teamIds:[],stats:blank()});
    const total=players.get(p.playerId); total.games+=p.games; total.eligibleGames+=p.eligibleGames;total.teamIds.push(team.id);
    for (const key of SEASON_COUNT_KEYS) total.stats[key]+=p.stats[key];
  }
  for (const key of SEASON_COUNT_KEYS.filter(k=>k!=='poss')) assert(
    Math.abs([...players.values()].reduce((n,p)=>n+p.stats[key],0)-standings.reduce((n,t)=>n+t.stats[key],0))<0.11,
    `Season player/team conservation failed: ${key}`);
  return {schemaVersion:1,season:league.season,seed,validation,
    rules:{mode:'timed',quarterSeconds:720,overtimeSeconds:300,model:'timed-v1-uncalibrated',
      fatigue:'within-game; reset every game',availability:'observed game participants, including zero-minute appearances',
      minutes:'season-in-team MPG normalized to 240, capped at 48; heuristic substitutions',
      homeAdvantage:false,backToBackFatigue:false,standingsTieBreak:'point differential, then team ID; not NBA playoff seeding'},
    standings,players:[...players.values()].sort((a,b)=>b.stats.pts-a.stats.pts||a.playerId-b.playerId),matches};
}

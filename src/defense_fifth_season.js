import {simulateDefenseFifthGame as simulateDefenseGame} from './defense_fifth_game.js';
import {lineupForGame,checkGameAccounting,SEASON_COUNT_KEYS} from './season_simulation.js';
import {thirdLineup as observedLineup} from './defense_third_minutes.js';
import {DEFENSE_COUNT_KEYS} from './defense_probability.js';
import {replayAccounting} from './replay_accounting.js';
import {normalizeSimGame} from './defense_pbp_analysis.js';
import {varianceAnalysis} from './defense_variance_sources.js';
import {read} from '../scripts/defense_io.js';
import {compressDiagnosticGames} from './defense_fifth_diagnostics.js';

export const A_TEAM_KEYS=['teamOreb','teamDreb','deadFtReb','reboundChances','periodMiss','clockCandidates','clockExpectedTouch','clockExpectedLive','offensiveFoulTov','otherViolationTov','passOutTov','handlingOutTov','unmappedDeadTov','madeFoul','missFoul','timeSetup','timePass','timeRelease','timeFlight','timeInbound','timeViolation','timeOther','timingDraws','timingSampleSeconds','timingRawMeanSeconds'];
export const DEFENSE_STATS=[...SEASON_COUNT_KEYS,...DEFENSE_COUNT_KEYS,...A_TEAM_KEYS];
const blank=()=>Object.fromEntries(DEFENSE_STATS.map(k=>[k,0]));
export const boxPossessions=s=>s.fga-s.oreb+s.tov+.44*s.fta;
const pct=(n,d)=>d>0?100*n/d:null;
const sum=(rows,key)=>rows.reduce((n,r)=>n+r[key],0);
export function checkDefenseAccounting(game){
  checkGameAccounting(game);
  for(const side of ['A','B']){
    const s=game['stat'+side],op=game['stat'+(side==='A'?'B':'A')],ps=game['players'+side];
    if(s.liveTov+s.deadTov!==s.tov||s.liveTov!==op.stl||s.stl!==s.passSteals+s.touchSteals||s.tov!==s.clockTov+s.touchTov+op.passSteals)throw new Error('Turnover/steal partition failed');
    if(s.fga!==s.fg3a+s.mida+s.rima||s.fgm!==s.fg3m+s.midm+s.rimm)throw new Error('Shot zone partition failed');
    if(s.blk>op.fga-op.fgm)throw new Error('Blocks exceed opponent misses');
    if(Math.abs(s.regulationSeconds-14400)>.01)throw new Error('Regulation minute budget failed');
    for(const k of DEFENSE_COUNT_KEYS)if(Math.abs(sum(ps,k)-s[k])>.01)throw new Error('Extended accounting failed: '+k);
  }
}
export function defensiveMeasurements(league,baseRows){
  const priorRate=sum(baseRows,'STL')/sum(baseRows,'MIN'),base=new Map(baseRows.map(p=>[p.PLAYER_ID,p]));
  const measured={...league,teams:league.teams.map(t=>({...t,roster:t.roster.map(p=>({...p,
    defenseMeasurement:{steals:base.get(p.playerId).STL,minutes:base.get(p.playerId).MIN},
    offenseMeasurement:{attempts:p.observed.FGA,freeThrows:p.observed.FTA,turnovers:p.observed.TOV,minutes:p.observed.MIN}}))}))};
  return {league:measured,priorRate};
}
export function runDefenseSeason(league,exposure,{seed,options,indices=null,replay=false,audit=false,post41=false,cutoff=41,baseline=null,onProgress=()=>{}}){
  const teams=new Map(league.teams.map(t=>[t.id,t])),games=new Map(exposure.games.map(g=>[g.id,g]));
  const totals=new Map(league.teams.map(t=>[t.id,{id:t.id,name:t.name,games:0,wins:0,stats:blank(),opponent:blank(),
    minuteError:0,regulationMinuteError:0,playerGames:0,overtimes:0,
    players:t.roster.map(p=>({playerId:p.playerId,name:p.name,plusMinus:0,stats:blank()}))}]));
  const wanted=indices?new Set(indices):null,matches=[],normal=[];
  const valid=new Set(read('data/defense-a-source/manifest.json').sources.map(s=>s.id)),order={},counter={};
  for(const g of league.schedule)for(const id of [g.homeId,g.awayId])order[g.id+'/'+id]=counter[id]=(counter[id]??0)+1;
  for(const [index,fixture] of league.schedule.entries()){
    if(wanted&&!wanted.has(index))continue;
    if(post41&&[fixture.homeId,fixture.awayId].every(id=>order[fixture.id+'/'+id]<=cutoff))continue;
    const observed=games.get(fixture.id);if(!observed)throw new Error('Missing official box '+fixture.id);
    const observedTeams=[fixture.homeId,fixture.awayId].map(id=>observed.teams.find(t=>t.teamId===id));
    const controlled=[fixture.homeId,fixture.awayId].map((id,i)=>observedLineup(teams.get(id),fixture[i?'awayPlayerIds':'homePlayerIds'],observedTeams[i],options.seasonMinuteTargets));
    const pair=options.minuteMode==='budget'||options.observedTargets?controlled:[lineupForGame(teams.get(fixture.homeId),fixture.homePlayerIds),lineupForGame(teams.get(fixture.awayId),fixture.awayPlayerIds)];
    const game=simulateDefenseGame(...pair,{...options,seed:(seed+Math.imul(index+1,7919))>>>0,replay:replay||audit});
    checkDefenseAccounting(game);
    if(audit&&valid.has(fixture.id)){const n=normalizeSimGame(game,fixture,pair);n.regulationScore=game.events.find(e=>e.type==='PERIOD_END'&&e.period===4).score;n.box=[game.statA,game.statB].map(s=>({fga:s.fga,fgm:s.fgm,fg3a:s.fg3a,fg3m:s.fg3m,fta:s.fta}));normal.push(n);}
    if(baseline&&(game.scoreA!==baseline.matches[index].homeScore||game.scoreB!==baseline.matches[index].awayScore))throw new Error('Legacy parity failed '+fixture.id);
    const accounting=replay?replayAccounting(game,pair):null;
    for(const [i,side] of ['A','B'].entries()){
      if(post41&&order[fixture.id+'/'+pair[i].id]<=cutoff)continue;
      const row=totals.get(pair[i].id),stats=game['stat'+side],op=game['stat'+(i?'A':'B')];
      row.games++;row.wins+=Number(i?!game.winnerA:game.winnerA);row.overtimes+=game.overtimes;
      for(const k of DEFENSE_STATS){row.stats[k]+=stats[k];row.opponent[k]+=op[k];}
      const targets=new Map(controlled[i].roster.map(p=>[p.playerId,p.targetMinutes*60]));
      const actual=new Map(observedTeams[i].players.map(p=>[p.playerId,p.seconds]));
      game['players'+side].forEach((p,j)=>{
        const id=pair[i].roster[j].playerId,target=targets.get(id),total=row.players.find(p=>p.playerId===id);
        row.minuteError+=Math.abs(p.seconds-actual.get(id))/60;
        row.regulationMinuteError+=Math.abs(p.regulationSeconds-target)/60;row.playerGames++;
        if(options.minuteMode==='budget'&&Math.abs(p.regulationSeconds-target)>.011)throw new Error('Exact regulation exposure failed');
        for(const k of DEFENSE_STATS)total.stats[k]+=p[k];
        if(accounting)total.plusMinus+=accounting.players[i][j].plusMinus;
      });
    }
    matches.push({id:fixture.id,homeId:fixture.homeId,awayId:fixture.awayId,scoreA:game.scoreA,scoreB:game.scoreB,overtimes:game.overtimes});
    if(matches.length%200===0)onProgress(matches.length);
  }
  const {timingCDF,defenseSignals,rotationCurve,...reportedOptions}=options;
  const analysis=audit?varianceAnalysis(normal):null;
  return {seed,options:reportedOptions,teams:[...totals.values()],matches,analysis:analysis?{...analysis,records:undefined}:null,diagnosticGames:compressDiagnosticGames(normal)};
}
export function teamDefenseMetrics(stats,opponent,games=82){
  const paired=(boxPossessions(stats)+boxPossessions(opponent))/2;
  return {ppg:stats.pts/games,opponentPPG:opponent.pts/games,fg:pct(stats.fgm,stats.fga),three:pct(stats.fg3m,stats.fg3a),
    two:pct(stats.fgm-stats.fg3m,stats.fga-stats.fg3a),efg:pct(stats.fgm+.5*stats.fg3m,stats.fga),
    opponentFG:pct(opponent.fgm,opponent.fga),opponentThree:pct(opponent.fg3m,opponent.fg3a),
    opponentTwo:pct(opponent.fgm-opponent.fg3m,opponent.fga-opponent.fg3a),opponentEFG:pct(opponent.fgm+.5*opponent.fg3m,opponent.fga),
    defensiveRatingProxy:100*opponent.pts/paired,offensiveRatingProxy:100*stats.pts/paired,
    possessionsProxy:paired/games,startedPossessions:stats.poss/games,
    steals:stats.stl/games,turnovers:stats.tov/games,forcedTurnovers:opponent.tov/games,
    forcedTOVRate:100*opponent.tov/paired,fta:stats.fta/games,opponentFTR:opponent.fta/opponent.fga,
    defensiveReboundPct:pct(stats.dreb,stats.dreb+opponent.oreb),threeShare:pct(stats.fg3a,stats.fga),
    midShare:pct(stats.mida,stats.fga),rimShare:pct(stats.rima,stats.fga),
    expectedFG:pct(stats.xfgm,stats.fga),expectedThree:pct(stats.x3m,stats.fg3a),
    passSteals:stats.passSteals/games,touchSteals:stats.touchSteals/games,liveTurnovers:stats.liveTov/games,deadTurnovers:stats.deadTov/games,
    clockTurnovers:stats.clockTov/games,touchTurnovers:stats.touchTov/games};
}
export function realCountStats(row,prefix=''){
  return Object.fromEntries(['PTS','FGM','FGA','FG3M','FG3A','FTA','OREB','DREB','TOV','STL','BLK','PF'].map(k=>[k.toLowerCase(),row[prefix+k]]));
}
export function globalDefenseMetrics(run){
  const stats=blank(),op=blank();
  for(const t of run.teams)for(const k of DEFENSE_STATS){stats[k]+=t.stats[k];op[k]+=t.opponent[k];}
  return teamDefenseMetrics(stats,op,run.matches.length*2);
}

import {teamDefenseMetrics,realCountStats} from './defense_validation.js';
import {mean,variance,sd} from './statistical_summary.js';
export {mean,variance,sd};
const cov=(x,y)=>{const mx=mean(x),my=mean(y);return mean(x.map((v,i)=>(v-mx)*(y[i]-my)));};
export const slope=(x,y)=>variance(x)>0?cov(x,y)/variance(x):null;
export function compareMetrics(actual,simulated,{observedCenter=mean(actual),simulatedCenter=mean(simulated)}={}){
  const x=actual,y=simulated,mx=observedCenter,my=simulatedCenter;
  return {simulatedSD:sd(y),observedSD:sd(x),sdRatio:sd(x)>0?sd(y)/sd(x):null,
    correlation:sd(x)*sd(y)>0?cov(x,y)/sd(x)/sd(y):null,slope:slope(x,y),
    centeredMAE:mean(x.map((v,i)=>Math.abs(y[i]-my-(v-mx)))),
    centeredRMSE:Math.sqrt(mean(x.map((v,i)=>(y[i]-my-(v-mx))**2)))};
}
export const SCOREBOARD_KEYS=['net','offensiveRatingProxy','defensiveRatingProxy','opponentTwo','opponentThree',
  'forcedTOVRate','defensiveReboundPct','opponentFTR','possessionsProxy'];
const addStats=rows=>Object.fromEntries(Object.keys(rows[0]).filter(k=>rows.every(r=>Number.isFinite(r[k]))).map(k=>[k,rows.reduce((n,r)=>n+r[k],0)]));
export function teamRows(run){return run.teams.map(t=>({id:t.id,name:t.name,wins:t.wins,...teamDefenseMetrics(t.stats,t.opponent,t.games),net:(t.stats.pts-t.opponent.pts)/t.games}));}
export function gameMetrics(games,rows){
  const nets=new Map(rows.map(t=>[t.id,t.net])),margins=games.map(g=>g.scoreA-g.scoreB);
  const residuals=games.map((g,i)=>margins[i]-(nets.get(g.homeId)-nets.get(g.awayId)));
  return {marginSD:sd(margins),residualSD:sd(residuals),closeShare:mean(margins.map(n=>Number(Math.abs(n)<=5))),
    blowoutShare:mean(margins.map(n=>Number(Math.abs(n)>=20))),winPerNet:slope(rows.map(t=>t.net),rows.map(t=>t.wins))};
}
export function scoreboard(runs,actualTeams,actualStats,actualGames){
  if(!runs.length)throw new Error('Need at least one season');
  for(const run of runs)if(run.matches.length!==1230||run.teams.length!==30||run.teams.some(t=>t.games!==82))throw new Error('Need complete 30 x 82 seasons');
  const bySeed=runs.map(run=>({seed:run.seed,rows:teamRows(run)}));
  const averaged=actualTeams.map(t=>({id:t.id,name:t.name,...Object.fromEntries(['wins',...SCOREBOARD_KEYS].map(k=>[k,
    mean(bySeed.map(run=>run.rows.find(row=>row.id===t.id)[k]))]))}));
  const pooled=addStats(runs.flatMap(run=>run.teams.map(t=>t.stats))),pooledOp=addStats(runs.flatMap(run=>run.teams.map(t=>t.opponent)));
  const simGlobal={...teamDefenseMetrics(pooled,pooledOp,2460*runs.length),net:0};
  const realGlobal={...teamDefenseMetrics(actualStats,actualStats,2460),net:0};
  const metrics=Object.fromEntries(SCOREBOARD_KEYS.map(k=>[k,{...compareMetrics(actualTeams.map(t=>t[k]),averaged.map(t=>t[k]),
    {observedCenter:realGlobal[k],simulatedCenter:simGlobal[k]}),
    simulatedPooled:simGlobal[k],observedPooled:realGlobal[k],bias:simGlobal[k]-realGlobal[k]}]));
  const single=bySeed.map(({seed,rows},i)=>({seed,winMAE:mean(rows.map(t=>Math.abs(t.wins-actualTeams.find(a=>a.id===t.id).wins))),...gameMetrics(runs[i].matches,rows)}));
  return {seeds:runs.map(r=>r.seed),metrics,teams:averaged.map(t=>({...t,observed:actualTeams.find(a=>a.id===t.id),
    offenseCenteredError:(t.offensiveRatingProxy-simGlobal.offensiveRatingProxy)-
      (actualTeams.find(a=>a.id===t.id).offensiveRatingProxy-realGlobal.offensiveRatingProxy)})),
    wins:{expectedMAE:mean(averaged.map(t=>Math.abs(t.wins-actualTeams.find(a=>a.id===t.id).wins))),
      ...compareMetrics(actualTeams.map(t=>t.wins),averaged.map(t=>t.wins)),
      winPerNet:slope(averaged.map(t=>t.net),averaged.map(t=>t.wins)),singleMAERange:[Math.min(...single.map(s=>s.winMAE)),Math.max(...single.map(s=>s.winMAE))]},
    games:{observed:gameMetrics(actualGames,actualTeams),single,range:Object.fromEntries(['marginSD','residualSD','closeShare','blowoutShare','winPerNet'].map(k=>[k,[Math.min(...single.map(s=>s[k])),Math.max(...single.map(s=>s[k]))]]))},
    global:{simulated:simGlobal,observed:realGlobal}};
}
export function actualScoreboardInputs(league,teamBase,teamOpp){
  const actualTeams=teamBase.map(t=>{const o=teamOpp.find(r=>r.TEAM_ID===t.TEAM_ID);return {id:t.TEAM_ID,name:t.TEAM_NAME,wins:t.W,
    ...teamDefenseMetrics(realCountStats(t),realCountStats(o,'OPP_')),net:(t.PTS-o.OPP_PTS)/82};});
  const actualStats=addStats(teamBase.map(t=>realCountStats(t)));
  return {actualTeams,actualStats,actualGames:league.schedule.map(g=>({id:g.id,homeId:g.homeId,awayId:g.awayId,scoreA:g.observed.homeScore,scoreB:g.observed.awayScore}))};
}

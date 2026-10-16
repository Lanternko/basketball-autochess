import {read,table} from '../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats} from './defense_fourth_season.js';
import {compareMetrics,slope,actualScoreboardInputs} from './defense_scoreboard.js';
import {mean,sd} from './statistical_summary.js';
import {makeRng} from './rng.js';
export const metricKeys=['netRMSE','netCorrelation','netSDRatio','residualSD','winMAE','winRMSE','winSlope','defenseCorrelation','defenseSDRatio'];
const sumStats=rows=>Object.fromEntries(Object.keys(rows[0]).filter(k=>rows.every(r=>Number.isFinite(r[k]))).map(k=>[k,rows.reduce((s,r)=>s+r[k],0)]));
export function actualRows(post41=false){
  const league=read('data/season-league.json'),logs=table('data/season-source/team-games.json'),counter={},order={};
  if(!post41){
    const base=table('data/benchmark-source/teams.json'),op=table('data/diagnostic-source/opponents.json'),a=actualScoreboardInputs(league,base,op);
    return {rows:a.actualTeams.map(t=>({...t,games:82,stats:realCountStats(base.find(r=>r.TEAM_ID===t.id)),opponent:realCountStats(op.find(r=>r.TEAM_ID===t.id),'OPP_')})),global:teamDefenseMetrics(a.actualStats,a.actualStats,2460)};
  }
  for(const g of league.schedule)for(const id of [g.homeId,g.awayId])order[g.id+'/'+id]=counter[id]=(counter[id]??0)+1;
  const rows=league.teams.map(t=>{const own=logs.filter(r=>r.TEAM_ID===t.id&&(!post41||order[r.GAME_ID+'/'+t.id]>41)),op=own.map(r=>logs.find(o=>o.GAME_ID===r.GAME_ID&&o.TEAM_ID!==t.id));
    const stats=sumStats(own.map(r=>realCountStats(r))),opponent=sumStats(op.map(r=>realCountStats(r)));return {id:t.id,name:t.name,games:own.length,wins:own.filter(r=>r.WL==='W').length,stats,opponent,...teamDefenseMetrics(stats,opponent,own.length),net:(stats.pts-opponent.pts)/own.length};});
  return {rows,global:teamDefenseMetrics(sumStats(rows.map(r=>r.stats)),sumStats(rows.map(r=>r.opponent)),rows.reduce((s,r)=>s+r.games,0))};
}
export function runRows(run){return run.teams.map(t=>({id:t.id,name:t.name,wins:t.wins,games:t.games,stats:t.stats,opponent:t.opponent,...teamDefenseMetrics(t.stats,t.opponent,t.games),net:(t.stats.pts-t.opponent.pts)/t.games}));}
export function summarize(runs,post41=false,draws=runs.map((_,i)=>i)){
  prepareRuns(runs);
  const actual=actualRows(post41),teams=actual.rows.map(a=>({id:a.id,name:a.name,games:a.games,observed:a,...Object.fromEntries(['wins','net','ppg','opponentPPG','offensiveRatingProxy','defensiveRatingProxy','opponentTwo','opponentThree','forcedTOVRate','defensiveReboundPct','opponentFTR','possessionsProxy'].map(k=>[k,mean(draws.map(i=>runs[i]._byTeam.get(a.id)[k]))]))}));
  const net=compareMetrics(teams.map(t=>t.observed.net),teams.map(t=>t.net)),def=compareMetrics(teams.map(t=>t.observed.defensiveRatingProxy),teams.map(t=>t.defensiveRatingProxy));
  const errors=teams.map(t=>t.wins-t.observed.wins);
  const metrics={netRMSE:net.centeredRMSE,netCorrelation:net.correlation,netSDRatio:net.sdRatio,residualSD:mean(draws.map(i=>runs[i].analysis?.marginResidualSD??0)),winMAE:mean(errors.map(Math.abs)),winRMSE:Math.sqrt(mean(errors.map(v=>v*v))),winSlope:slope(teams.map(t=>t.net),teams.map(t=>t.wins)),defenseCorrelation:def.correlation,defenseSDRatio:def.sdRatio};
  const pooled=sumStats(draws.flatMap(i=>runs[i].teams.map(t=>t.stats))),pooledOp=sumStats(draws.flatMap(i=>runs[i].teams.map(t=>t.opponent))),global=teamDefenseMetrics(pooled,pooledOp,draws.reduce((s,i)=>s+runs[i].teams.reduce((a,t)=>a+t.games,0),0));
  return {metrics,teams,global:{simulated:global,observed:actual.global},details:Object.fromEntries(['net','offensiveRatingProxy','defensiveRatingProxy','opponentTwo','opponentThree','forcedTOVRate','defensiveReboundPct','opponentFTR','possessionsProxy'].map(k=>[k,compareMetrics(teams.map(t=>t.observed[k]),teams.map(t=>t[k]),{observedCenter:k==='net'?0:actual.global[k],simulatedCenter:k==='net'?0:global[k]})]))};
}
const prepared=new WeakSet();
export function prepareRuns(runs){if(!prepared.has(runs)){for(const r of runs){r._rows=runRows(r);r._byTeam=new Map(r._rows.map(t=>[t.id,t]));}prepared.add(runs);}return runs;}
export function comparison(runs,base,post41=false,B=2000){
  prepareRuns(runs);prepareRuns(base);if(runs.some((r,i)=>r.seed!==base[i].seed))throw Error('Unpaired seed order');
  // Bootstrap only vectors; avoid re-reading sources and rebuilding totals per draw.
  const actual=actualRows(post41),truth=actual.rows,measure=(rs,draws)=>{
    const y=truth.map(t=>({net:mean(draws.map(i=>rs[i]._byTeam.get(t.id).net)),wins:mean(draws.map(i=>rs[i]._byTeam.get(t.id).wins)),def:mean(draws.map(i=>rs[i]._byTeam.get(t.id).defensiveRatingProxy))}));
    const n=compareMetrics(truth.map(t=>t.net),y.map(t=>t.net)),d=compareMetrics(truth.map(t=>t.defensiveRatingProxy),y.map(t=>t.def)),e=y.map((t,j)=>t.wins-truth[j].wins);
    return {netRMSE:n.centeredRMSE,netCorrelation:n.correlation,netSDRatio:n.sdRatio,residualSD:mean(draws.map(i=>rs[i].analysis?.marginResidualSD??0)),winMAE:mean(e.map(Math.abs)),winRMSE:Math.sqrt(mean(e.map(v=>v*v))),winSlope:slope(y.map(t=>t.net),y.map(t=>t.wins)),defenseCorrelation:d.correlation,defenseSDRatio:d.sdRatio};};
  const all=runs.map((_,i)=>i),a=measure(runs,all),b=measure(base,all),samples=Object.fromEntries(metricKeys.map(k=>[k,[]])),rng=makeRng(20261112);
  for(let n=0;n<B;n++){const draws=all.map(()=>Math.floor(rng()*all.length)),x=measure(runs,draws),y=measure(base,draws);for(const k of metricKeys)samples[k].push(x[k]-y[k]);}
  return Object.fromEntries(metricKeys.map(k=>{const v=samples[k].sort((a,b)=>a-b);return [k,{estimate:a[k]-b[k],standardError:sd(v),ci95:[v[Math.floor(.025*B)],v[Math.floor(.975*B)]]}];}));
}

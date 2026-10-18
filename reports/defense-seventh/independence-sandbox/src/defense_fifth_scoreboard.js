import {read,table} from '../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats} from './defense_fifth_season.js';
import {compareMetrics,slope} from './defense_scoreboard.js';
import {mean,sd} from './statistical_summary.js';
import {makeRng} from './rng.js';
import {actualRows as frozenTruth} from './defense_fourth_scoreboard.js';
export const metricKeys=['netRMSE','netCorrelation','netSDRatio','calibrationSlope','calibrationError','residualSD','winMAE','winRMSE','winSlope','defenseCorrelation','defenseSDRatio'];
const add=rows=>Object.fromEntries(Object.keys(rows[0]).map(k=>[k,rows.reduce((s,r)=>s+r[k],0)]));
export function actualFifth(k=0){
 const l=read('data/season-league.json'),logs=table('data/season-source/team-games.json'),lookup=new Map(logs.map(r=>[r.GAME_ID+'/'+r.TEAM_ID,r])),order={},count={};
 for(const g of l.schedule)for(const id of [g.homeId,g.awayId])order[g.id+'/'+id]=count[id]=(count[id]??0)+1;
 if(k===0){const a=frozenTruth(false);return {teams:a.rows,global:a.global,order};}
 const teams=l.teams.map(t=>{const fixtures=l.schedule.filter(g=>[g.homeId,g.awayId].includes(t.id)&&order[g.id+'/'+t.id]>k),own=fixtures.map(g=>lookup.get(g.id+'/'+t.id)),op=fixtures.map(g=>lookup.get(g.id+'/'+(g.homeId===t.id?g.awayId:g.homeId))),stats=add(own.map(r=>realCountStats(r))),opponent=add(op.map(r=>realCountStats(r)));return {id:t.id,name:t.name,games:own.length,wins:own.filter(r=>r.WL==='W').length,stats,opponent,...teamDefenseMetrics(stats,opponent,own.length),net:(stats.pts-opponent.pts)/own.length};});
 return {teams,order,global:teamDefenseMetrics(add(teams.map(t=>t.stats)),add(teams.map(t=>t.opponent)),teams.reduce((s,t)=>s+t.games,0))};
}
export function prepare(runs){for(const r of runs)if(!r._fifth)Object.defineProperty(r,'_fifth',{value:new Map(r.teams.map(t=>[t.id,{...t,...teamDefenseMetrics(t.stats,t.opponent,t.games),net:(t.stats.pts-t.opponent.pts)/t.games}]))});return runs;}
export function summarizeFifth(runs,k=0,draws=runs.map((_,i)=>i),truth=actualFifth(k)){
 prepare(runs);const teams=truth.teams.map(t=>({id:t.id,name:t.name,observed:t,...Object.fromEntries(['wins','net','ppg','opponentPPG','defensiveRatingProxy','offensiveRatingProxy','possessionsProxy'].map(key=>[key,mean(draws.map(i=>runs[i]._fifth.get(t.id)[key]))]))}));
 const net=compareMetrics(teams.map(t=>t.observed.net),teams.map(t=>t.net)),def=compareMetrics(teams.map(t=>t.observed.defensiveRatingProxy),teams.map(t=>t.defensiveRatingProxy)),e=teams.map(t=>t.wins-t.observed.wins),cal=slope(teams.map(t=>t.net),teams.map(t=>t.observed.net));
 return {teams,metrics:{netRMSE:net.centeredRMSE,netCorrelation:net.correlation,netSDRatio:net.sdRatio,calibrationSlope:cal,calibrationError:Math.abs(cal-1),residualSD:mean(draws.map(i=>runs[i].analysis?.marginResidualSD??0)),winMAE:mean(e.map(Math.abs)),winRMSE:Math.sqrt(mean(e.map(v=>v*v))),winSlope:slope(teams.map(t=>t.net),teams.map(t=>t.wins)),defenseCorrelation:def.correlation,defenseSDRatio:def.sdRatio},global:{simulated:teamDefenseMetrics(add(draws.flatMap(i=>runs[i].teams.map(t=>t.stats))),add(draws.flatMap(i=>runs[i].teams.map(t=>t.opponent))),draws.reduce((s,i)=>s+runs[i].teams.reduce((a,t)=>a+t.games,0),0)),observed:truth.global}};
}
export function compareFifth(runs,base,k=0,B=2000){
 if(runs.some((r,i)=>r.seed!==base[i].seed))throw Error('Unpaired seeds');prepare(runs);prepare(base);const truth=actualFifth(k),all=runs.map((_,i)=>i),measure=(rs,draws)=>{const t=truth.teams,y=t.map(t=>({net:mean(draws.map(i=>rs[i]._fifth.get(t.id).net)),wins:mean(draws.map(i=>rs[i]._fifth.get(t.id).wins)),def:mean(draws.map(i=>rs[i]._fifth.get(t.id).defensiveRatingProxy))})),n=compareMetrics(t.map(t=>t.net),y.map(t=>t.net)),d=compareMetrics(t.map(t=>t.defensiveRatingProxy),y.map(t=>t.def)),e=y.map((r,i)=>r.wins-t[i].wins),cal=slope(y.map(t=>t.net),t.map(t=>t.net));return {netRMSE:n.centeredRMSE,netCorrelation:n.correlation,netSDRatio:n.sdRatio,calibrationSlope:cal,calibrationError:Math.abs(cal-1),residualSD:mean(draws.map(i=>rs[i].analysis?.marginResidualSD??0)),winMAE:mean(e.map(Math.abs)),winRMSE:Math.sqrt(mean(e.map(v=>v*v))),winSlope:slope(y.map(t=>t.net),y.map(t=>t.wins)),defenseCorrelation:d.correlation,defenseSDRatio:d.sdRatio};};
 const a=measure(runs,all),b=measure(base,all),samples=Object.fromEntries(metricKeys.map(k=>[k,[]])),rng=makeRng(20261202);
 for(let i=0;i<B;i++){const draw=all.map(()=>Math.floor(rng()*all.length)),a=measure(runs,draw),b=measure(base,draw);for(const key of metricKeys)samples[key].push(a[key]-b[key]);}
 return Object.fromEntries(metricKeys.map(key=>{const v=samples[key].sort((a,b)=>a-b);return [key,{estimate:a[key]-b[key],standardError:sd(v),ci95:[v[Math.floor(.025*B)],v[Math.floor(.975*B)]]}];}));
}

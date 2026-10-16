import {table,read} from '../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats} from './defense_sixth_season.js';
import {summarizeFifth,prepare,metricKeys} from './defense_fifth_scoreboard.js';
import {makeRng} from './rng.js';
import {sd} from './statistical_summary.js';
export function calendarTruth(c,phase='post'){
 const league=read(c.leagueFile),logs=table(c.paths['data/season-source/team-games.json']),lookup=new Map(logs.map(r=>[r.GAME_ID+'/'+r.TEAM_ID,r])),sum=rs=>Object.fromEntries(Object.keys(realCountStats(logs[0])).map(k=>[k,rs.reduce((s,r)=>s+(r[k]??0),0)]));
 const teams=league.teams.map(t=>{const gs=league.schedule.filter(g=>[g.homeId,g.awayId].includes(t.id)&&(phase==='train'?g.date<=c.date:g.date>c.date)),own=gs.map(g=>lookup.get(g.id+'/'+t.id)),op=gs.map(g=>lookup.get(g.id+'/'+(g.homeId===t.id?g.awayId:g.homeId))),stats=sum(own.map(r=>realCountStats(r))),opponent=sum(op.map(r=>realCountStats(r)));return {id:t.id,name:t.name,games:gs.length,wins:own.filter(r=>r.WL==='W').length,stats,opponent,...teamDefenseMetrics(stats,opponent,gs.length),net:(stats.pts-opponent.pts)/gs.length};});
 return {teams,global:teamDefenseMetrics(sum(teams.map(t=>t.stats)),sum(teams.map(t=>t.opponent)),teams.reduce((s,t)=>s+t.games,0))};
}
export function pairedCalendar(a,b,truth,B=2000){
 if(a.length!==b.length||a.some((r,i)=>r.seed!==b[i].seed))throw Error('Unpaired seeds');prepare(a);prepare(b);const all=a.map((_,i)=>i),ma=summarizeFifth(a,0,all,truth).metrics,mb=summarizeFifth(b,0,all,truth).metrics,samples=Object.fromEntries(metricKeys.map(k=>[k,[]])),rng=makeRng(20261202);
 for(let n=0;n<B;n++){const draw=all.map(()=>Math.floor(rng()*all.length)),aa=summarizeFifth(a,0,draw,truth).metrics,bb=summarizeFifth(b,0,draw,truth).metrics;for(const k of metricKeys)samples[k].push(aa[k]-bb[k]);}
 return Object.fromEntries(metricKeys.map(k=>{const x=samples[k].sort((a,b)=>a-b);return [k,{estimate:ma[k]-mb[k],standardError:sd(x),ci95:[x[Math.floor(.025*B)],x[Math.floor(.975*B)]]}];}));
}
export function simpleCalendar(c){
 const train=calendarTruth(c,'train'),test=calendarTruth(c),b=read(c.leagueFile),logs=table(c.paths['data/season-source/team-games.json']),lookup=new Map(logs.map(r=>[r.GAME_ID+'/'+r.TEAM_ID,r])),fixtures=b.schedule.filter(g=>g.date<=c.date);
 // One global Pythagorean exponent, estimated by first-half game likelihood.
 const rates=new Map(train.teams.map(t=>[t.id,{pf:t.stats.pts/t.games,pa:t.opponent.pts/t.games}]));let lo=0,hi=40;
 const loss=x=>train.teams.reduce((s,t)=>{const p=1/(1+Math.exp(-x*Math.log(t.stats.pts/t.opponent.pts)));return s-t.wins*Math.log(p)-(t.games-t.wins)*Math.log(1-p);},0);
 for(let i=0;i<70;i++){const a=lo+(hi-lo)/3,z=hi-(hi-lo)/3;if(loss(a)<loss(z))hi=z;else lo=a;}const exponent=(lo+hi)/2;
 const teams=train.teams.map(t=>{const post=test.teams.find(p=>p.id===t.id);return {id:t.id,name:t.name,games:post.games,wins:post.games/(1+(t.opponent.pts/t.stats.pts)**exponent),stats:post.stats,opponent:post.opponent,net:t.net};});
 // Fixed comparator prediction is represented through real-shaped counts with
 // the predicted mean margin; this is evaluation only, never engine input.
 const run={seed:0,teams:teams.map(t=>({...t,stats:{...t.stats,pts:t.opponent.pts+t.net*t.games}}))};prepare([run]);
 return {run,exponent,summary:summarizeFifth([run],0,[0],test),method:'Training mean net margin + Pythagorean expected win probability. Exponent estimated only from pre-calendar training game outcomes. Same future game counts, conditional schedule/rosters; comparator does not adjust opponents.'};
}

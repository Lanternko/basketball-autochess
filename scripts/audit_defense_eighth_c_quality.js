import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {verifyC} from './run_defense_eighth_c_versions.js';
const p=verifyC(),root='reports/defense-eighth/c',result={preregHash:hash(root+'/prereg-supplement.json'),seasons:{},definition:p.quality};
for(const season of [...p.developmentSeasons,...p.blindSeasons]){
 const old=season==='2025-26',league=read(old?'data/season-league.json':`data/defense-seventh/${season}/league.json`),sample=read(old?'reports/defense-b1/defensive-samples.json':`reports/defense-seventh/${season}/stints/defensive-samples.json`),reasons=new Map();
 for(const field of ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames'])for(const x of sample[field]){const id=typeof x==='string'?x:x.id;if(!reasons.has(id))reasons.set(id,{});reasons.get(id)[field]=x;}
 const gp=Object.fromEntries(league.teams.map(t=>[t.id,league.schedule.filter(g=>[g.homeId,g.awayId].includes(t.id)).length]));if(league.schedule.length!==1230||Object.values(gp).some(n=>n!==82))throw Error('Official regular season schedule invariant');
 const failures=league.schedule.filter(g=>reasons.has(g.id)).map(g=>({...g,reasons:reasons.get(g.id)})),strict=league.schedule.length-failures.length;if(strict!==sample.strictUsableGames)throw Error('Strict game union disagrees with audit '+season);
 const byTeam=league.teams.map(t=>({id:t.id,name:t.name,games:gp[t.id],missing:failures.filter(g=>[g.homeId,g.awayId].includes(t.id)).length})),months=[...new Set(league.schedule.map(g=>g.date.slice(0,7)))],byMonth=months.map(month=>({month,total:league.schedule.filter(g=>g.date.startsWith(month)).length,missing:failures.filter(g=>g.date.startsWith(month)).length})),teamMonth=byTeam.map(t=>({id:t.id,name:t.name,months:Object.fromEntries(months.map(m=>[m,failures.filter(g=>g.date.startsWith(m)&&[g.homeId,g.awayId].includes(t.id)).length]))}));
 const tournament=season==='2023-24'?{method:p.quality.inSeasonTournament2023,championship:{id:'0062300001',date:'2023-12-09',inRegularSchedule:league.schedule.some(g=>g.id==='0062300001'),excluded:true},knockoutRegularGames:league.schedule.filter(g=>['2023-12-04','2023-12-05','2023-12-07'].includes(g.date)).map(g=>({id:g.id,date:g.date,homeId:g.homeId,awayId:g.awayId})),regularGameIDs:league.schedule.filter(g=>!g.id.startsWith('002')).map(g=>g.id)}:null;
 if(tournament?.championship.inRegularSchedule)throw Error('Tournament final in regular schedule');
 result.seasons[season]={strictUsableGames:strict,regularGames:1230,strictCoverage:strict/1230,coverageInsufficient:strict/1230<p.quality.strictMinimumCoverage,minuteValidation:sample.minuteValidation,failureCount:failures.length,failures,byTeam,byMonth,teamMonth,tournament,sourceSampleHash:hash(old?'reports/defense-b1/defensive-samples.json':`reports/defense-seventh/${season}/stints/defensive-samples.json`)};
 console.log('C QUALITY',season,strict,strict/1230,result.seasons[season].coverageInsufficient);
}
fs.writeFileSync(root+'/quality.json',JSON.stringify(result,null,2)+'\n');

import fs from 'node:fs';
import {read,table} from '../../../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats} from '../../../src/defense_sixth_season.js';
import {pool,job,root,verify} from './run.mjs';
import {logit} from './model.mjs';
verify();const p=read(root+'/protocol.json'),clip=(v,a,b)=>Math.max(a,Math.min(b,v)),sum=rs=>Object.fromEntries(Object.keys(rs[0]).map(k=>[k,rs.reduce((s,r)=>s+(r[k]??0),0)]));
const jobs=p.seasons.flatMap(season=>['pooled','dreb'].map(version=>({season,version}))),states=jobs.map(({season,version})=>{const base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`,logs=table(base+'/team-games.json'),stats=sum(logs.map(r=>realCountStats(r))),target=teamDefenseMetrics(stats,stats,logs.length);return{season,version,target,orbTarget:stats.oreb/(stats.oreb+stats.dreb),calibration:{shotDelta:0,options:{leagueOrbLogit:0}},history:[],done:fs.existsSync(`${root}/${season}/calibration-${version}.json`)};});
for(let iteration=0;iteration<p.calibration.iterations;iteration++){
 const active=states.filter(s=>!s.done);if(!active.length)break;
 const results=await pool(active.flatMap(s=>p.calibration.seeds.map(seed=>job(s.season,s.version,seed,s.calibration))),{quiet:true});
 for(const s of active){const rs=results.filter(m=>m.job.season===s.season&&m.job.version===s.version).map(m=>m.result),stats=sum(rs.flatMap(r=>r.teams.map(t=>t.stats))),op=sum(rs.flatMap(r=>r.teams.map(t=>t.opponent))),sim=teamDefenseMetrics(stats,op,rs.reduce((n,r)=>n+r.teams.reduce((n,t)=>n+t.games,0),0)),orb=stats.oreb/(stats.oreb+stats.dreb);
 s.history.push({iteration,calibration:structuredClone(s.calibration),sim,orb});console.log('CAL',s.season,s.version,iteration,'eff', (sim.offensiveRatingProxy-s.target.offensiveRatingProxy).toFixed(3),'poss',(sim.possessionsProxy-s.target.possessionsProxy).toFixed(3),'orbpp',((orb-s.orbTarget)*100).toFixed(3));
 const t=p.calibration.tolerances;s.done=Math.abs(sim.offensiveRatingProxy-s.target.offensiveRatingProxy)<t.efficiency&&Math.abs(sim.possessionsProxy-s.target.possessionsProxy)<t.possessions&&Math.abs(orb-s.orbTarget)<t.orebShare;
 if(s.done||iteration===p.calibration.iterations-1){fs.writeFileSync(`${root}/${s.season}/calibration-${s.version}.json`,JSON.stringify({season:s.season,version:s.version,target:s.target,orbTarget:s.orbTarget,converged:s.done,selected:s.history.at(-1).calibration,history:s.history},null,2)+'\n');s.done=true;continue;}
 const b=read(`reports/defense-tenth/step4-t0/${s.season}/bundle.json`),base=job(s.season,s.version,0).baseCalibration,o={...b.options,...base?.options,...s.calibration.options};s.calibration.shotDelta+=clip((s.target.offensiveRatingProxy-sim.offensiveRatingProxy)/65,-.08,.08);s.calibration.options.pace=clip(o.pace*s.target.possessionsProxy/sim.possessionsProxy,.5,2);s.calibration.options.leagueOrbLogit+=clip(logit(s.orbTarget)-logit(orb),-.25,.25);
 }
}

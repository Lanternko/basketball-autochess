import fs from 'node:fs';
import {read,table} from '../../../scripts/defense_io.js';
import {teamDefenseMetrics,realCountStats} from '../../../src/defense_sixth_season.js';
import {pool} from './run.mjs';
const d='reports/defense-tenth/step4-t0',season=process.argv[2],root=d+'/'+season,c=read(root+'/config.json'),bundle=read(root+'/bundle.json'),logs=table(c.paths['data/season-source/team-games.json']);
const sum=rs=>Object.fromEntries(Object.keys(rs[0]).map(z=>[z,rs.reduce((s,r)=>s+(r[z]??0),0)])),stats=sum(logs.map(r=>realCountStats(r))),target=teamDefenseMetrics(stats,stats,logs.length),groups=bundle.measured.turnoverGroups,n=2*c.trainGames.length;
const targets={passSteals:(groups.passing?.live??0)/n,touchSteals:Object.entries(groups).filter(([k])=>k!=='passing').reduce((s,[k,g])=>s+g.live,0)/n,clock:(groups.shotClock?.count??0)/n};
let calibration={shotDelta:0,options:{}},history=[];const seeds=[20260101,20260102,20260103];
for(let iteration=0;iteration<5;iteration++){
 const raw=await pool(seeds.map(seed=>({season,version:'v3',seed,bundle:root+'/bundle.json',calibration})),{workers:3,quiet:true});const rs=raw.map(m=>m.result),ss=sum(rs.flatMap(r=>r.teams.map(t=>t.stats))),op=sum(rs.flatMap(r=>r.teams.map(t=>t.opponent))),sim=teamDefenseMetrics(ss,op,rs.reduce((s,r)=>s+r.teams.reduce((s,t)=>s+t.games,0),0));history.push({iteration,calibration:structuredClone(calibration),sim,target,targets});console.log('CAL',season,iteration,sim.offensiveRatingProxy,sim.possessionsProxy,sim.turnovers);
 if(Math.abs(sim.offensiveRatingProxy-target.offensiveRatingProxy)<.12&&Math.abs(sim.possessionsProxy-target.possessionsProxy)<.15&&Math.abs(sim.opponentFTR-target.opponentFTR)<.002&&Math.abs(sim.turnovers-target.turnovers)<.15)break;
 const o={...bundle.options,...calibration.options},clip=(x,a,b)=>Math.max(a,Math.min(b,x));calibration.shotDelta+=clip((target.offensiveRatingProxy-sim.offensiveRatingProxy)/65,-.08,.08);
 calibration.options.pace=clip(o.pace*target.possessionsProxy/sim.possessionsProxy,.5,2);calibration.options.foulScale=clip(o.foulScale*target.opponentFTR/sim.opponentFTR,.1,3);calibration.options.passTurnoverScale=clip(o.passTurnoverScale*targets.passSteals/Math.max(.01,sim.passSteals),.1,5);
 calibration.options.touchTurnoverScale=clip(o.touchTurnoverScale*(target.turnovers-targets.passSteals-targets.clock)/Math.max(.01,sim.touchTurnovers),.1,5);calibration.options.touchLiveShare=clip(o.touchLiveShare*targets.touchSteals/Math.max(.01,sim.touchSteals),.01,.99);calibration.options.clockViolationProbability=clip(o.clockViolationProbability*targets.clock/Math.max(.01,sim.clockTurnovers),0,.2);
}
fs.writeFileSync(root+'/calibration-v3.json',JSON.stringify({season,seeds,selected:history.at(-1).calibration,history,method:'Preregistered existing fifth/seventh pooled league moment updates, actual soft-minute full season; last evaluated point, no net/rank objective.'},null,2)+'\n');

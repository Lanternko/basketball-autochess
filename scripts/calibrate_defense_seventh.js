import fs from 'node:fs';
import {read,table} from './defense_io.js';
import {runSeventh} from './run_defense_seventh.js';
import {teamDefenseMetrics,realCountStats} from '../src/defense_sixth_season.js';
const root='reports/defense-seventh',k=Number(process.argv[2]),label=process.argv[3]??'forward',seeds=[20260101,20260102,20260103];
const train=new Set(read(`${root}/model-pre${k}-forward.json`).trainGames),logs=table('data/season-source/team-games.json').filter(r=>train.has(r.GAME_ID)),league=read('data/season-league.json'),indices=league.schedule.flatMap((g,i)=>train.has(g.id)?[i]:[]);
const sum=rs=>Object.fromEntries(Object.keys(realCountStats(logs[0])).map(z=>[z,rs.reduce((s,r)=>s+(r[z]??0),0)])),stats=sum(logs.map(r=>realCountStats(r))),target=teamDefenseMetrics(stats,stats,logs.length),c={shotDelta:0,options:{}},history=[];
for(let i=0;i<5;i++){
 const runs=await runSeventh(`cal-${label}-${k}-${i}`,{cutoff:k,phase:'train',indices,cardFile:`${root}/pre${k}-${label}-league.json`,calibration:c},seeds),ss=sum(runs.flatMap(r=>r.teams.map(t=>t.stats))),op=sum(runs.flatMap(r=>r.teams.map(t=>t.opponent))),sim=teamDefenseMetrics(ss,op,runs.reduce((s,r)=>s+r.teams.reduce((s,t)=>s+t.games,0),0));history.push({iteration:i,calibration:structuredClone(c),sim,target});
 if(Math.abs(sim.offensiveRatingProxy-target.offensiveRatingProxy)<.12&&Math.abs(sim.possessionsProxy-target.possessionsProxy)<.15)break;
 c.shotDelta+=Math.max(-.08,Math.min(.08,(target.offensiveRatingProxy-sim.offensiveRatingProxy)/65));
 c.options.pace=(c.options.pace??runs[0].options.pace)*target.possessionsProxy/sim.possessionsProxy;
}
// Last evaluated configuration, never the untested update after the final loop.
const selected=history.at(-1).calibration;
fs.writeFileSync(`${root}/calibration-pre${k}-${label}.json`,JSON.stringify({k,label,seeds,trainingGames:[...train],target,history,selected,method:'Three fixed training-only Monte Carlo seeds, at most five evaluated iterations. Global shooting logit correction and global pace only; no team adjustment. Step efficiency error/65 bounded ±0.08, pace multiplied by observed/simulated pooled possessions. Stop at training |efficiency|<0.12 and |possession|<0.15; retain last evaluated configuration.'},null,2)+'\n');console.log('CALIBRATED',k,label,JSON.stringify(selected));

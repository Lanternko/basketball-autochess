import {parentPort} from 'node:worker_threads';
import {clockInputs} from '../src/defense_clock_jobs.js';
import {thirdOptions} from '../src/defense_third_jobs.js';
import {thirdLineup} from '../src/defense_third_minutes.js';
import {simulateDefenseThirdGame} from '../src/defense_third_game.js';
import {normalizeSimGame} from '../src/defense_pbp_analysis.js';
import {varianceAnalysis} from '../src/defense_variance_sources.js';
import {variance} from '../src/statistical_summary.js';
import {read} from './defense_io.js';
const {inputs}=clockInputs(),teams=new Map(inputs.league.teams.map(t=>[t.id,t])),boxes=new Map(inputs.exposure.games.map(g=>[g.id,g]));
const valid=new Set(read('data/defense-a-source/manifest.json').sources.map(s=>s.id));
parentPort.on('message',({index,job})=>{try{
  const options=thirdOptions(job.preset,job.options??{}),games=[],counts={},own=[];
  for(const [i,f] of inputs.league.schedule.entries()){
    if(!valid.has(f.id))continue;
    const b=boxes.get(f.id),pair=[f.homeId,f.awayId].map((id,j)=>thirdLineup(teams.get(id),f[j?'awayPlayerIds':'homePlayerIds'],b.teams.find(t=>t.teamId===id)));
    const g=simulateDefenseThirdGame(...pair,{...options,replay:true,seed:(job.seed+Math.imul(i+1,7919))>>>0});
    const n=normalizeSimGame(g,f,pair);games.push(n);
    for(const p of n.possessions)if(p.period<=4){counts[p.points]=(counts[p.points]??0)+1;own.push(p.points);}
  }
  const v=varianceAnalysis(games);parentPort.postMessage({index,result:{seed:job.seed,preset:job.preset,counts,pointsVariance:variance(own),analysis:{...v,records:undefined}}});
}catch(e){parentPort.postMessage({index,error:e.stack});}});

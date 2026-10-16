import {parentPort} from 'node:worker_threads';
import {read} from './defense_io.js';
import {inputN,counterfactualN,pairN,analyticN} from '../src/defense_ninth_rosters.js';
import {runDefenseSeason} from '../src/defense_seventh_season.js';
let cachedKey,base,analytic;
parentPort.on('message',({index,job})=>{try{
 const key=job.configFile+'/'+job.version;if(key!==cachedKey){base=inputN(read(job.configFile),job.version);analytic=job.version==='v3'?analyticN(base):null;cachedKey=key;}
 const ctrl=counterfactualN(base,job.seed),indices=base.league.schedule.flatMap((g,i)=>g.date>base.config.date?[i]:[]);
 const run=runDefenseSeason(ctrl.league,ctrl.exposure,{seed:job.seed,options:ctrl.options,indices,audit:false,replay:false});
 const ds=analytic?indices.map(i=>{const f=base.league.schedule[i],a=pairN(base,f,i,job.seed),b=pairN(base,f,i,job.seed,true);return {id:f.id,homeId:f.homeId,awayId:f.awayId,seg:analytic.seg(a)-analytic.seg(b),naive:analytic.naive(a)-analytic.naive(b)};}):null;
 parentPort.postMessage({index,result:{seed:job.seed,teams:run.teams.map(t=>({id:t.id,name:t.name,games:t.games,net:(t.stats.pts-t.opponent.pts)/t.games})),matches:run.matches,analytic:ds,analyticAudit:analytic?{missing:[...analytic.missing],poss:analytic.poss}:null}});
}catch(e){parentPort.postMessage({index,error:e.stack});}});

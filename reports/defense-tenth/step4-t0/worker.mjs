import {parentPort} from 'node:worker_threads';
import {read} from '../../../scripts/defense_io.js';
import {runDefenseSeason} from '../../../src/defense_fourth_season.js';
import * as M from '../../../src/probability_model.js';
import * as C from '../../../src/constants.js';
import {inverse} from '../../../scripts/export_defense_sixth_cards.js';
parentPort.on('message',j=>{try{
 const b=structuredClone(read(j.bundle));
 if(j.calibration){const c=j.calibration;b.options={...b.options,...c.options};for(const t of b.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(c.shotDelta??0))),curve)));}}
 b.options.seasonMinuteTargets=false;b.options.neutralContests=false;
 if(j.version==='pure'){for(const z of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[z]=false;delete b.options.defenseSignals;}
 const r=runDefenseSeason(b.league,b.exposure,{seed:j.seed,options:b.options,audit:false,replay:false});
 parentPort.postMessage({job:j,result:r});
 }catch(e){parentPort.postMessage({job:j,error:e.stack});}});

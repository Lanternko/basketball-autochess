import fs from 'node:fs';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {inverse} from '../../scripts/export_defense_sixth_cards.js';
import {attachBoxAllocationMeasurements} from '../../src/individual_box_allocation.js';
const read=f=>JSON.parse(fs.readFileSync(f));
export function loadInput(season){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`);
 const project=c=>{if(!c)return;b.options={...b.options,...c.options};for(const t of b.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){
  const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));
  p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(c.shotDelta??0))),curve)));
 }};
 if(season!=='2025-26')project(read(`reports/defense-tenth/step4-t0/${season}/calibration-v3.json`).selected);
 project(read(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`).selected);
 Object.assign(b.options,{seasonMinuteTargets:false,neutralContests:false,individualOrebCard:true,individualOrebAllocation:true,putbackTiming:true,putbackCDF:read('reports/defense-tenth/step4-rebounds-putback-time/putback-cdf.json').cdf,clockRecalibration:true,splitTurnoverTiming:true,pace:read(`reports/defense-tenth/step4-rebounds-turnover-time/${season}/calibration.json`).selected.pace});
 for(const k of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[k]=false;delete b.options.defenseSignals;
 b.options.timingCDF={...b.options.timingCDF,...read(`reports/defense-tenth/step4-rebounds-turnover-time/${season}/turnover-cdf.json`).states};
 const orebs=read(`reports/defense-tenth/step4-rebounds-oreb/${season}/cards.json`).players,roles=read(`reports/player-impact-v1/${season}-cards.json`).cards;
 attachBoxAllocationMeasurements(b.league);
 for(const t of b.league.teams)for(const p of t.roster){p.individualOreb=orebs[p.playerId];p.offenseMeasurement={...p.offenseMeasurement,assists:p.observed.AST};p.shotCreationMeasurement=roles[p.playerId];if(!p.shotCreationMeasurement)throw Error('Missing measured creation role');}
 return b;
}

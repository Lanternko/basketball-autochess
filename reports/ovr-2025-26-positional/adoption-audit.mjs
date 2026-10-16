import fs from 'node:fs';
import assert from 'node:assert/strict';
import {inputs} from '../ovr-2025-26-latest/runtime.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {inverse} from '../../scripts/export_defense_sixth_cards.js';
const read=f=>JSON.parse(fs.readFileSync(f));
const root='reports/ovr-2025-26-positional',b=read('reports/defense-tenth/step4-t0/2025-26/bundle.json');
const cal=read('reports/defense-tenth/step4-rebounds-oreb/2025-26/calibration-oreb.json').selected;
const clock=read('reports/defense-tenth/step4-rebounds-turnover-time/2025-26/calibration.json').selected;
const orebs=read('reports/defense-tenth/step4-rebounds-oreb/2025-26/cards.json').players;
const x=inputs(),ps=new Map(x.players.map(p=>[p.playerId,p]));let cards=0;
// Independently replay the current season worker's card projection, rather than
// comparing OVR's own inputs with themselves. Team-stint volume is intentionally
// not identical to the candidate's full-season merged volume.
for(const t of b.league.teams)for(const raw of t.roster){
  const p=structuredClone(raw);
  for(const z of ['long','mid','short']){
    const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z];
    const v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));
    p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(cal.shotDelta??0))),curve)));
  }
  const candidate=ps.get(p.playerId);
  for(const k of ATTRIBUTES)assert.equal(candidate[k],p[k],`${p.playerId} ${k}`);
  assert.deepEqual(candidate.defenseMeasurement,p.defenseMeasurement);
  assert.deepEqual(candidate.individualOreb,orebs[p.playerId]);cards++;
}
const eventOptions={...b.options,...cal.options};
delete eventOptions.defenseSignals;
for(const k of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])eventOptions[k]=false;
Object.assign(eventOptions,{seasonMinuteTargets:false,neutralContests:false,individualOrebCard:true,individualOrebAllocation:true,
  putbackTiming:true,putbackCDF:read('reports/defense-tenth/step4-rebounds-putback-time/putback-cdf.json').cdf,
  clockRecalibration:true,splitTurnoverTiming:true,pace:clock.pace});
eventOptions.timingCDF={...eventOptions.timingCDF,...read('reports/defense-tenth/step4-rebounds-turnover-time/2025-26/turnover-cdf.json').states};
const expectedDifferences=['observedTargets','excludeZeroTargets','rotationCurve'];
for(const [k,v]of Object.entries(eventOptions))if(!expectedDifferences.includes(k))assert.deepEqual(x.options[k],v,k);
const result={passed:true,playerTeamStintCardsCompared:cards,uniquePlayers:ps.size,
  attributesCompared:ATTRIBUTES,cardProjectionSameAsAdoptedSeasonWorker:true,eventOptionsMatch:true,
  differences:{exposure:'OVR disables rotations, fatigue, observed minute targets and overtime; 14.4 rather than 48 regulation minutes.',
    candidateVolume:'OVR candidate combines team stints into full-season shot/volume inputs.',
    teammates:'Artificial baseline instead of observed NBA game roster.',positions:'Five-slot average in old OVR; modal natural-role position in this diagnostic.'},
  unknownAll70:x.players.every(p=>['offBall','screen','handle','breakDbl'].every(k=>p[k]===70)),
  signalFlags:{oldV3:Object.fromEntries(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].map(k=>[k,b.options[k]])),
    adoptedSeasonAndOvr:Object.fromEntries(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].map(k=>[k,x.options[k]]))},
  explanation:'Same adopted event mechanics and individual attributes; different measurement environment. Old v3 signals differ from the currently adopted pure-card path. No validation of individual transfer is implied.'};
fs.writeFileSync(root+'/adoption-audit.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));

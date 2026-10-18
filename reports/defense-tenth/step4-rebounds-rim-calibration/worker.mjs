import {collector as eventCollector,simEvent} from './collect.mjs';
import crypto from 'node:crypto';
import {experimentalSeason as baselineSeason} from '../step4-rebounds-turnover-time/adapter.mjs';
import {parentPort} from 'node:worker_threads';

import fs from 'node:fs';

import {read} from '../../../scripts/defense_io.js';

import {runDefenseSeason} from '../../../src/defense_fourth_season.js';

import {experimentalSeason} from '../step4-rebounds-rim-clock/adapter.mjs';

import * as M from '../../../src/probability_model.js';

import * as C from '../../../src/constants.js';

import {inverse} from '../../../scripts/export_defense_sixth_cards.js';

const root='reports/defense-tenth/step4-rebounds-turnover-time';

import {simEvents,measure} from '../step4-rebounds-state-time/classify.mjs';

import {simCollector} from '../step4-rebounds-after/classify.mjs';

parentPort.on('message',async j=>{try{

 const b=structuredClone(read(j.bundle));

 const project=c=>{if(!c)return;b.options={...b.options,...c.options};for(const t of b.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(c.shotDelta??0))),curve)));}};

 project(j.baseCalibration);project(j.calibration);

 b.options.seasonMinuteTargets=false;b.options.neutralContests=false;

 for(const k of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[k]=false;

 delete b.options.defenseSignals;

 b.options.individualOrebCard=true;b.options.individualOrebAllocation=true;b.options.putbackTiming=true;b.options.putbackCDF=read('reports/defense-tenth/step4-rebounds-putback-time/putback-cdf.json').cdf;b.options.clockRecalibration=true;b.options.splitTurnoverTiming=j.version!=='off';if(b.options.splitTurnoverTiming)b.options.timingCDF={...b.options.timingCDF,...read(`${root}/${j.season}/turnover-cdf.json`).states};if(b.options.clockRecalibration&&j.clockCalibration)b.options.pace=j.clockCalibration.pace;

 if(b.options.individualOrebCard){const cards=read('reports/defense-tenth/step4-rebounds-oreb/'+j.season+'/cards.json').players;for(const t of b.league.teams)for(const p of t.roster){p.individualOreb=cards[p.playerId];if(!p.individualOreb)throw Error('Missing DREB card '+p.playerId);}}

 const trace={fgOreb:0,ftOreb:0,dreb:0,expectedOldPutback:0,expectedNewPutback:0,selectedPutbackProbability:0};

 b.options.allocationObserver=x=>{if(!x.offensive){trace.dreb++;return;}if(x.freeThrow){trace.ftOreb++;return;}trace.fgOreb++;trace.expectedOldPutback+=x.oldExpected;trace.expectedNewPutback+=x.newExpected;trace.selectedPutbackProbability+=x.selectedExpected;};

 const collector=simCollector(),stateGames=[],events=[];if(j.diagnostic)b.options.eventObserver=e=>{collector.event(e);if(['FGM','FGX','FTM','FTX','FOUL','STEAL','TOV','SHOT_CLOCK','OREB','TEAM_OREB','DREB','TEAM_DREB','PERIOD_START','PERIOD_END'].includes(e.type))events.push(e);if(e.type==='GAME_END'){stateGames.push(measure(simEvents(events)));events.length=0;}};

 const eventCounts=eventCollector();
 b.options.eventObserver=e=>eventCounts.event(simEvent(e));
 b.options.rimContactClock=true;
 b.options.rimContactResolver=(context,rng)=>rng()>=j.pEffective;
 const run=j.baseline?await baselineSeason():await experimentalSeason();

 const r=run(b.league,b.exposure,{seed:j.seed,options:b.options,audit:false,replay:false,indices:j.indices??null});

 r.eventCounts=eventCounts.finish();if(r.eventCounts.length!==r.matches.length)throw Error('Event game alignment failed');
 delete r.options.rimContactResolver;delete r.options.eventObserver;delete r.options.putbackCDF;if(j.diagnostic)r.postOreb=collector.finish();

 delete r.options.allocationObserver;r.allocationTrace=trace;if(j.diagnostic){if(stateGames.length!==r.matches.length||events.length)throw Error('State game count');r.stateTiming=stateGames.map((g,i)=>({...r.matches[i],...g}));}

 if(j.file)fs.writeFileSync(j.file,JSON.stringify(r)+'\n');

 parentPort.postMessage({job:j,result:j.file?{saved:true,games:r.matches.length}:r});

 }catch(e){parentPort.postMessage({job:j,error:e.stack});}});


import {parentPort} from 'node:worker_threads';
import fs from 'node:fs';
import {read} from '../../../scripts/defense_io.js';
import {runDefenseSeason} from '../../../src/defense_fourth_season.js';
import {experimentalSeason} from './adapter.mjs';
import * as M from '../../../src/probability_model.js';
import * as C from '../../../src/constants.js';
import {inverse} from '../../../scripts/export_defense_sixth_cards.js';
const root='reports/defense-tenth/step4-rebounds-oreb';
parentPort.on('message',async j=>{try{
 const b=structuredClone(read(j.bundle));
 const project=c=>{if(!c)return;b.options={...b.options,...c.options};for(const t of b.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(c.shotDelta??0))),curve)));}};
 project(j.baseCalibration);project(j.calibration);
 b.options.seasonMinuteTargets=false;b.options.neutralContests=false;
 for(const k of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[k]=false;
 delete b.options.defenseSignals;
 b.options.individualOrebCard=j.version==='oreb';
 if(b.options.individualOrebCard){const cards=read(root+'/'+j.season+'/cards.json').players;for(const t of b.league.teams)for(const p of t.roster){p.individualOreb=cards[p.playerId];if(!p.individualOreb)throw Error('Missing DREB card '+p.playerId);}}
 const run=j.native?runDefenseSeason:await experimentalSeason();
 const r=run(b.league,b.exposure,{seed:j.seed,options:b.options,audit:false,replay:false,indices:j.indices??null});
 if(j.file)fs.writeFileSync(j.file,JSON.stringify(r)+'\n');
 parentPort.postMessage({job:j,result:r});
 }catch(e){parentPort.postMessage({job:j,error:e.stack});}});

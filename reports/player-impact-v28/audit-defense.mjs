import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v26/input.mjs';
import {interpolate} from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
const root='reports/player-impact-v28',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),output=root+'/defense-curve-audit.json';
if(fs.existsSync(output))throw Error('Preserve audit');
const seasons=[];
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),ps=new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])),rows=[];
 for(const p of ps.values())for(const [zone,key,curve]of [['long','onBall',C.CURVE_DEF_3PT],['short','help',C.CURVE_DEF_RIM]]){
  const m=p.defenseExposureMeasurement[zone];if(m.sourceMissing||!m.attempts||!Number.isFinite(m.rawDifference))continue;
  const sourcePosterior=m.rawDifference*m.attempts/(m.attempts+200),throughCurve=interpolate(p[key],curve),difference=sourcePosterior-throughCurve;
  rows.push({playerId:p.playerId,name:p.name,zone,attribute:p[key],attempts:m.attempts,sourceDifference:m.rawDifference,sourcePosterior,throughCurve,difference,teamZoneDeltaDifference:m.rate*difference/p.defenseExposureMeasurement.leagueAttemptsPerTeamMinute[zone]});
 }
 const mismatches=rows.filter(r=>Math.abs(r.difference)>1e-8);
 seasons.push({season,rows,counts:{withSource:rows.length,mismatch:mismatches.length,absoluteMismatchOver1pp:mismatches.filter(r=>Math.abs(r.difference)>.01).length}});
 console.log(JSON.stringify({season,counts:seasons.at(-1).counts,selected:rows.filter(r=>[1641705,1629011,1630595].includes(r.playerId))}));
}
const files=[root+'/audit-defense.mjs','reports/player-impact-v26/validation-protocol.json',...seasons.map(s=>`reports/player-impact-v20/${s.season}-defense-exposure.json`)];
fs.writeFileSync(output,JSON.stringify({design:'Compare existing 200-attempt-shrunk closest-defender tracking difference against inverse-then-forward defense attributes. No new fit, no on/off or rank inputs. Differences can identify serialization/cap loss, not missing unobserved defensive deterrence.',seasons,hashes:Object.fromEntries(files.map(p=>[p,hash(p)]))},null,2));

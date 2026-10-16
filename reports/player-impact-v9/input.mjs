import fs from 'node:fs';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {loadInput as previousInput} from '../player-impact-v6/input.mjs';
const zones=['long','mid','short'],curves={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT};
export function attachShooting(players,season){
 const cards=JSON.parse(fs.readFileSync(`reports/player-impact-v6/${season}-cards.json`)).cards;
 const prior=Object.fromEntries(zones.map(z=>{let a=0,m=0;for(const p of Object.values(cards)){a+=p.freshShotCounts?.[z+'A']??0;m+=p.freshShotCounts?.[z+'M']??0;}return[z,m/a];}));
 // Retain the old shared league projection; no individual simulation residual
 // is used to change a card. Replace only its lossy empirical-rate round trip.
 let shift=JSON.parse(fs.readFileSync(`reports/defense-tenth/step4-rebounds-oreb/${season}/calibration-oreb.json`)).selected.shotDelta??0;
 if(season!=='2025-26')shift+=JSON.parse(fs.readFileSync(`reports/defense-tenth/step4-t0/${season}/calibration-v3.json`)).selected.shotDelta??0;
 for(const p of players){
  const m=cards[p.playerId];if(!m)throw Error('Missing observed fresh-shot input');
  const rates=Object.fromEntries(zones.map(z=>{const a=m.freshShotCounts?.[z+'A']??0,made=m.freshShotCounts?.[z+'M']??0,q=(made+100*prior[z])/(a+100);return[z,1/(1+Math.exp(-Math.log(q/(1-q))-shift))];}));
  p.shootingMeasurement={rates,sourceBase:Object.fromEntries(zones.map(z=>[z,M.interpolate(p[z],curves[z])])),priorAttempts:100,season};
 }
 return players;
}
export function loadInput(season){const b=previousInput(season);attachShooting(b.league.teams.flatMap(t=>t.roster),season);return b;}

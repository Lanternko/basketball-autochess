import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v46/input.mjs';
import {interpolate} from '../../src/probability_model.js';
import {CURVE_FT} from '../../src/constants.js';
let fit;
export function loadInput(season){
 const b=previousInput(season);fit??=JSON.parse(fs.readFileSync('reports/player-impact-v47/ft-fit.json'));const ref=fit.references[season];if(!ref)throw Error('Missing FT season');
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const m=ref.players[p.playerId];if(!m)throw Error('Missing FT player');
  p.freeThrowAccuracyMeasurement={...m,sourceProbability:Math.max(.30,Math.min(.98,interpolate(p.ft,CURVE_FT))),priorAttempts:fit.kappa,source:'Official same-season FT counts, all FT categories; common count prior chosen on older three seasons, whole-game heldout FT NLL. Display ft attribute preserved.'};
 }
 return b;
}

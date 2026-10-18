import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousMeasurements} from '../player-impact-v14/input.mjs';
import {attachFreeThrowProfilePrior} from '../../src/free_throw_profile_prior.js';
const fit=JSON.parse(fs.readFileSync('reports/player-impact-v16/ftr-prior.json'));
export function attachPrior(players,season){return attachFreeThrowProfilePrior(players,fit.references[season],fit.kappaFga);}
export function loadInput(season){const b=previousInput(season);attachPrior(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousMeasurements(players,season);return attachPrior(players,season);}

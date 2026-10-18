import {ovrInput as previousInput} from '../player-impact-v29/ovr-input.mjs';
import {attachMeasurements} from './input.mjs';
import {attachCreationDependence} from '../../src/source_creation_dependence.js';
export async function ovrInput(season='2025-26'){
 const x=structuredClone(await previousInput(season));attachMeasurements(x.players,season);
 for(const team of x.opponents)attachMeasurements(team.roster,season);
 attachCreationDependence(x.profiles);return x;
}

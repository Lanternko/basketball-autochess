import {ovrInput as previousInput} from '../player-impact-v30/ovr-input.mjs';
import {attachMeasurements} from './input.mjs';
export async function ovrInput(season='2025-26'){
 const x=structuredClone(await previousInput(season));attachMeasurements(x.players,season);
 for(const team of x.opponents)attachMeasurements(team.roster,season);
 return x;
}

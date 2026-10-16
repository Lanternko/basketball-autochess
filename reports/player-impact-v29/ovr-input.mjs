import {ovrInput as previousInput} from '../player-impact-v26/ovr-input.mjs';
import {attachMeasurements} from '../player-impact-v28/input.mjs';
export async function ovrInput(season='2025-26'){
 const x=structuredClone(await previousInput(season));
 attachMeasurements(x.players,season);
 for(const t of x.opponents)attachMeasurements(t.roster,season);
 return x;
}

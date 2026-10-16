// v47 OVR input plus v52 perimeter defense (reports/player-impact-v52/perimeter.mjs).
import {ovrInput as v47Input} from '../ovr-v47-2025-26/input.mjs';
import {applyPerimeter} from '../player-impact-v52/perimeter.mjs';
export async function ovrInput(k, season = '2025-26') {
  return applyPerimeter(await v47Input(season), k);
}

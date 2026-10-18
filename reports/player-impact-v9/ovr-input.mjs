import {ovrInput as previousInput} from '../player-impact-v6/ovr-input.mjs';
import {attachShooting} from './input.mjs';
export function ovrInput(){const x=previousInput();attachShooting(x.players,'2025-26');for(const t of x.opponents)attachShooting(t.roster,'2025-26');return x;}

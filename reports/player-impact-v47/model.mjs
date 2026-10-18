import {terminalDefenseProbabilities as previousTerminal,exposureDefenseProbabilities as previousExposure} from '../player-impact-v45/model.mjs';
import {withMeasuredFreeThrow} from './ft-model.mjs';
export function terminalDefenseProbabilities(handler,...args){return withMeasuredFreeThrow(previousTerminal(handler,...args),handler);}
export function exposureDefenseProbabilities(handler,...args){return withMeasuredFreeThrow(previousExposure(handler,...args),handler);}

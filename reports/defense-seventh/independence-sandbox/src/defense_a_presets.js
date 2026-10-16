import {NBA_DEFENSE_V1} from './defense_presets.js';
export const A_PRESET_NAMES=['a-accounting','a-rebounds','a-accounting-clock','a-rebounds-clock'];
// Experimental candidates only. No A4 variance intervention is adopted here.
export function stageAPreset(name,{rates,clock}){
  if(!A_PRESET_NAMES.includes(name))throw new Error('Unknown A preset');
  const family=name.startsWith('a-rebounds')?'a-rebounds':'a-accounting';
  const pace=name.endsWith('-clock')?clock?.[family]:NBA_DEFENSE_V1.pace;
  if(!Number.isFinite(pace))throw new Error('Need clock calibration for this preset');
  return {...NBA_DEFENSE_V1,reboundAccounting:true,reboundProfile:family==='a-rebounds',reboundRates:rates,pace};
}

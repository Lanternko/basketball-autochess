import {read} from '../scripts/defense_io.js';
export const NBA_DEFENSE_V3_NAME='nba-defense-v3';
export const NBA_DEFENSE_V3=Object.freeze(read('reports/defense-fifth/v3-frozen.json').options);
export const NBA_DEFENSE_V3_HOLDOUT=Object.freeze({...NBA_DEFENSE_V3,...read('reports/defense-fourth/normalization-pre41.json').selected});

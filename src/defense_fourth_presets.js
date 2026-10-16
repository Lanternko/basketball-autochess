// Named clean baseline; earlier presets are imported without modifying them.
import {thirdOptions} from './defense_third_jobs.js';
import {read} from '../scripts/defense_io.js';
export const NBA_DEFENSE_V2=Object.freeze(thirdOptions('combined',{
  ...read('reports/defense-third/calibration-grid.json').selected,
  ...read('reports/defense-fourth/v2-calibration.json').selected,
  relativeFouls:true,continuousTiming:true,
  foulProfileMeans:read('reports/defense-fourth/foul-profile-means.json').full,
}));
export const NBA_DEFENSE_V2_NAME='nba-defense-v2';

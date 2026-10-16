import fs from 'node:fs';
import {loadInput as previousInput,attachCreationRates as previousRates} from '../player-impact-v19/role-input.mjs';
export {attachShooting} from '../player-impact-v9/input.mjs';
export function attachExposure(players,season){
 const source=JSON.parse(fs.readFileSync(`reports/player-impact-v20/${season}-defense-exposure.json`));
 for(const p of players){
  if(!source.cards[p.playerId])throw Error('Missing source contest exposure');
  p.defenseExposureMeasurement={...source.cards[p.playerId],leagueAttemptsPerTeamMinute:source.leagueAttemptsPerTeamMinute};
 }
 return players;
}
export function attachCreationRates(players,season){previousRates(players,season);return attachExposure(players,season);}
export function loadInput(season){const b=previousInput(season);attachExposure(b.league.teams.flatMap(t=>t.roster),season);return b;}

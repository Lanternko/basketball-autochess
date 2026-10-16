import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v30/input.mjs';
const cache=new Map();
function contexts(players,season){
 if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v36/${season}-contexts.json`)));
 for(const p of players){const m=cache.get(season).cards[p.playerId];if(!m)throw Error('Missing source-self context');p.shootingMeasurement={...p.shootingMeasurement,...m};}
 return players;
}
export function loadInput(season){const b=structuredClone(previousInput(season));contexts(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return contexts(players,season);}

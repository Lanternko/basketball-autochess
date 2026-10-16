import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v28/input.mjs';
import {attachCreationDependence} from '../../src/source_creation_dependence.js';
const cache=new Map();
function attach(players,season){
 attachCreationDependence(players);
 if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v30/${season}-contexts.json`)));
 const contexts=cache.get(season);
 for(const p of players){const m=contexts.cards[p.playerId];if(!m)throw Error('Missing new dependence context');p.shootingMeasurement={...p.shootingMeasurement,...m};}
 return players;
}
export function loadInput(season){const b=previousInput(season);attach(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attach(players,season);}

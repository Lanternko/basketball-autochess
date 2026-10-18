import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v23/input.mjs';
const cache=new Map();
export function drebSource(season){if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v24/${season}-dreb-rates.json`)));return cache.get(season);}
export function attachDreb(players,season){
 const src=drebSource(season);for(const p of players){const m=src.cards[p.playerId];if(!m)throw Error('Missing source conditional DREB card');p.drebRecipientMeasurement={...m,source:'Conditional recipient allocation from actual five and individual team-won DREB. Relative within-lineup strength, not causal team rebound effect; disconnected-team scale selected by zero-centered log prior.'};}return players;
}
export function loadInput(season){const b=previousInput(season);attachDreb(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachDreb(players,season);}

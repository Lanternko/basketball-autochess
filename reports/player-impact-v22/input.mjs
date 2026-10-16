import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v21/input.mjs';
const cache=new Map();
export function putbackSource(season){if(!cache.has(season))cache.set(season,{rates:JSON.parse(fs.readFileSync(`reports/player-impact-v22/${season}-putback-rates.json`)),contexts:JSON.parse(fs.readFileSync(`reports/player-impact-v22/${season}-putback-contexts.json`))});return cache.get(season);}
export function attachPutback(players,season){const src=putbackSource(season);for(const p of players){const rate=src.rates.cards[p.playerId],context=src.contexts.cards[p.playerId];if(!rate||!context)throw Error('Missing measured putback card');p.putbackMeasurement={...rate,...context,source:'Strict same-player 0-3-second short FGA after FG-miss OREB proxy. Fitted common attempt prior; source PB-context centering uses attempts, not makes. Not official play-type labels.'};}return players;}
export function loadInput(season){const b=previousInput(season);attachPutback(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachPutback(players,season);}

import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v22/input.mjs';
const cache=new Map();
export function choiceSource(season){if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v23/${season}-choice-rates.json`)));return cache.get(season);}
export function attachChoice(players,season){const src=choiceSource(season);for(const p of players){const m=src.cards[p.playerId];if(!m)throw Error('Missing source putback choice card');p.putbackChoiceMeasurement={...m,source:'MAP style/production tendency: own fast putback FGA per missed-FG OREB, corrected for source-model FGA survival. Not a new physical or dribbling skill. Choice tendency fixed across counterfactual lineups; make/turnover/foul/rebound mechanisms still respond.'};}return players;}
export function loadInput(season){const b=previousInput(season);attachChoice(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachChoice(players,season);}

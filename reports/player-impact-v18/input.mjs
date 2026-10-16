import {attachCreationRates} from './role-input.mjs';
import {attachCreationContext} from '../../src/measured_creation_context.js';
import fs from 'node:fs';
import {loadInput as previousInput,attachShooting} from './role-input.mjs';
export function attachContexts(players,season){const source=JSON.parse(fs.readFileSync(`reports/player-impact-v18/${season}-contexts.json`)),cards=source.cards;attachCreationContext(players,source.contextReference);for(const p of players){if(!cards[p.playerId])throw Error('Missing source context');p.shootingMeasurement={...p.shootingMeasurement,...cards[p.playerId]};}return players;}
export function loadInput(season){const b=previousInput(season);attachContexts(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function attachMeasurements(players,season){attachShooting(players,season);attachCreationRates(players,season);return attachContexts(players,season);}

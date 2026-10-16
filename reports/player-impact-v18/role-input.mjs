import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v9/input.mjs';
import {attachCreationReference} from './creation-reference.mjs';
export {attachShooting} from '../player-impact-v9/input.mjs';
export function attachCreationRates(players,season){return attachCreationReference(players,JSON.parse(fs.readFileSync(`reports/player-impact-v17/${season}-creation-audit.json`)));}
export function loadInput(season){const b=previousInput(season);attachCreationRates(b.league.teams.flatMap(t=>t.roster),season);return b;}

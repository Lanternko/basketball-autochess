import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v20/input.mjs';
const cache=new Map();
export function riskSource(season){if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v21/${season}-terminal-risk.json`)));return cache.get(season);}
export function attachTerminalRisk(players,season){const source=riskSource(season);for(const p of players){const m=source.cards[p.playerId];if(!m)throw Error('Missing terminal source card');p.terminalRiskMeasurement={...m,source:'Strict PBP classified conditional terminal event risk; common event-count prior, live risk normalized for actual source opponent pressure. Production association, not a dribble skill rating.'};}return players;}
export function loadInput(season){const b=previousInput(season);attachTerminalRisk(b.league.teams.flatMap(t=>t.roster),season);b.options.measuredTouchTurnovers=true;return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachTerminalRisk(players,season);}

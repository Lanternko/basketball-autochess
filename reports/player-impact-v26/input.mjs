import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v25/input.mjs';
const cache=new Map();
export function intensitySource(season){if(!cache.has(season))cache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v26/${season}-contact-rates.json`)));return cache.get(season);}
export function attachIntensity(players,season){const src=intensitySource(season);for(const p of players){const r=src.cards[p.playerId];if(!r)throw Error('Missing contact intensity source');p.contactIntensityMeasurement={...r,source:'Source ordinary contacts and terminal events per strict floor minute, Gamma-Poisson source prior. Descriptive role/production, not causal skill.'};}return players;}
export function contactOptions(season){return {measuredOrdinaryContacts:true,unassignedTerminalRate:intensitySource(season).unassignedTerminalRatePerTeamMinute};}
export function loadInput(season){const b=structuredClone(previousInput(season));attachIntensity(b.league.teams.flatMap(t=>t.roster),season);Object.assign(b.options,contactOptions(season));return b;}
export function attachMeasurements(players,season){previousAttach(players,season);return attachIntensity(players,season);}

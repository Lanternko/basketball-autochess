import fs from 'node:fs';
import {loadInput as previousInput,attachMeasurements as previousAttach} from '../player-impact-v26/input.mjs';
import {attachDefenseAnchors} from './defense-input.mjs';
const contextCache=new Map();
function attach(players,season){
 if(!contextCache.has(season))contextCache.set(season,JSON.parse(fs.readFileSync(`reports/player-impact-v28/${season}-contexts.json`)));
 const contexts=contextCache.get(season);attachDefenseAnchors(players);
 for(const p of players){const card=contexts.cards[p.playerId];if(!card)throw Error('Missing rebuilt source context');p.shootingMeasurement={...p.shootingMeasurement,...card};}
 return players;
}
export function loadInput(season,{restore=true}={}){
 const b=structuredClone(previousInput(season));if(restore)attach(b.league.teams.flatMap(t=>t.roster),season);return b;
}
export function attachMeasurements(players,season){previousAttach(players,season);return attach(players,season);}

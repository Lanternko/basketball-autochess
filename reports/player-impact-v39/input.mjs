import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v30/input.mjs';
const read=p=>JSON.parse(fs.readFileSync(p));let fits;
export function attachBlockMeasurements(players,season){
 fits??=read('reports/player-impact-v39/fit.json');const s=fits.seasons.find(s=>s.season===season);if(!s)throw Error('Missing fitted season');
 const hazards=new Map(s.playerIds.map((pid,i)=>[pid,s.playerLogHazards[i]]));
 for(const p of players){if(!hazards.has(p.playerId))throw Error('Missing block hazard');p.blockEventMeasurement={logHazard:hazards.get(p.playerId),zoneLogBase:Object.fromEntries(['long','mid','short'].map((z,i)=>[z,s.zoneLogBase[i]])),sourceOnBall:p.onBall,sourceHelp:p.help,sourcePhysique:p.physique};}
 return players;
}
export function loadInput(season){const x=structuredClone(previousInput(season));attachBlockMeasurements(x.league.teams.flatMap(t=>t.roster),season);return x;}

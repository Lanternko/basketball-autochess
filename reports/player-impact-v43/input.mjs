import fs from 'node:fs';
import {loadSourceInput as previousSource} from '../player-impact-v42/input.mjs';
let fit;
export function loadSourceInput(season){
 const b=previousSource(season);fit??=JSON.parse(fs.readFileSync('reports/player-impact-v43/fit.json'));
 const s=fit.seasons.find(s=>s.season===season),lookup=new Map(s.playerIds.map((id,i)=>[id,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const i=lookup.get(p.playerId);if(i===undefined)throw Error('Missing make-defense player');
  p.freshDefenseMeasurement={...p.freshDefenseMeasurement,logits:Object.fromEntries(s.zones.map(z=>[z.zone,z.defenderLogits[i]])),source:'Fresh recorded-FGA association controlling shooter and five defenders; convex shrinkage family selected on older whole-game folds. Descriptive, not causal.'};
 }
 return b;
}
export function loadInput(season){
 const b=loadSourceInput(season),contexts=JSON.parse(fs.readFileSync(`reports/player-impact-v43/${season}-contexts.json`));
 for(const p of b.league.teams.flatMap(t=>t.roster)){const c=contexts.cards[p.playerId];if(!c)throw Error('Missing source context');p.shootingMeasurement={...p.shootingMeasurement,...c};}
 return b;
}

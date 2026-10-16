import fs from 'node:fs';
import {loadSourceInput as previousSource} from '../player-impact-v41/input.mjs';
let fit;
export function attachChoice(players,season){
 fit??=JSON.parse(fs.readFileSync('reports/player-impact-v42/choice-fit.json'));
 const s=fit.seasons.find(s=>s.season===season),lookup=new Map(s.playerIds.map((id,i)=>[id,i]));
 for(const p of players){
  const i=lookup.get(p.playerId);if(i===undefined)throw Error('Missing shot-choice player');
  p.defensiveChoiceMeasurement={shooter:Object.fromEntries(s.branches.map(b=>[b.branch,b.intercept+b.shooterLogits[i]])),defender:Object.fromEntries(s.branches.map(b=>[b.branch,b.defenderLogits[i]])),source:'Source fresh-FGA zone-choice association controlling shooter and five defenders; not causal intent.'};
 }
 return players;
}
export function loadSourceInput(season){const b=structuredClone(previousSource(season));attachChoice(b.league.teams.flatMap(t=>t.roster),season);return b;}
export function loadInput(season){
 const b=loadSourceInput(season),contexts=JSON.parse(fs.readFileSync(`reports/player-impact-v42/${season}-contexts.json`));
 for(const p of b.league.teams.flatMap(t=>t.roster)){const c=contexts.cards[p.playerId];if(!c)throw Error('Missing new source context');p.shootingMeasurement={...p.shootingMeasurement,...c};}
 return b;
}

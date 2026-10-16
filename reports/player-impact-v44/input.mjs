import fs from 'node:fs';
import {loadSourceInput as previousSource} from '../player-impact-v42/input.mjs';
let fit;
export function loadSourceInput(season){
 const b=previousSource(season);fit??=JSON.parse(fs.readFileSync('reports/player-impact-v41/fit.json'));
 const s=fit.seasons.find(s=>s.season===season),lookup=new Map(s.playerIds.map((id,i)=>[id,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const i=lookup.get(p.playerId);if(i===undefined)throw Error('Missing source shooter');
  p.sourceMakeTransfer={shooterLogits:Object.fromEntries(s.zones.map(z=>[z.zone,z.intercept+z.shooterLogits[i]]))};
 }
 return b;
}
export function loadInput(season){
 const b=loadSourceInput(season),contexts=JSON.parse(fs.readFileSync(`reports/player-impact-v44/${season}-contexts.json`));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const c=contexts.cards[p.playerId];if(!c)throw Error('Missing logit source context');
  p.sourceMakeTransfer={...p.sourceMakeTransfer,contexts:c.contexts};
 }
 return b;
}

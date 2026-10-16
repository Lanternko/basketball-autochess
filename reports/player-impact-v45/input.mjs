import fs from 'node:fs';
import {loadSourceInput as previousSource} from '../player-impact-v42/input.mjs';
let make,choice;
export function loadSourceInput(season){
 const b=previousSource(season);make??=JSON.parse(fs.readFileSync('reports/player-impact-v45/make-fit.json'));choice??=JSON.parse(fs.readFileSync('reports/player-impact-v45/choice-fit.json'));
 const m=make.seasons.find(s=>s.season===season),c=choice.seasons.find(s=>s.season===season),mi=new Map(m.playerIds.map((id,i)=>[id,i])),ci=new Map(c.playerIds.map((id,i)=>[id,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const i=mi.get(p.playerId),j=ci.get(p.playerId);if(i===undefined||j===undefined)throw Error('Missing fine defense player');
  // Replace old baseline coefficients; never stack old and new make defense.
  p.freshDefenseMeasurement={...p.freshDefenseMeasurement,logits:{long:0,mid:0,short:0}};
  p.fineDefenseMeasurement={makeShooter:Object.fromEntries(m.models.map(z=>[z.name,z.intercept+z.shooterLogits[i]])),makeDefender:Object.fromEntries(m.models.map(z=>[z.name,z.defenderLogits[i]])),choiceShooter:Object.fromEntries(c.models.map(z=>[z.name,z.intercept+z.shooterLogits[j]])),choiceDefender:Object.fromEntries(c.models.map(z=>[z.name,z.defenderLogits[j]]))};
 }
 return b;
}
export function loadInput(season){
 const b=loadSourceInput(season),ctx=JSON.parse(fs.readFileSync(`reports/player-impact-v45/${season}-contexts.json`));
 for(const p of b.league.teams.flatMap(t=>t.roster)){const c=ctx.cards[p.playerId];if(!c)throw Error('Missing fine neutral source context');p.fineDefenseMeasurement={...p.fineDefenseMeasurement,contexts:c.contexts};}
 return b;
}

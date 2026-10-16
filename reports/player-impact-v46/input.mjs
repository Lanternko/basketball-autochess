import fs from 'node:fs';
import {loadSourceInput as previousSource,loadInput as previousInput} from '../player-impact-v45/input.mjs';
let fit;
function replacePaint(b,season){
 fit??=JSON.parse(fs.readFileSync('reports/player-impact-v46/make-fit.json'));const s=fit.seasons.find(s=>s.season===season),index=new Map(s.playerIds.map((id,i)=>[id,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const i=index.get(p.playerId);if(i===undefined)throw Error('Missing shared-paint player');
  for(const z of ['ra','paint']){const m=s.models.find(m=>m.name===z);p.fineDefenseMeasurement.makeShooter[z]=m.intercept+m.shooterLogits[i];p.fineDefenseMeasurement.makeDefender[z]=m.defenderLogits[i];}
 }
 return b;
}
export const loadSourceInput=season=>replacePaint(previousSource(season),season);
// v45 neutral contexts depend on raw attributes, source energy/exposure and
// unchanged choice, not fine make coefficients. Reuse the frozen references.
export const loadInput=season=>replacePaint(previousInput(season),season);

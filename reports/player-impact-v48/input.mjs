import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v47/input.mjs';
let fit;
export function loadInput(season){
 const b=previousInput(season);fit??=JSON.parse(fs.readFileSync('reports/player-impact-v48/make-fit.json'));const s=fit.seasons.find(s=>s.season===season),index=new Map(s.playerIds.map((id,i)=>[id,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){
  const i=index.get(p.playerId);if(i===undefined)throw Error('Missing offensive lineup descriptor');
  p.offensiveLineupMeasurement={shooterDelta:Object.fromEntries(s.models.map(m=>[m.name,m.intercept+m.shooterLogits[i]-p.fineDefenseMeasurement.makeShooter[m.name]])),teammateLogits:Object.fromEntries(s.models.map(m=>[m.name,m.teammateLogits[i]])),source:'Joint shooter + other-four-teammate observational fresh two-point make association, frozen defensive offsets; not separately identified causal spacing or off-ball tracking.'};
 }
 return b;
}

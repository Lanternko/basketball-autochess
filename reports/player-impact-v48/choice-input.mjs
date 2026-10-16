import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v47/input.mjs';
let fit;
export function loadInput(season){
 const b=previousInput(season);fit??=JSON.parse(fs.readFileSync('reports/player-impact-v48/choice-fit.json'));const s=fit.seasons.find(s=>s.season===season),index=new Map(s.playerIds.map((pid,i)=>[pid,i]));
 for(const p of b.league.teams.flatMap(t=>t.roster)){const i=index.get(p.playerId);if(i===undefined)throw Error('Missing offensive choice descriptor');p.offensiveChoiceMeasurement={shooterDelta:Object.fromEntries(s.models.map(m=>[m.name,m.intercept+m.shooterLogits[i]-p.fineDefenseMeasurement.choiceShooter[m.name]])),teammateLogits:Object.fromEntries(s.models.map(m=>[m.name,m.teammateLogits[i]])),source:'Conditional fresh two-point choice association with shooter and other four teammates, fixed training-only defender offsets; not causal off-ball tracking.'};}
 return b;
}

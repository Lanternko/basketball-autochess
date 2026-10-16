import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v2/input.mjs';
export function loadInput(season){
 const b=previousInput(season),cards=JSON.parse(fs.readFileSync(`reports/player-impact-v3/${season}-cards.json`)).cards;
 for(const t of b.league.teams)for(const p of t.roster)p.opportunityMeasurement=cards[p.playerId];
 return b;
}

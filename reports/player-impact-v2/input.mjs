import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v1/input.mjs';
export function loadInput(season){
 const b=previousInput(season),risk=JSON.parse(fs.readFileSync(`reports/player-impact-v2/${season}-risk.json`)).cards;
 for(const t of b.league.teams)for(const p of t.roster)p.passingRiskMeasurement=risk[p.playerId];
 return b;
}

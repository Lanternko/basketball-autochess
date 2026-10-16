import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v2/input.mjs';
export function loadInput(season){
 const b=previousInput(season),cards=JSON.parse(fs.readFileSync(`reports/player-impact-v6/${season}-cards.json`)).cards;
 const totals=b.league.teams.flatMap(t=>t.roster).reduce((s,p)=>({fga:s.fga+p.observed.FGA,fta:s.fta+p.observed.FTA,fg3a:s.fg3a+p.observed.FG3A}),{fga:0,fta:0,fg3a:0});
 for(const t of b.league.teams)for(const p of t.roster){
  p.opportunityMeasurement=cards[p.playerId];
  if(!p.shotProfile)p.shotProfile={threeRate:p.observed.FGA?p.observed.FG3A/p.observed.FGA:totals.fg3a/totals.fga,
   freeThrowsPerAttempt:p.observed.FGA?p.observed.FTA/p.observed.FGA:totals.fta/totals.fga,
   source:'Missing exported profile reconstructed from official counts; league prior only with zero observed FGA'};
 }
 return b;
}

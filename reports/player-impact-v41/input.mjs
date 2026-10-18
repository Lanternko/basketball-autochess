import fs from 'node:fs';
import {loadInput as previousInput} from '../player-impact-v39/input.mjs';
const read=f=>JSON.parse(fs.readFileSync(f));let fits;
export function attachFreshDefense(players,season){
 fits??=read('reports/player-impact-v41/fit.json');const s=fits.seasons.find(s=>s.season===season);if(!s)throw Error('Missing source fresh FG defense season');
 const lookup=new Map(s.playerIds.map((pid,i)=>[pid,i]));
 for(const p of players){const index=lookup.get(p.playerId);if(index===undefined)throw Error('Missing fresh FG defense descriptor');p.freshDefenseMeasurement={logits:Object.fromEntries(s.zones.map(z=>[z.zone,z.defenderLogits[index]])),sourceOnBall:p.onBall,sourceHelp:p.help,sourcePhysique:p.physique,source:'Fresh-FGA shooter-adjusted five-defender source association, selected whole-game Gaussian prior. Not pure or causal defensive skill.'};}
 return players;
}
export function loadSourceInput(season){const x=structuredClone(previousInput(season));attachFreshDefense(x.league.teams.flatMap(t=>t.roster),season);return x;}
export function loadInput(season){const x=loadSourceInput(season),contexts=read(`reports/player-impact-v41/${season}-contexts.json`);for(const p of x.league.teams.flatMap(t=>t.roster)){const m=contexts.cards[p.playerId];if(!m)throw Error('Missing new defense source centering');p.shootingMeasurement={...p.shootingMeasurement,...m};}return x;}

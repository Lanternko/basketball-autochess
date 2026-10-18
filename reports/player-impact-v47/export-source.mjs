import fs from 'node:fs';
import {loadInput} from '../player-impact-v46/input.mjs';
import {interpolate} from '../../src/probability_model.js';
import {CURVE_FT} from '../../src/constants.js';
const seasons=JSON.parse(fs.readFileSync('reports/player-impact-v46/protocol.json')).seasons;
const rows=seasons.map(season=>{const b=loadInput(season);return {season,gameIds:b.league.schedule.map(g=>g.id),players:b.league.teams.flatMap(t=>t.roster.map(p=>({playerId:p.playerId,name:p.name,teamId:t.id,ft:p.ft,oldProbability:interpolate(p.ft,CURVE_FT),observed:p.observed})))};});
fs.writeFileSync('reports/player-impact-v47/source-cards.json',JSON.stringify({seasons:rows}));
console.log(JSON.stringify({seasons:rows.length,entries:rows.reduce((s,r)=>s+r.players.length,0)}));

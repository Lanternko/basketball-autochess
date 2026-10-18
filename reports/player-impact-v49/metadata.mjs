import fs from 'node:fs';
import {loadInput} from '../player-impact-v47/input.mjs';
for(const s of JSON.parse(fs.readFileSync('reports/player-impact-v49/protocol.json')).seasons){const b=loadInput(s);fs.writeFileSync(`reports/player-impact-v49/${s}-metadata.json`,JSON.stringify({exposure:b.exposure,teams:b.league.teams.map(t=>({id:t.id,players:t.roster.map(p=>({playerId:p.playerId,name:p.name,pos:p.pos,heightInches:p.heightInches}))}))}));}

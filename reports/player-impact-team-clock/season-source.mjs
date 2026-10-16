import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const url=f=>pathToFileURL(path.resolve(f)).href;
export function teamClockSeasonSource(){
 let s=fs.readFileSync('src/defense_fourth_season.js','utf8');
 const replace=(a,b)=>{if(s.split(a).length!==2)throw Error('Team-only accounting source drift');s=s.replace(a,b);};
 replace("import {lineupForGame,checkGameAccounting,SEASON_COUNT_KEYS} from './season_simulation.js';",`import {lineupForGame,SEASON_COUNT_KEYS} from './season_simulation.js';\nimport {checkTeamClockAccounting as checkGameAccounting} from '${url('src/individual_team_accounting.js')}';`);
 replace("Math.abs(sum(ps,k)-s[k])>.01","Math.abs(sum(ps,k)+(['deadTov','clockTov'].includes(k)?s.clockTov:0)-s[k])>.01");
 return s;
}

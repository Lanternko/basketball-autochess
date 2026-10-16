import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href;
let source=fs.readFileSync('reports/player-impact-v6/engine.mjs','utf8');
const anchor=" const anchor='  const gu=encode(g),s=';";
if(source.split(anchor).length!==2)throw Error('Team clock engine source drift');
const injection=`
 replace("const player=O.lineup[0];record(off,player,'tov');record(off,player,'deadTov');record(off,player,'clockTov');emit('SHOT_CLOCK',off,player,{independent:true});", "const player=null;record(off,player,'tov');record(off,player,'deadTov');record(off,player,'clockTov');emit('SHOT_CLOCK',off,player,{independent:true});");
 replace("record(off,shooter,'tov');record(off,shooter,'deadTov');record(off,shooter,'clockTov');emit('SHOT_CLOCK',off,shooter);", "record(off,null,'tov');record(off,null,'deadTov');record(off,null,'clockTov');emit('SHOT_CLOCK',off,null);");
 const seasonAnchor="fs.readFileSync('src/defense_fourth_season.js','utf8')";
 if(source.split(seasonAnchor).length!==2)throw Error('Team clock season source drift');
 source=source.replace(seasonAnchor,'teamClockSeasonSource()');
 source=${JSON.stringify(`import {teamClockSeasonSource} from '${url('reports/player-impact-team-clock/season-source.mjs')}';\n`)}+source;
`;
source=source.replace(anchor,injection+anchor);
export const impactEngine=(await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'))).impactEngine;

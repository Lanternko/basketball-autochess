import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href,cache=new Map();
export async function impactEngine(version,options={}){
 const key=JSON.stringify([version,options]);if(cache.has(key))return cache.get(key);
 let s=fs.readFileSync('reports/player-impact-v41/engine.mjs','utf8');
 const replace=(a,b)=>{if(s.split(a).length!==2)throw Error('v42 source anchor drift: '+a);s=s.replace(a,b);};
 replace("url('reports/player-impact-v41/model.mjs')","url('reports/player-impact-v42/model.mjs')");
 replace("url('reports/player-impact-v22/model.mjs')","url('reports/player-impact-v44/space-model.mjs')");
 // Observation only: enrich archived FG snapshots without changing RNG or events.
 replace("{type,side,zone:extra.zone,playerId:","{type,side,elapsed:elapsed/10,zone:extra.zone,playerId:");
 const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
 const run=await mod.impactEngine(version,options);cache.set(key,run);return run;
}

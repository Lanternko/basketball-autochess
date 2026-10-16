import fs from 'node:fs';
const cache=new Map();
export async function impactEngine(version,options={}){
 const key=JSON.stringify([version,options]);if(cache.has(key))return cache.get(key);let s=fs.readFileSync('reports/player-impact-v48/engine.mjs','utf8');
 const a="url('reports/player-impact-v48/model.mjs')",b="url('reports/player-impact-v48/choice-model.mjs')";if(s.split(a).length!==2)throw Error('Choice model anchor drift');s=s.replace(a,b);
 const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));const run=await mod.impactEngine(version,options);cache.set(key,run);return run;
}

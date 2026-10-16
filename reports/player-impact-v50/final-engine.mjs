import fs from 'node:fs';
const cache=new Map();
export async function impactEngine(version){
 if(cache.has(version))return cache.get(version);let s=fs.readFileSync('reports/player-impact-v49/engine.mjs','utf8');const a="url('src/measured_rotation.js')",b="url('reports/player-impact-v50/final-rotation.mjs')";if(s.split(a).length!==2)throw Error('Tuning source drift');s=s.replace(a,b);const run=await(await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'))).impactEngine(version);cache.set(version,run);return run;
}

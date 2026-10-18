import fs from 'node:fs';
export async function impactEngine(version,options={}){
 let s=fs.readFileSync('reports/player-impact-v41/engine.mjs','utf8');
 const a='{type,side,zone:extra.zone,playerId:';
 if(s.split(a).length!==2)throw Error('Baseline observer anchor drift');
 s=s.replace(a,'{type,side,elapsed:elapsed/10,zone:extra.zone,playerId:');
 const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));return mod.impactEngine(version,options);
}

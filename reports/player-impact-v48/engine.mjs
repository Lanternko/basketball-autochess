import fs from 'node:fs';
const cache=new Map();
export async function impactEngine(version,options={}){
 const key=JSON.stringify([version,options]);if(cache.has(key))return cache.get(key);
 let s=fs.readFileSync('reports/player-impact-v47/engine.mjs','utf8');
 const replace=(a,b)=>{if(s.split(a).length!==2)throw Error('Offensive lineup adapter anchor drift: '+a);s=s.replace(a,b);};
 replace("url('reports/player-impact-v47/model.mjs')","url('reports/player-impact-v48/model.mjs')");
 const a='contextLongScale:opt.contextLongScale,contextShortScale:opt.contextShortScale},ds,opt);',b='contextLongScale:opt.contextLongScale,contextShortScale:opt.contextShortScale,offensiveLineup:os},ds,opt);';
 replace(' const changes=[',' const changes=[\n'+JSON.stringify([a,b])+',');
 const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
 const run=await mod.impactEngine(version,options);cache.set(key,run);return run;
}

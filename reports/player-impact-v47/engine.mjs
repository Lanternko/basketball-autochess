import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href,cache=new Map();
export async function impactEngine(version,options={}){
 const key=JSON.stringify([version,options]);if(cache.has(key))return cache.get(key);
 let s=fs.readFileSync('reports/player-impact-v45/engine.mjs','utf8');
 const replace=(a,b)=>{if(s.split(a).length!==2)throw Error('FT adapter source anchor drift: '+a);s=s.replace(a,b);};
 replace("url('reports/player-impact-v45/model.mjs')","url('reports/player-impact-v47/model.mjs')");
 const anchor=" const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));";
 const changes=[
  ['clamp(M.interpolate(sides[off].roster[taker].ft,C.CURVE_FT),0.3,0.98)','measuredFreeThrowPercentage(sides[off].roster[taker])'],
  ['clamp(M.interpolate(ls[off][hi].ft,C.CURVE_FT),0.3,0.98)','measuredFreeThrowPercentage(ls[off][hi])'],
  ['sides[off].roster[b].ft-sides[off].roster[a].ft','measuredFreeThrowPercentage(sides[off].roster[b])-measuredFreeThrowPercentage(sides[off].roster[a])'],
 ];
 const gameImport=`g=${JSON.stringify(`import {measuredFreeThrowPercentage} from '${url('reports/player-impact-v47/ft-model.mjs')}';\n`)}+g;`;
 const additions=changes.map(([a,b])=>`replace(${JSON.stringify(a)},${JSON.stringify(b)});`).join('\n')+`\npatches.push(${JSON.stringify(gameImport)});\n`;
 const ftAnchor=" const anchor='  const gu=encode(g),s=';";
 const extra=`const ftAnchor=${JSON.stringify(ftAnchor)};if(s.split(ftAnchor).length!==2)throw Error('FT patches anchor drift');s=s.replace(ftAnchor,${JSON.stringify(additions)}+ftAnchor);\n`;
 replace(anchor,extra+anchor);
 const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
 const run=await mod.impactEngine(version,options);cache.set(key,run);return run;
}

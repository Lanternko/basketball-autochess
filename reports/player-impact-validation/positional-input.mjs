import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const linked=(s,file,map={})=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${map[f]??pathToFileURL(path.resolve(path.dirname(file),f)).href}${q}`);
const cache=new Map();
export async function positionalOvrInput(season){
 if(!['2022-23','2023-24','2024-25','2025-26'].includes(season))throw Error('Unsupported measured season');
 if(cache.has(season))return cache.get(season);
 // Reuse the frozen natural-position/mean70 protocol, changing only the
 // season. Historical cards must include their original pre-OREB projection.
 const runtimeFile='reports/ovr-2025-26-latest/runtime.mjs';
 let runtime=fs.readFileSync(runtimeFile,'utf8').replaceAll('2025-26',season);
 if(season!=='2025-26'){
  const anchor="  const cal=read(";
  const insertion=`  const historical=read('reports/defense-tenth/step4-t0/${season}/calibration-v3.json').selected;
  Object.assign(b.options,historical.options);
  for(const t of b.league.teams)for(const p of t.roster)for(const z of ['long','mid','short']){
   const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));
   p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(historical.shotDelta??0))),curve)));
  }
`;
  if(runtime.split(anchor).length!==2)throw Error('Historical projection anchor drift');runtime=runtime.replace(anchor,insertion+anchor);
 }
 const runtimeURL=encode(linked(runtime,runtimeFile));
 const protocolFile='reports/ovr-2025-26-positional/protocol.mjs';
 const protocol=fs.readFileSync(protocolFile,'utf8').replaceAll('2025-26',season);
 const protocolURL=encode(linked(protocol,protocolFile,{[`../ovr-${season}-latest/runtime.mjs`]:runtimeURL}));
 const inputFile='reports/player-impact-v6/ovr-input.mjs';
 const input=fs.readFileSync(inputFile,'utf8').replaceAll('2025-26',season);
 const inputURL=encode(linked(input,inputFile,{[`../ovr-${season}-positional/protocol.mjs`]:protocolURL}));
 const x=(await import(inputURL)).ovrInput();cache.set(season,x);return x;
}

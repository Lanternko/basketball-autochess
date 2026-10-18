import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const cache=new Map();
export async function candidateSeason(version){
  if(cache.has(version))return cache.get(version);
  if(!['control','creator-touch','pass-credit','creator-and-credit'].includes(version))throw Error('Unknown intervention');
  let source=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
  const edits=[];
  if(version==='creator-touch'||version==='creator-and-credit'){
    edits.push(`const creatorFrom="volumeWeights(ls[off]):M.handlingWeights(ls[off])";
      if(g.split(creatorFrom).length!==2)throw Error('Creator touch anchor drift');
      g=g.replace(creatorFrom,"creationTouchWeights(ls[off]):M.handlingWeights(ls[off])");
      g+='\\nfunction creationTouchWeights(lineup){return lineup.map(p=>{const m=p.offenseMeasurement;if(!(m?.minutes>0)||!(m.assists>=0))throw Error("Missing creator observations");return Math.max(.005,(m.attempts+.44*m.freeThrows+m.turnovers+m.assists)/m.minutes);});}\\n';`);
  }
  if(version==='pass-credit'||version==='creator-and-credit'){
    edits.push(`const from="if(usedAssist && passer!==null && passer!==shooter)record(off,passer,'ast');";
      if(g.split(from).length!==2)throw Error('Assist credit anchor drift');
      g=g.replace(from,"if(passer!==null && passer!==shooter)record(off,passer,'ast');");
      if(g.split('assist:made&&usedAssist?passer:null').length!==2)throw Error('Assist event anchor drift');
      g=g.replace('assist:made&&usedAssist?passer:null','assist:made&&passer!==shooter?passer:null');`);
  }
  const anchor='  const gu=encode(g),s=';
  if(source.split(anchor).length!==2)throw Error('Adopted adapter anchor drift');
  source=source.replace(anchor,edits.join('\n')+'\n'+anchor);
  // The original adapter imports through generated absolute URLs; this module
  // itself has only node built-ins. Its original source remains untouched.
  const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
  const run=await mod.experimentalSeason();cache.set(version,run);return run;
}

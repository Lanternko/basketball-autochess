// node reports/player-impact-v53/luck-demo.mjs   (runs here: base engine only, no research inputs)
// Demo on the base engine: same game flow (dice decide), plus a luck ledger
// luck[side] += (made - p) * points for every FG and FT. Expected margin = margin - (luckA - luckB).
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=new URL('../../src/', import.meta.url).pathname;
let s=fs.readFileSync(root+'simulation_engine.js','utf8');
s=s.replace(/from '\.\/([^']+)'/g,(_,f)=>`from '${pathToFileURL(root+f).href}'`);
const rep=(a,b)=>{if(s.split(a).length!==2)throw Error('anchor '+a);s=s.replace(a,b);};
rep("  if ((x -= p.zone.long) <= 0) return rng() < p.make.long ? 'FG3M' : 'FG3X';\n  if ((x -= p.zone.mid) <= 0) return rng() < p.make.mid ? 'MIDM' : 'MIDX';\n  return rng() < p.make.short ? 'RIMM' : 'RIMX';",
"  const shot=(q,v,m,x)=>{const made=rng()<q;globalThis.__luck[globalThis.__off]+=((made?1:0)-q)*v;return made?m:x;};\n  if ((x -= p.zone.long) <= 0) return shot(p.make.long,3,'FG3M','FG3X');\n  if ((x -= p.zone.mid) <= 0) return shot(p.make.mid,2,'MIDM','MIDX');\n  return shot(p.make.short,2,'RIMM','RIMX');");
rep("      const ev = sampleShot(p, rng);","      globalThis.__off=off; const ev = sampleShot(p, rng);");
rep("          const made = rng() < p.ftPct;","          const made = rng() < p.ftPct; globalThis.__luck[off]+=(made?1:0)-p.ftPct;");
const m=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
const {TEAMS}=await import(pathToFileURL(root+'teams.js').href);
const [A,B]=[TEAMS.OKC,TEAMS.NYK];
const N=3000,act=[],exp=[];
for(let i=0;i<N;i++){
  globalThis.__luck=[0,0];
  const g=m.simulateGame(A,B,{seed:1000+i,possessions:100});
  const margin=g.scoreA-g.scoreB;act.push(margin);exp.push(margin-(globalThis.__luck[0]-globalThis.__luck[1]));
}
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(a.reduce((x,y)=>x+(y-m)**2,0)/(a.length-1));};
console.log(JSON.stringify({games:N,actualMean:mean(act).toFixed(3),expectedMean:mean(exp).toFixed(3),
 meanSE:(sd(act)/Math.sqrt(N)).toFixed(3),actualSD:sd(act).toFixed(2),expectedSD:sd(exp).toFixed(2),
 varianceRatio:(sd(exp)**2/sd(act)**2).toFixed(3),gamesNeededFactor:(sd(act)**2/sd(exp)**2).toFixed(2)}));

import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {read,hash} from '../../../scripts/defense_io.js';
const root='reports/defense-tenth/step4-rebounds-turnover-time',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
let s=fs.readFileSync('src/defense_pbp_analysis.js','utf8');
const anchor="end(e,i,'turnover');";if(s.split(anchor).length!==3)throw Error('Real parser anchor drift');
s=s.replaceAll(anchor,"end(e,i,e.actionType==='turnover'&&e.stealPersonId>0?'liveTurnover':'deadTurnover');");
s=s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${pathToFileURL(path.resolve('src',f)).href}${q}`);
const {normalizeRealGame}=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
const metadata={};
for(const season of p.seasons){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),folder=season==='2025-26'?'data/defense-a-source/pbp':`data/defense-seventh/${season}/pbp`,states={liveTurnover:[],deadTurnover:[]},missing=[],failures=[];let games=0,zero=0;
 for(const f of b.league.schedule){const file=folder+'/'+f.id+'.json';if(!fs.existsSync(file)){missing.push(f.id);continue;}try{
  const g=normalizeRealGame(read(file).data.game.actions,f);if(!g.pointsValid)throw Error('Score accounting failed');games++;
  for(const z of g.segments)if(z.state in states&&z.duration>=0&&z.duration<=60){if(z.duration<.1){zero++;continue;}states[z.state].push(z.duration);}
 }catch(e){failures.push({id:f.id,error:e.message});}}
 for(const v of Object.values(states))v.sort((a,b)=>a-b);
 const combined=Object.values(states).flat().sort((a,b)=>a-b),old=b.options.timingCDF.turnover;
 if(JSON.stringify(combined)!==JSON.stringify(old))throw Error('CDF union differs from frozen turnover: '+season+' '+combined.length+' vs '+old.length);
 fs.mkdirSync(root+'/'+season,{recursive:true});fs.writeFileSync(`${root}/${season}/turnover-cdf.json`,JSON.stringify({season,states})+'\n');
 metadata[season]={games,missing,failures,zeroExcluded:zero,unionExactlyFrozen:true,states:Object.fromEntries(Object.entries(states).map(([k,a])=>[k,{n:a.length,mean:a.reduce((s,v)=>s+v,0)/a.length}]))};console.log('CDF',season,JSON.stringify(metadata[season]));
}
fs.writeFileSync(root+'/cdf-audit.json',JSON.stringify(metadata,null,2)+'\n');

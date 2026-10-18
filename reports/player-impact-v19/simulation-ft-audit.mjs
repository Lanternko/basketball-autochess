import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput as v14} from '../player-impact-v14/input.mjs';
import {loadInput as v18} from '../player-impact-v18/input.mjs';
import {impactEngine} from '../player-impact-v14/engine.mjs';
const root='reports/player-impact-v19';
for(const [version,loadInput]of [['v14',v14],['v18',v18]]){
 const b=loadInput('2025-26'),run=await impactEngine('rotation-space'),counts={},fouls={};let lastFoul=null;
 const increment=(group,key)=>group[key]=(group[key]??0)+1;
 b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=JSON.parse(fs.readFileSync('reports/player-impact-v7/2025-26-center.json')).fullCenter;
 b.options.eventObserver=e=>{
  if(e.type==='FOUL'){lastFoul={kind:e.kind,period:e.period,clock:e.clock};increment(fouls,e.kind);}
  if(['FTM','FTX'].includes(e.type)){const kind=e.technical?'technical':lastFoul?.period===e.period&&lastFoul?.clock===e.clock?lastFoul.kind:'unresolved';increment(counts,kind);}
  if(e.type==='GAME_END'||e.type==='PERIOD_START')lastFoul=null;
 };
 const result=run(b.league,b.exposure,{seed:20261012,options:b.options,audit:false,replay:false});
 const fta=result.teams.reduce((s,t)=>s+t.stats.fta,0),sum=Object.values(counts).reduce((s,x)=>s+x,0);if(fta!==sum)throw Error('FT ledger mismatch');
 const original=JSON.parse(fs.readFileSync(`reports/player-impact-${version}/runs/2025-26-rotation-space-full-20261012.json`));
 if(JSON.stringify(result.matches)!==JSON.stringify(original.matches)||JSON.stringify(result.teams)!==JSON.stringify(original.teams))throw Error('Passive FT observer changed simulation');
 const artifact={version,season:'2025-26',seed:20261012,games:result.matches.length,counts,fouls,fta,sourceShootingFTAPerGame:(counts.shooting+counts.andOne)/(2*result.matches.length),otherFTAPerGame:(fta-counts.shooting-counts.andOne)/(2*result.matches.length),passiveTeamAndMatchParity:true,codeSHA256:crypto.createHash('sha256').update(fs.readFileSync(root+'/simulation-ft-audit.mjs')).digest('hex')};
 fs.writeFileSync(root+'/'+version+'-simulation-ft-audit.json',JSON.stringify(artifact,null,2));console.log(JSON.stringify(artifact));
}

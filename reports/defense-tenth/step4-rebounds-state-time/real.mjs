import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {realEvents,measure} from './classify.mjs';
import {normalizeRealGame} from '../../../src/defense_pbp_analysis.js';
const root='reports/defense-tenth/step4-rebounds-state-time',p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
const out={};
for(const season of p.seasons){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),folder=season==='2025-26'?'data/defense-a-source/pbp':`data/defense-seventh/${season}/pbp`,games=[],missing=[],failures=[],scoreAudit=[];
 for(const f of b.league.schedule){const file=folder+'/'+f.id+'.json';if(!fs.existsSync(file)){missing.push(f.id);continue;}try{
  const a=read(file).data.game.actions,old=normalizeRealGame(a,f),e=realEvents(a,[f.homeId,f.awayId]);
  if(!old.pointsValid)scoreAudit.push({id:f.id,anomalies:old.anomalies});
  games.push({id:f.id,homeId:f.homeId,awayId:f.awayId,...measure(e.events),referenceAudit:e.audit,pointsValid:old.pointsValid});
 }catch(err){failures.push({id:f.id,error:err.stack});}}
 out[season]={games,missing,failures,scoreAudit};console.log('REAL',season,games.length,'score audit failures',scoreAudit.length);
}
fs.writeFileSync(root+'/real.json',JSON.stringify(out)+'\n');

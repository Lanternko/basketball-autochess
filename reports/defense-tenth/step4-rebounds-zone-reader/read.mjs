import fs from 'node:fs';import assert from 'node:assert/strict';
import {read,hash} from '../../../scripts/defense_io.js';
import {normalizeRealGame,realFactorEvent,clockSeconds} from '../../../src/defense_pbp_analysis.js';
import {pathDetails} from '../step4-rebounds-paths/collector.mjs';
import {readZone,oldZone} from './zone.mjs';
const root='reports/defense-tenth/step4-rebounds-zone-reader',p=read(root+'/protocol.json');assert.equal(hash(root+'/protocol.json'),fs.readFileSync(root+'/protocol.sha256','utf8').trim());
const special=e=>/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((e.qualifiers??[]).join(' '));
const real={},audits={},parity=[];
for(const season of p.seasons){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),folder=season==='2025-26'?'data/defense-a-source/pbp':`data/defense-seventh/${season}/pbp`,games=[],failures=[],reasons={},transitions={},changes=[],unknown=[];
 const audit=(e,id)=>{const z=readZone(e);reasons[z.reason]=(reasons[z.reason]??0)+1;transitions[z.old+'->'+z.zone]=(transitions[z.old+'->'+z.zone]??0)+1;const row={id,actionNumber:e.actionNumber,playerId:e.personId,old:z.old,zone:z.zone,reason:z.reason,area:e.area,subType:e.subType,descriptor:e.descriptor,shotDistance:z.distance,geometryFeet:z.geometry};if(z.old!==z.zone)changes.push(row);if(z.zone==='unknown')unknown.push(row);};
 for(const f of b.league.schedule){const id=f.id??f.gameId;try{
  const actions=read(`${folder}/${id}.json`).data.game.actions,refs=new Map(actions.map(e=>[e.actionNumber,e])),n=normalizeRealGame(actions,f,null);
  if(!n.pointsValid){failures.push({id,reason:'score-accounting'});continue;}
  for(const e of actions)if(['2pt','3pt'].includes(e.actionType)&&e.isFieldGoal)audit(e,id);
  const rows=[];for(const pos of n.possessions){const es=actions.slice(pos.startIndex,pos.endIndex+1);if(es.some(e=>e.actionType==='freethrow'&&special(e)))continue;
   const anchors=es.flatMap((e,i)=>{const s=refs.get(e.shotActionNumber);return e.actionType==='rebound'&&e.subType==='offensive'&&e.personId>0&&!(e.qualifiers??[]).includes('team')&&s?.teamId===e.teamId&&s?.period===e.period&&['2pt','3pt'].includes(s?.actionType)&&s.shotResult==='Missed'?[i]:[];});
   for(let k=0;k<anchors.length;k++){let fg=0,ft=0;for(const e of es.slice(anchors[k]+1))if(e.teamId===n.ids[pos.side]){const c=realFactorEvent(e);if(e.actionType==='freethrow')ft+=c.points;else fg+=c.points;}
    const detail=es.slice(anchors[k]+1).flatMap(e=>{
     const own=e.teamId===n.ids[pos.side];
     if(['2pt','3pt'].includes(e.actionType)&&own)return [{kind:'fg',zone:readZone(e).zone,oldZone:oldZone(e),made:e.shotResult==='Made',points:realFactorEvent(e).points,player:e.personId,clock:clockSeconds(e)}];
     if(e.actionType==='freethrow'&&own)return [{kind:'ft'}];
     if(e.actionType==='turnover')return [{kind:'loss',lossKind:e.subType??'turnover'}];
     if(e.actionType==='rebound')return e.subType==='defensive'?[{kind:'loss',lossKind:'DREB'}]:[{kind:'reb',own,team:!e.personId||(e.qualifiers??[]).includes('team'),freeThrow:refs.get(e.shotActionNumber)?.actionType==='freethrow'}];
     if(e.actionType==='foul')return [{kind:'foul'}];return [];
    });const first=detail.find(e=>e.kind==='fg'),reb=es[anchors[k]],seconds=first?clockSeconds(reb)-first.clock:null,same=first?.player===reb.personId,quick=same&&seconds!==null&&seconds>=0&&seconds<=3;
    rows.push({off:pos.side,first:k===0,points:fg+ft,fgPoints:fg,ftPoints:ft,additionalOreb:anchors.length-k-1,...pathDetails(detail),oldQuickProxy:!!quick&&first.oldZone==='short',quickProxy:!!quick&&first.zone==='short',quickUnknown:!!quick&&first.zone==='unknown'});
   }
  }games.push({id,ids:n.ids,rows});
 }catch(e){failures.push({id,reason:e.message});}}
 const prior=read(`reports/defense-tenth/step4-rebounds-paths/real.json`)[season];
 assert.equal(games.length,prior.games.length);let count=0;for(let i=0;i<games.length;i++){assert.equal(games[i].id,prior.games[i].id);assert.equal(games[i].rows.length,prior.games[i].rows.length);for(let j=0;j<games[i].rows.length;j++){const x=games[i].rows[j],y=prior.games[i].rows[j];for(const key of Object.keys(y).filter(k=>!['route','firstFgZone'].includes(k)))assert.deepEqual(x[key],y[key],`${season}/${i}/${j}/${key}`);count++;}}
 real[season]={games,failures};audits[season]={reasons,transitions,allFgChanges:changes,unknown};parity.push({season,games:games.length,anchorRows:count,allUnzonedFieldsIdentical:true});console.log('READ',season,games.length,'rows',count,'changed',changes.length,'unknown',unknown.length);
}
fs.writeFileSync(root+'/real.json',JSON.stringify(real));fs.writeFileSync(root+'/source-audit.json',JSON.stringify(audits));fs.writeFileSync(root+'/parity.json',JSON.stringify(parity,null,2));

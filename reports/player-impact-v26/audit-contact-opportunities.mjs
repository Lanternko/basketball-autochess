import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput,intensitySource} from './input.mjs';
import {contactSource} from '../player-impact-v25/input.mjs';
import {impactEngine} from './audit-engine.mjs';
const root='reports/player-impact-v26',season='2025-26',seed=20261012,read=f=>JSON.parse(fs.readFileSync(f));
const b=loadInput(season),source=contactSource(season),valid=new Set(read(`reports/player-impact-v1/${season}-on-court-truth.json`).gameIds),run=await impactEngine('rotation-space'),cards=source.recipient.cards,rates=intensitySource(season).cards,players={},counts={};
b.options.creationPolicy='rotation-space';b.options.contextLongScale=1;b.options.spaceCenter=read(`reports/player-impact-v7/${season}-center.json`).fullCenter;
b.options.onCourtObserver=e=>{
 if(e.type!=='FOUL'||e.kind!=='nonShooting')return;
 const ids=e.teams[1-e.side].lineup;assert.ok(ids.includes(e.drawnPlayerId));const den=ids.reduce((s,pid)=>s+rates[pid].contactRate,0);
 for(const pid of ids){const p=players[pid]??={opportunities:0,expectedContacts:0,contacts:0};p.opportunities++;p.expectedContacts+=rates[pid].contactRate/den;if(pid===e.drawnPlayerId)p.contacts++;}
};
const result=run(b.league,b.exposure,{seed,options:b.options,audit:false,replay:false,indices:b.league.schedule.flatMap((g,i)=>valid.has(g.id)?[i]:[])}),original=read(`${root}/runs/${season}-rotation-space-strict-${seed}.json`);
assert.deepEqual(result.matches,original.matches);assert.deepEqual(result.teams,original.teams);
const rows=Object.entries(cards).map(([pid,c])=>({playerId:Number(pid),name:source.source.players[pid],sourceOpportunities:c.sourceContactOpportunities,sourceContacts:c.sourceDrawnContacts,sourceV25ConditionalExpectedContacts:c.sourceExpectedContacts,simulated:players[pid]??{opportunities:0,expectedContacts:0,contacts:0}}));
assert.equal(rows.reduce((s,p)=>s+p.simulated.opportunities,0),5*original.contactAudit.counts.nonShooting);assert.equal(rows.reduce((s,p)=>s+p.simulated.contacts,0),original.contactAudit.counts.nonShooting);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),out={season,seed,games:result.matches.length,passiveExactMatchAndTeamParity:true,rows,hashes:Object.fromEntries(['audit-engine.mjs','audit-contact-opportunities.mjs'].map(f=>[root+'/'+f,hash(root+'/'+f)]))};
fs.writeFileSync(root+'/contact-opportunity-audit.json',JSON.stringify(out,null,2));console.log(JSON.stringify({season,games:out.games,selected:rows.filter(p=>[201939,203999,1628983,1629029,1629674].includes(p.playerId))}));

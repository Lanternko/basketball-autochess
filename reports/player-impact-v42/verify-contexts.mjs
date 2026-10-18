import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {loadSourceInput} from './input.mjs';
import {loadSourceInput as oldSource} from '../player-impact-v41/input.mjs';
const read=f=>JSON.parse(fs.readFileSync(f)),root='reports/player-impact-v42',checks=[];
for(const season of read(root+'/protocol.json').seasons){
 const a=read(`reports/player-impact-v41/${season}-contexts.json`),b=read(`${root}/${season}-contexts.json`),old=oldSource(season),next=loadSourceInput(season);
 const attrs=['long','mid','short','offBall','screen','handle','breakDbl','onBall','help','physique'];
 const oldPlayers=old.league.teams.flatMap(t=>t.roster),newPlayers=next.league.teams.flatMap(t=>t.roster);assert.equal(oldPlayers.length,newPlayers.length);
 for(let i=0;i<oldPlayers.length;i++){
  const p=oldPlayers[i],q=newPlayers[i];for(const k of attrs)assert.equal(p[k],q[k]);
  const stripped={...q};delete stripped.defensiveChoiceMeasurement;assert.deepEqual(stripped,p);
 }
 assert.equal(a.stints,b.stints);assert.equal(a.states,b.states);assert.equal(Object.keys(a.cards).length,Object.keys(b.cards).length);
 let maximumChange=0;
 for(const[id,p]of Object.entries(a.cards)){
  const q=b.cards[id];assert.equal(p.strictSeconds,q.strictSeconds);assert.deepEqual(p.sourceZoneAttempts,q.sourceZoneAttempts);assert.equal(p.meanSourceShootingMultiplier,q.meanSourceShootingMultiplier);
  for(const z of ['long','mid','short']){assert.ok(Number.isFinite(q.contexts['rotation-space'][z]));maximumChange=Math.max(maximumChange,Math.abs(q.contexts['rotation-space'][z]-p.contexts['rotation-space'][z]));}
 }
 for(const[file,key]of [[root+'/prepare-contexts.mjs','codeSHA256'],[root+'/choice-fit.json','choiceFitSHA256'],['reports/player-impact-v41/fit.json','freshDefenseFitSHA256']])assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),b.sources[key]);
 checks.push({season,cards:Object.keys(b.cards).length,states:b.states,maximumContextChange:maximumChange,originalAttributesAndDescriptorsUnchanged:true,sourceMinutesEnergyAndAttemptsUnchanged:true});
}
fs.writeFileSync(root+'/context-verification.json',JSON.stringify({passed:true,checks},null,2));console.log(JSON.stringify({passed:true,checks}));

import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
import {ovrInput as oldInput} from '../player-impact-v30/ovr-input.mjs';
import {ovrInput} from './ovr-input.mjs';
const a=structuredClone(await oldInput()),b=await ovrInput();assert.deepEqual(b.profiles,a.profiles);
assert.equal(b.profiles.length,5);assert.equal(new Set(b.profiles.map(p=>p.pos)).size,5);
for(const p of b.profiles)assert.ok(Math.abs(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/ATTRIBUTES.length-70)<1e-9);
for(let i=0;i<a.players.length;i++)for(const k of ATTRIBUTES)assert.equal(a.players[i][k],b.players[i][k]);
assert.equal(b.players.length,582);
const file='reports/player-impact-v34/verify-profiles.mjs';
fs.writeFileSync('reports/player-impact-v34/profile-verification.json',JSON.stringify({passed:true,profiles:5,actualPlayers:582,allProfilesExactlyV30:true,attributeArithmeticMean:70,actualAttributesExactlyV30:true,
 hashes:{[file]:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')}},null,2));
console.log('5 unchanged distinct positional profiles: arithmetic mean70; 582 actual attributes unchanged.');

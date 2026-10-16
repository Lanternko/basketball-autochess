// Diagnostic only. No runtime import or parameter update.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v30/input.mjs';
import {beta} from '../player-impact-v8/model.mjs';
const root='reports/player-impact-v36',file=root+'/passer-choice-inputs.json',sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
if(fs.existsSync(file))throw Error('Preserve diagnostic inputs');
const seasons=['2022-23','2023-24','2024-25','2025-26'],inputs={};
for(const season of seasons){const b=loadInput(season);inputs[season]=Object.fromEntries(b.league.teams.map(t=>[t.id,Object.fromEntries(t.roster.map(p=>[p.playerId,p.opportunityMeasurement.passOpportunityRate]))]));}
const files=[root+'/passer-choice-inputs.mjs',root+'/marked-fit.json','reports/player-impact-v8/assist-fit.json','reports/player-impact-v30/validation-protocol.json'];
const out={scope:'Untransformed source pass prior by team/player, frozen for conditional assister-identity diagnostic. Does not change v36 runtime beta or selfScale.',beta,inputs,hashes:Object.fromEntries(files.map(f=>[f,sha(f)]))};
fs.writeFileSync(file,JSON.stringify(out));console.log(JSON.stringify({seasons:4,beta,runtimeChanged:false}));

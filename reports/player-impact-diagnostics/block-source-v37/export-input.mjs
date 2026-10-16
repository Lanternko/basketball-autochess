import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../../player-impact-v30/input.mjs';
const f='reports/player-impact-diagnostics/block-source-v37/source-cards.json';assert.ok(!fs.existsSync(f));
const rows=['2022-23','2023-24','2024-25','2025-26'].map(season=>({season,teams:loadInput(season).league.teams.map(t=>({teamId:t.id,cards:t.roster.map(p=>({playerId:p.playerId,pos:p.courtPosition??p.pos,onBall:p.onBall,help:p.help,physique:p.physique,box:p.boxAllocationMeasurement}))}))}));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
fs.writeFileSync(f,JSON.stringify({seasons:rows,hashes:Object.fromEntries(['reports/player-impact-diagnostics/block-source-v37/export-input.mjs','reports/player-impact-v30/validation-protocol.json'].map(p=>[p,hash(p)]))}));

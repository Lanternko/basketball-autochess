import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='reports/player-impact-v24/all-2025-26',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol=read(root+'/protocol.json'),manifest=read(root+'/manifest.json'),state=read(root+'/checkpoint.json'),rank=read(root+'/ranking.json');
for(const[f,h]of Object.entries(protocol.hashes))assert.equal(hash(f),h,`Frozen source drift: ${f}`);
assert.equal(hash(root+'/checkpoint.json'),manifest.checkpointSHA256);assert.equal(state.fingerprint,protocol.fingerprint);assert.equal(manifest.fingerprint,protocol.fingerprint);assert.equal(rank.protocolFingerprint,protocol.fingerprint);
assert.equal(state.rows.length,587);assert.equal(state.rows.filter(r=>r.job.kind==='player').length,582);assert.equal(state.rows.filter(r=>r.job.kind==='baseline').length,5);
assert.equal(new Set(state.rows.map(r=>r.job.key)).size,587);assert.equal(rank.players.length,582);
const baseline=read('reports/player-box-audit/baseline.json').seasons.find(s=>s.season==='2025-26'),ids=new Set(baseline.players.map(p=>p.playerId));
assert.deepEqual(new Set(rank.players.map(p=>p.playerId)),ids);
for(const r of state.rows){assert.equal(r.job.samples,40);assert.equal(r.result.games,2400);assert.equal(r.result.independentPairs,1200);}
for(let i=0;i<rank.players.length;i++){
 const p=rank.players[i];assert.equal(p.rank,i+1);assert.ok(p.winRate>=0&&p.winRate<=1);assert.ok(p.ci95[0]<=p.winRate&&p.ci95[1]>=p.winRate);
 if(i)assert.ok(rank.players[i-1].winRate>=p.winRate);
}
assert.equal(rank.guardCountTop50,rank.players.slice(0,50).filter(p=>['PG','SG'].includes(p.position)).length);
assert.equal(rank.lowMinutesUnder500Top50,rank.players.slice(0,50).filter(p=>p.actualMinutes<500).length);
const archived=read('reports/player-impact-v23/verification.json');assert.equal(hash('reports/player-impact-v23/ovr-checkpoint.json'),archived.artifacts['reports/player-impact-v23/ovr-checkpoint.json']);
const old=read('reports/player-impact-v23/ovr-checkpoint.json');let overlap=0;
for(const r of old.rows){const current=state.rows.find(p=>p.job.key===r.job.key);assert.ok(current);assert.deepEqual(current.result,r.result,'DREB-recipient-only change must preserve every v23 sample benchmark result');overlap++;}
assert.equal(overlap,36);
const report=fs.readFileSync(root+'/report.md','utf8');for(const p of rank.players.slice(0,50))assert.ok(report.includes(`| ${p.rank} | ${p.name} |`));
assert.equal(read('reports/player-impact-v24/status.json').officialModelAdopted,false);
const artifacts=['protocol.json','manifest.json','checkpoint.json','ranking.json','ranking.csv','report.md','verify.mjs','../rank.py'];
const output={frozenSourceFiles:Object.keys(protocol.hashes).length,players:582,baselinePositions:5,gamesPerPlayer:2400,totalGames:587*2400,allPlayersRetained:true,guardCountTop50:rank.guardCountTop50,lowMinutesUnder500Top50:rank.lowMinutesUnder500Top50,exactV23SampleOverlap:overlap,officialModelAdopted:false,goalComplete:false,artifacts:Object.fromEntries(artifacts.map(f=>[root+'/'+f,hash(root+'/'+f)]))};
fs.writeFileSync(root+'/verification.json',JSON.stringify(output,null,2));console.log(JSON.stringify({...output,artifacts:undefined},null,2));

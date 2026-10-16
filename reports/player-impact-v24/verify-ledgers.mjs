import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const root='reports/player-impact-v24',manifest=JSON.parse(fs.readFileSync(root+'/validation-manifest.json'));
let teamSeasons=0,games=0;
const keys=['pts','ast','fga','fgm','fg3a','fg3m','fta','ftm','oreb','dreb','stl','blk','liveTov','deadTov','touchTov'];
for(const job of manifest.jobs){
 const bytes=fs.readFileSync(job.file);assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),job.sha256);
 const run=JSON.parse(bytes);games+=run.matches.length;
 for(const t of run.teams){
  teamSeasons++;
  for(const k of keys){
   const sum=t.players.reduce((s,p)=>s+(p.stats[k]??0),0),expected=t.stats[k]??0;
   assert.equal(sum+(k==='deadTov'?(t.stats.clockTov??0):0),expected,`${job.file} ${t.id} ${k}`);
  }
  assert.equal(t.players.reduce((s,p)=>s+(p.stats.tov??0),0)+(t.stats.clockTov??0),t.stats.tov);
  assert.equal(t.players.reduce((s,p)=>s+(p.stats.clockTov??0),0),0);
  assert.equal(t.stats.tov,t.stats.liveTov+t.stats.deadTov);
  assert.equal(t.stats.pts,2*t.stats.fgm+t.stats.fg3m+t.stats.ftm);
  assert.ok(t.stats.ast<=t.stats.fgm);
 }
 const totals=run.teams.reduce((s,t)=>({steals:s.steals+t.stats.stl,live:s.live+t.stats.liveTov}),{steals:0,live:0});assert.equal(totals.steals,totals.live);
}
const output={files:manifest.jobs.length,teamSeasons,games,passed:true,scope:'All full and strict runs: team-player basic stat conservation, team-only shot clock violations, scoring identity, AST no more than FGM, paired steals/live turnovers. On-court 5/4/1 ledgers independently checked in scorer.'};
fs.writeFileSync(root+'/ledger-verification.json',JSON.stringify(output,null,2));console.log(output);

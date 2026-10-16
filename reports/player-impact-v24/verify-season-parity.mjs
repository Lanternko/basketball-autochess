import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const root='reports/player-impact-v24',read=f=>JSON.parse(fs.readFileSync(f)),manifest=read(root+'/validation-manifest.json');
let games=0,playerTeamSeasons=0,changedPlayerTeamSeasons=0;const rows=[];
const strip=s=>{const x={...s};delete x.dreb;delete x.reb;return x;};
for(const job of manifest.jobs){
 const current=read(job.file),old=read(job.file.replace('player-impact-v24','player-impact-v23'));
 assert.deepEqual(current.matches,old.matches);assert.deepEqual(current.onCourt,old.onCourt);assert.deepEqual(current.putbackAudit,old.putbackAudit);
 let changed=0;
 for(const t of current.teams){
  const before=old.teams.find(p=>p.id===t.id);assert.deepEqual(t.stats,before.stats);assert.equal(t.games,before.games);
  for(const p of t.players){
   const q=before.players.find(v=>v.playerId===p.playerId);assert.ok(q);assert.deepEqual(strip(p.stats),strip(q.stats));playerTeamSeasons++;
   if(p.stats.dreb!==q.stats.dreb){changed++;changedPlayerTeamSeasons++;}
  }
 }
 games+=current.matches.length;rows.push({season:job.season,seed:job.seed,strict:job.strict,games:current.matches.length,changedPlayerTeamSeasons:changed});
}
assert.equal(manifest.jobs.length,24);assert.ok(changedPlayerTeamSeasons>0);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),out={files:manifest.jobs.length,games,playerTeamSeasons,changedPlayerTeamSeasons,allMatchesAndTeamStatsExact:true,onCourtFgLedgersExact:true,putbackAuditExact:true,allPersonalNonDrebCountersExact:true,rows,hashes:{[root+'/verify-season-parity.mjs']:hash(root+'/verify-season-parity.mjs')}};
fs.writeFileSync(root+'/season-parity.json',JSON.stringify(out,null,2));console.log(JSON.stringify({...out,rows:undefined,hashes:undefined},null,2));

import {Worker} from 'node:worker_threads';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const execute=version=>new Promise((resolve,reject)=>{
  const w=new Worker(new URL('./worker.mjs',import.meta.url));
  w.on('error',reject);w.on('message',m=>{w.terminate();if(m.error)reject(Error(m.error));else resolve(m.result);});
  w.postMessage({season:'2025-26',version,seed:20261015});
});
const [control,credit]=await Promise.all([execute('control'),execute('pass-credit')]);
const old=JSON.parse(fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/runs/2025-26-split-20261015.json'));
assert.deepEqual(control.matches,old.matches);assert.deepEqual(control.teams,old.teams);assert.deepEqual(control.matches,credit.matches);
for(let i=0;i<control.teams.length;i++){
  const a=structuredClone(control.teams[i]),b=structuredClone(credit.teams[i]);
  delete a.stats.ast;delete b.stats.ast;delete a.opponent.ast;delete b.opponent.ast;
  for(const p of a.players)delete p.stats.ast;for(const p of b.players)delete p.stats.ast;
  assert.deepEqual(a,b);
}
const result={passed:true,controlFullTeamsAndPlayersIdentical:true,games:1230,assistCreditOnlyChangesAssistCounts:true};
fs.writeFileSync('reports/player-box-audit/experiment/parity.json',JSON.stringify(result,null,2));console.log(result);

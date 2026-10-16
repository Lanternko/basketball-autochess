import fs from 'node:fs';
import os from 'node:os';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-box-audit/round2',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const versions=['hazard-balance','creator-hazard','creator-only-hazard'],seasons=['2022-23','2023-24','2024-25','2025-26'],seeds=[20261012,20261013,20261014];
fs.mkdirSync(root+'/runs',{recursive:true});
const inputs=['adapter.mjs','worker.mjs','run.mjs','prepare.py'].map(f=>root+'/'+f);
for(const f of Object.keys(read('reports/player-box-audit/source-hashes.json')))inputs.push(f);
for(const f of fs.readdirSync('src').filter(f=>f.endsWith('.js')))inputs.push('src/'+f);
for(const s of seasons)for(const f of [`reports/defense-tenth/step4-rebounds-oreb/${s}/calibration-oreb.json`,`reports/defense-tenth/step4-rebounds-turnover-time/${s}/calibration.json`])inputs.push(f);
const hashes=Object.fromEntries([...new Set(inputs)].map(f=>[f,hash(f)]));
const protocol={version:'observed-receiver-stopping-hazard-1',seasons,seeds,variants:versions,
  creatorTouch:'hazard-balance uses original initial involvement. creator-hazard adds AST/min. creator-only-hazard uses AST/min alone. On receiving, all divide observed FGA/min by the existing probability of shooting at the next pass state. This tests whether measured final FGA was double weighted by finishing EV; it is not a fitted player offset or positional boost.',
  passCredit:'Original pass/assist accounting untouched. No direct FG, rebound or steal probability edit. Inverse shot willingness only approximates terminal hazard: pass failures, fouls, turnovers, clocks and putbacks still affect realized shots.',
  comparison:'Archived adopted model, matching seeds; control parity before changes. Each mechanism and joint variant independently evaluated. No recalibration or fitted player offsets.',
  limits:'Four already-seen seasons, same-season diagnostic; 2025 baseline has been inspected. Not blind validation. Unknown offBall/screen/handle/breakDbl remain70.',
  gates:'No promotion from diagnostic alone. Require lower individual AST/PTS MAE on historical development seasons, no worsening team net RMSE or OREB/STL/3P beyond Monte Carlo uncertainty, and held-out-seed confirmation. Assist credit-only must have exact gameplay parity.',hashes};
const fingerprint=hashes[root+'/adapter.mjs']+'-'+crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex');
if(fs.existsSync(root+'/protocol.json')){if(read(root+'/protocol.json').fingerprint!==fingerprint)throw Error('Protocol changed; use a new output directory');}
else fs.writeFileSync(root+'/protocol.json',JSON.stringify({...protocol,fingerprint},null,2)+'\n');
const all=seasons.flatMap(season=>versions.flatMap(version=>seeds.map(seed=>({season,version,seed,file:`${root}/runs/${season}-${version}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file)),workers=[];let next=0,done=0;const start=Date.now();
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
  for(let i=0;i<Math.min(8,os.availableParallelism(),jobs.length);i++){
    const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));done++;
      console.log(JSON.stringify({done,total:jobs.length,season:m.job.season,version:m.job.version,seed:m.job.seed,seconds:Math.round((Date.now()-start)/1000)}));if(done===jobs.length)resolve();else dispatch(w);
    });dispatch(w);
  }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const [f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Source drift: '+f);
fs.writeFileSync(root+'/manifest.json',JSON.stringify({fingerprint,files:all.map(j=>({...j,sha256:hash(j.file)}))},null,2)+'\n');

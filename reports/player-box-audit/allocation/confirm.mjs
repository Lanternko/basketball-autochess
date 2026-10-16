import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
const root='reports/player-box-audit/allocation',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol={version:'recipient-allocation-unseen-seed-confirmation-1',seasons:['2022-23','2023-24','2024-25','2025-26'],seeds:[20261015,20261016,20261017],variants:['box-allocation'],
 limits:'Unseen random seeds, not unseen seasons or players. Conditional same-season box reconstruction only.',
 gates:'All match results and complete team statistics identical. All player statistics except DREB/BLK identical. Lower individual DREB and BLK errors on four seasons.',
 hashes:Object.fromEntries([root+'/adapter.mjs',root+'/worker.mjs','src/individual_box_allocation.js',root+'/confirm.mjs'].map(f=>[f,hash(f)]))};
const dir=root+'/confirmation';fs.mkdirSync(dir+'/runs',{recursive:true});
if(fs.existsSync(dir+'/protocol.json'))assert.deepEqual(read(dir+'/protocol.json'),protocol);else fs.writeFileSync(dir+'/protocol.json',JSON.stringify(protocol,null,2));
const jobs=protocol.seasons.flatMap(season=>protocol.seeds.map(seed=>({season,seed,version:'box-allocation',file:`${dir}/runs/${season}-box-allocation-${seed}.json`})));
let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<4;i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{
   if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,seed:m.job.seed}));if(done===jobs.length)resolve();else dispatch(w);
 });dispatch(w);}
});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const [f,h]of Object.entries(protocol.hashes))assert.equal(hash(f),h);
console.log('confirmation simulation complete; run parity and scoring');

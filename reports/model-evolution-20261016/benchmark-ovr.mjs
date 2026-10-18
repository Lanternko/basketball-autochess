import {Worker} from 'node:worker_threads';
import fs from 'node:fs';
const root='reports/model-evolution-20261016';
const latest=process.argv.includes('--latest');
const rank=JSON.parse(fs.readFileSync('reports/player-impact-v24/all-2025-26/ranking.json'));
const ids=rank.players.slice(0,8).map(p=>p.playerId),workers=[];
const started=performance.now(),times=[];
let next=0,done=0;
try { await new Promise((resolve,reject)=>{
  const dispatch=w=>{if(next<ids.length)w.postMessage({season:'2025-26',samples:latest?1:4,seed:20261016,version:'rotation-space',variant:'v41',id:ids[next++],kind:'player'});};
  for(let i=0;i<4;i++){
    const w=new Worker(new URL(latest?'../player-impact-v41/probe-worker.mjs':'../player-impact-v24/season-ovr-worker.mjs',import.meta.url));workers.push(w);
    w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));times.push({name:m.result.name,elapsedSeconds:(performance.now()-started)/1000});done++;if(done===ids.length)resolve();else dispatch(w);});dispatch(w);
  }
}); } finally {await Promise.all(workers.map(w=>w.terminate()));}
const d={kind:'timing-only; no ranking update',variant:latest?'v41':'v24',workers:4,games:8*240,gameSeconds:latest?2880:864,wallSeconds:(performance.now()-started)/1000,times};
fs.writeFileSync(root+(latest?'/ovr-timing-v41.json':'/ovr-timing.json'),JSON.stringify(d,null,2));console.log(JSON.stringify(d));

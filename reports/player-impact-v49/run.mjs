import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v49',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const protocol=read(root+'/protocol.json');
const files=['protocol.json','worker.mjs','input.mjs','run.mjs','engine.mjs','fit.py','selection.json','source-hashes.json','season-source.mjs','rotation-collector.mjs',...protocol.seasons.flatMap(s=>[s+'-profiles.json',s+'-metadata.json'])];
const hashes={...read('reports/player-impact-v47/candidate-run-protocol.json').hashes,...read(root+'/source-hashes.json'),...Object.fromEntries(files.map(f=>[root+'/'+f,hash(root+'/'+f)])),...Object.fromEntries(['src/measured_rotation.js','reports/player-impact-v48/offense-collector.mjs'].map(f=>[f,hash(f)]))};
const verify=()=>{for(const[p,h]of Object.entries(hashes))if(hash(p)!==h)throw Error('Frozen source drift '+p);};verify();
const pf=root+'/candidate-run-protocol.json',frozen={variant:'v49',hashes,protocol};if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify(frozen))throw Error('Run protocol changed');}else fs.writeFileSync(pf,JSON.stringify(frozen,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=[...protocol.seasons].reverse().flatMap(season=>[...protocol.seeds.flatMap(seed=>[false,true].map(strict=>({variant:'v49',season,seed,strict}))),...protocol.seeds.map(seed=>({variant:'v47',season,seed,strict:true}))]).map(j=>({...j,file:`${root}/runs/${j.season}-${j.variant}-${j.strict?'strict':'full'}-${j.seed}.json`}));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[],started=Date.now(),status=state=>fs.writeFileSync(root+'/candidate-status.json',JSON.stringify({state,total:all.length,completed:all.length-jobs.length+done,elapsedSeconds:(Date.now()-started)/1000,updatedAt:new Date().toISOString()},null,2));
status('running');
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));done++;status('running');console.log(JSON.stringify({done,total:jobs.length,season:m.job.season,variant:m.job.variant,strict:m.job.strict,games:m.games}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);}});verify();status('complete');fs.writeFileSync(root+'/candidate-run-verification.json',JSON.stringify({passed:true,jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));}catch(e){status('failed');throw e;}finally{await Promise.all(workers.map(w=>w.terminate()));}

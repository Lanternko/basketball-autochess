import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v44',mode=process.argv[2]??'candidate',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!['baseline','candidate'].includes(mode))throw Error('Choose baseline or candidate');
const protocol=read(root+'/protocol.json'),selected=process.argv[3],seasons=selected?[selected]:[...protocol.seasons].reverse(),variant='v44',prefix=selected?selected+'-':'';
if(seasons.some(s=>!protocol.seasons.includes(s)))throw Error('Unknown season');
const files=['protocol.json','worker.mjs','input.mjs','run.mjs','space-model.mjs','engine.mjs','prepare-contexts.mjs'];
if(mode==='candidate')files.push(...seasons.map(s=>s+'-contexts.json'));
const hashes={...read('reports/player-impact-v42/candidate-run-protocol.json').hashes,...Object.fromEntries(files.map(f=>[root+'/'+f,hash(root+'/'+f)]))};
const verify=()=>{for(const[p,h]of Object.entries(hashes))if(hash(p)!==h)throw Error('Frozen source drift '+p);};verify();
const pf=`${root}/${prefix}${mode}-run-protocol.json`,frozen={variant,hashes,protocol};
if(fs.existsSync(pf)){if(JSON.stringify(read(pf))!==JSON.stringify(frozen))throw Error('Run protocol changed');}else fs.writeFileSync(pf,JSON.stringify(frozen,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=seasons.flatMap(season=>protocol.seeds.flatMap(seed=>(mode==='baseline'?[true]:[false,true]).map(strict=>({variant,season,seed,strict,file:`${root}/runs/${season}-${variant}-${strict?'strict':'full'}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[],started=Date.now();
const status=state=>fs.writeFileSync(`${root}/${prefix}${mode}-status.json`,JSON.stringify({state,total:all.length,completed:all.length-jobs.length+done,elapsedSeconds:(Date.now()-started)/1000,updatedAt:new Date().toISOString()},null,2));
status('running');console.log(JSON.stringify({mode,pending:jobs.length}));
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);
  w.on('message',m=>{if(m.error)return reject(Error(m.error));done++;status('running');console.log(JSON.stringify({mode,done,total:jobs.length,season:m.job.season,seed:m.job.seed,strict:m.job.strict,games:m.games}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
 }
});verify();status('complete');fs.writeFileSync(`${root}/${prefix}${mode}-run-verification.json`,JSON.stringify({passed:true,allSourceHashesPassed:true,jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));
}catch(e){status('failed');fs.writeFileSync(`${root}/${mode}-failure.txt`,e.stack);throw e;}finally{await Promise.all(workers.map(w=>w.terminate()));}

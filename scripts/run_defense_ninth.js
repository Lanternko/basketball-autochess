import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from './defense_io.js';
import {seasonsN,cutoffsN,seedsN,configN} from '../src/defense_ninth_rosters.js';
const root='reports/defense-ninth/development',spec=read(root+'/prereg.json');
if(hash(root+'/prereg.json')!==fs.readFileSync(root+'/prereg.sha256','utf8').trim())throw Error('Prereg changed');
for(const [p,h]of Object.entries(spec.sourceHashes))if(hash(p)!==h)throw Error('Frozen/input source changed '+p);
fs.mkdirSync(root+'/runs',{recursive:true});
const jobs=seasonsN.flatMap(s=>cutoffsN.flatMap(k=>['v3','v4'].map(version=>({season:s,k,version,configFile:configN(s,k)}))));
for(const j of jobs){
 const file=`${root}/${j.season}-K${j.k}-${j.version}.json`;if(fs.existsSync(file)){console.log('CACHED',file);continue;}
 let next=0,done=0;const results=Array(20),workers=[],start=Date.now();console.log('START',j.season,j.k,j.version);
 try{await new Promise((resolve,reject)=>{const dispatch=w=>{if(next<20){const index=next++;w.postMessage({index,job:{...j,seed:seedsN[index]}});}};for(let n=0;n<4;n++){const w=new Worker(new URL('./defense_ninth_worker.js',import.meta.url));workers.push(w);w.on('error',reject);w.on('exit',code=>{if(code&&done<20)reject(Error('Worker exit '+code));});w.on('message',m=>{if(m.error)return reject(Error(m.error));results[m.index]=m.result;if(++done%5===0)console.log('PROGRESS',j.season,j.k,j.version,done);if(done===20)resolve();else dispatch(w);});dispatch(w);}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
 const files=results.map(r=>{const p=`${root}/runs/${j.season}-K${j.k}-${j.version}-seed${r.seed}.json`;fs.writeFileSync(p,JSON.stringify(r)+'\n');return {file:p,seed:r.seed,sha256:hash(p)};});
 fs.writeFileSync(file,JSON.stringify({job:j,files,seconds:(Date.now()-start)/1000,preregHash:hash(root+'/prereg.json'),sources:Object.fromEntries(['src/defense_ninth_rosters.js','scripts/defense_ninth_worker.js','scripts/run_defense_ninth.js'].map(p=>[p,hash(p)]))},null,2)+'\n');console.log('DONE',file);
}

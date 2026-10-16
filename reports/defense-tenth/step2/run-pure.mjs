import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {read,hash} from '../../../scripts/defense_io.js';
import {cManifest} from '../../../scripts/defense_eighth_c_data.js';
const dir='reports/defense-tenth/step2',p=read(dir+'/protocol.json');
const jobs=p.seasons.flatMap(season=>p.cutoffs.flatMap(k=>{
 const mf=read(cManifest(season,k,'v3'));
 return p.seeds.map(seed=>({season,k,seed,extra:mf.extra}));
}));
const code=`const {parentPort}=require('node:worker_threads'),{pathToFileURL}=require('node:url'),path=require('node:path');(async()=>{
 const {seventhInputs}=await import(pathToFileURL(path.resolve('src/defense_seventh_jobs.js')).href);
 const {runDefenseSeason}=await import(pathToFileURL(path.resolve('src/defense_seventh_season.js')).href);
 parentPort.on('message',j=>{try{
 const b=seventhInputs(j.extra);for(const z of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[z]=false;delete b.options.defenseSignals;
 const indices=b.league.schedule.flatMap((g,i)=>g.date>j.extra.calendarDate?[i]:[]);
 const r=runDefenseSeason(b.league,b.exposure,{seed:j.seed,options:b.options,indices,audit:false,replay:false});
 parentPort.postMessage({season:j.season,k:j.k,seed:j.seed,options:r.options,teams:r.teams.map(({players,...t})=>t),matches:r.matches,analysis:r.analysis});
 }catch(e){parentPort.postMessage({error:e.stack});}});})();`;
const todo=jobs.filter(j=>!fs.existsSync(`${dir}/pure/${j.season}-${j.k}-${j.seed}.json`));
fs.mkdirSync(dir+'/pure',{recursive:true});let next=0,done=0;const workers=[],start=Date.now();
try{await new Promise((resolve,reject)=>{if(!todo.length)return resolve();const dispatch=w=>{if(next<todo.length)w.postMessage(todo[next++]);};for(let i=0;i<Math.min(8,todo.length);i++){
 const w=new Worker(code,{eval:true,execArgv:[]});workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));const f=`${dir}/pure/${m.season}-${m.k}-${m.seed}.json`;fs.writeFileSync(f,JSON.stringify(m)+'\n');done++;if(done%5===0)console.log('PURE',done+'/'+todo.length,m.season,m.k,'seconds',((Date.now()-start)/1000).toFixed(1));if(done===todo.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
const files=jobs.map(j=>{const file=`${dir}/pure/${j.season}-${j.k}-${j.seed}.json`;return {...j,extra:undefined,file,sha256:hash(file)};});
for(const[f,h]of Object.entries(p.fingerprints))if(hash(f)!==h)throw Error('Changed frozen/input '+f);
fs.writeFileSync(dir+'/pure-manifest.json',JSON.stringify({finishedAt:new Date().toISOString(),protocolHash:hash(dir+'/protocol.json'),files,seconds:(Date.now()-start)/1000},null,2)+'\n');console.log('PURE COMPLETE',files.length);

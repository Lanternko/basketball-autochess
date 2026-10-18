import fs from 'node:fs';
import {Worker} from 'node:worker_threads';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {read,hash} from '../../../scripts/defense_io.js';
import {seventhInputs} from '../../../src/defense_seventh_jobs.js';
import {cManifest} from '../../../scripts/defense_eighth_c_data.js';
const d='reports/defense-tenth/step2',p=read('reports/defense-tenth/step1/protocol.json'),b=seventhInputs(read(cManifest('2025-26',41,'v3')).extra),base=p.cases.find(c=>c.id==='real-rim').players,opponent=p.opponent;
for(const z of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])b.options[z]=false;delete b.options.defenseSignals;
const fixed={fatigue:false,substitutions:false,foulOut:99,maxOvertimes:0,replay:false,auditIds:base.map(p=>p.playerId)};
const treatments=[
 {id:'as-card',description:'Unchanged effective v3 real-rim cards, five C positions.'},
 {id:'all-PG',description:'Only pos/courtPosition=PG for all five; attributes and measurements unchanged.'},
 {id:'neutral-positions',description:'Only positions PG/SG/SF/PF/C in existing order.'},
 {id:'no-oreb',options:{auditNoOreb:true},description:'Audit in-memory override: attacking test team never retains team/player OREB; all recorded misses instead end possession. Opponent unchanged.'},
 {id:'twoP-prior-neutral',neutralTwoP:true,description:'Audit in-memory probability model: remaining two-point attempt prior split half mid/half paint, instead of league fixed mid/paint ratio. All threeRate and skills unchanged.'},
 {id:'neutral-shot-skills',description:'Only long/mid/short=training-minute weighted league average.'},
 {id:'legacy-ball-allocation',options:{shotSelection:'legacy'},description:'Existing handlingWeights/receiverWeights rather than measured volume allocation, no new ability estimate.'},
 {id:'full-context',options:{contextLongScale:1,contextShortScale:1},description:'Existing direct teammate make context coefficients set to1.'},
 {id:'no-context',options:{contextLongScale:0,contextShortScale:0},description:'Existing direct teammate make context coefficients set to0; zone accessibility and spacing tax remain.'},
 {id:'neutral-creation',options:{auditNeutralCreation:true},description:'Test team context.create=70 only; other context unchanged.'},
 {id:'no-spacing-gravity',options:{auditNoSpacing:true},description:'Test team context.spacing/gravity=70 only; other context unchanged.'},
 {id:'weak-control-fields',description:'Test team handle/pass/tovSkill=0. Deliberate stress substitution, not an estimate of those actual players.'},
 {id:'combined-stress',options:{auditNoOreb:true,shotSelection:'legacy'},description:'Combination of handle/pass/tovSkill=0, allPG, and no attacking OREB; not a proposed model.'}
];
const reg={registeredAt:new Date().toISOString(),sourceProtocolHash:hash('reports/defense-tenth/step1/protocol.json'),treatments,N:1000,seed0:202610120,controls:fixed,instrumentationHash:hash(d+'/audit-loader.mjs'),scope:'mechanism diagnostics only; frozen engine files untouched'};fs.writeFileSync(d+'/centers-protocol.json',JSON.stringify(reg,null,2)+'\n');fs.writeFileSync(d+'/centers-protocol.sha256',hash(d+'/centers-protocol.json')+'\n');
const jobs=treatments.map((t,index)=>{const roster=structuredClone(base);if(['all-PG','combined-stress'].includes(t.id))roster.forEach(p=>p.pos=p.courtPosition='PG');if(t.id==='neutral-positions')roster.forEach((p,i)=>p.pos=p.courtPosition=['PG','SG','SF','PF','C'][i]);if(t.id==='neutral-shot-skills')roster.forEach(q=>['long','mid','short'].forEach(z=>q[z]=p.averageCard[z]));if(['weak-control-fields','combined-stress'].includes(t.id))roster.forEach(p=>p.handle=p.pass=p.tovSkill=0);return {index,id:t.id,neutralTwoP:t.neutralTwoP,team:{name:t.id,roster},options:{...b.options,...fixed,...t.options}};});
const keys=['pts','poss','fga','fgm','fg3a','fg3m','rima','rimm','tov','oreb','dreb','fta','ast','passes'];
const code=`const{parentPort,workerData}=require('node:worker_threads');(async()=>{const{auditEngine}=await import(workerData.loader);const a=await auditEngine(),b=await auditEngine('fourth',{neutralTwoP:true});parentPort.on('message',j=>{try{const fn=j.neutralTwoP?b:a,rows=[];for(let i=0;i<workerData.N;i++){const g=fn(j.team,workerData.opponent,{...j.options,seed:workerData.seed0+i});rows.push([workerData.keys.map(k=>g.statA[k]),workerData.keys.map(k=>g.statB[k])]);}parentPort.postMessage({index:j.index,id:j.id,rows});}catch(e){parentPort.postMessage({error:e.stack});}});})();`;
// Verify that the diagnostic loader without interventions is bit-for-bit identical.
const {auditEngine}=await import('./audit-loader.mjs'),audit=await auditEngine(),{simulateDefenseFourthGame:original}=await import('../../../src/defense_fourth_game.js');
for(let i=0;i<5;i++){const a=audit(jobs[0].team,opponent,{...jobs[0].options,seed:reg.seed0+i}),b=original(jobs[0].team,opponent,{...jobs[0].options,seed:reg.seed0+i});if(JSON.stringify([a.statA,a.statB])!==JSON.stringify([b.statA,b.statB]))throw Error('Audit loader baseline changed');}
let next=0,done=0;const workers=[],results=[];try{await new Promise((resolve,reject)=>{const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<3;i++){const w=new Worker(code,{eval:true,execArgv:[],workerData:{loader:pathToFileURL(path.resolve(d,'audit-loader.mjs')).href,N:reg.N,seed0:reg.seed0,opponent,keys}});workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));results[m.index]=m;console.log('CENTERS',++done,jobs.length,m.id);if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
fs.writeFileSync(d+'/centers-results.json',JSON.stringify({protocolHash:hash(d+'/centers-protocol.json'),keys,baselineParity:true,results})+'\n');

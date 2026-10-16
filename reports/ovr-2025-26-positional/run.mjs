import fs from 'node:fs';
import crypto from 'node:crypto';
import os from 'node:os';
import {Worker} from 'node:worker_threads';
import {ROOT,positionalInputs,representativeIds,unknown} from './protocol.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';
const x=positionalInputs(),samples=Number(process.env.POS_OVR_SAMPLES??80),seed=20261015;
if(!Number.isSafeInteger(samples)||samples<2)throw Error('Need >=2 seeds per opponent');
const all=process.argv.includes('--all'),ids=all?x.players.map(p=>p.playerId):representativeIds;
for(const id of ids)if(!x.roleMap.has(id))throw Error('Unknown requested player '+id);
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const previous=JSON.parse(fs.readFileSync('reports/ovr-2025-26-latest/protocol-16.json'));
const hashes={...previous.hashes,...Object.fromEntries(['protocol.mjs','worker.mjs','run.mjs'].map(f=>[ROOT+'/'+f,hash(ROOT+'/'+f)]))};
for(const [f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Source changed: '+f);
const protocol={version:'natural-role-positional-mean70-diagnostic-1',model:previous.model,season:previous.season,
  seed,samples,gamesPerPlayer:60*samples,scope:all?'all-players':'fixed-20-representative-diagnostic',ids,
  exposure:previous.exposure,opponents:previous.opponentPool,
  roleMethod:'Modal minute-weighted official starter position. Exact PG/SG/SF/PF/C when supplied; for G/F/C-only boxes split guards by season AST/MIN, forwards by height. No starts: original height-band fallback, explicitly flagged. This is observed primary role, not proof of best position.',
  referenceMethod:'Five distinct minute-weighted positional profiles from players with at least five supported starts. Preserve measured attribute offsets with a common shift until each profile arithmetic mean is exactly 70. Unknown four stay 70. Auxiliary measured rates retain positional values. This does not equate attribute mean with OVR.',
  remainingGap:'Individual offBall/screen/handle/breakDbl remain unmeasured. This diagnostic cannot implement a measured PG-handle/C-screen distinction; no invented positional or star priors are supplied.',
  calibration:'Common win-rate scale from positional 40/70/99 synthetic anchors, equally pooled over five slots. Report same-position baseline delta as well. No fit to player ranking, team wins, or reputation.',
  interventions:'Candidate-only sensitivity: physique=70; rebound=70 and positional-average OREB share; help=70; short=70. All other inputs fixed. These are not proposed real player cards, and effects must not be added.',
  unknown,roleAudit:x.roleAudit,roles:x.roles,profiles:x.profiles,hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex');
const suffix=(all?'all':'representative')+'-'+samples,file=ROOT+'/checkpoint-'+suffix+'.json';
let state={fingerprint,startedAt:new Date().toISOString(),rows:[]};
if(fs.existsSync(file)){state=JSON.parse(fs.readFileSync(file));if(state.fingerprint!==fingerprint)throw Error('Checkpoint mismatch');}
fs.writeFileSync(ROOT+'/protocol-'+suffix+'.json',JSON.stringify({...protocol,fingerprint},null,2)+'\n');
let jobs=[...x.profiles.flatMap((_,slot)=>[40,70,99].map(level=>({key:`anchor-${slot}-${level}`,kind:'anchor',slot,level,baseline:'positional'}))),
  ...ids.flatMap(id=>['flat','positional'].map(baseline=>({key:`${id}-${baseline}`,kind:'player',id,baseline}))),
  ...[1629674,201939].flatMap(id=>['physique70','rebound-neutral','help70','short70'].map(intervention=>({key:`${id}-${intervention}`,kind:'sensitivity',id,baseline:'positional',intervention})))];
jobs=jobs.filter(j=>!state.rows.some(r=>r.job.key===j.key)).map(j=>({...j,samples,seed}));
const ws=[],start=Date.now();let next=0,done=0;
const save=()=>{state.updatedAt=new Date().toISOString();fs.writeFileSync(file,JSON.stringify(state)+'\n');};
try{await new Promise((resolve,reject)=>{
  if(!jobs.length)return resolve();
  const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
  for(let i=0;i<Math.min(Number(process.env.POS_OVR_WORKERS??8),os.availableParallelism(),jobs.length);i++){
    const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);w.on('error',reject);
    w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);save();done++;
      console.log(JSON.stringify({done,total:jobs.length,key:m.job.key,name:m.result.name,winRate:m.result.winRate,seconds:Math.round((Date.now()-start)/1000)}));
      if(done===jobs.length)resolve();else dispatch(w);
    });dispatch(w);
  }
});}finally{await Promise.all(ws.map(w=>w.terminate()));}
for(const [f,h]of Object.entries(hashes))if(hash(f)!==h)throw Error('Source changed during run: '+f);
save();console.log('Finished '+state.rows.length+' measurements; candidate means '+x.profiles.map(p=>ATTRIBUTES.reduce((s,k)=>s+p[k],0)/16).join(','));

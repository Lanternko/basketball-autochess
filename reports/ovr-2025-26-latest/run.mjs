import fs from 'node:fs';
import crypto from 'node:crypto';
import os from 'node:os';
import {Worker} from 'node:worker_threads';
import {ROOT,inputs} from './runtime.mjs';
const x=inputs(),samples=Number(process.env.OVR_SAMPLES??16),seed=20261015;
if(!Number.isInteger(samples)||samples<2)throw Error('Need >=2 samples per stratum');
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const files=[...fs.readdirSync('src').filter(f=>f.endsWith('.js')).map(f=>'src/'+f),
  ...['runtime.mjs','worker.mjs','run.mjs'].map(f=>ROOT+'/'+f),
  'scripts/export_defense_sixth_cards.js','reports/defense-tenth/step4-t0/2025-26/bundle.json',
  'reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs',
  'reports/defense-tenth/step4-rebounds-allocation/model.mjs','reports/defense-tenth/step4-rebounds-oreb/model.mjs',
  'reports/defense-tenth/step4-rebounds-oreb/2025-26/cards.json',
  'reports/defense-tenth/step4-rebounds-oreb/2025-26/calibration-oreb.json',
  'reports/defense-tenth/step4-rebounds-putback-time/timing.mjs',
  'reports/defense-tenth/step4-rebounds-putback-time/putback-cdf.json',
  'reports/defense-tenth/step4-rebounds-turnover-time/2025-26/calibration.json',
  'reports/defense-tenth/step4-rebounds-turnover-time/2025-26/turnover-cdf.json',
  'reports/defense-tenth/step4-rebounds-closeout/status.json'];
const hashes=Object.fromEntries(files.map(f=>[f,hash(f)]));
const protocol={model:'pure-oreb-turnover-time-1',season:'2025-26',samples,seed,playerCount:x.players.length,
  opponentCount:30,slots:5,gamesPerPlayer:30*5*samples*2,
  exposure:{quarterSeconds:216,gameSeconds:864,fatigue:false,substitutions:false,foulOut:99,overtime:false,tieWinCredit:.5},
  selection:'All 582 unique season players. Candidate observed counts are summed across team stints; full-season shot/volume profiles recomputed. Opponents retain team-specific profiles: each team top five by observed in-team minutes, height-ordered positions. Players swap all five slots beside four neutral-70 teammates.',
  mapping:'Same winToOvr piecewise function: flat16 attributes 40/70/99 anchors; auxiliary volume, steal and OREB fields held at pooled league neutral values for all anchors.',
  uncertainty:'Paired seating is one sample, stratified by opponent and slot. Conditional OVR CI holds fitted anchors fixed; excludes card uncertainty and model error. Nearby ranks not guaranteed.',
  measurementScope:'New 14.4-minute timed OVR protocol, preserving adopted event/timing mechanics. Does not inherit acceptance of old fixed-possession OVR report. Equal exposure removes availability/stamina/rotation value.',
  opponentPool:x.opponents.map(t=>({id:t.id,name:t.name,roster:t.roster.map(p=>({id:p.playerId,name:p.name,pos:p.pos}))})),
  neutral:x.base.roster[0],hashes};
const fingerprint=crypto.createHash('sha256').update(JSON.stringify(protocol)).digest('hex');
const checkpoint=ROOT+'/checkpoint-'+samples+'.json';
let state={fingerprint,startedAt:new Date().toISOString(),rows:[]};
if(fs.existsSync(checkpoint)){state=JSON.parse(fs.readFileSync(checkpoint));if(state.fingerprint!==fingerprint)throw Error('Checkpoint source/protocol mismatch');}
fs.writeFileSync(ROOT+'/protocol-'+samples+'.json',JSON.stringify({...protocol,fingerprint},null,2)+'\n');
let jobs=[...x.anchors.map(p=>({kind:'anchor',id:p.playerId})),...x.players.map(p=>({kind:'player',id:p.playerId}))]
  .filter(j=>!state.rows.some(r=>r.job.kind===j.kind&&r.job.id===j.id)).map(j=>({...j,samples,seed}));
if(process.env.OVR_LIMIT)jobs=jobs.slice(0,Number(process.env.OVR_LIMIT));
const workers=Math.min(Number(process.env.OVR_WORKERS??8),os.availableParallelism(),jobs.length),ws=[];
const start=Date.now();let next=0,done=0;
const save=()=>{state.updatedAt=new Date().toISOString();fs.writeFileSync(checkpoint,JSON.stringify(state)+'\n');};
try{await new Promise((resolve,reject)=>{
  if(!jobs.length)return resolve();
  const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
  for(let i=0;i<workers;i++){
    const w=new Worker(new URL('./worker.mjs',import.meta.url));ws.push(w);w.on('error',reject);
    w.on('message',m=>{if(m.error)return reject(Error(m.error));state.rows.push(m);save();done++;
      console.log(JSON.stringify({done,total:jobs.length,cached:state.rows.length,name:m.result.name,
        winRate:m.result.winRate,seconds:Math.round((Date.now()-start)/1000)}));
      if(done===jobs.length)resolve();else dispatch(w);
    });dispatch(w);
  }
});}finally{await Promise.all(ws.map(w=>w.terminate()));}
for(const [file,expected] of Object.entries(hashes))if(hash(file)!==expected)throw Error('Source changed during calculation: '+file);
save();console.log('Finished '+state.rows.length+' measurements');

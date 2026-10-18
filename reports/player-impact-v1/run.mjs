import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v1',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol={version:'measured-creation-flow-1',seasons:['2022-23','2023-24','2024-25','2025-26'],seeds:[20261012,20261013,20261014],variants:['control','creation-flow','creation-flow-balanced'],
 design:'Handler prior = self-created made-FG production (excluding immediate putback proxy) + AST/min. Own/creation choice uses the same two measured production rates. A completed creation pass terminates with the receiver shot; receiver demand uses assisted-FG production. balanced additionally divides receiving demand by current predicted FG-make probability, avoiding weighting measured makes by efficiency again.',
 limits:'Same-season inputs and all four seasons previously seen. Assisted made-FG share is not an observed assisted-attempt probability. This is a measured role prior, not a new measured handle/offBall score. Putbacks remain in the original rebound path. No player-name/ranking adjustments, no use of on/off outcomes to set cards.',
 validation:'All-player PTS/AST/REB/STL/BLK/FG/3P; strict matching-game on-court team and teammate FG/3P, OFF only same games in which the player was available. Full-season gameplay guardrails. SGA/Luka/Jokic and guard representation checked on equal-exposure natural-position OVR, never edited directly.',
 hashes:Object.fromEntries(['engine.mjs','input.mjs','worker.mjs','on-court.mjs','run.mjs','prepare.py',...['2022-23','2023-24','2024-25','2025-26'].flatMap(s=>[s+'-cards.json',s+'-on-court-truth.json'])].map(f=>root+'/'+f).concat(['src/shot_creation_model.js','src/individual_box_allocation.js','src/defense_fourth_game.js','src/probability_model.js']).map(f=>[f,hash(f)]))};
const pf=root+'/protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Source changed: use a new version');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
// First diagnostic slice includes one full season and one strictly matched
// on-court replay for each variant. Expand only after inspecting mechanisms.
const jobs=protocol.variants.flatMap(version=>[false,true].map(strict=>({season:'2025-26',seed:20261012,version,strict,onCourt:strict,file:`${root}/runs/2025-26-${version}-${strict?'strict':'full'}-20261012.json`})));
let next=0,done=0;const pending=jobs.filter(j=>!fs.existsSync(j.file)),workers=[];
try{await new Promise((resolve,reject)=>{if(!pending.length)return resolve();const dispatch=w=>{if(next<pending.length)w.postMessage(pending[next++]);};for(let i=0;i<Math.min(4,pending.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:pending.length,...m.job,games:m.result.games}));if(done===pending.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const[f,h]of Object.entries(protocol.hashes))if(hash(f)!==h)throw Error('Source drift: '+f);
fs.writeFileSync(root+'/manifest-diagnostic.json',JSON.stringify({jobs:jobs.map(j=>({...j,sha256:hash(j.file)}))},null,2));

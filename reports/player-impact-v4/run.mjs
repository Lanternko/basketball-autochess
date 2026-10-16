import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v4',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const protocol={version:'balanced-source-opportunity-4',seasons:['2022-23','2023-24','2024-25','2025-26'],seeds:[20261012,20261013,20261014],variants:['balanced-flow','balanced-contests'],
 design:'FROZEN source-context conversion, NOT counterfactual probability inversion. Self make-rate / predicted FG-event probability; AST-rate / expected receiver FG-event probability. Each passing opportunity adds observed pass-stolen rate, conditioned on current measured defense pressure. One creation pass ends with receiver shot. A decision is already conditioned on finding a receiver, replacing the extra legacy 70-default open gate. No player-name or ranking offsets.',
 limits:'Same-season role inputs, all seasons previously seen. Diagnostic mechanics, not prospective validation. Current model still lacks measured speed, handle/offBall/screen/breakDbl remain 70. No measured miss-level assisted shot labels.',
 hashes:Object.fromEntries(['engine.mjs','model.mjs','input.mjs','worker.mjs','run.mjs',...['2022-23','2023-24','2024-25','2025-26'].map(s=>s+'-cards.json')].map(f=>root+'/'+f).concat(['reports/player-impact-v1/input.mjs','src/probability_model.js','src/defense_fourth_game.js']).map(f=>[f,hash(f)]))};
const pf=root+'/protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Source changed: use a new version');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const jobs=protocol.variants.flatMap(version=>[false].map(strict=>({season:'2025-26',seed:20261012,version,strict,onCourt:strict,file:`${root}/runs/2025-26-${version}-${strict?'strict':'full'}-20261012.json`})));
let next=0,done=0;const pending=jobs.filter(j=>!fs.existsSync(j.file)),workers=[];
try{await new Promise((resolve,reject)=>{if(!pending.length)return resolve();const dispatch=w=>{if(next<pending.length)w.postMessage(pending[next++]);};for(let i=0;i<Math.min(4,pending.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:pending.length,...m.job,games:m.result.games}));if(done===pending.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const[f,h]of Object.entries(protocol.hashes))if(hash(f)!==h)throw Error('Source drift: '+f);
fs.writeFileSync(root+'/manifest-diagnostic.json',JSON.stringify({jobs:jobs.map(j=>({...j,sha256:hash(j.file)}))},null,2));

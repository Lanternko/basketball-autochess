import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';
const root='reports/player-impact-v6',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const dependencies=['src/constants.js','src/probability_model.js','src/defense_fourth_game.js','src/defense_fourth_season.js','src/defense_probability.js','src/defense_fourth_effects.js','src/individual_box_allocation.js','reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs',
 ...[1,2,3,4,5,6].flatMap(v=>fs.readdirSync(`reports/player-impact-v${v}`).filter(f=>/\.(mjs|js|py)$/.test(f)).map(f=>`reports/player-impact-v${v}/`+f)),
 ...['2022-23','2023-24','2024-25','2025-26'].flatMap(s=>[`reports/player-impact-v6/${s}-cards.json`,`reports/player-impact-v1/${s}-cards.json`,`reports/player-impact-v2/${s}-risk.json`,`reports/player-impact-v1/${s}-on-court-truth.json`])];
const protocol={version:'terminal-flow-validation-6',seasons:['2022-23','2023-24','2024-25','2025-26'],seeds:[20261012,20261013,20261014],variants:['terminal-flow','terminal-contests'],
 limits:'Four previously seen seasons, current-season official input cards; this tests internal fidelity, not prospective player/team prediction. Raw on/off is descriptive and confounded. No on/off or ranking fit. Low-minute players exported but primary minute-weighted errors use >=500 actual minutes.',
 gates:{individual:'Four-season PTS/AST/DREB/BLK mean MAE improves; report OREB/STL/TOV and each season separately, reject material regressions.',team:'No automatic promotion if net RMSE > control+0.30 or wins MAE > control+0.50 or mean PPG bias >1.5; compare matching seed ensembles.',onCourt:'No automatic promotion if main team/teammate FG or 3P MAE rises >0.20 percentage points; matched strict game sets.',ovr:'All-player natural-position equal-exposure scan required; 20-player screen cannot establish Top50. SGA/Luka/Jokic desired Top10-20, guard representation visible, no name-specific adjustment.'},
 hashes:Object.fromEntries([...new Set(dependencies)].sort().map(f=>[f,hash(f)]))};
const pf=root+'/validation-protocol.json';if(fs.existsSync(pf)){if(JSON.stringify(JSON.parse(fs.readFileSync(pf)))!==JSON.stringify(protocol))throw Error('Validation source drift');}else fs.writeFileSync(pf,JSON.stringify(protocol,null,2));
fs.mkdirSync(root+'/runs',{recursive:true});
const all=protocol.seasons.flatMap(season=>protocol.seeds.flatMap(seed=>protocol.variants.flatMap(version=>[false,true].map(strict=>({season,seed,version,strict,onCourt:strict,file:`${root}/runs/${season}-${version}-${strict?'strict':'full'}-${seed}.json`})))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};for(let i=0;i<Math.min(4,jobs.length);i++){
 const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,version:m.job.version,strict:m.job.strict,seed:m.job.seed,games:m.result.games}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
}});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const [f,h]of Object.entries(protocol.hashes))if(hash(f)!==h)throw Error('Validation source drift: '+f);
fs.writeFileSync(root+'/validation-manifest.json',JSON.stringify({games:all.reduce((s,j)=>s+(j.strict?JSON.parse(fs.readFileSync(`reports/player-impact-v1/${j.season}-on-court-truth.json`)).strictGames:1230),0),jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

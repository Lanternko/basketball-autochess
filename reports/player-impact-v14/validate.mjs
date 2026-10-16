import fs from 'node:fs';
import crypto from 'node:crypto';
import {Worker} from 'node:worker_threads';

const root='reports/player-impact-v14',previous=JSON.parse(fs.readFileSync('reports/player-impact-v6/validation-protocol.json'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const[f,h]of Object.entries(previous.hashes))if(hash(f)!==h)throw Error('Previously frozen source drift: '+f);
const sources=[
 'src/source_rotation_energy.js','src/measured_creation_context.js','src/opportunity_transport.js','src/individual_team_accounting.js',
 'reports/player-impact-team-clock/season-source.mjs','reports/player-impact-v7/model.mjs',
 'reports/player-impact-v8/model.mjs','reports/player-impact-v8/usage-fit.json','reports/player-impact-v8/assist-fit.json',
 'reports/player-impact-v9/model.mjs','reports/player-impact-v9/input.mjs','reports/player-impact-v11/model.mjs',
 'reports/player-impact-validation/fast-model.mjs',
 ...['engine.mjs','model.mjs','input.mjs','worker.mjs','prepare.mjs'].map(f=>root+'/'+f),
 ...previous.seasons.map(s=>root+'/'+s+'-contexts.json'),
 ...previous.seasons.map(s=>'reports/player-impact-v7/'+s+'-center.json')
];
const protocol={version:'rotation-source-context-validation-14',seasons:previous.seasons,seeds:previous.seeds,variants:['rotation-space'],
 design:'Four historically seen seasons, matching archived seeds and strict PBP games. Same-season reconstruction, not prospective accuracy. Mean source rotation energy is centered with source lineup/creation context; future fatigue deviations remain. Production-based spacing/creation proxies, exact zero-diagonal creation transport, role elasticity fitted to actual actor choices, team-only clock turnovers. No player names, OVR ranks or on/off outcomes used as fit targets.',
 evaluation:{primaryMinimumActualMinutes:500,equalSeasonWeight:true,individualMetrics:'actual-minute weighted per36 and source-attempt qualified FG; high-usage subgroup separately',onCourt:'same-game ON/OFF and teammate FG, descriptive rather than causal',teamWinsMaeMargin:.5},
 hashes:{...previous.hashes,...Object.fromEntries(sources.map(f=>[f,hash(f)]))}};
const file=root+'/validation-protocol.json';
if(fs.existsSync(file)){if(JSON.stringify(JSON.parse(fs.readFileSync(file)))!==JSON.stringify(protocol))throw Error('Validation source drift');}
else fs.writeFileSync(file,JSON.stringify(protocol,null,2));
const all=protocol.seasons.flatMap(season=>protocol.seeds.flatMap(seed=>[false,true].map(strict=>({season,seed,version:'rotation-space',strict,onCourt:strict,file:`${root}/runs/${season}-rotation-space-${strict?'strict':'full'}-${seed}.json`}))));
const jobs=all.filter(j=>!fs.existsSync(j.file));let next=0,done=0;const workers=[];
try{await new Promise((resolve,reject)=>{
 if(!jobs.length)return resolve();const dispatch=w=>{if(next<jobs.length)w.postMessage(jobs[next++]);};
 for(let i=0;i<Math.min(4,jobs.length);i++){
  const w=new Worker(new URL('./worker.mjs',import.meta.url));workers.push(w);w.on('error',reject);
  w.on('message',m=>{if(m.error)return reject(Error(m.error));console.log(JSON.stringify({done:++done,total:jobs.length,season:m.job.season,seed:m.job.seed,strict:m.job.strict}));if(done===jobs.length)resolve();else dispatch(w);});dispatch(w);
 }
});}finally{await Promise.all(workers.map(w=>w.terminate()));}
for(const[f,h]of Object.entries(protocol.hashes))if(hash(f)!==h)throw Error('Post-run source drift: '+f);
fs.writeFileSync(root+'/validation-manifest.json',JSON.stringify({protocolSHA256:hash(file),jobs:all.map(j=>({...j,sha256:hash(j.file)}))},null,2));

import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-t1',read=p=>JSON.parse(fs.readFileSync(p));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const protectedHashes=read(root+'/protected-before.json'),issues=[];
for(const [p,h] of Object.entries(protectedHashes))if(!fs.existsSync(p)||hash(p)!==h)issues.push({reason:'protected file changed',file:p});
const p=read(root+'/protocol.json'),a=read(root+'/analysis.json');
if(hash(root+'/protocol.json')!==a.protocolHash||a.protocolHash!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])issues.push({reason:'protocol hash'});
for(const [file,h] of Object.entries(p.inputHashes))if(hash(file)!==h)issues.push({reason:'scoring source changed',file});
const summaries=[];let verifiedRuns=0;
for(const c of a.cells){
  let files;
  if(c.task==='task1'){
    const m=read(c.source);files=m.files.map(f=>f.file);
    for(const f of m.files)if(hash(f.file)!==f.sha256)issues.push({reason:'legacy manifest mismatch',file:f.file});
  }else files=p.seeds.map(seed=>c.version==='L1'?`reports/defense-tenth/step3-a/preseason-schedule/runs/${c.season}-oracle-${seed}.json`:`reports/defense-tenth/step3-a2/runs/${c.season}-L2-${seed}.json`);
  const runs=files.map(read);verifiedRuns+=runs.length;
  if(runs.length!==20||new Set(runs.map(r=>r.seed)).size!==20)issues.push({reason:'seed coverage',season:c.season,version:c.version});
  let maxDifference=0;
  for(const t of c.teams){
    const rt=runs.map(r=>r.teams.find(x=>x.id===t.id));
    const avg=fn=>rt.reduce((s,x)=>s+fn(x),0)/rt.length;
    const values={wins:avg(x=>x.wins),net:avg(x=>(x.stats.pts-x.opponent.pts)/x.games),off:avg(x=>x.stats.pts/x.games),allowed:avg(x=>x.opponent.pts/x.games)};
    for(const [k,v] of Object.entries(values)){const d=Math.abs(v-t[k]);maxDifference=Math.max(maxDifference,d);if(d>1e-9)issues.push({reason:'stored aggregate does not reproduce',season:c.season,version:c.version,team:t.name,k,d});}
    if(Math.abs(t.O+t.D-t.netError)>1e-9)issues.push({reason:'error identity',team:t.name});
  }
  const allTeams=runs.flatMap(r=>r.teams),meanActualMinuteMAE=allTeams.reduce((s,t)=>s+t.minuteError,0)/allTeams.reduce((s,t)=>s+t.playerGames,0);
  summaries.push({task:c.task,season:c.season,version:c.version,runs:runs.length,matches:runs.reduce((s,r)=>s+r.matches.length,0),maximumAggregateDifference:maxDifference,meanActualMinuteMAE});
}
const real=read(root+'/real-diagnostics.json');
const validCoverage=Object.fromEntries(Object.entries(real).map(([s,j])=>[s,{minimumTeamCoverage:Math.min(...j.teams.map(t=>t.clutchCoverage)),validGames:j.validGames,missingOrInvalid:j.failures.length}]));
const audit={completedAt:new Date().toISOString(),issues,protectedFiles:Object.keys(protectedHashes).length,verifiedExistingRuns:verifiedRuns,summaries,validCoverage,protocolHash:a.protocolHash,newSimulations:0,unchanged:['A','A2','src'],stopAt:'T1'};
fs.writeFileSync(root+'/completion-audit.json',JSON.stringify(audit,null,2)+'\n');
const outputs=fs.readdirSync(root).filter(f=>fs.statSync(root+'/'+f).isFile()&&f!=='deliverable-hashes.json').sort();
fs.writeFileSync(root+'/deliverable-hashes.json',JSON.stringify(Object.fromEntries(outputs.map(f=>[f,hash(root+'/'+f)])),null,2)+'\n');
console.log(JSON.stringify(audit));
if(issues.length)process.exitCode=1;

import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {playerErrors} from './diagnose_defense_seventh.js';
import {seventhInputs} from '../src/defense_seventh_jobs.js';
const root='reports/defense-seventh',result={cutoffs:{},definition:'All calendar heldout official appearances, minute-weighted MAE/RMSE/bias; ratios pp. Bounds from actual deployed calibrated cards, unique playerID; all engine ability attributes audited, not just shooting.'},attrs=['long','mid','short','ft','drive','tovSkill','pass','rebound','stamina','physique','onBall','help','offBall','screen','handle','breakDbl'];
for(const k of [25,41,55]){
 const c=read(`${root}/2025-26/calendar-${k}/config.json`),r={date:c.date};
 for(const version of ['v3','v4']){
  const label='2025-26-calendar-'+k+'-'+version,m=read(root+'/'+label+'-seeds.json'),b=seventhInputs(m.extra),unique=[...new Map(b.league.teams.flatMap(t=>t.roster.map(p=>[p.playerId,p]))).values()],bounds=unique.filter(p=>attrs.some(z=>p[z]<=1e-6||p[z]>=120-1e-6));
  r[version]={...playerErrors(loadSeventh(label),k,c.date),bounds:bounds.map(p=>({id:p.playerId,name:p.name,attributes:Object.fromEntries(attrs.filter(z=>p[z]<=1e-6||p[z]>=120-1e-6).map(z=>[z,p[z]]))}))};
 }result.cutoffs[k]=r;console.log(k,'PLAYER MAE',JSON.stringify(Object.fromEntries(['v3','v4'].map(v=>[v,{errors:Object.fromEntries(Object.entries(r[v].metrics).map(([z,m])=>[z,m.MAE])),bounds:r[v].bounds.length}]))));
}
fs.writeFileSync(root+'/calendar-player-diagnosis.json',JSON.stringify(result,null,2)+'\n');

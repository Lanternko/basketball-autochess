import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step4-t0',s='2023-24',root=d+'/'+s,c=read(root+'/config.json'),b=read(c.leagueOutput),ex=read(c.exposure),records=[];
for(const t of b.teams)for(const p of t.roster){
 for(const kind of ['offenseMeasurement','defenseMeasurement'])if(p[kind].minutes===0){const ts=ex.games.flatMap(g=>g.teams.filter(x=>kind==='defenseMeasurement'||x.teamId===t.id).flatMap(x=>x.players.filter(x=>x.playerId===p.playerId)));const minutes=ts.reduce((s,x)=>s+x.seconds,0)/60;records.push({teamId:t.id,playerId:p.playerId,name:p.name,kind,logged:0,exactBoxMinutes:minutes,replacement:minutes||1});p[kind].minutes=minutes||1;}
}
b.provenance.zeroMinuteCorrections=records;fs.writeFileSync(root+'/v3-league-positive-minutes.json',JSON.stringify(b)+'\n');c.leagueOutput=root+'/v3-league-positive-minutes.json';c.paths['data/season-league.json']=c.leagueOutput;fs.writeFileSync(root+'/config-positive-minutes.json',JSON.stringify(c,null,2)+'\n');
if(fs.existsSync(root+'/bundle.json'))fs.copyFileSync(root+'/bundle.json',root+'/bundle-before-positive-minutes.json');
fs.writeFileSync(root+'/zero-minute-corrections.json',JSON.stringify({at:new Date().toISOString(),supplementSHA:hash(d+'/zero-minute-supplement.json'),records},null,2)+'\n');console.log(records);

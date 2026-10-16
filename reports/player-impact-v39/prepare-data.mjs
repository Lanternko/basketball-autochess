// Group actual missed FGAs by whole game, defensive five and shot zone.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../player-impact-v30/input.mjs';
const root='reports/player-impact-v39',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const out=root+'/'+season+'-miss-data.json';assert.ok(!fs.existsSync(out));
 const input=loadInput(season),players=new Map(input.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,{playerId:p.playerId,name:p.name,position:p.pos}]));
 const tf=`reports/player-impact-v1/${season}-on-court-truth.json`,valid=new Set(read(tf).gameIds),mf=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',specs=new Map(read(mf).sources.map(s=>[s.id,s]));
 const sf=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,frames=new Map(),hashes={};
 for(const line of fs.readFileSync(sf,'utf8').trim().split('\n')){const s=JSON.parse(line);if(valid.has(s.id)&&s.seconds>=0){const rows=frames.get(s.id)??[];rows.push(s);frames.set(s.id,rows);}}
 const rows=[],minutes=[];let fga=0,misses=0,blocks=0;
 for(const [id,stints]of frames){
  const file=specs.get(id).file,actions=read(file).data.game.actions;hashes[file]=sha(file);const grouped=new Map(),exposure=new Map(),fold=parseInt(crypto.createHash('sha256').update(id).digest('hex').slice(0,8),16)%5;
  for(const s of stints){
   const ids=s.teams.map(t=>[...t.players].sort((a,b)=>a-b));
   for(const side of [0,1])for(const pid of ids[side])exposure.set(pid,(exposure.get(pid)??0)+s.seconds/60);
   const local=[0,0];
   for(let i=s.startIndex;i<s.endIndex;i++){
    const e=actions[i];if(!e.isFieldGoal||!['2pt','3pt'].includes(e.actionType))continue;
    const off=s.teams.findIndex(t=>t.teamId===e.teamId);assert.ok(off>=0);local[1-off]++;fga++;
    if(e.shotResult==='Made'){assert.ok(!e.blockPersonId);continue;}
    assert.equal(e.shotResult,'Missed');const def=1-off,zone=e.actionType==='3pt'?0:e.area==='Mid-Range'?1:2,key=s.teams[def].teamId+':'+ids[def].join(',')+':'+zone;
    let row=grouped.get(key);if(!row){row=[id,fold,s.teams[def].teamId,zone,ids[def],0,[0,0,0,0,0]];grouped.set(key,row);}row[5]++;misses++;
    if(e.blockPersonId){const index=ids[def].indexOf(e.blockPersonId);assert.ok(index>=0);row[6][index]++;blocks++;}
   }
   for(const side of [0,1])assert.equal(local[side],s.teams[side].opponent.fga);
  }
  rows.push(...grouped.values());minutes.push([id,fold,[...exposure]]);
 }
 assert.equal(frames.size,valid.size);for(const r of rows)assert.ok(r[6].reduce((s,v)=>s+v,0)<=r[5]);
 for(const f of [sf,mf,tf,root+'/prepare-data.mjs','reports/player-impact-v30/validation-protocol.json'])hashes[f]=sha(f);
 fs.writeFileSync(out,JSON.stringify({season,columns:['gameId','fold','defensiveTeam','zoneIndex','playerIds','misses','blocksByPlayer'],zones:['long','mid','short'],coverage:{games:frames.size,fga,misses,blocks,rows:rows.length},players:[...players.values()],minutes,rows,hashes}));console.log(JSON.stringify({season,...{games:frames.size,fga,misses,blocks,rows:rows.length}}));
}

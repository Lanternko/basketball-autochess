import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v20/input.mjs';
import {pressureSignal} from '../../src/defense_probability.js';
const root='reports/player-impact-v21',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-terminal-events.json`;if(fs.existsSync(output))throw Error('Preserve source event audit');
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const truth=`reports/player-impact-v1/${season}-on-court-truth.json`,valid=new Set(read(truth).gameIds);
 const stintFile=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`;
 const manifestFile=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json';
 const stints=new Map(),hashes=Object.fromEntries([truth,stintFile,manifestFile,`${root}/build-terminal-risk.mjs`].map(f=>[f,hash(f)]));
 for(const line of fs.readFileSync(stintFile,'utf8').trim().split('\n')){const s=JSON.parse(line);if(valid.has(s.id)){const rows=stints.get(s.id)??[];rows.push(s);stints.set(s.id,rows);}}
 const totals={fga:0,nonpassLive:0,nonpassDead:0,passStolen:0,teamTurnovers:0,unrecordedShootingFouls:0,recordedShootingFouls:0,multipleShotMatches:0,missingDrawn:0,unmappedEvents:0,actorOutsideLineup:0},games=[],issues=[];
 for(const spec of read(manifestFile).sources){
  if(!valid.has(spec.id))continue;hashes[spec.file]=hash(spec.file);
  const actions=read(spec.file).data.game.actions,ss=stints.get(spec.id);if(!ss)throw Error('Missing game stints');
  const shots=new Map();for(const e of actions)if(e.isFieldGoal&&['2pt','3pt'].includes(e.actionType)){const k=[e.period,e.clock,e.personId].join(':');shots.set(k,(shots.get(k)??0)+1);}
  const rows=new Map(),counts={};const add=k=>{counts[k]=(counts[k]??0)+1;totals[k]++;};
  for(let index=0;index<actions.length;index++){
   const e=actions[index];let pid=e.personId,kind=null;
   if(e.isFieldGoal&&['2pt','3pt'].includes(e.actionType)){kind='fga';add(kind);}
   else if(e.actionType==='turnover'){
    if(!pid){add('teamTurnovers');continue;}
    const pass=e.subType==='bad pass'||(e.subType==='out-of-bounds'&&e.descriptor==='bad pass');
    if(pass&&e.stealPersonId){add('passStolen');continue;}
    kind=e.stealPersonId?'nonpassLive':'nonpassDead';add(kind);
   }else if(e.actionType==='foul'&&e.descriptor==='shooting'){
    pid=e.foulDrawnPersonId;if(!pid){add('missingDrawn');continue;}
    const matches=shots.get([e.period,e.clock,pid].join(':'))??0;
    if(matches){add('recordedShootingFouls');if(matches>1)add('multipleShotMatches');continue;}
    kind='unrecordedShootingFouls';add(kind);
   }
   if(!kind)continue;
   const s=ss.find(s=>s.startIndex<=index&&index<s.endIndex);
   if(!s){add('unmappedEvents');issues.push({game:spec.id,index,pid,kind,reason:'outside stint'});continue;}
   const side=s.teams.findIndex(t=>t.players.includes(pid));
   if(side<0){add('actorOutsideLineup');issues.push({game:spec.id,index,pid,kind,reason:'actor outside lineup'});continue;}
   const defense=s.teams[1-side],players=defense.players.map(id=>teams.get(defense.teamId).get(id));
   if(players.some(p=>!p))throw Error('Missing source defender');
   const r=pressureSignal(players,b.options.stealPriorRate).relative,key=pid+':'+s.startIndex;
   const row=rows.get(key)??[pid,0,0,0,r];row[1]++;if(kind==='nonpassDead')row[2]++;if(kind==='nonpassLive')row[3]++;rows.set(key,row);
  }
  games.push({id:spec.id,fold:Number(BigInt(spec.id)%5n),counts,rows:[...rows.values()]});
 }
 const sourceAudit=read(`reports/player-impact-v19/${season}-foul-contact-audit.json`);
 if(totals.fga!==sourceAudit.counts.fga||totals.unrecordedShootingFouls!==sourceAudit.counts.unrecordedShootingFouls)throw Error('Foul/FGA scope drift');
 if(totals.missingDrawn||totals.unmappedEvents||totals.actorOutsideLineup)throw Error('Resolve source mapping before fitting: '+JSON.stringify({totals,issues:issues.slice(0,10)}));
 const players=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,{playerId:p.playerId,name:p.name}])).values()];
 fs.writeFileSync(output,JSON.stringify({season,method:'Strict PBP terminal opportunities: recorded FGA + shooting fouls without same-clock drawn-player FGA + person-attributed TOV excluding bad passes with recorded steal. Pass-stolen has an existing separate branch. Team TOV excluded. Rows [playerId,opportunities,dead,live,opponentPressure]. Same-clock multi-FGA ambiguity retained and counted; no exact foul linkage claimed. Pressure uses existing source-STL/min posterior; attributes are unchanged.',rowFields:['playerId','opportunities','dead','live','opponentPressure'],totals,players,games,hashes}));
 console.log(JSON.stringify({season,games:games.length,totals,rows:games.reduce((a,g)=>a+g.rows.length,0)}));
}

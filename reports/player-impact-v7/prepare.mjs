import fs from 'node:fs';
import crypto from 'node:crypto';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {loadInput} from '../player-impact-v6/input.mjs';
const root='reports/player-impact-v7';fs.mkdirSync(root,{recursive:true});
// Center the enabled teammate-context term against source lineups. These are
// source-exposure weights, without using FG outcomes or on/off answers to fit it.
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,valid=new Set(JSON.parse(fs.readFileSync(`reports/player-impact-v1/${season}-on-court-truth.json`)).gameIds);
 const memo=new Map();let num=0,den=0,stints=0;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){
  const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<=0)continue;stints++;
  for(const t of s.teams){
   const team=teams.get(t.teamId);if(t.players.some(id=>!team.has(id)))throw Error('Unknown strict-lineup player');
   const key=t.teamId+':'+t.players.join(',');let cell=memo.get(key);
   if(!cell){const ls=t.players.map(id=>team.get(id));cell=ls.map((p,i)=>{
    const ctx=M.teammateContext(ls,i),opts={contextScale:0},q0=M.possessionProbabilities(p,ctx,{onBall:70},70,70,70,70,opts),q1=M.possessionProbabilities(p,ctx,{onBall:70},70,70,70,70,{contextScale:1});
    const rate=p.observed.MIN>0?p.observed.FG3A/p.observed.MIN:0;
    return {delta:q1.make.long-q0.make.long,rate};
   });memo.set(key,cell);}
   for(const c of cell){num+=s.seconds*c.rate*c.delta;den+=s.seconds*c.rate;}
  }
 }
 const out={season,fullCenter:num/den,strictStints:stints,uniqueLineups:memo.size,design:'Mean contextLong full-minus-zero predicted make difference, source strict lineup seconds times observed 3PA/min. No FG outcomes, on/off targets, names or OVR ranks fit. Shared centering constant keeps source league accuracy from absorbing a uniform boost while retaining relative passing/spacing effects.',source:{file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')}};
 fs.writeFileSync(`${root}/${season}-center.json`,JSON.stringify(out,null,2));console.log(JSON.stringify(out));
}

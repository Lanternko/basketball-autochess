import fs from 'node:fs';
import {read,table} from '../../../scripts/defense_io.js';
import {REBOUND_RULES} from '../../../src/rebound_block_model.js';
import {root,verify} from './run.mjs';
verify();const p=read(root+'/protocol.json'),mean=a=>a.reduce((s,x)=>s+x,0)/a.length,sd=a=>Math.sqrt(mean(a.map(x=>(x-mean(a))**2))),corr=(a,b)=>mean(a.map((x,i)=>(x-mean(a))*(b[i]-mean(b))))/(sd(a)*sd(b));
const out=[];
for(const season of p.seasons){
 const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),cards=read(`${root}/${season}/cards.json`).players,base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`,logs=table(base+'/player-games.json'),teams=table(base+'/team-games.json'),rows=[];
 for(const t of b.league.teams){const rs=logs.filter(r=>r.TEAM_ID===t.id),minutes=rs.reduce((s,r)=>s+r.MIN,0),pm=new Map(t.roster.map(q=>[q.playerId,q])),tm=new Map();for(const r of rs)tm.set(r.PLAYER_ID,(tm.get(r.PLAYER_ID)??0)+r.MIN);
  let raw=0,shrunk=0,old=0;for(const[id,min]of tm){const q=pm.get(id),c=cards[id];if(!q||!c)throw Error('Missing player');raw+=min*(c.rawShare??c.share);shrunk+=min*c.share;const near=REBOUND_RULES.inside[q.courtPosition??q.pos]??.5,long=REBOUND_RULES.longBounce.short;old+=min*((1-long)*near+long*(1-near))*Math.exp((.7*q.rebound+.3*q.physique-70)/45);}
  const tr=teams.filter(r=>r.TEAM_ID===t.id),dreb=tr.reduce((s,r)=>s+r.DREB,0),oreb=tr.reduce((s,r)=>s+teams.find(o=>o.GAME_ID===r.GAME_ID&&o.TEAM_ID!==t.id).OREB,0);rows.push({id:t.id,name:t.name,rawFiveShares:5*raw/minutes,posteriorFiveShares:5*shrunk/minutes,oldInteriorContest:5*old/minutes,actualDrebPct:100*dreb/(dreb+oreb)});
 }
 const clipping={starters:0,lower:0,upper:0};for(const g of b.exposure.games)for(const t of g.teams){const starter=t.players.filter(q=>q.starter);if(starter.length!==5)continue;const n=starter.reduce((s,q)=>s+cards[q.playerId].share,0);clipping.starters++;if(n<.05)clipping.lower++;if(n>.95)clipping.upper++;}
 out.push({season,label:'Post-registration input diagnostic; not used to tune or fit the candidate',rawShareCorrelation:corr(rows.map(r=>r.rawFiveShares),rows.map(r=>r.actualDrebPct)),posteriorShareCorrelation:corr(rows.map(r=>r.posteriorFiveShares),rows.map(r=>r.actualDrebPct)),oldInteriorContestCorrelation:corr(rows.map(r=>r.oldInteriorContest),rows.map(r=>r.actualDrebPct)),startingLineupClipping:clipping,teams:rows});
}
fs.writeFileSync(root+'/input-diagnostic.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out.map(({teams,...o})=>o)));

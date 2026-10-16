import fs from 'node:fs';
import {read} from '../../../scripts/defense_io.js';
import {REBOUND_RULES} from '../../../src/rebound_block_model.js';
import {root,verify} from './run.mjs';
verify();const p=read(root+'/protocol.json'),prior=read(root+'/input-diagnostic.json'),mean=a=>a.reduce((s,x)=>s+x,0)/a.length,sd=a=>Math.sqrt(mean(a.map(x=>(x-mean(a))**2))),corr=(a,b)=>mean(a.map((x,i)=>(x-mean(a))*(b[i]-mean(b))))/(sd(a)*sd(b));
const output=[];
for(const season of p.seasons){const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),tm=new Map(b.league.teams.map(t=>[t.id,t])),agg=new Map(),positionMinutes={};
 for(const g of b.exposure.games)for(const t of g.teams){const roster=new Map(tm.get(t.teamId).roster.map(q=>[q.playerId,q]));let a=agg.get(t.teamId)??{seconds:0,contest:0};for(const r of t.players){if(r.seconds<=0)continue;const q=roster.get(r.playerId),pos=(r.starter||["PG","SG","G","SF","PF","F","C"].includes(r.position))?r.position:(q.courtPosition??q.pos),near=REBOUND_RULES.inside[pos]??.5,long=REBOUND_RULES.longBounce.short;a.seconds+=r.seconds;a.contest+=r.seconds*((1-long)*near+long*(1-near))*Math.exp((.7*q.rebound+.3*q.physique-70)/45);if(q.name==='Josh Hart'){const key=t.teamId+'/'+pos;positionMinutes[key]=(positionMinutes[key]??0)+r.seconds/60;}}agg.set(t.teamId,a);}
 const before=prior.find(x=>x.season===season),teams=before.teams.map(t=>({...t,nominalOldContest:t.oldInteriorContest,gamePositionOldContest:5*agg.get(t.id).contest/agg.get(t.id).seconds}));
 output.push({season,label:'Post hoc diagnostic; not a candidate change. Earlier input-diagnostic uses nominal card positions, while actual game starters override those positions.',nominalOldCorrelation:before.oldInteriorContestCorrelation,officialGamePositionOldCorrelation:corr(teams.map(t=>t.gamePositionOldContest),teams.map(t=>t.actualDrebPct)),individualPosteriorCorrelation:before.posteriorShareCorrelation,hartPositionMinutes:positionMinutes,teams});}
fs.writeFileSync(root+'/game-position-diagnostic.json',JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output.map(({teams,...s})=>s)));


import {read,table} from '../scripts/defense_io.js';
import {seventhInputs} from './defense_seventh_jobs.js';
import {thirdLineup} from './defense_third_minutes.js';
import {makeRng} from './rng.js';
export const seasonsN=['2024-25','2025-26','2023-24','2022-23'],cutoffsN=[25,41,55],seedsN=Array.from({length:20},(_,i)=>20261012+i);
export const configN=(s,k)=>`reports/defense-seventh/${s}/calendar-${k}/config.json`;
export function inputN(c,v){
 const mf=read(`reports/defense-seventh/${c.season}-calendar-${c.k}-${v}-seeds.json`),base=seventhInputs(mf.extra),all=new Map();
 for(const t of base.league.teams)for(const p of t.roster)if(!all.has(p.playerId))all.set(p.playerId,p);
 const e=new Map(base.exposure.games.map(g=>[g.id,g])),pools=new Map(base.league.teams.map(t=>[t.id,[]])),templates=new Map();
 for(const g of base.league.schedule)if(g.date<=c.date)for(const [side,id]of [g.homeId,g.awayId].entries()){
  const ids=g[side?'awayPlayerIds':'homePlayerIds'],team=e.get(g.id).teams.find(t=>t.teamId===id),players=team.players.filter(p=>ids.includes(p.playerId));
  if(players.filter(p=>p.starter).length!==5||players.length!==ids.length)throw Error('Invalid training roster template '+g.id+'/'+id);
  const template={sourceGame:g.id,date:g.date,ids,players:players.map(p=>({playerId:p.playerId,starter:p.starter,position:p.position}))};pools.get(id).push(template);
 }
 for(const t of base.league.teams){
  const native=new Map(t.roster.map(p=>[p.playerId,p]));for(const z of pools.get(t.id))for(const id of z.ids)if(!native.has(id)){if(!all.has(id))throw Error('No cutoff card '+id);native.set(id,structuredClone(all.get(id)));}
  // Added cards preserve every cutoff attribute. The actual active list is unchanged.
  t.roster=[...native.values()];templates.set(t.id,native);
 }
 return {...base,pools,templates,manifest:mf,config:c};
}
export function sampleTemplateN(base,fixture,index,side,seed){
 const id=side?fixture.awayId:fixture.homeId,pool=base.pools.get(id),rng=makeRng(((seed^0x9B137AC1)+Math.imul(index+1,7919)+side)>>>0);
 return pool[Math.floor(rng()*pool.length)];
}
export function pairN(base,fixture,index,seed,counterfactual=false){
 const ex=base.exposure.games.find(g=>g.id===fixture.id);
 return [fixture.homeId,fixture.awayId].map((id,side)=>{
  const team=base.league.teams.find(t=>t.id===id),template=counterfactual?sampleTemplateN(base,fixture,index,side,seed):null,ids=template?.ids??fixture[side?'awayPlayerIds':'homePlayerIds'];
  const original=template?.players??ex.teams.find(t=>t.teamId===id).players;
  const players=original.filter(p=>ids.includes(p.playerId)).map(p=>({playerId:p.playerId,starter:p.starter,position:p.position,seconds:60*(base.templates.get(id).get(p.playerId).seasonMinutesPerGame??20)}));
  return thirdLineup(team,ids,{teamId:id,players},true);
 });
}
export function counterfactualN(base,seed){
 const league=structuredClone(base.league),exposure=structuredClone(base.exposure),ex=new Map(exposure.games.map(g=>[g.id,g]));
 for(const [index,g]of league.schedule.entries())if(g.date>base.config.date){
  for(const [side,id]of [g.homeId,g.awayId].entries()){
   const template=sampleTemplateN(base,g,index,side,seed);g[side?'awayPlayerIds':'homePlayerIds']=[...template.ids];
   const t=ex.get(g.id).teams.find(t=>t.teamId===id);t.players=template.players.map(p=>({...p,seconds:60*(base.templates.get(id).get(p.playerId).seasonMinutesPerGame??20)}));
  }
 }
 return {league,exposure,options:base.options};
}
export function analyticN(base){
 const c=base.config,model=read(c.root+'/ability-model-forward.json'),role=model.models.role,ids=new Map(model.players.map((id,i)=>[id,i])),w=model.minutes,ws=w.reduce((a,b)=>a+b,0),wm=a=>a.reduce((s,x,i)=>s+x*w[i],0)/ws;
 const fallbackO=wm(role.priorOffense),fallbackD=wm(role.priorDefenseAllowed),PM=new Map();
 for(const r of table(c.paths['data/season-source/player-games.json']))if(r.GAME_DATE.slice(0,10)<=c.date){const a=PM.get(r.PLAYER_ID)??{minutes:0,pm:0};a.minutes+=r.MIN;a.pm+=r.PLUS_MINUS;PM.set(r.PLAYER_ID,a);}
 const rows=table(c.paths['data/season-source/team-games.json']).filter(r=>r.GAME_DATE.slice(0,10)<=c.date),poss=rows.reduce((s,r)=>s+r.FGA-r.OREB+r.TOV+.44*r.FTA,0)/rows.length;
 const missing=new Set(),eta=(off,def)=>{
  let n=role.intercept;for(const [team,prior,residual,fallback]of [[off,role.priorOffense,role.offenseResidual,fallbackO],[def,role.priorDefenseAllowed,role.defenseResidual,fallbackD]])for(const p of team.roster){const i=ids.get(p.playerId);if(i===undefined)missing.add(p.playerId);n+=p.targetMinutes/240*(i===undefined?fallback:prior[i]+residual[i]);}
  return Math.exp(Math.max(-8,Math.min(8,n)));
 };
 const naive=t=>t.roster.reduce((s,p)=>{const r=PM.get(p.playerId);return s+p.targetMinutes*(r?.minutes>0?r.pm/r.minutes:0)/5;},0);
 return {seg:pair=>poss*(eta(pair[0],pair[1])-eta(pair[1],pair[0])),naive:pair=>naive(pair[0])-naive(pair[1]),missing,poss,modelFile:c.root+'/ability-model-forward.json'};
}

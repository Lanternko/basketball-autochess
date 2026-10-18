import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {makeRng} from '../../../src/rng.js';
const d='reports/defense-tenth/step3-a',n=d+'/preseason-schedule',p=read(n+'/protocol.json'),slots=['PG','SG','SF','PF','C'];fs.mkdirSync(n+'/bundles',{recursive:true});
for(const[prior,target]of p.pairs){
 const opening=read(target==='2025-26'?'data/defense-seventh/preseason-2025-26/opening-schedule.json':`${d}/opening-schedule-${target}.json`);
 const fixtures=opening.schedule.map(({id,date,homeId,awayId,neutral,neutralSite})=>({id,date,homeId,awayId,neutral:!!(neutral??neutralSite)}));
 for(const seed of p.seeds)for(const mode of ['preseason','oracle']){const old=read(`${d}/bundles/${target}-${mode}-${seed}.json`),league={...structuredClone(old.league),schedule:structuredClone(fixtures)},exposure={games:[]},counter={},rng=makeRng((seed^0x51aa33)>>>0);let fallback=0;
  const queue={};if(mode==='oracle'){const by=new Map(old.exposure.games.map(g=>[g.id,g]));for(const f of old.league.schedule)for(const id of [f.homeId,f.awayId])(queue[id]??=[]).push(by.get(f.id).teams.find(t=>t.teamId===id));}
  for(const f of league.schedule){const ts=[];for(const[i,id]of [f.homeId,f.awayId].entries()){const j=counter[id]??0;counter[id]=j+1;
   if(mode==='oracle'){const t=structuredClone(queue[id][j]);ts.push(t);f[i?'awayPlayerIds':'homePlayerIds']=t.players.map(q=>q.playerId);continue;}
   const t=league.teams.find(t=>t.id===id),eligible=t.roster.filter(q=>j+1>q.preseasonAvailableAfter),active=eligible.filter(q=>rng()<q.preseasonAvailability).sort((a,b)=>b.seasonMinutesPerGame-a.seasonMinutesPerGame||a.playerId-b.playerId);
   for(const q of [...eligible].sort((a,b)=>b.seasonMinutesPerGame-a.seasonMinutesPerGame||a.playerId-b.playerId)){if(active.length>=8)break;if(!active.includes(q)){active.push(q);fallback++;}}active.splice(12);if(active.length<5)throw Error('Not enough players');const starters=[];for(const slot of slots){const rest=active.filter(q=>!starters.includes(q));rest.sort((a,b)=>Math.abs(slots.indexOf(a.pos)-slots.indexOf(slot))-Math.abs(slots.indexOf(b.pos)-slots.indexOf(slot))||b.seasonMinutesPerGame-a.seasonMinutesPerGame||a.playerId-b.playerId);starters.push(rest[0]);}f[i?'awayPlayerIds':'homePlayerIds']=active.map(q=>q.playerId);ts.push({teamId:id,players:active.map(q=>({playerId:q.playerId,seconds:60*q.seasonMinutesPerGame,starter:starters.includes(q),position:starters.includes(q)?slots[starters.indexOf(q)]:q.pos}))});}
   exposure.games.push({id:f.id,teams:ts});
  }
  if(Object.values(counter).some(x=>x!==82))throw Error('Invalid schedule');
  const b={league,exposure,options:old.options,provenance:{prior,target,mode,seed,fallbackSelections:fallback,protocolHash:hash(n+'/protocol.json'),parentBundleHash:hash(`${d}/bundles/${target}-${mode}-${seed}.json`),scheduleType:'pre-opening80plus2assumed',oracleExposureMapping:mode==='oracle'?'same team game ordinal, irrespective of actual opponent':null}};
  fs.writeFileSync(`${n}/bundles/${target}-${mode}-${seed}.json`,JSON.stringify(b)+'\n');
 }
 fs.copyFileSync(`${d}/coverage-${target}.json`,`${n}/coverage-${target}.json`);console.log('OPENING PREP',target);
}
for(const[f,h]of Object.entries(p.fingerprints))if(hash(f)!==h)throw Error('Source changed '+f);
fs.writeFileSync(n+'/prepared.json',JSON.stringify({completedAt:new Date().toISOString(),protocolHash:hash(n+'/protocol.json'),parentProtocolHash:hash(d+'/protocol.json'),unchanged:'All ability attributes, measurements and constants copied byte-equivalent; only fixture/exposure ordering changes',scheduleGames:1230,teamGames:82},null,2)+'\n');

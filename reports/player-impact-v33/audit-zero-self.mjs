// Diagnose impossible unassisted outcomes; no fitted coefficients or runtime edits.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {loadInput} from '../player-impact-v30/input.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
import {supplyFlow} from '../player-impact-v11/model.mjs';
const root='reports/player-impact-v33';
const read=f=>JSON.parse(fs.readFileSync(f));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const seasons=[],players=[],hashes={};
for(const season of ['2022-23','2023-24','2024-25','2025-26']){
 const f=`${root}/${season}-conditional-data.json`,d=read(f),ix=Object.fromEntries(d.columns.map((c,i)=>[c,i]));hashes[f]=hash(f);
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const counts=new Map(),cache=new Map();let actualSelfMakes=0,sourceFlowSaturated=0,nonSaturation=0,offendingStintActors=0;
 for(const row of d.rows)for(let i=0;i<5;i++){
  const n=row[ix.selfMakes][i];
  if(!n||row[ix.selfMakeBase][i]>0||row[ix.selfMakeSlope][i]>0)continue;
  actualSelfMakes+=n;offendingStintActors++;
  const ids=row[ix.playerIds],teamId=row[ix.teamId],key=teamId+':'+ids.join(',');let state=cache.get(key);
  if(!state){const cards=ids.map(pid=>teams.get(teamId).get(pid)),lineup=elasticLineup(cards,'elastic-creation'),flow=supplyFlow(lineup);state={cards,lineup,flow};cache.set(key,state);}
  const {cards,lineup,flow}=state,m=lineup[i].opportunityMeasurement;
  const saturated=Math.abs(flow.self[i])<1e-12&&Math.abs(flow.incoming[i]-m.terminalOpportunityRate)<1e-10;
  if(saturated)sourceFlowSaturated+=n;else nonSaturation+=n;
  const pid=ids[i],p=counts.get(pid)??{season,playerId:pid,name:cards[i].name,actualUnassistedMakesWithZeroModelSupport:0,saturatedIncomingMakes:0,games:new Set(),examples:[]};
  p.actualUnassistedMakesWithZeroModelSupport+=n;if(saturated)p.saturatedIncomingMakes+=n;p.games.add(row[ix.gameId]);
  if(p.examples.length<2)p.examples.push({gameId:row[ix.gameId],teamId,startIndex:row[ix.startIndex],endIndex:row[ix.endIndex],actualSelfMakes:n,sourceSelfRate:m.selfOpportunityRate,assignedSelfRate:flow.self[i],assignedIncomingRate:flow.incoming[i],terminalRate:m.terminalOpportunityRate,saturated});
  counts.set(pid,p);
 }
 for(const p of counts.values())players.push({...p,games:p.games.size});
 seasons.push({season,actualSelfMakes,offendingStintActors,sourceFlowSaturated,nonSaturation,players:counts.size});
 console.log(JSON.stringify(seasons.at(-1)));
}
const expected=read(`${root}/compensation-fit.json`);
for(const s of seasons){const e=expected.seasons.find(x=>x.season===s.season).measurements.find(x=>x.label==='fullCompensation');assert.equal(s.actualSelfMakes,e.unsupportedSelfMakes);}
hashes[`${root}/audit-zero-self.mjs`]=hash(`${root}/audit-zero-self.mjs`);
const out={passed:true,design:'Observed unassisted makes in source stints assigned exactly zero own-make probability at both lambda endpoints. Re-evaluate source flow to distinguish terminal capacity saturation from other causes. No correction or causal interpretation.',seasons,players,hashes};
const file=`${root}/zero-self-audit.json`;assert.ok(!fs.existsSync(file));fs.writeFileSync(file,JSON.stringify(out,null,2));

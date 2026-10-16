import fs from 'node:fs';
import {ovrInput as previousInput} from '../player-impact-v22/ovr-input.mjs';
import {attachChoice,choiceSource} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=structuredClone(await previousInput(season)),src=choiceSource(season);
 attachChoice(x.players,season);for(const t of x.opponents)attachChoice(t.roster,season);
 const source=JSON.parse(fs.readFileSync(`reports/player-impact-v23/${season}-choice-survival.json`)),rows=source.games.flatMap(g=>g.rows),k=src.kappaRebounds,mu=src.leagueSelectionReference;
 x.profiles=x.profiles.map((p,slot)=>{
  const ids=new Set(x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence).map(q=>q.playerId)),pool=rows.filter(r=>ids.has(r[0]));
  if(!pool.length)throw Error('Missing natural-position putback choice opportunities');
  const fastFga=pool.reduce((s,r)=>s+r[1],0),survivalSum=pool.reduce((s,r)=>s+r[2],0);let lo=1e-10,hi=1-1e-10;
  for(let j=0;j<36;j++){
   const theta=(lo+hi)/2,failure=pool.reduce((s,r)=>s+(1-r[1])*r[2]/(1-theta*r[2]),0),gradient=(fastFga+k*mu)/theta-k*(1-mu)/(1-theta)-failure;
   if(gradient>0)lo=theta;else hi=theta;
  }
  return {...p,putbackChoiceMeasurement:{rebounds:pool.length,fastFga,survivalSum,selectionProbabilityMAP:(lo+hi)/2,source:'Confident natural-position source opportunity pool, same source-survival likelihood and common Beta prior as individual cards; original-source style held fixed under counterfactuals. Attributes remain arithmetic mean70.'}};
 });
 cache.set(season,x);return x;
}

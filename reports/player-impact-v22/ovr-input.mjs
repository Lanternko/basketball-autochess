import {ovrInput as previousInput} from '../player-impact-v21/ovr-input-isolated.mjs';
import {attachPutback,putbackSource} from './input.mjs';
const cache=new Map();
export async function ovrInput(season){
 if(cache.has(season))return cache.get(season);
 const x=structuredClone(await previousInput(season)),src=putbackSource(season);
 attachPutback(x.players,season);for(const t of x.opponents)attachPutback(t.roster,season);
 x.profiles=x.profiles.map((p,slot)=>{
  const ps=x.players.filter(q=>x.roleMap.get(q.playerId).slot===slot&&!x.roleMap.get(q.playerId).lowConfidence),a=ps.reduce((s,q)=>s+q.putbackMeasurement.attempts,0),made=ps.reduce((s,q)=>s+q.putbackMeasurement.makes,0),ref=src.rates.reference;
  if(!a)throw Error('No pooled positional putback attempts');
  const weighted=key=>ps.reduce((s,q)=>s+q.putbackMeasurement.attempts*q.putbackMeasurement[key],0)/a;
  return {...p,putbackMeasurement:{attempts:a,makes:made,rate:(made+ref.kappaAttempts*ref.leagueRecordedFG)/(a+ref.kappaAttempts),sourceBase:weighted('sourceBase'),context:weighted('context'),source:'Confident natural-position PB attempt pool, same prior and source context adjustment. Synthetic attributes remain mean70; reference source curve is pooled from original source cards.'}};
 });
 cache.set(season,x);return x;
}

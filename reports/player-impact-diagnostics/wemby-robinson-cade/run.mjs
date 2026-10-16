import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {ovrInput} from '../../player-impact-v24/ovr-input.mjs';
import {impactEngine} from '../../player-impact-v24/engine.mjs';
import {lineup} from '../../ovr-2025-26-positional/protocol.mjs';
import {selfCreation} from '../../../src/probability_model.js';
const root='reports/player-impact-diagnostics/wemby-robinson-cade';
const read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const frozen=read('reports/player-impact-v24/all-2025-26/protocol.json');
const hashes={...frozen.hashes,[root+'/run.mjs']:hash(root+'/run.mjs')};
const verify=()=>{for(const [p,h] of Object.entries(hashes))assert.equal(hash(p),h,p);};verify();
const x=await ovrInput('2025-26'),run=await impactEngine('rotation-space',{game:true,memoized:true});
const ids=[1629011,1641705,1630595],samples=12,seedBase=20261015;
const variants=['original','oreb_card','rebound_bundle','rim_contest','passing','dreb_recipient'];
const protocol={season:'2025-26',model:'v24 frozen full-OVR engine',ids,samples,seedBase,opponents:30,seats:2,gamesPerCase:720,
 scope:'Fixed-lineup 864s no-fatigue/no-substitution diagnostic, same natural position and distinct mean70 positional teammates as v24. Paired original seed prefix, no rank changes or fitted coefficients. Component replacement uses the same-position synthetic mean70 profile. Non-additive local sensitivity, not causal real-player impact or an OVR correction.',
 interventions:{oreb_card:['individualOreb'],rebound_bundle:['rebound','individualOreb','putbackMeasurement','putbackChoiceMeasurement','drebRecipientMeasurement'],rim_contest:['help','defenseExposureMeasurement.short'],passing:['pass','opportunityMeasurement.passOpportunityRate','opportunityMeasurement.passStolenPerMinute','creationContextMeasurement.creation with sourceCreation reanchored to current attributes'],dreb_recipient:['drebRecipientMeasurement']},hashes};
assert.ok(!fs.existsSync(root+'/results.json'),'Preserve completed diagnostic');
fs.writeFileSync(root+'/protocol.json',JSON.stringify(protocol,null,2));
const center=read('reports/player-impact-v20/2025-26-synthetic-center.json').fullCenter;
const options={...x.options,creationPolicy:'rotation-space',contextLongScale:1,spaceCenter:center};
const teamKeys=['pts','fga','fgm','fg3a','fg3m','fta','ftm','ast','oreb','dreb','blk','stl','tov'];
const cases=[];
for(const id of ids){
 const original=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,base=x.profiles[slot];
 const records={};
 for(const variant of variants){
  const p=structuredClone(original);
  if(variant==='oreb_card')p.individualOreb=structuredClone(base.individualOreb);
  if(variant==='rebound_bundle')for(const k of protocol.interventions.rebound_bundle)p[k]=structuredClone(base[k]);
  if(variant==='rim_contest'){p.help=base.help;p.defenseExposureMeasurement.short=structuredClone(base.defenseExposureMeasurement.short);}
  if(variant==='passing'){
   p.pass=base.pass;
   for(const k of ['passOpportunityRate','passStolenPerMinute'])p.opportunityMeasurement[k]=base.opportunityMeasurement[k];
   p.creationContextMeasurement.creation=base.creationContextMeasurement.creation;
   p.creationContextMeasurement.sourceCreation=selfCreation(p);
  }
  if(variant==='dreb_recipient')p.drebRecipientMeasurement=structuredClone(base.drebRecipientMeasurement);
  const team=lineup(x,p,slot),rows=[];
  for(let opponent=0;opponent<30;opponent++){
   const caches=[new Map(),new Map()];
   for(let i=0;i<samples;i++){
    const seed=(seedBase+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
    for(let seat=0;seat<2;seat++){
     const args=seat?[x.opponents[opponent],team]:[team,x.opponents[opponent]];
     const g=run(...args,{...options,seed,ovrCache:caches[seat]});assert.equal(g.gameSeconds,864);
     const tag=seat?'B':'A',other=seat?'A':'B',own=g['stat'+tag],opp=g['stat'+other];
     const personal=g['players'+tag].find(q=>q.playerId===id)??g['players'+tag][slot];assert.ok(personal);
     rows.push({opponent,i,seat,seed,win:own.pts>opp.pts?1:g.tie?.5:0,margin:own.pts-opp.pts,team:Object.fromEntries(teamKeys.map(k=>[k,own[k]])),opposition:Object.fromEntries(teamKeys.map(k=>[k,opp[k]])),personal:Object.fromEntries(teamKeys.map(k=>[k,personal[k]]))});
    }
   }
  }
  records[variant]=rows;
  if(variant==='dreb_recipient')rows.forEach((r,i)=>{assert.deepEqual(r.team,records.original[i].team);assert.deepEqual(r.opposition,records.original[i].opposition);});
  const n=rows.length,mean=k=>rows.reduce((s,r)=>s+r[k],0)/n;
  const result={id,name:p.name,position:base.pos,variant,games:n,winRate:mean('win'),meanMargin:mean('margin'),team:Object.fromEntries(teamKeys.map(k=>[k,rows.reduce((s,r)=>s+r.team[k],0)/n])),opposition:Object.fromEntries(teamKeys.map(k=>[k,rows.reduce((s,r)=>s+r.opposition[k],0)/n])),personal:Object.fromEntries(teamKeys.map(k=>[k,rows.reduce((s,r)=>s+r.personal[k],0)/n])),rows};
  if(variant!=='original'){
   const ds=[];let variance=0;
   for(let o=0;o<30;o++){
    const values=[];
    for(let i=0;i<samples;i++){let d=0;for(let seat=0;seat<2;seat++){const j=(o*samples+i)*2+seat;d+=(rows[j].margin-records.original[j].margin)/2;}values.push(d);}
    const m=values.reduce((a,b)=>a+b,0)/samples;ds.push(m);variance+=values.reduce((s,v)=>s+(v-m)**2,0)/(samples-1)/samples/(30*30);
   }
   result.pairedMarginChange=ds.reduce((a,b)=>a+b,0)/30;result.pairedMarginChange95=[result.pairedMarginChange-1.96*Math.sqrt(variance),result.pairedMarginChange+1.96*Math.sqrt(variance)];
  }
  cases.push(result);console.log(JSON.stringify({name:p.name,variant,winRate:result.winRate,meanMargin:result.meanMargin,pairedChange:result.pairedMarginChange,ci:result.pairedMarginChange95}));
 }
}
verify();
fs.writeFileSync(root+'/results.json',JSON.stringify({protocol,cases,games:cases.reduce((n,c)=>n+c.games,0)}));

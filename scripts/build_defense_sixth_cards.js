import fs from 'node:fs';
import * as C from '../src/constants.js';
import * as M from '../src/probability_model.js';
import {read,hash} from './defense_io.js';
import {sixthInputs} from '../src/defense_sixth_jobs.js';
import {createRater,inverse} from './export_defense_sixth_cards.js';
const root='reports/defense-sixth';
const sigmoid=x=>1/(1+Math.exp(-x)),logit=p=>Math.log(p/(1-p));
const variants={role:{role:true},offense:{offense:true},'role-offense':{role:true,offense:true},'role-offense-net':{role:true,offense:true,net:true}};
export function buildCards(k,variant){
 const flag=variants[variant];if(!flag)throw Error('Unknown ability variant');
 const {league:original,options}=sixthInputs({cutoff:k}),league=structuredClone(original),signals=structuredClone(options.defenseSignals),model=read(`${root}/model-pre${k}.json`),raw=read(`${root}/card-values-pre${k}.json`),id=new Map(model.players.map((p,i)=>[p,i])),values=new Map(raw.players.map(p=>[p.id,p]));
 const weights=model.minutes,avg=v=>v.reduce((s,x,i)=>s+x*weights[i],0)/weights.reduce((a,b)=>a+b,0),selected=model.models[flag.role?'role':'plain'];
 const centerO=avg(model.players.map(p=>values.get(p).offense)),centerD=avg(model.players.map(p=>values.get(p).defenseAllowed));
 const off=selected.priorOffense.map((v,i)=>v+(flag.offense?selected.offenseResidual[i]:0)),def=selected.priorDefenseAllowed.map((v,i)=>v+(flag.net?selected.defenseResidual[i]:0));
 const oc=avg(off),dc=avg(def),plain=model.models.plain,role=model.models.role,drO=role.priorOffense.map((v,i)=>v-plain.priorOffense[i]),drD=role.priorDefenseAllowed.map((v,i)=>v-plain.priorDefenseAllowed[i]),co=avg(drO),cd=avg(drD);
 const r=createRater(league,{...options,defenseSignals:signals}),projection=[],cache=new Map();
 for(const team of league.teams)for(const p of team.roster){
  if(cache.has(p.playerId)){const q=cache.get(p.playerId);Object.assign(p,q.attributes);p.abilityVersion='nba-player-ability-sixth-'+variant;p.abilityEstimate=q.estimate;projection.push({...q.row,teamId:team.id});continue;}
  const i=id.get(p.playerId),before=r.value(p),targetOff=flag.offense?centerO+100*model.leaguePPP*(off[i]-oc):before.offense+100*model.leaguePPP*(drO[i]-co);
  const targetDef=flag.net?centerD+100*model.leaguePPP*(def[i]-dc):before.defenseAllowed+(flag.role?100*model.leaguePPP*(drD[i]-cd):0);
  const originalAttrs={long:p.long,mid:p.mid,short:p.short},baseMake=Object.fromEntries(Object.entries(originalAttrs).map(([z,a])=>[z,M.interpolate(a,({long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT})[z])]));
  const setShot=delta=>{for(const z of ['long','mid','short'])p[z]=Math.max(0,Math.min(120,inverse(sigmoid(logit(Math.max(.001,Math.min(.999,baseMake[z])))+delta),({long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT})[z])));};
  let lo=-4,hi=4;for(let j=0;j<35;j++){const m=(lo+hi)/2;setShot(m);if(r.value(p).offense<targetOff)lo=m;else hi=m;}setShot((lo+hi)/2);
  const oldSignal=signals.values[p.playerId].shortFG;lo=-4;hi=4;
  if(flag.role||flag.net){for(let j=0;j<35;j++){const m=(lo+hi)/2;signals.values[p.playerId].shortFG=oldSignal+m;if(r.value(p).defenseAllowed<targetDef)lo=m;else hi=m;}signals.values[p.playerId].shortFG=oldSignal+(lo+hi)/2;}
  const after=r.value(p);projection.push({id:p.playerId,teamId:team.id,name:p.name,minutes:weights[i],before,targetOff,targetDef,after,offenseProjectionError:after.offense-targetOff,defenseProjectionError:after.defenseAllowed-targetDef,originalAttrs,attributes:{long:p.long,mid:p.mid,short:p.short},defenseShortEffect:signals.values[p.playerId].shortFG-oldSignal});
  p.abilityVersion='nba-player-ability-sixth-'+variant;p.abilityEstimate={cutoff:k,rolePrior:!!flag.role,offenseResidual:!!flag.offense,netResidual:!!flag.net,offenseTarget:targetOff,defenseAllowedTarget:targetDef};
  cache.set(p.playerId,{attributes:{long:p.long,mid:p.mid,short:p.short},estimate:p.abilityEstimate,row:projection.at(-1)});
 }
 league.sixthSignals=signals;league.sixthProvenance={cutoff:k,variant,switches:flag,trainingGames:model.trainGames,method:'Player-only pre-cutoff count model projected into existing shooting attributes / existing shortFG defense signal. League training-minute weighted means preserved in analytic card coordinates. No engine change, team parameter, win or post outcome. Same player estimates reused across team instances; trades carry values. Net switch maps remaining joint player scoring/allowed estimate into defense card.',sources:Object.fromEntries([`${root}/model-pre${k}.json`,`${root}/card-values-pre${k}.json`,'scripts/build_defense_sixth_cards.js'].map(f=>[f,hash(f)]))};
 fs.writeFileSync(`${root}/pre${k}-${variant}-league.json`,JSON.stringify(league)+'\n');fs.writeFileSync(`${root}/pre${k}-${variant}-projection.json`,JSON.stringify({cutoff:k,variant,switches:flag,players:projection,meanAbsoluteOffenseProjectionError:projection.reduce((s,p)=>s+Math.abs(p.offenseProjectionError),0)/projection.length,meanAbsoluteDefenseProjectionError:projection.reduce((s,p)=>s+Math.abs(p.defenseProjectionError),0)/projection.length})+'\n');
 console.log('CARDS',k,variant);
}
if(process.argv[1]?.endsWith('build_defense_sixth_cards.js'))for(const k of process.argv[2]?[Number(process.argv[2])]:[25,41,55])for(const v of process.argv[3]?[process.argv[3]]:Object.keys(variants))buildCards(k,v);

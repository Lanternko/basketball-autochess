import fs from 'node:fs';
import * as M from '../src/probability_model.js';
import * as C from '../src/constants.js';
import {fourthProbability} from '../src/defense_fourth_effects.js';
import {volumeWeights,pressureSignal} from '../src/defense_probability.js';
import {sixthInputs} from '../src/defense_sixth_jobs.js';
import {hash} from './defense_io.js';
const root='reports/defense-sixth';
export const inverse=(p,curve)=>{for(let i=1;i<curve.length;i++){const [a,b]=curve[i-1],[c,d]=curve[i];if(p>=Math.min(b,d)&&p<=Math.max(b,d))return a+(p-b)/(d-b)*(c-a);}return Math.abs(p-curve[0][1])<Math.abs(p-curve.at(-1)[1])?curve[0][0]:curve.at(-1)[0];};
export function createRater(league,options){
 const attrs=['long','mid','short','drive','tovSkill','pass','ft','rebound','onBall','help','stamina','physique','offBall','screen'],ps=league.teams.flatMap(t=>t.roster),w=ps.map(p=>p.observed.MIN),den=w.reduce((a,b)=>a+b,0);
 const ref=Object.fromEntries(attrs.map(a=>[a,ps.reduce((s,p,i)=>s+p[a]*w[i],0)/den]));ref.playerId=-1;ref.offenseMeasurement={attempts:1,freeThrows:.26,turnovers:.15,minutes:1};ref.shotProfile={threeRate:ps.reduce((s,p,i)=>s+p.shotProfile.threeRate*w[i],0)/den,freeThrowsPerAttempt:.26};
 const rr=Array.from({length:5},()=>({...ref}));
 const tr=l=>C.weightedTop(l.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
 const rate=(o,d)=>{const v=volumeWeights(o,'shot'),total=v.reduce((a,b)=>a+b,0);return 100*o.reduce((s,p,i)=>s+v[i]/total*fourthProbability(p,M.teammateContext(o,i),d[i],M.helpDefense(d),tr(o),tr(d),M.teamPhysique(d),{contextScale:options.contextScale,turnoverScale:options.turnoverScale,turnoverMode:options.turnoverMode,pressureAttribute:options.liveSignal?70:pressureSignal(d,options.stealPriorRate).attribute,contextLongScale:options.contextLongScale,contextShortScale:options.contextShortScale},d,options).ev,0);};
 const baseline=rate(rr,rr);return {reference:ref,baseline,rate,value:p=>({offense:baseline+5*(rate([p,...rr.slice(1)],rr)-baseline),defenseAllowed:baseline+5*(rate(rr,[p,...rr.slice(1)])-baseline)})};
}
if(process.argv[1]?.endsWith('export_defense_sixth_cards.js'))for(const cutoff of [25,41,55]){
 const {league,options}=sixthInputs({cutoff}),r=createRater(league,options);
 const players=league.teams.flatMap(t=>t.roster.map(p=>({teamId:t.id,name:p.name,id:p.playerId,pos:p.pos,minutes:p.observed.MIN,GP:p.observed.GP,MPG:p.seasonMinutesPerGame,...r.value(p),attributes:Object.fromEntries(['long','mid','short','ft','pass','rebound','onBall','help'].map(a=>[a,p[a]])),raw:p.observed,shotProfile:p.shotProfile})));
 fs.writeFileSync(`${root}/card-values-pre${cutoff}.json`,JSON.stringify({cutoff,baseline:r.baseline,reference:r.reference,players,definition:'One player replaces one training-minute weighted reference player; engine analytic EV difference multiplied by five. Linear diagnostic, no simulation, no final possession/rebound/clock recursion. Defensive values include existing B1 effects. These values are not OVR.',source:hash(cutoff===41?'reports/defense-fourth/pre41-league.json':`reports/defense-fifth/pre${cutoff}-league.json`),curves:{long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT,ft:C.CURVE_FT}})+'\n');
}

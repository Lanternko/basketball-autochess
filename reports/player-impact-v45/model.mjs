import {terminalDefenseProbabilities as previousTerminal,exposureDefenseProbabilities as previousExposure} from '../player-impact-v41/model.mjs';
import {applyRecordedZone} from '../player-impact-v42/choice-model.mjs';
export const fineZones=['ra','paint','mid','corner','arc'];
export const coarseOf={ra:'short',paint:'short',mid:'mid',corner:'long',arc:'long'};
const sigmoid=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
export function fineSourcePlan(player,defenders){
 const p=player.fineDefenseMeasurement;if(!p||defenders.length!==5||defenders.some(d=>!d.fineDefenseMeasurement))throw Error('Missing fine source descriptors');
 const choice=k=>sigmoid(p.choiceShooter[k]+defenders.reduce((s,d)=>s+d.fineDefenseMeasurement.choiceDefender[k],0));
 const three=choice('three'),paint=choice('paintGivenTwo'),ra=choice('raGivenPaint'),corner=choice('cornerGivenThree');
 const zone={ra:(1-three)*paint*ra,paint:(1-three)*paint*(1-ra),mid:(1-three)*(1-paint),corner:three*corner,arc:three*(1-corner)};
 const makeEta=Object.fromEntries(fineZones.map(z=>[z,p.makeShooter[z]+defenders.reduce((s,d)=>s+d.fineDefenseMeasurement.makeDefender[z],0)]));
 return {zone,makeEta};
}
export const collapseZone=zone=>({long:zone.corner+zone.arc,mid:zone.mid,short:zone.ra+zone.paint});
export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
 const q=previousTerminal(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt);if(opts.putback)return q;
 const fine=fineSourcePlan(handler,lineup);return {...q,defensiveZone:collapseZone(fine.zone),finePlan:fine};
}
export function exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup){
 const q=previousExposure(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup);if(opts.putback)return q;
 return applyRecordedZone(q,opts.sourceFineZone??collapseZone(fineSourcePlan(handler,lineup).zone));
}

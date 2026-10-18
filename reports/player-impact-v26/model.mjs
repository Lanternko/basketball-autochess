import {contactRecipientWeights as previousWeights} from '../player-impact-v25/model.mjs';
function rates(lineup){
 if(lineup.length!==5)throw Error('Need five players for contact intensity');
 const values=lineup.map(p=>p.contactIntensityMeasurement);
 if(values.some(x=>!x||!Number.isFinite(x.contactRate)||x.contactRate<=0||!Number.isFinite(x.terminalRate)||x.terminalRate<=0))throw Error('Missing positive source contact/terminal intensity');
 return values;
}
export function ordinaryContactProbability(lineup,opt){
 if(!opt.measuredOrdinaryContacts)return opt.nonShootingFoulRate;
 const x=rates(lineup),C=x.reduce((s,r)=>s+r.contactRate,0),N=x.reduce((s,r)=>s+r.terminalRate,0),unassigned=opt.unassignedTerminalRate;
 if(!Number.isFinite(unassigned)||unassigned<0)throw Error('Missing source team-unassigned terminal rate');
 return C/(C+N+unassigned);
}
export function contactRecipientWeights(lineup,opt){
 if(!opt.measuredOrdinaryContacts)return previousWeights(lineup);
 const x=rates(lineup),C=x.reduce((s,r)=>s+r.contactRate,0);return x.map(r=>r.contactRate/C);
}

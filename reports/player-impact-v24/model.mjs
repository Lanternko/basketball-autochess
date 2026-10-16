import {measuredRecipientWeights} from '../../src/individual_box_allocation.js';
export function recipientWeights(lineup,kind){
 if(kind!=='dreb')return measuredRecipientWeights(lineup,kind);
 const weights=lineup.map(p=>p.drebRecipientMeasurement?.strength);
 if(weights.some(w=>!Number.isFinite(w)||w<=0))throw Error('Missing positive conditional DREB allocation strength');
 const total=weights.reduce((s,w)=>s+w,0);return weights.map(w=>w/total);
}

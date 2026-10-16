export function contactRecipientWeights(lineup){
 if(lineup.length!==5)throw Error('Need five potential nonshooting contact victims');
 const values=lineup.map(p=>p.contactRecipientMeasurement?.strength);
 if(values.some(x=>!Number.isFinite(x)||x<=0))throw Error('Missing positive source contact recipient strength');
 const total=values.reduce((s,x)=>s+x,0);return values.map(x=>x/total);
}

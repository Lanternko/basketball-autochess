// Conditional recipient allocation for same-season box reconstruction.
// Team event probabilities stay in the existing rebound/block model. These
// measured rates are not new ability scores or estimates of causal impact.
export const BOX_ALLOCATION_PRIOR_MINUTES=240;
export function measuredRecipientWeights(lineup,kind){
  if(!['dreb','blk'].includes(kind))throw new Error('Unknown allocation event');
  if(!Array.isArray(lineup)||!lineup.length)throw new Error('Empty allocation lineup');
  const rates=lineup.map(p=>{
    const m=p.boxAllocationMeasurement;
    if(!m||!Number.isFinite(m.minutes)||m.minutes<0||!Number.isFinite(m[kind])||m[kind]<0||!Number.isFinite(m.priorRates?.[kind])||m.priorRates[kind]<=0)throw new Error('Missing or invalid '+kind+' allocation measurement');
    return (m[kind]+BOX_ALLOCATION_PRIOR_MINUTES*m.priorRates[kind])/(m.minutes+BOX_ALLOCATION_PRIOR_MINUTES);
  });
  const total=rates.reduce((a,b)=>a+b,0);
  return rates.map(r=>r/total);
}
export function attachBoxAllocationMeasurements(league){
  // Merge traded stints first; each player's numerator and denominator must
  // cover the same season. Do not mix a stint BLK with a full-season MIN.
  const players=new Map();
  for(const t of league.teams)for(const p of t.roster){
    const r=players.get(p.playerId)??{minutes:0,dreb:0,blk:0};
    for(const [key,col] of [['minutes','MIN'],['dreb','DREB'],['blk','BLK']]){
      if(!Number.isFinite(p.observed?.[col])||p.observed[col]<0)throw new Error('Missing official '+col);
      r[key]+=p.observed[col];
    }
    players.set(p.playerId,r);
  }
  const total=[...players.values()].reduce((a,r)=>({minutes:a.minutes+r.minutes,dreb:a.dreb+r.dreb,blk:a.blk+r.blk}),{minutes:0,dreb:0,blk:0});
  if(!(total.minutes>0))throw new Error('Empty observed exposure');
  const priorRates={dreb:total.dreb/total.minutes,blk:total.blk/total.minutes};
  for(const t of league.teams)for(const p of t.roster)p.boxAllocationMeasurement={...players.get(p.playerId),priorRates};
  return {uniquePlayers:players.size,priorMinutes:BOX_ALLOCATION_PRIOR_MINUTES,priorRates};
}

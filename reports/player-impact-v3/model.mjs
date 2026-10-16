export function opportunityPlan(lineup,probability,pressure=1){
 const rows=lineup.map((p,i)=>{
  const m=p.opportunityMeasurement;
  if(!m)throw Error('Missing source-context opportunity measurement');
  const self=m.selfOpportunityRate,pass=m.passOpportunityRate+m.passStolenPerMinute*pressure,total=self+pass;
  return {weight:total,shoot:total?self/total:1,intercept:pass?Math.min(.95,m.passStolenPerMinute*pressure/pass):0,
   receivers:lineup.map((q,j)=>j===i?0:Math.max(.0001,q.opportunityMeasurement.receiveOpportunityRate))};
 });
 return {weights:rows.map(r=>Math.max(.0001,r.weight)),rows};
}
export function contestHelp(lineup){
 const w=lineup.map(p=>p.opportunityMeasurement.contestExposurePerMinute),total=w.reduce((s,v)=>s+v,0);
 return lineup.reduce((s,p,i)=>s+w[i]/total*p.help,0);
}

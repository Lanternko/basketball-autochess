// Convert observed MADE production to opportunity demand exactly once.
// The old creation-flow priors multiplied observed makes by FG probability
// again. A passing decision here already represents finding a shot, so the
// legacy pass-open gate must not thin the observed creation demand a second time.
const clip=p=>Math.max(.01,Math.min(.99,p));
export function opportunityPlan(lineup,probability,pressure=1){
 const own=lineup.map((_,i)=>probability(i)),fg=p=>clip(p.FG3M+p.MIDM+p.RIMM);
 const rows=lineup.map((p,i)=>{
  const m=p.shotCreationMeasurement,r=p.passingRiskMeasurement;
  if(!m||!r||!Number.isFinite(r.passStolenPerMinute))throw Error('Missing observed role/risk');
  const caught=lineup.map((_,j)=>{const q=probability(j,p.pass);return q.ev>=own[j].ev?q:own[j];});
  const receivers=lineup.map((q,j)=>i===j?0:Math.max(.0001,q.shotCreationMeasurement.assistedMakesPerMinute)/fg(caught[j]));
  const total=receivers.reduce((a,v)=>a+v,0),success=receivers.reduce((a,v,j)=>a+v*fg(caught[j]),0)/total;
  const completed=m.assistsPerMinute/success,stolen=r.passStolenPerMinute*pressure;
  const pass=completed+stolen,self=m.selfMakesPerMinute/fg(own[i]),weight=self+pass;
  return {weight,shoot:weight?self/weight:1,intercept:pass?Math.min(.95,stolen/pass):0,receivers};
 });
 return {weights:rows.map(r=>Math.max(.0001,r.weight)),rows};
}

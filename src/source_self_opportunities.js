// Descriptive source-role alternative: a receiver shortfall is not automatically
// evidence of additional self creation. Source rates are anchors, not hard
// physiological maxima; this restriction must be validated as a model choice.
export function sourceSupportedSelf(flow, measurements){
 if(flow.self.length!==measurements.length||flow.incoming.length!==measurements.length)throw Error('Role flow dimensions');
 return measurements.map((m,i)=>{
  const self=m.selfOpportunityRate,terminal=m.terminalOpportunityRate,receive=m.receiveOpportunityRate;
  if(![self,terminal,receive,flow.incoming[i]].every(Number.isFinite)||self<0||terminal<0||receive<0||
     Math.abs(self+receive-terminal)>1e-8||flow.incoming[i]<-1e-9||flow.incoming[i]>terminal+1e-8)
   throw Error('Invalid source self/receive accounting');
  return Math.min(self,Math.max(0,terminal-flow.incoming[i]));
 });
}

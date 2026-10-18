import * as M from './probability_model.js';
import * as C from './constants.js';
const clamp=x=>Math.max(0,Math.min(1,x));

export function attachCreationDependence(players){
 for(const p of players){
  const m=p.opportunityMeasurement;
  if(!m||!Number.isFinite(m.terminalOpportunityRate)||m.terminalOpportunityRate<=0||
     !Number.isFinite(m.receiveOpportunityRate)||m.receiveOpportunityRate<0||m.receiveOpportunityRate>m.terminalOpportunityRate+1e-9)
   throw Error('Need source self/received terminal opportunity roles');
  p.creationDependenceMeasurement={receivedShare:m.receiveOpportunityRate/m.terminalOpportunityRate,
   sourceSelfCreation:M.selfCreation(p),source:'Existing source role received/terminal opportunity ratio; descriptive recipient dependence, not a measured dribble skill or a new fit. Current-attribute deltas preserve the original counterfactual slope.'};
 }
 return players;
}

export function creationDependence(player){
 const m=player.creationDependenceMeasurement;
 if(!m)return clamp(C.CREATE_DEP_BASE+(70-M.selfCreation(player))/C.CREATE_DEP_SCALE);
 if(!Number.isFinite(m.receivedShare)||m.receivedShare<0||m.receivedShare>1||!Number.isFinite(m.sourceSelfCreation))
  throw Error('Invalid source creation dependence');
 return clamp(m.receivedShare-(M.selfCreation(player)-m.sourceSelfCreation)/C.CREATE_DEP_SCALE);
}

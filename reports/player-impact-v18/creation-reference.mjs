export function conditionalCreationReference(row,leagueSuccess,priorMinutes=60){
 if(!Number.isFinite(leagueSuccess)||leagueSuccess<=0||leagueSuccess>1||!Number.isFinite(priorMinutes)||priorMinutes<=0)throw Error('Invalid creation prior');
 const minutes=row?.minutes??0,success=row?.conditionalSuccess;
 if(!Number.isFinite(minutes)||minutes<0||(minutes>0&&(!Number.isFinite(success)||success<=0||success>1)))throw Error('Invalid source creation support');
 return ((minutes>0?minutes*success:0)+priorMinutes*leagueSuccess)/(minutes+priorMinutes);
}
export function attachCreationReference(players,audit){
 const rows=new Map(audit.rows.map(r=>[r.playerId,r]));
 for(const p of players){
  const row=rows.get(p.playerId);if(!row)throw Error('Missing source creation reference');
  const probability=conditionalCreationReference(row,audit.conditionalSuccess),old=row.oldGlobalSuccess;
  if(!Number.isFinite(old)||old<=0||old>1)throw Error('Invalid old creation reference');
  const original=p.opportunityMeasurement.passOpportunityRate;
  if(!Number.isFinite(original)||original<0)throw Error('Invalid creation rate');
  p.opportunityMeasurement={...p.opportunityMeasurement,passOpportunityRate:original*old/probability};
  p.creationSuccessMeasurement={sourceMinutes:row.minutes,sourceProbability:row.conditionalSuccess,priorMinutes:60,leagueProbability:audit.conditionalSuccess,probability,oldGlobalSuccess:old,rawPassRate:original};
 }
 return players;
}

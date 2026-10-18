// Source-count sample-size correction. This is a role/attempt-frequency
// estimate, not a measured driving skill or an individual ranking adjustment.
export function posteriorFreeThrowRatio(attempts,freeThrows,leagueRatio,priorAttempts){
 if(![attempts,freeThrows,leagueRatio,priorAttempts].every(Number.isFinite)||attempts<0||freeThrows<0||leagueRatio<=0||priorAttempts<=0)throw Error('Invalid free-throw profile prior');
 return (freeThrows+priorAttempts*leagueRatio)/(attempts+priorAttempts);
}
export function attachFreeThrowProfilePrior(players,reference,priorAttempts){
 for(const p of players){
  const counts=reference.counts[p.playerId];if(!counts||!p.shotProfile)throw Error('Missing source free-throw profile');
  const ratio=posteriorFreeThrowRatio(counts.FGA,counts.FTA,reference.leagueFtr,priorAttempts);
  p.shotProfile={...p.shotProfile,freeThrowsPerAttempt:ratio};
  p.freeThrowProfileMeasurement={attempts:counts.FGA,freeThrows:counts.FTA,minutes:counts.MIN,
   rawRatio:counts.FGA?counts.FTA/counts.FGA:null,posteriorRatio:ratio,leagueRatio:reference.leagueFtr,priorAttempts,
   source:'Merged official same-season counts; common count-mix prior fitted on source game folds in three prior seasons. No names, ranks or simulation residuals.',
   driveAttributeChanged:false};
 }
 return players;
}

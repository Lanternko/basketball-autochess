// Observed made-production priors for who creates a fresh FG opportunity.
// These are role measurements, not fabricated handle/off-ball ability scores.
const checked=p=>{
 const m=p.shotCreationMeasurement;
 if(!m||['selfMakesPerMinute','assistedMakesPerMinute','assistsPerMinute'].some(k=>!Number.isFinite(m[k])||m[k]<0))throw new Error('Missing measured shot creation role');
 return m;
};
export function creationHandlerWeights(lineup){return lineup.map(p=>{const m=checked(p);return Math.max(.005,m.selfMakesPerMinute+m.assistsPerMinute);});}
export function creationShootProbability(player,passesLeft,maxPasses){
 if(passesLeft!==maxPasses)return 1;
 const m=checked(player),sum=m.selfMakesPerMinute+m.assistsPerMinute;
 return sum?m.selfMakesPerMinute/sum:.5;
}
export function creationReceiverWeights(lineup,passerIndex,makeProbabilities=null){
 if(makeProbabilities&&makeProbabilities.length!==lineup.length)throw new Error('Invalid expected-make vector');
 return lineup.map((p,i)=>{
  const m=checked(p);if(i===passerIndex)return 0;
  const prob=makeProbabilities?makeProbabilities[i]:1;
  if(!Number.isFinite(prob)||prob<=0||prob>1)throw new Error('Invalid expected FG make probability');
  return Math.max(.005,m.assistedMakesPerMinute)/Math.max(.01,prob);
 });
}

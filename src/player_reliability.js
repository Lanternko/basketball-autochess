import {recurrentAbsence} from './player_workload.js';

// Healthy workload contribution is measured against a matched average-player
// baseline, not raw win probability or a 0..99 score. Reliability discounts only
// positive demonstrated contribution: absence can never award rating points.
// Coefficient is a disclosed provisional rating preference, not medical risk.
export function reliabilityAdjustedContribution(healthyContribution, history, coefficient=.10){
 if(!Number.isFinite(healthyContribution))throw new RangeError('Invalid healthy contribution');
 const {persistentRate,reliabilityScale}=recurrentAbsence(history,coefficient);
 const deduction=Math.max(0,healthyContribution)*(1-reliabilityScale);
 return {healthyContribution,persistentRate,reliabilityScale,deduction,adjustedContribution:healthyContribution-deduction};
}

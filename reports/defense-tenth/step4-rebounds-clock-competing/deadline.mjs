export function deadlineDecision({pending,periodTicks,shotTicks,enabled,probability,rng}) {
 if(!Number.isFinite(periodTicks)||!Number.isFinite(shotTicks)||periodTicks<0||shotTicks<0)throw Error('Invalid clocks');
 if(!Number.isFinite(probability)||probability<0||probability>1)throw Error('Invalid deadline probability');
 const eligible=Boolean(pending)&&periodTicks>shotTicks;
 return {eligible,violation:eligible&&enabled&&rng()<probability};
}

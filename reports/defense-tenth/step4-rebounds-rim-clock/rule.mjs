// A rule transition, not an estimate of how often a shot misses the rim.
export function offensiveReboundClock({remainingTicks, periodTicks, rimContact, freeThrow=false}) {
  for (const n of [remainingTicks,periodTicks]) if (!Number.isFinite(n)||n<0) throw new Error('Invalid clock');
  if (typeof freeThrow!=='boolean') throw new Error('Invalid freeThrow');
  if (!freeThrow&&typeof rimContact!=='boolean') throw new Error('Rim contact must be explicit');
  if (periodTicks===0) return {clockTicks:remainingTicks,violation:false,periodEnded:true,reset:false};
  const reset=freeThrow||rimContact;
  return {clockTicks:reset?140:remainingTicks,violation:!reset&&remainingTicks===0,periodEnded:false,reset};
}

export function resolveContact(resolver, context, rng) {
  const contact=resolver(Object.freeze({...context}),rng);
  if (typeof contact!=='boolean') throw new Error('Rim resolver must return an explicit boolean');
  return contact;
}

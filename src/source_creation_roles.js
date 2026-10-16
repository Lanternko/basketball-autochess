// Reconstruct from immutable source cards every time. Applying this operation
// twice must never multiply the conditional-success correction a second time.
export const CREATION_REFERENCE_PRIOR_MINUTES = 60;

export function attachCanonicalCreationRoles(players, sourceCards, audit) {
  if (!Array.isArray(players) || !sourceCards || !Array.isArray(audit?.rows) ||
      !Number.isFinite(audit.conditionalSuccess) || audit.conditionalSuccess <= 0 || audit.conditionalSuccess > 1)
    throw new RangeError('Invalid canonical creation sources');
  const rows = new Map(audit.rows.map(r => [r.playerId, r]));
  // Validate the whole batch before changing any card.
  const updates = players.map(p => {
    const base = sourceCards[p.playerId], row = rows.get(p.playerId);
    if (!base || !row || !Number.isFinite(base.passOpportunityRate) || base.passOpportunityRate < 0 ||
        !Number.isFinite(row.minutes) || row.minutes < 0 ||
        row.minutes > 0 && (!Number.isFinite(row.conditionalSuccess) || row.conditionalSuccess <= 0 || row.conditionalSuccess > 1) ||
        !Number.isFinite(row.oldGlobalSuccess) || row.oldGlobalSuccess <= 0 || row.oldGlobalSuccess > 1)
      throw new RangeError('Missing or invalid canonical player creation source');
    const probability = ((row.minutes > 0 ? row.minutes * row.conditionalSuccess : 0) +
      CREATION_REFERENCE_PRIOR_MINUTES * audit.conditionalSuccess) / (row.minutes + CREATION_REFERENCE_PRIOR_MINUTES);
    return {
      opportunityMeasurement: {...structuredClone(base), passOpportunityRate: base.passOpportunityRate * row.oldGlobalSuccess / probability},
      creationSuccessMeasurement: {
        sourceMinutes: row.minutes, sourceProbability: row.conditionalSuccess,
        priorMinutes: CREATION_REFERENCE_PRIOR_MINUTES, leagueProbability: audit.conditionalSuccess,
        probability, oldGlobalSuccess: row.oldGlobalSuccess, rawPassRate: base.passOpportunityRate,
      },
    };
  });
  players.forEach((p, i) => Object.assign(p, updates[i]));
  return players;
}

// Explicit rating policy. This does not infer a player's physiological ceiling,
// change a skill attribute, or diagnose why the coach chose a role.
export function workloadEvidence(playedMinutes, capMinutes) {
  if (!Number.isFinite(capMinutes) || capMinutes <= 0 || capMinutes > 48 ||
      !Array.isArray(playedMinutes) || !playedMinutes.length ||
      playedMinutes.some(m => !Number.isFinite(m) || m <= 0 || m > 100))
    throw new RangeError('Need positive played-game minutes and a regulation load cap');
  const supportedMinutes = playedMinutes.reduce((s, m) => s + Math.min(m, capMinutes), 0) / playedMinutes.length;
  return {supportedMinutes, workloadShare: supportedMinutes / capMinutes};
}

export function recurrentAbsence(history, coefficient = .10) {
  if (!Array.isArray(history) || !Number.isFinite(coefficient) || coefficient < 0 || coefficient > .10)
    throw new RangeError('Invalid recurrent absence policy');
  const rates = history.filter(h => h.historyCoverageAdequate).map(h => {
    if (!Number.isInteger(h.listedGames) || h.listedGames <= 0 ||
        !Number.isInteger(h.documentedInjuryIllnessGames) || h.documentedInjuryIllnessGames < 0 ||
        h.documentedInjuryIllnessGames > h.listedGames) throw new RangeError('Invalid source absence counts');
    return h.documentedInjuryIllnessGames / h.listedGames;
  }).sort((a, b) => b - a);
  const persistentRate = rates[1] ?? 0;
  return {persistentRate, reliabilityScale: 1 - coefficient * persistentRate};
}

// Each quarter has two half-quarter windows. The player rests in the middle of
// each window; phase alternates whether they start or finish it. This is a
// standardized workload experiment, not a claim about observed coaching.
// The first five roster entries are positional primary cards; entries 5..9 are
// their same-position replacements. Every moment has exactly one of each slot.
export function workloadRotation(minutesBySlot, phase = 0) {
  if (!Array.isArray(minutesBySlot) || minutesBySlot.length !== 5 ||
      minutesBySlot.some(m => !Number.isFinite(m) || m < 0 || m > 48) ||
      !Number.isInteger(phase)) throw new RangeError('Invalid positional workload schedule');
  const ticks = minutesBySlot.map(m => Math.round(m * 600));
  const slots = ticks.map((target, slot) => {
    const rows = [];
    for (let w = 0; w < 8; w++) {
      // Integer allocation preserves exact total tenths even for noninteger MPG.
      const on = Math.floor(target / 8) + Number(w < target % 8), start = w * 3600;
      const primaryFirst = ((w + slot + phase) % 2 + 2) % 2 === 0;
      const split = start + (primaryFirst ? on : 3600 - on);
      if (split > start) rows.push({start, end: split, player: primaryFirst ? slot : slot + 5});
      if (split < start + 3600) rows.push({start: split, end: start + 3600, player: primaryFirst ? slot + 5 : slot});
    }
    return rows;
  });
  const boundaries = [...new Set([0, 28800, ...slots.flatMap(rs => rs.flatMap(r => [r.start, r.end]))])].sort((a, b) => a - b);
  return boundaries.slice(0, -1).map((start, i) => {
    const end = boundaries[i + 1], mid = (start + end) / 2;
    const lineup = slots.map(rs => rs.find(r => mid >= r.start && mid < r.end)?.player);
    if (lineup.some(i => !Number.isInteger(i)) || new Set(lineup).size !== 5)
      throw Error('Invalid workload rotation');
    return {start: start / 10, end: end / 10, lineup};
  });
}

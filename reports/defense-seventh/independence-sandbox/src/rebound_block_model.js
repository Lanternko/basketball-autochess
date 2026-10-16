// Small opportunity model, not a coordinate/lineup tactics simulator.
// Constants below are explicit prototype assumptions, not measured tracking data.
import { ATTR_MIDPOINT } from './constants.js';

export const REBOUND_RULES = {
  luckShare: 0.30, skillScale: 45,
  longBounce: { long: 0.55, mid: 0.35, short: 0.18 },
  inside: { PG: 0.15, SG: 0.20, SF: 0.35, PF: 0.65, C: 0.85, G: 0.18, F: 0.50 },
  crash: { PG: 0.20, SG: 0.25, SF: 0.40, PF: 0.85, C: 1.00, G: 0.22, F: 0.65 },
  shooterInside: { long: 0.04, mid: 0.20, short: 0.72 },
};
export const BLOCK_RULES = {
  basePerAttempt: { long: 0.006, mid: 0.022, short: 0.095 },
  directDefenderShare: { long: 0.90, mid: 0.60, short: 0.25 },
  skillScale: 45, skillSpan: 0.65, maxMissShare: 0.65,
};
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const attribute = v => clamp(Number.isFinite(v) ? v : ATTR_MIDPOINT, 0, 150);
const normalized = values => {
  const total = values.reduce((a,b) => a+b,0);
  return values.map(v => v / total);
};
export const courtPosition = p => p.courtPosition ?? p.pos;
function inside(p) { return REBOUND_RULES.inside[courtPosition(p)] ?? 0.5; }
function validate(lineup, zone) {
  if (!lineup.length) throw new RangeError('Empty lineup');
  if (!Object.hasOwn(REBOUND_RULES.longBounce, zone)) throw new RangeError('Unknown shot zone');
}

/** Chance to collect a rebound, conditional on that team recovering the miss.
 * Uniform luck gives everyone a floor. The remaining share is opportunity × skill.
 * No player-specific tuning and no new numeric player attribute.
 */
export function opportunityReboundWeights(lineup, { side = 'defense', zone = 'short', shooterIndex = -1 } = {}) {
  const contest = reboundContest(lineup, { side, zone, shooterIndex });
  return normalized(contest).map(w => REBOUND_RULES.luckShare/lineup.length + (1-REBOUND_RULES.luckShare)*w);
}

function reboundContest(lineup, { side, zone, shooterIndex = -1 }) {
  validate(lineup, zone);
  if (!['offense','defense'].includes(side)) throw new RangeError('Unknown rebound side');
  const long = REBOUND_RULES.longBounce[zone];
  const contest = lineup.map((p, i) => {
    const near = side === 'offense' && i === shooterIndex
      ? REBOUND_RULES.shooterInside[zone] : inside(p);
    const landingAccess = (1-long)*near + long*(1-near);
    const crash = side === 'offense' ? (REBOUND_RULES.crash[courtPosition(p)] ?? 0.65) : 1;
    const skill = 0.7*attribute(p.rebound) + 0.3*attribute(p.physique);
    return landingAccess * crash * Math.exp((skill-ATTR_MIDPOINT)/REBOUND_RULES.skillScale);
  });
  return contest;
}

// Recorded OREB / (OREB + DREB), NBA 2025-26 regular season.
// Proxy: includes FT rebounds in the source; this engine models FG rebounds only.
export const DEFAULT_OREB_SHARE = 0.25994687569655994;
const neutralReboundLineup = ['PG','SG','SF','PF','C'].map(pos =>
  ({ pos, rebound: ATTR_MIDPOINT, physique: ATTR_MIDPOINT }));
export function offensiveReboundProbability(offense, defense, {
  zone = 'short', shooterIndex = -1, leagueShare = DEFAULT_OREB_SHARE,
} = {}) {
  if (!Number.isFinite(leagueShare) || leagueShare <= 0 || leagueShare >= 1)
    throw new RangeError('leagueShare must be between zero and one');
  const sum = xs => xs.reduce((a,b) => a+b,0);
  const options = { zone, shooterIndex, side: 'offense' };
  const attack = sum(reboundContest(offense, options)) /
    sum(reboundContest(neutralReboundLineup, { ...options,
      shooterIndex: shooterIndex < 0 ? -1 : neutralReboundLineup.findIndex(p =>
        p.pos === courtPosition(offense[shooterIndex])) }));
  const defendOptions = { zone, side: 'defense' };
  const defend = sum(reboundContest(defense, defendOptions)) /
    sum(reboundContest(neutralReboundLineup, defendOptions));
  const odds = leagueShare / (1-leagueShare) * attack / defend;
  return clamp(odds / (1+odds), 0.05, 0.60);
}

/** Split already-modelled misses into blocks and other misses.
 * Defensive FG curves already include shot blocking: applying a second make
 * penalty would double count it. p(block|miss) = p(block)/p(miss).
 */
export function blockProfile(lineup, { zone = 'short', shooterIndex = 0, makeProbability = 0.5 } = {}) {
  validate(lineup, zone);
  if (!Number.isInteger(shooterIndex) || shooterIndex<0 || shooterIndex>=lineup.length) throw new RangeError('Invalid matchup');
  if (!Number.isFinite(makeProbability) || makeProbability<0 || makeProbability>1) throw new RangeError('Invalid make probability');
  const duties = normalized(lineup.map(inside));
  const direct = BLOCK_RULES.directDefenderShare[zone];
  const contribution = lineup.map((p,i) => {
    const exposure = (1-direct)*duties[i] + (i===shooterIndex ? direct : 0);
    const skill = zone === 'long'
      ? 0.7*attribute(p.onBall)+0.3*attribute(p.physique)
      : 0.8*attribute(p.help)+0.2*attribute(p.physique);
    return exposure*(1+BLOCK_RULES.skillSpan*Math.tanh((skill-ATTR_MIDPOINT)/BLOCK_RULES.skillScale));
  });
  const missProbability = 1-makeProbability;
  const perAttempt = Math.min(BLOCK_RULES.basePerAttempt[zone]*contribution.reduce((a,b)=>a+b,0),
    missProbability*BLOCK_RULES.maxMissShare);
  return { perAttempt, conditionalOnMiss: missProbability ? perAttempt/missProbability : 0,
    weights: normalized(contribution) };
}

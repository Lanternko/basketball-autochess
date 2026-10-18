// First defense prototype: rates use same-season observed measurements.
// Clock and zone-context coefficients use explicit retrospective global-rate
// probes, followed by full-season independent-seed stability. Never fit wins.
export const NBA_DEFENSE_V1=Object.freeze({minuteMode:'heuristic',observedTargets:true,excludeZeroTargets:true,
  turnoverMode:'pressure',foulConditioning:true,shotSelection:'volume',pace:1.15,touchLiveShare:.5,
  contextLongScale:0,contextShortScale:.5});

import { BASELINE } from './teams.js';

/** Attribute percentile only. This does NOT estimate player OVR or team strength PR. */
export function percentileAttribute(pr) {
  if (!Number.isFinite(pr) || pr<1 || pr>99) throw new RangeError('Percentile must be 1..99');
  return pr<50 ? Math.round(40+(pr-1)/49*30) : Math.round(70+(pr-50)/49*29);
}
export function percentileTeam(pr) {
  const value = percentileAttribute(pr);
  return { name:`全屬性 ${value} 壓力測試隊（單項 PR${pr}；非球隊 PR）`, benchmarkKind: 'uniform-attribute-stress', attributePercentile: pr, season:'synthetic',
    roster:BASELINE.roster.map((p,i)=>Object.fromEntries(Object.entries(p).map(([k,v])=>
      [k,k==='name' ? `PR${pr}-${i+1}` : typeof v==='number' ? value : v]))) };
}

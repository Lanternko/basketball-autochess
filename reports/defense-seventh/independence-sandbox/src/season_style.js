// Measured shot tendency, not an ability rating or an independent validation target.
export function withSeasonStyle(team, reference, { freeThrowStyle = false } = {}) {
 return {...team,roster:team.roster.map(p=>{
  const r=reference.players.find(x=>x.name===p.name);
  if(!r || !(r.totals.FGA>0)) throw new Error('Missing shot sample: '+p.name);
  return {...p,shotProfile:{threeRate:r.totals.FG3A/r.totals.FGA,...(freeThrowStyle ? {freeThrowsPerAttempt:r.totals.FTA/r.totals.FGA} : {}),sourceSeason:reference.season}};
 })};
}

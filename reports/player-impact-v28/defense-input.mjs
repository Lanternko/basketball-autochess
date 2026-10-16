// Attach before counterfactual edits; these are original source anchors.
export function attachDefenseAnchors(players){
 for(const p of players){
  const m=p.defenseExposureMeasurement;if(!m)throw Error('Missing defense exposure');
  p.defenseExposureMeasurement={...m,long:{...m.long,sourceAttribute:p.onBall},short:{...m.short,sourceAttribute:p.help}};
 }
 return players;
}

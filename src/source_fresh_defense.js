// Adjusted source FG associations for five defenders. These are not pure skills.
import * as M from './probability_model.js';
import * as C from './constants.js';
const zones=['long','mid','short'];
export function sourceFreshDefense(lineup){
 if(lineup.length!==5)throw new RangeError('Need five defenders');
 const logits=Object.fromEntries(zones.map(z=>[z,0])),attributeDelta={long:0,short:0};let sourcePhysique=0;
 for(const p of lineup){
  const m=p.freshDefenseMeasurement;
  if(!m||![m.sourceOnBall,m.sourceHelp,m.sourcePhysique,...zones.map(z=>m.logits?.[z])].every(Number.isFinite))throw new TypeError('Missing finite source FG defense descriptor');
  for(const z of zones)logits[z]+=m.logits[z];sourcePhysique+=m.sourcePhysique;
  for(const[z,key,anchor,curve]of [['long','onBall','sourceOnBall',C.CURVE_DEF_3PT],['short','help','sourceHelp',C.CURVE_DEF_RIM]]){
   const exposure=p.defenseExposureMeasurement,rate=exposure?.[z]?.rate,den=exposure?.leagueAttemptsPerTeamMinute?.[z];
   if(!Number.isFinite(p[key])||!Number.isFinite(rate)||rate<0||!Number.isFinite(den)||den<=0)throw new TypeError('Missing source contest activity for attribute delta');
   if(p[key]!==m[anchor])attributeDelta[z]+=rate*(M.interpolate(p[key],curve)-M.interpolate(m[anchor],curve))/den;
  }
 }
 attributeDelta.mid=(attributeDelta.long+attributeDelta.short)*.5*C.DEF_MID_SCALE;
 return {logits,attributeDelta,sourcePhysique:sourcePhysique/5};
}
export function shiftMakeLogit(probability,delta){
 if(!Number.isFinite(probability)||probability<0||probability>1||!Number.isFinite(delta))throw new RangeError('Invalid make/logit inputs');
 if(probability===0||probability===1||delta===0)return probability;
 const eta=Math.log(probability)-Math.log1p(-probability)+delta;
 if(eta>=0)return 1/(1+Math.exp(-eta));const odds=Math.exp(eta);return odds/(1+odds);
}

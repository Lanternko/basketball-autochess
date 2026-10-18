// Source event descriptors for blocks conditional on an already determined miss.
// FG defense already includes blocking; this module never changes make chance.
import {BLOCK_RULES} from './rebound_block_model.js';
const attr=v=>Math.max(0,Math.min(150,Number.isFinite(v)?v:70));
const contribution=(p,zone)=>1+BLOCK_RULES.skillSpan*Math.tanh(((zone==='long'?.7*attr(p.onBall)+.3*attr(p.physique):.8*attr(p.help)+.2*attr(p.physique))-70)/BLOCK_RULES.skillScale);
export function measuredBlockProbabilities(lineup,zone='short'){
 if(!['long','mid','short'].includes(zone)||lineup.length!==5)throw new RangeError('Block labels require five defenders and a valid zone');
 const logs=lineup.map(p=>{
  const m=p.blockEventMeasurement;
  if(!m||![m.logHazard,m.zoneLogBase?.[zone],m.sourceOnBall,m.sourceHelp,m.sourcePhysique].every(Number.isFinite))throw new TypeError('Missing finite block event descriptor');
  const source={onBall:m.sourceOnBall,help:m.sourceHelp,physique:m.sourcePhysique};
  return m.logHazard+m.zoneLogBase[zone]+Math.log(contribution(p,zone)/contribution(source,zone));
 });
 const maximum=Math.max(0,...logs),scaled=logs.map(v=>Math.exp(v-maximum)),none=Math.exp(-maximum),total=none+scaled.reduce((a,b)=>a+b,0),probabilities=scaled.map(v=>v/total);
 return {probabilities,noneProbability:none/total,conditionalOnMiss:probabilities.reduce((a,b)=>a+b,0)};
}
export function drawMeasuredBlock(lineup,zone,u){
 if(!Number.isFinite(u)||u<0||u>=1)throw new RangeError('Block draw must be in [0,1)');
 const {probabilities}=measuredBlockProbabilities(lineup,zone);let cumulative=0;
 for(let i=0;i<5;i++){cumulative+=probabilities[i];if(u<cumulative)return i;}
 return -1;
}
export function coupledBlockLabel(lineup,{zone='short',legacyProbability},rng){
 if(!Number.isFinite(legacyProbability)||legacyProbability<0||legacyProbability>1)throw new RangeError('Invalid legacy block probability');
 const u=rng();
 // Preserve the archived engine's RNG schedule. The consumed recipient draw
 // never controls the new label, which uses one joint categorical uniform.
 if(u<legacyProbability)rng();
 return drawMeasuredBlock(lineup,zone,u);
}

import {freshZoneProbability} from '../player-impact-v5/model.mjs';
export {opportunityPlan,contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';
export function spaceProbability(p,player,putback,opt){
 const q={...p,make:{...p.make,long:Math.max(.05,Math.min(.62,p.make.long-(opt.spaceCenter??0)))}};
 // Force rebuilding expected events for putbacks as well; their three zone
 // weight is zero but altered EV fields must never remain stale.
 const r=freshZoneProbability(q,player,false),zone=putback?{long:0,mid:0,short:1}:r.zone,shot=Math.max(0,1-r.pTovTouch-r.pFoul);
 for(const [z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){r[m]=shot*zone[z]*r.make[z];r[x]=shot*zone[z]*(1-r.make[z]);}
 r.zone=zone;r.ev=r.FG3M*3+(r.MIDM+r.RIMM)*2+r.pFoul*2*r.ftPct;return r;
}

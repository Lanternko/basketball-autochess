import {spaceProbability as previousSpace} from '../player-impact-v14/model.mjs';
import * as C from '../../src/constants.js';
export function measuredPutbackMake(probability,measurement){
 if(!measurement||![probability,measurement.rate,measurement.sourceBase,measurement.context].every(Number.isFinite)||measurement.rate<0||measurement.rate>1)throw Error('Missing valid measured putback source');
 const value=probability+measurement.rate-measurement.sourceBase-measurement.context;
 return Math.max(C.CLAMP.makeShort[0],Math.min(C.CLAMP.makeShort[1],value));
}
export function spaceProbability(p,player,putback,opt){
 if(!putback)return previousSpace(p,player,false,opt);
 const q=previousSpace(p,player,true,opt),make={...q.make,short:measuredPutbackMake(p.make.short,player.putbackMeasurement)},shot=Math.max(0,1-q.pTovTouch-q.pFoul);
 q.make=make;q.zone={long:0,mid:0,short:1};q.FG3M=q.FG3X=q.MIDM=q.MIDX=0;q.RIMM=shot*make.short;q.RIMX=shot*(1-make.short);
 q.ev=q.RIMM*2+q.pFoul*C.FT_ATTEMPTS*q.ftPct;
 return q;
}

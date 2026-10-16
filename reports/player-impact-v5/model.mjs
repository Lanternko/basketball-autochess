export {opportunityPlan,balancedReceivers,contestHelp} from '../player-impact-v4/model.mjs';
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function freshZoneProbability(p,player,putback){
 if(putback)return p;
 const zone=player.opportunityMeasurement.freshZone;
 if(!zone)throw Error('Missing fresh-shot zone profile');
 const q={...p,zone:{...zone}},shot=Math.max(0,1-p.pTovTouch-p.pFoul);
 for(const [z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){q[m]=shot*zone[z]*p.make[z];q[x]=shot*zone[z]*(1-p.make[z]);}
 q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+p.pFoul*2*p.ftPct;return q;
}
export function observedFoulInputs(p,player,opt,attemptMakeProbability){
 const zones=['long','mid','short'],r=player.shotProfile.freeThrowsPerAttempt;
 if(!Number.isFinite(r)||r<0)throw Error('Missing measured FT/FGA');
 const inputs=k=>Object.fromEntries(zones.map(z=>{
  const base=opt.foulRates[z],qMiss=clamp(base.foulGivenMiss*k,0,.8),qMake=clamp(base.foulGivenMake*k,0,.4);
  const raw=attemptMakeProbability(p.make[z],qMiss);
  return [z,{qMiss,qMake,raw,recorded:1-(1-raw)*qMiss}];
 }));
 // FTA/FGA = P(make|FGA)*P(and-one|make)
 // + P(miss|FGA)*qMiss/(1-qMiss)*FT attempts. The denominator
 // excludes foul misses, exactly as NBA recorded FGA does.
 const ftr=x=>zones.reduce((s,z)=>s+p.zone[z]*(p.make[z]*x[z].qMake+(1-p.make[z])*x[z].qMiss/(1-x[z].qMiss)*(z==='long'?3:2)),0);
 let lo=0,hi=1;while(hi<1024&&ftr(inputs(hi))<r)hi*=2;
 for(let i=0;i<28;i++){const mid=(lo+hi)/2;if(ftr(inputs(mid))<r)lo=mid;else hi=mid;}
 return inputs((lo+hi)/2);
}

const sigmoid=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
export function recordedZoneChoice(player,defenders){
 const own=player.defensiveChoiceMeasurement;
 if(!own||defenders.length!==5||defenders.some(p=>!p.defensiveChoiceMeasurement))throw Error('Incomplete defensive shot-choice descriptors');
 const eta=key=>own.shooter[key]+defenders.reduce((s,p)=>s+p.defensiveChoiceMeasurement.defender[key],0);
 const long=sigmoid(eta('three')),paint=sigmoid(eta('paintGivenTwo'));
 return {long,mid:(1-long)*(1-paint),short:(1-long)*paint};
}
export function applyRecordedZone(probability,zone){
 if(!zone||['long','mid','short'].some(z=>!Number.isFinite(zone[z])||zone[z]<0)||Math.abs(zone.long+zone.mid+zone.short-1)>1e-10)throw Error('Invalid defensive zone simplex');
 const q={...probability,zone:{...zone}},shot=Math.max(0,1-q.pTovTouch-q.pFoul);
 for(const[z,m,x]of [['long','FG3M','FG3X'],['mid','MIDM','MIDX'],['short','RIMM','RIMX']]){q[m]=shot*zone[z]*q.make[z];q[x]=shot*zone[z]*(1-q.make[z]);}
 q.ev=q.FG3M*3+(q.MIDM+q.RIMM)*2+q.pFoul*2*q.ftPct;return q;
}

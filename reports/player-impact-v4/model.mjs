const cache=new Map();
export function balancedReceivers(row,column){
 const n=row.length,total=row.reduce((s,v)=>s+v,0),cs=column.reduce((s,v)=>s+v,0);
 if(!total||!cs)return row.map((_,i)=>column.map((v,j)=>i===j?0:v));
 let c=column.map(v=>v/cs*total);
 // No player can assist himself. Redistribute an infeasible column demand.
 for(let k=0;k<n+1;k++){
  let excess=0,room=0;
  c=c.map((v,j)=>{const cap=Math.max(1e-9,total-row[j])*.999999;if(v>cap){excess+=v-cap;return cap;}room+=cap-v;return v;});
  if(excess<1e-10)break;
  c=c.map((v,j)=>v+excess*Math.max(0,(total-row[j])*.999999-v)/room);
 }
 const a=row.map((_,i)=>c.map((v,j)=>i===j?0:v));
 for(let k=0;k<40;k++){
  for(let i=0;i<n;i++){const sum=a[i].reduce((s,v)=>s+v,0);if(sum)for(let j=0;j<n;j++)a[i][j]*=row[i]/sum;}
  for(let j=0;j<n;j++){const sum=a.reduce((s,r)=>s+r[j],0);if(sum)for(let i=0;i<n;i++)a[i][j]*=c[j]/sum;}
 }
 return a;
}
export function opportunityPlan(lineup,probability,pressure=1){
 const key=lineup.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');
 let receivers=cache.get(key);
 if(!receivers){receivers=balancedReceivers(lineup.map(p=>p.opportunityMeasurement.passOpportunityRate),lineup.map(p=>p.opportunityMeasurement.receiveOpportunityRate));if(cache.size>4096)cache.clear();cache.set(key,receivers);}
 const rows=lineup.map((p,i)=>{
  const m=p.opportunityMeasurement;if(!m)throw Error('Missing source-context opportunity measurement');
  const self=m.selfOpportunityRate,pass=m.passOpportunityRate+m.passStolenPerMinute*pressure,total=self+pass;
  return {weight:total,shoot:total?self/total:1,intercept:pass?Math.min(.95,m.passStolenPerMinute*pressure/pass):0,receivers:receivers[i]};
 });
 return {weights:rows.map(r=>Math.max(.0001,r.weight)),rows};
}
export {contestHelp} from '../player-impact-v3/model.mjs';

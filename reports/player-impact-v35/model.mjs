// Joint creator->finisher allocation. Diagonal is own shooting, never an assist.
// Frozen source roles define a prior rather than a hard self/pass boundary.
import {elasticLineup} from '../player-impact-v8/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';

export function balanceKernel(kernel,row,column){
 const n=row.length,total=row.reduce((s,v)=>s+v,0);
 if(!n||column.length!==n||kernel.length!==n||row.some(v=>!Number.isFinite(v)||v<=0)||column.some(v=>!Number.isFinite(v)||v<=0)||Math.abs(total-column.reduce((s,v)=>s+v,0))>1e-8||kernel.some(r=>r.length!==n||r.some(v=>!Number.isFinite(v)||v<=0)))throw Error('Joint transport requires positive source support and equal marginals');
 const a=kernel.map(r=>[...r]);let converged=false;
 for(let k=0;k<1000;k++){
  for(let i=0;i<n;i++){const den=a[i].reduce((s,v)=>s+v,0),scale=row[i]/den;for(let j=0;j<n;j++)a[i][j]*=scale;}
  for(let j=0;j<n;j++){const den=a.reduce((s,r)=>s+r[j],0),scale=column[j]/den;for(let i=0;i<n;i++)a[i][j]*=scale;}
  const error=Math.max(...a.map((r,i)=>Math.abs(r.reduce((s,v)=>s+v,0)-row[i])));
  if(error<1e-11*Math.max(1,total)){converged=true;break;}
 }
 if(!converged||a.some(r=>r.some(v=>!Number.isFinite(v)||v<=0)))throw Error('Joint creator transport failed convergence');
 return a;
}

export function jointFlow(lineup){
 const ms=lineup.map(p=>p.opportunityMeasurement),n=ms.length;
 if(n!==5)throw Error('Joint creator flow requires five players');
 for(const m of ms)if(['terminalOpportunityRate','selfOpportunityRate','receiveOpportunityRate','passOpportunityRate'].some(k=>!Number.isFinite(m[k])||m[k]<=0)||!Number.isFinite(m.passStolenPerMinute)||m.passStolenPerMinute<0||Math.abs(m.selfOpportunityRate+m.receiveOpportunityRate-m.terminalOpportunityRate)>1e-8)throw Error('Invalid positive source role accounting');
 const terminal=ms.map(m=>m.terminalOpportunityRate),rawCreator=ms.map(m=>m.selfOpportunityRate+m.passOpportunityRate),total=terminal.reduce((s,v)=>s+v,0),normalization=total/rawCreator.reduce((s,v)=>s+v,0),creator=rawCreator.map(v=>v*normalization);
 const receive=ms.map(m=>m.receiveOpportunityRate),receiveTotal=receive.reduce((s,v)=>s+v,0);
 const kernel=ms.map((m,i)=>receive.map((v,j)=>i===j?m.selfOpportunityRate:m.passOpportunityRate*v/(receiveTotal-receive[i])));
 const joint=balanceKernel(kernel,creator,terminal),self=ms.map((_,i)=>joint[i][i]),matrix=joint.map((r,i)=>r.map((v,j)=>i===j?0:v)),rows=matrix.map(r=>r.reduce((s,v)=>s+v,0)),incoming=ms.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 for(let i=0;i<n;i++)if(Math.abs(self[i]+incoming[i]-terminal[i])>1e-8||Math.abs(self[i]+rows[i]-creator[i])>1e-8)throw Error('Joint opportunity conservation failed');
 return {matrix,rows,incoming,self,terminal,creator,rawCreator,normalization,kernel,joint};
}
const cache=new Map();
export function opportunityPlan(lineup,probability,pressure=1,policy='rotation-space'){
 if(!['rotation-space','supply-creation'].includes(policy))throw Error('Unknown joint creator policy');
 const ls=elasticLineup(lineup,'elastic-creation');
 const key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');let flow=cache.get(key);
 if(!flow){flow=jointFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{
  const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;
  return {weight,shoot:flow.self[i]/weight,intercept:Math.min(.95,lost/pass),receivers:flow.matrix[i]};
 });
 return {weights:rows.map(r=>r.weight),rows};
}

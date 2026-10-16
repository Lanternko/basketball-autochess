// Strict-feasibility prototype only. Not imported by any season/OVR runtime.
import {supplyFlow} from '../../player-impact-v11/model.mjs';

export function ownPoolFlow(lineup){
 const old=supplyFlow(lineup),total=old.terminal.reduce((s,v)=>s+v,0),own=total-old.rows.reduce((s,v)=>s+v,0),tol=1e-10*Math.max(1,total);
 const sourceOwn=lineup.map(p=>p.opportunityMeasurement.selfOpportunityRate);
 if(lineup.length!==5||sourceOwn.some(v=>!Number.isFinite(v)||v<=0)||own<=tol||old.rows.some((v,i)=>total-old.terminal[i]-v<=tol))throw new RangeError('Need strictly feasible positive own-pool and fixed passer rows');
 const row=[...old.rows,own],column=old.terminal,prior=[...old.matrix.map(r=>[...r]),sourceOwn],a=prior.map(r=>[...r]);let iterations=0,converged=false;
 for(;iterations<20000;iterations++){
  for(let i=0;i<6;i++){const scale=row[i]/a[i].reduce((s,v)=>s+v,0);for(let j=0;j<5;j++)a[i][j]*=scale;}
  for(let j=0;j<5;j++){const scale=column[j]/a.reduce((s,r)=>s+r[j],0);for(let i=0;i<6;i++)a[i][j]*=scale;}
  const error=Math.max(...a.map((r,i)=>Math.abs(r.reduce((s,v)=>s+v,0)-row[i])));
  if(error<1e-11*Math.max(1,total)){converged=true;break;}
 }
 if(!converged)throw Error('Own-pool transport did not converge; never silently fall back');
 const matrix=a.slice(0,5),self=a[5],rows=matrix.map(r=>r.reduce((s,v)=>s+v,0)),incoming=column.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 for(let i=0;i<5;i++){
  if(!(self[i]>0)||matrix[i][i]!==0||Math.abs(rows[i]-old.rows[i])>1e-8||Math.abs(self[i]+incoming[i]-column[i])>1e-8)throw Error('Own-pool conservation failed');
 }
 return {matrix,self,rows,incoming,terminal:column,prior,joint:a,ownPool:own,iterations:iterations+1,old};
}

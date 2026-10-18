// Preserve successful passer supply when a positive autonomous pool is feasible.
// Otherwise relax passer rows explicitly using an unfitted source column prior.
import {supplyFlow} from '../player-impact-v11/model.mjs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';

export function sourceFlow(lineup){
 const ms=lineup.map(p=>p.opportunityMeasurement);
 if(ms.length!==5||ms.some(m=>!m||['terminalOpportunityRate','selfOpportunityRate','receiveOpportunityRate','passOpportunityRate'].some(k=>!Number.isFinite(m[k])||m[k]<=0)||!Number.isFinite(m.passStolenPerMinute)||m.passStolenPerMinute<0||Math.abs(m.selfOpportunityRate+m.receiveOpportunityRate-m.terminalOpportunityRate)>1e-8))throw Error('Need five positive source roles');
 const old=supplyFlow(lineup),terminal=old.terminal,total=terminal.reduce((s,v)=>s+v,0),ownPool=total-old.rows.reduce((s,v)=>s+v,0),tol=1e-10*Math.max(1,total);
 const strict=ownPool>tol&&old.rows.every((v,i)=>total-terminal[i]-v>tol);
 let prior,joint,iterations=0;
 if(strict){
  prior=[...old.matrix.map(r=>[...r]),ms.map(m=>m.selfOpportunityRate)];
  joint=prior.map(r=>[...r]);const margins=[...old.rows,ownPool];let converged=false;
  for(;iterations<20000;iterations++){
   for(let i=0;i<6;i++){const scale=margins[i]/joint[i].reduce((s,v)=>s+v,0);for(let j=0;j<5;j++)joint[i][j]*=scale;}
   for(let j=0;j<5;j++){const scale=terminal[j]/joint.reduce((s,r)=>s+r[j],0);for(let i=0;i<6;i++)joint[i][j]*=scale;}
   const error=Math.max(...joint.map((r,i)=>Math.abs(r.reduce((s,v)=>s+v,0)-margins[i])));
   if(error<1e-11*Math.max(1,total)){converged=true;break;}
  }
  if(!converged)throw Error('Own-pool projection did not converge; no numerical fallback');
  iterations++;
 }else{
  const receive=ms.map(m=>m.receiveOpportunityRate),sum=receive.reduce((s,v)=>s+v,0);
  prior=ms.map((m,i)=>receive.map((v,j)=>i===j?m.selfOpportunityRate:m.passOpportunityRate*v/(sum-receive[i])));
  joint=prior.map(r=>[...r]);
  for(let j=0;j<5;j++){const scale=terminal[j]/joint.reduce((s,r)=>s+r[j],0);for(let i=0;i<5;i++)joint[i][j]*=scale;}
 }
 const self=strict?joint[5]:joint.map((r,i)=>r[i]),matrix=strict?joint.slice(0,5):joint.map((r,i)=>r.map((v,j)=>i===j?0:v));
 const rows=matrix.map(r=>r.reduce((s,v)=>s+v,0)),incoming=terminal.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 for(let i=0;i<5;i++)if(!(self[i]>0)||!Number.isFinite(self[i])||matrix[i][i]!==0||matrix[i].some(v=>!Number.isFinite(v)||v<0)||Math.abs(self[i]+incoming[i]-terminal[i])>1e-8||strict&&Math.abs(rows[i]-old.rows[i])>1e-8)throw Error('Own/pass conservation failed');
 return {branch:strict?'fixed-pass-rows':'relaxed-source-columns',matrix,self,rows,incoming,terminal,prior,joint,ownPool,iterations,old};
}
const cache=new Map();
export function opportunityPlan(lineup,probability,pressure=1,policy='rotation-space'){
 if(!['rotation-space','supply-creation'].includes(policy)||!Number.isFinite(pressure)||pressure<0)throw Error('Invalid own-pool policy or pressure');
 const ls=elasticLineup(lineup,'elastic-creation'),key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');let flow=cache.get(key);
 if(!flow){flow=sourceFlow(ls);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;return {weight,shoot:flow.self[i]/weight,intercept:Math.min(.95,lost/pass),receivers:flow.matrix[i]};});
 return {weights:rows.map(r=>r.weight),rows};
}

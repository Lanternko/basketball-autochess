// Receiver terminal budgets are conserved. Source creation is a positive prior,
// not a hard creator-row budget or a hard self floor/ceiling.
import fs from 'node:fs';
import {elasticLineup} from '../player-impact-v8/model.mjs';
export {contestHelp} from '../player-impact-v6/model.mjs';
export {observedFoulInputs} from '../player-impact-validation/fast-model.mjs';

export function priorFlow(lineup,selfScale=1){
 const ms=lineup.map(p=>p.opportunityMeasurement),n=ms.length;
 if(n!==5||!Number.isFinite(selfScale)||selfScale<=0)throw Error('Need five players and positive self scale');
 for(const m of ms)if(['terminalOpportunityRate','selfOpportunityRate','receiveOpportunityRate','passOpportunityRate'].some(k=>!Number.isFinite(m[k])||m[k]<=0)||!Number.isFinite(m.passStolenPerMinute)||m.passStolenPerMinute<0||Math.abs(m.selfOpportunityRate+m.receiveOpportunityRate-m.terminalOpportunityRate)>1e-8)throw Error('Invalid positive source role');
 const receive=ms.map(m=>m.receiveOpportunityRate),total=receive.reduce((s,v)=>s+v,0);
 const kernel=ms.map((m,i)=>receive.map((v,j)=>i===j?m.selfOpportunityRate:m.passOpportunityRate*v/(total-receive[i])));
 const terminal=ms.map(m=>m.terminalOpportunityRate),joint=kernel.map((r,i)=>r.map((v,j)=>v*(i===j?selfScale:1)));
 for(let j=0;j<n;j++){const den=joint.reduce((s,r)=>s+r[j],0);for(let i=0;i<n;i++)joint[i][j]*=terminal[j]/den;}
 const self=ms.map((_,i)=>joint[i][i]),matrix=joint.map((r,i)=>r.map((v,j)=>i===j?0:v)),rows=matrix.map(r=>r.reduce((s,v)=>s+v,0)),incoming=ms.map((_,j)=>matrix.reduce((s,r)=>s+r[j],0));
 for(let i=0;i<n;i++)if(!(self[i]>0)||Math.abs(self[i]+incoming[i]-terminal[i])>1e-9)throw Error('Terminal prior flow failed');
 return {kernel,joint,matrix,rows,self,incoming,terminal};
}
const cache=new Map();let fittedScale;
export function opportunityPlan(lineup,probability,pressure=1,policy='rotation-space'){
 if(!['rotation-space','supply-creation'].includes(policy))throw Error('Unknown terminal-prior policy');
 if(fittedScale===undefined){const f=JSON.parse(fs.readFileSync('reports/player-impact-v36/marked-fit.json'));fittedScale=f.selfScale;if(!Number.isFinite(fittedScale)||fittedScale<=0)throw Error('Missing positive fitted scale');}
 const ls=elasticLineup(lineup,'elastic-creation'),key=ls.map(p=>p.playerId+':'+Object.values(p.opportunityMeasurement).join(',')).join('|');let flow=cache.get(key);
 if(!flow){flow=priorFlow(ls,fittedScale);if(cache.size>4096)cache.clear();cache.set(key,flow);}
 const rows=ls.map((p,i)=>{const lost=p.opportunityMeasurement.passStolenPerMinute*pressure,pass=flow.rows[i]+lost,weight=flow.self[i]+pass;return {weight,shoot:flow.self[i]/weight,intercept:Math.min(.95,lost/pass),receivers:flow.matrix[i]};});
 return {weights:rows.map(r=>r.weight),rows};
}

import fs from 'node:fs';
import * as M from '../../../src/probability_model.js';
import * as C from '../../../src/constants.js';
const root='reports/defense-tenth/step4-t2b',read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const inverse=(p,curve)=>{for(let i=1;i<curve.length;i++){const [a,b]=curve[i-1],[c,d]=curve[i];if(p>=Math.min(b,d)&&p<=Math.max(b,d))return a+(p-b)/(d-b)*(c-a);}return Math.abs(p-curve[0][1])<Math.abs(p-curve.at(-1)[1])?curve[0][0]:curve.at(-1)[0];};
const p=read(root+'/protocol.json'),out=[];
for(const c of p.cases){
 const priorFile=`reports/defense-tenth/step3-a2/bundles/${c.season}-L2-20261012.json`,currentFile=`reports/defense-tenth/step4-t0/${c.season}/bundle.json`;
 const old=read(priorFile),cur=read(currentFile),a=old.league.teams.find(t=>t.name===c.team),b=cur.league.teams.find(t=>t.name===c.team);
 const calibration=c.season==='2025-26'?null:read(`reports/defense-tenth/step4-t0/${c.season}/calibration-v3.json`).selected;
 for(const q of b.roster){
  const previous=a.roster.find(x=>x.playerId===q.playerId);if(!previous)throw Error('Missing L2 roster '+q.playerId);
  const now=structuredClone(q);
  if(calibration)for(const z of ['long','mid','short']){const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z],v=Math.max(.001,Math.min(.999,M.interpolate(now[z],curve)));now[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-(calibration.shotDelta??0))),curve)));}
  const fields=x=>Object.fromEntries(['long','mid','short','handle','pass','drive','offBall'].map(k=>[k,x[k]]));
  out.push({season:c.season,team:c.team,id:q.playerId,name:q.name,priorKind:previous.a2CardSource,priorAbilitySource:previous.abilitySource,prior:fields(previous),currentRaw:fields(q),currentEffective:fields(now),priorInterpolated:Object.fromEntries(['long','mid','short'].map(k=>[k,M.interpolate(previous[k],{long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[k])])),currentInterpolated:Object.fromEntries(['long','mid','short'].map(k=>[k,M.interpolate(now[k],{long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[k])])),sources:{prior:priorFile,current:currentFile,currentShotDelta:calibration?.shotDelta??0}});
 }
}
fs.writeFileSync(root+'/card-comparisons.json',JSON.stringify(out,null,2)+'\n');console.log('CARDS',out.length);

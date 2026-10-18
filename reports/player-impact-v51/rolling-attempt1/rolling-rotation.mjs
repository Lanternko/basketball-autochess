import {jointPlan} from './rolling-planner.mjs';
// Game-minute targets + out-of-fold historical phase and pair preferences.
// No player ability, name, score outcome, or target-game stint input is used.
const states=new WeakMap();
const sigmoid=x=>1/(1+Math.exp(-x)),clip=(x,a,b)=>Math.max(a,Math.min(b,x));
const pairKey=(a,b)=>a<b?a+'/'+b:b+'/'+a;
function overlap(ma,mb,logOR){
 let lo=Math.max(0,ma+mb-48),hi=Math.min(ma,mb);
 for(let i=0;i<45;i++){const x=(lo+hi)/2,log=Math.log(Math.max(1e-12,x))+Math.log(Math.max(1e-12,48-ma-mb+x))-Math.log(Math.max(1e-12,ma-x))-Math.log(Math.max(1e-12,mb-x));if(log<logOR)lo=x;else hi=x;}
 return (lo+hi)/2;
}
function prepare(sides,opt){
 const fit=opt.measuredRotationProfiles,fold=fit?.foldByGame[opt.rotationGameId],ref=fold===undefined?fit?.fallbackPrior:fit.folds[fold];
 if(!fit||!ref)throw Error('Missing rotation profiles');
 const state=sides.map(s=>{
  const tid=s.rotationTeamId,n=s.roster.length,targets=s.roster.map(p=>p.targetMinutes??0);
  const logits=Array.from({length:24},(_,b)=>s.roster.map(p=>{const q=clip(ref.players[`${tid}/${p.playerId}/${Number(Boolean(p.officialStarter))}`]?.[b]??(p.targetMinutes??0)/48,1e-6,1-1e-6);return Math.log(q/(1-q));}));
  // Alternate logistic row/column calibration: five players per phase and each
  // player's game-minute total, then normalize each cumulative quota endpoint.
  const a=Array(n).fill(0),beta=Array(24).fill(0);
  for(let it=0;it<80;it++){
   for(let j=0;j<n;j++){let sum=0,d=0;for(let b=0;b<24;b++){const q=sigmoid(logits[b][j]+a[j]+beta[b]);sum+=q;d+=q*(1-q);}a[j]+=clip((targets[j]/2-sum)/Math.max(.001,d),-2,2);}
   for(let b=0;b<24;b++){let sum=0,d=0;for(let j=0;j<n;j++){const q=sigmoid(logits[b][j]+a[j]+beta[b]);sum+=q;d+=q*(1-q);}beta[b]+=clip((5-sum)/Math.max(.001,d),-2,2);}
  }
  const cdf=s.roster.map((p,j)=>{const w=logits.map((row,b)=>sigmoid(row[j]+a[j]+beta[b])),den=w.reduce((a,b)=>a+b,0);let sum=0;return [0,...w.map(v=>(sum+=v)*targets[j]/den)];});
  const pairs=new Map();for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const pa=s.roster[i].playerId,pb=s.roster[j].playerId,logOR=ref.pairs[`${tid}/${pairKey(pa,pb)}`]??0;pairs.set(pairKey(i,j),{target:overlap(targets[i],targets[j],logOR),played:0});}
  const state={targets,cdf,pairs,lastOut:Array(n).fill(-Infinity),minimumStint:fit.minimumByFold?.[fold]?.minimumStint??fit.minimumStintSeconds,minimumRest:fit.minimumByFold?.[fold]?.minimumRest??fit.minimumRestSeconds};
  if(opt.rotationController!=='baseline'){
   state.plan=jointPlan({targets,cdf,pairs,starters:s.lineup,minimumStint:state.minimumStint,minimumRest:state.minimumRest,seed:51001,passes:6000});
   state.sourceCDF=cdf;state.cdf=state.plan.cdf;state.epoch=0;state.offset=Array(n).fill(0);state.availableKey=s.roster.flatMap((p,i)=>!p.injured&&p.targetMinutes>0&&s.players[i].pf<opt.foulOut?[i]:[]).join(',');
   opt.rotationPlanObserver?.({gameId:opt.rotationGameId,teamId:tid,targets,plan:state.plan});
  }
  return state;
 });states.set(sides,state);return state;
}
export function observeRotationInterval(sides,seconds,opt){
 if(opt.rotationPolicy!=='measured'||!(seconds>0))return;
 const state=states.get(sides)??prepare(sides,opt);
 sides.forEach((s,si)=>{for(let a=0;a<5;a++)for(let b=a+1;b<5;b++)state[si].pairs.get(pairKey(s.lineup[a],s.lineup[b])).played+=seconds/60;});
}
export function measuredRotate({sides,period,clock,elapsed,opt,protectedPlayer,protectedSide,emit}){
 if(opt.rotationPolicy!=='measured'||period>4)return false;
 // Preserve the engine's existing minimum-five foul-exhaustion fallback. This
 // experiment changes rotation, not the separate technical-foul event model.
 if(sides.some(s=>s.roster.filter((p,i)=>!p.injured&&p.targetMinutes>0&&s.players[i].pf<opt.foulOut).length<5)){
  opt.rotationExceptionObserver?.({gameId:opt.rotationGameId,period,elapsed:elapsed/10,reason:'minimum-five-foul-exhaustion-legacy-fallback'});return false;
 }
 const statesForGame=states.get(sides)??prepare(sides,opt),now=elapsed/10,remaining=Math.max(0,2880-now);
 for(const [si,s] of sides.entries()){
  const state=statesForGame[si],played=s.players.map(p=>p.regulationSeconds/60),available=s.roster.flatMap((p,i)=>!p.injured&&p.targetMinutes>0&&s.players[i].pf<opt.foulOut?[i]:[]);
  if(state.plan&&remaining>0&&((period>1&&clock===opt.quarterSeconds*10&&state.epoch!==now)||available.join(',')!==state.availableKey)){
   const duration=remaining/60,slots=Math.max(4,Math.ceil(remaining/120)*4),B=slots/4;
   const rem=state.targets.map((x,i)=>available.includes(i)?Math.min(duration,Math.max(0,x-played[i])):0);
   const wanted=5*duration;let sum=rem.reduce((a,b)=>a+b,0);
   if(sum>wanted)for(let i=0;i<rem.length;i++)rem[i]*=wanted/sum;
   else for(let pass=0;pass<20&&wanted-sum>1e-8;pass++){
    const free=available.filter(i=>rem[i]<duration-1e-9),weight=free.reduce((v,i)=>v+Math.max(.01,state.targets[i]-played[i]),0),gap=wanted-sum;
    for(const i of free)rem[i]=Math.min(duration,rem[i]+gap*Math.max(.01,state.targets[i]-played[i])/weight);
    sum=rem.reduce((a,b)=>a+b,0);
   }
   const sourceAt=(i,time)=>{const phase=Math.min(24,time/120),b=Math.min(23,Math.floor(phase)),f=Math.min(1,phase-b),c=state.sourceCDF[i];return c[b]+f*(c[b+1]-c[b]);};
   const futureCDF=rem.map((x,i)=>{const start=sourceAt(i,now),den=sourceAt(i,2880)-start;return Array.from({length:B+1},(_,b)=>den>1e-9?(sourceAt(i,now+remaining*b/B)-start)*x/den:x*b/B);});
   const futurePairs=new Map();for(let i=0;i<rem.length;i++)for(let j=i+1;j<rem.length;j++){const p=state.pairs.get(pairKey(i,j));futurePairs.set(pairKey(i,j),{target:clip(p.target-p.played,Math.max(0,rem[i]+rem[j]-duration),Math.min(rem[i],rem[j]))});}
   const starters=s.lineup.filter(i=>available.includes(i)&&rem[i]>0);
   const rest=available.filter(i=>!starters.includes(i)&&rem[i]>0).sort((a,b)=>(futureCDF[b][1]-futureCDF[a][1])||b-a);while(starters.length<5)starters.push(rest.shift());
   state.plan=jointPlan({targets:rem,cdf:futureCDF,pairs:futurePairs,starters,minimumStint:state.minimumStint,minimumRest:state.minimumRest,slots,minutes:duration,seed:51001,passes:6000});
   state.cdf=state.plan.cdf;state.offset=played.slice();state.epoch=now;state.availableKey=available.join(',');
   opt.rotationPlanObserver?.({gameId:opt.rotationGameId,teamId:s.rotationTeamId,now,targets:rem,plan:state.plan});
  }
  const eligible=available.filter(i=>state.targets[i]-played[i]>.05);
  if(si===protectedSide&&available.includes(protectedPlayer)&&!eligible.includes(protectedPlayer))eligible.push(protectedPlayer);
  // A completed short appearance must not be stretched to the ordinary minimum
  // stint. Dead-ball timing may exhaust budgets slightly before the final horn.
  for(const i of available.filter(i=>!eligible.includes(i)).sort((a,b)=>(state.targets[b]-played[b])-(state.targets[a]-played[a])))if(eligible.length<5)eligible.push(i);
  if(eligible.length<5)throw Error('Fewer than five rotation-eligible players '+JSON.stringify({game:opt.rotationGameId,side:si,available,players:s.roster.map((p,i)=>({id:p.playerId,injured:p.injured,target:p.targetMinutes,pf:s.players[i].pf}))}));
  const horizon=Math.min(2880,state.plan?now:now+state.minimumStint),phase=state.plan?(horizon-state.epoch)/state.plan.stepSeconds:horizon/120,bin=Math.min(state.plan?state.plan.on[0].length-1:23,Math.floor(phase)),fraction=Math.min(1,phase-bin);
  const desired=state.cdf.map((c,i)=>(state.plan?state.offset[i]:0)+c[bin]+fraction*(c[bin+1]-c[bin]));
  const debt=desired.map((x,i)=>x-played[i]);
  const guard=i=>/G/.test(s.roster[i].pos)||(s.roster[i].heightInches??80)<=77;
  const big=i=>/C|PF/.test(s.roster[i].pos)||(s.roster[i].heightInches??78)>=81;
  const needGuard=eligible.some(guard),needBig=eligible.some(big);
  const protectedIndex=si===protectedSide?protectedPlayer:null;
  const periodOpening=period>1&&clock===opt.quarterSeconds*10;
  const urgent=i=>state.targets[i]-played[i]>=remaining/60-.05;
  const locked=new Set(s.lineup.filter(i=>i===protectedIndex||(!periodOpening&&eligible.includes(i)&&s.stint[i]<state.minimumStint&&remaining>180&&!s.lineup.some(j=>!eligible.includes(j)))));
  if(state.plan){for(const i of locked)if(i!==protectedIndex)locked.delete(i);}
  const canEnter=i=>Boolean(state.plan)||periodOpening||s.lineup.includes(i)||now-state.lastOut[i]>=state.minimumRest||remaining<=180||urgent(i)||s.lineup.some(j=>!eligible.includes(j));
  const candidates=eligible.filter(canEnter);
  const mandatory=state.plan?eligible.filter(urgent).sort((a,b)=>(state.targets[b]-played[b])-(state.targets[a]-played[a])):[];
  if(protectedIndex!==null&&!mandatory.includes(protectedIndex)&&eligible.includes(protectedIndex))mandatory.unshift(protectedIndex);
  if(mandatory.length>5){opt.rotationPlanConflictObserver?.({gameId:opt.rotationGameId,teamId:s.rotationTeamId,now,reason:'more-than-five-minute-deadlines'});mandatory.length=5;}
  const valid=ls=>new Set(ls).size===5&&ls.every(i=>eligible.includes(i))&&[...locked].every(i=>ls.includes(i))&&mandatory.every(i=>ls.includes(i))&&(state.plan||!needGuard||ls.some(guard))&&(state.plan||!needBig||ls.some(big));
  if(locked.size===5&&valid(s.lineup))continue;
  const pairDebt=Array.from({length:s.roster.length},()=>[]);
  for(let i=0;i<s.roster.length;i++)for(let j=i+1;j<s.roster.length;j++){const p=state.pairs.get(pairKey(i,j)),progress=((state.targets[i]?desired[i]/state.targets[i]:0)+(state.targets[j]?desired[j]/state.targets[j]:0))/2;pairDebt[i][j]=pairDebt[j][i]=state.plan?0:(p.target*progress-p.played)/4*Math.min(1,remaining/720);}
  const score=ls=>{
   let v=ls.reduce((sum,i)=>sum+debt[i]+(urgent(i)?remaining/60:0),0);
   for(let a=0;a<5;a++)for(let b=a+1;b<5;b++)v+=pairDebt[ls[a]][ls[b]];
   if(state.plan)for(const i of ls)v+=state.plan.on[i][Math.min(state.plan.on[0].length-1,Math.floor((now-state.epoch)/state.plan.stepSeconds))]*state.minimumStint/60;
   return v;
  };
  let best=s.lineup.slice();
  // Invalid/fouled-out players are replaced before ordinary optimization.
  for(let slot=0;slot<5;slot++)if(!eligible.includes(best[slot])){const possible=candidates.filter(i=>!best.includes(i));possible.sort((a,b)=>debt[b]-debt[a]);if(!possible.length)throw Error('Cannot replace disqualified player');best[slot]=possible[0];}
  for(const i of mandatory)if(!best.includes(i)){const possible=best.map((j,slot)=>({j,slot})).filter(x=>!mandatory.includes(x.j)&&!locked.has(x.j)).sort((a,b)=>debt[a.j]-debt[b.j]);if(possible.length)best[possible[0].slot]=i;}
  for(let pass=0;pass<3;pass++){
   let improvement=null,bestScore=valid(best)?score(best):-Infinity;
   for(let slot=0;slot<5;slot++)for(const i of candidates){if(best.includes(i)||locked.has(best[slot]))continue;const ls=best.slice();ls[slot]=i;if(!valid(ls))continue;const value=score(ls);if(value>bestScore+1e-9){bestScore=value;improvement=ls;}}
   if(!improvement)break;best=improvement;
  }
  const originalValid=valid(s.lineup),minimumGain=state.minimumStint/600;
  if(originalValid&&score(best)<=score(s.lineup)+minimumGain)continue;
  for(let slot=0;slot<5;slot++)if(best[slot]!==s.lineup[slot]){const out=s.lineup[slot],into=best[slot];state.lastOut[out]=now;s.lineup[slot]=into;s.stint[out]=0;s.stint[into]=0;emit('SUBSTITUTION',si,into,{out,forced:!eligible.includes(out),measuredRotation:true});}
 }
 return true;
}

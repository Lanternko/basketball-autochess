// Joint 30-second grid; entirely separate from the simulation's random stream.
export function jointPlan({targets,cdf,pairs,starters,minimumStint,minimumRest=0,seed=51001,passes=6000}){
 const n=targets.length,T=96,step=.5,minSlots=minimumStint/30;
 const quota=targets.map((x,i)=>Math.max(starters.includes(i)?1:0,Math.min(T,Math.floor(x/step))));
 while(quota.reduce((a,b)=>a+b,0)!==5*T){
  const add=quota.reduce((a,b)=>a+b,0)<5*T;
  const candidates=quota.map((q,i)=>i).filter(i=>add?quota[i]<T&&targets[i]>0:quota[i]>(starters.includes(i)?1:0));
  if(!candidates.length)throw Error('Infeasible minute quotas');
  candidates.sort((a,b)=>add?(targets[b]/step-quota[b])-(targets[a]/step-quota[a]):(quota[b]-targets[b]/step)-(quota[a]-targets[a]/step));
  quota[candidates[0]]+=add?1:-1;
 }
 const on=Array.from({length:n},()=>new Uint8Array(T)),left=quota.slice(),used=Array(n).fill(0),stint=Array(n).fill(0);
 const at=(i,t)=>{const phase=Math.min(24,t/4),b=Math.min(23,Math.floor(phase)),f=Math.min(1,phase-b);return (cdf[i][b]+f*(cdf[i][b+1]-cdf[i][b]))/step;};
 for(let t=0;t<T;t++){
  const urgent=left.flatMap((v,i)=>v>=T-t?[i]:[]),chosen=t===0?starters.slice():urgent.slice();
  if(chosen.length>5)throw Error('Too many mandatory grid players');
  const candidates=left.flatMap((v,i)=>v>0&&!chosen.includes(i)?[i]:[]);
  const rank=i=>at(i,Math.min(T,t+minSlots))-used[i]+(t&&on[i][t-1]&&stint[i]<minSlots?minSlots-stint[i]:0);
  candidates.sort((a,b)=>rank(b)-rank(a)||a-b);
  while(chosen.length<5)chosen.push(candidates.shift());
  if(new Set(chosen).size!==5||chosen.some(i=>!Number.isInteger(i)||left[i]<=0))throw Error('Invalid initial grid');
  for(let i=0;i<n;i++){const yes=chosen.includes(i);on[i][t]=Number(yes);if(yes){left[i]--;used[i]++;stint[i]++;}else stint[i]=0;}
 }
 const bins=on.map(row=>Array.from({length:24},(_,b)=>row.slice(4*b,4*b+4).reduce((a,v)=>a+v,0)));
 const desired=cdf.map(c=>Array.from({length:24},(_,b)=>c[b+1]-c[b]));
 const total=Array.from({length:n},()=>Array(n).fill(0)),pairTarget=Array.from({length:n},()=>Array(n).fill(0));
 for(let a=0;a<n;a++)for(let b=a+1;b<n;b++){
  for(let t=0;t<T;t++)total[a][b]+=on[a][t]*on[b][t];
  pairTarget[a][b]=pairs.get(`${a}/${b}`).target;
 }
 const rowCost=row=>{let value=0,start=-1;for(let t=0;t<=T;t++){
  if(t<T&&row[t]&&start<0){start=t;if(t>0)value+=minimumStint/600;}
  if(start>=0&&(t===T||!row[t])){value+=Math.max(0,minimumStint-(t-start)*30)/60;start=-1;}
 }return value;};
 const originalRowCost=rowCost;
 const costWithRest=row=>{let value=originalRowCost(row),start=-1;for(let t=0;t<T;t++){if(!row[t]&&t>0&&row[t-1])start=t;if(row[t]&&start>=0){value+=Math.max(0,minimumRest-(t-start)*30)/60;start=-1;}}return value;};
 const costs=on.map(costWithRest);let state=seed>>>0;
 const random=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
 let accepted=0;
 for(let pass=0;pass<passes;pass++){
  const a=Math.floor(random()*n),b=Math.floor(random()*n);if(a===b)continue;
  const t=1+Math.floor(random()*(T-1)),u=1+Math.floor(random()*(T-1));if(t===u||!on[a][t]||on[b][t]||on[a][u]||!on[b][u])continue;
  let limit=Math.min(Math.ceil(minSlots),T-t,T-u,Math.abs(t-u));
  for(let k=1;k<limit;k++)if(!on[a][t+k]||on[b][t+k]||on[a][u+k]||!on[b][u+k]){limit=k;break;}
  const length=1+Math.floor(random()*limit),binChange=new Map(),pairChange=new Map();
  const deltaBin=(i,t,d)=>{const key=i*24+Math.floor(t/4);binChange.set(key,(binChange.get(key)??0)+d);};
  const deltaPair=(i,j,d)=>{const key=Math.min(i,j)*n+Math.max(i,j);pairChange.set(key,(pairChange.get(key)??0)+d);};
  for(let k=0;k<length;k++){
   deltaBin(a,t+k,-1);deltaBin(b,t+k,1);deltaBin(a,u+k,1);deltaBin(b,u+k,-1);
   for(let c=0;c<n;c++)if(c!==a&&c!==b){if(on[c][t+k]){deltaPair(a,c,-1);deltaPair(b,c,1);}if(on[c][u+k]){deltaPair(a,c,1);deltaPair(b,c,-1);}}
  }
  let change=0;
  for(const[key,d]of binChange){const i=Math.floor(key/24),b=key%24,x=bins[i][b]*step-desired[i][b];change+=(x+d*step)**2-x*x;}
  for(const[key,d]of pairChange){const i=Math.floor(key/n),j=key%n,x=total[i][j]*step-pairTarget[i][j];change+=.25*((x+d*step)**2-x*x);}
  for(let k=0;k<length;k++){on[a][t+k]=0;on[b][t+k]=1;on[a][u+k]=1;on[b][u+k]=0;}
  const ca=costWithRest(on[a]),cb=costWithRest(on[b]);change+=ca+cb-costs[a]-costs[b];
  if(change< -1e-9){
   costs[a]=ca;costs[b]=cb;accepted++;
   for(const[key,d]of binChange)bins[Math.floor(key/24)][key%24]+=d;
   for(const[key,d]of pairChange)total[Math.floor(key/n)][key%n]+=d;
  }else for(let k=0;k<length;k++){on[a][t+k]=1;on[b][t+k]=0;on[a][u+k]=0;on[b][u+k]=1;}
 }
 const planCDF=on.map(row=>{let sum=0;return [0,...Array.from(row,v=>(sum+=v*step))];});
 for(let t=0;t<T;t++)if(on.reduce((s,row)=>s+row[t],0)!==5)throw Error('Joint plan lost five-player constraint');
 for(let i=0;i<n;i++)if(on[i].reduce((s,v)=>s+v,0)!==quota[i])throw Error('Joint plan lost quota');
 return {on: on.map(row=>Array.from(row)),cdf:planCDF,quota,accepted,stepSeconds:30};
}

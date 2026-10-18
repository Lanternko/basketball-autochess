// Continuous transport of creation supply into receiver demand. Columns and
// rows are exact marginals; diagonal cells are forbidden (no self-assists).
export function creationTransport(row,column){
 const n=row.length,total=row.reduce((s,x)=>s+x,0),eps=1e-11;
 if(n!==column.length||row.some(x=>!Number.isFinite(x)||x<0)||column.some(x=>!Number.isFinite(x)||x<0)||Math.abs(total-column.reduce((s,x)=>s+x,0))>1e-8)throw Error('Invalid transport marginals');
 if(column.some((x,i)=>x>total-row[i]+1e-8))throw Error('Self-assist constraint makes marginals infeasible');
 const a=row.map((_,i)=>column.map((x,j)=>i===j?0:x));
 if(!total)return a;
 // Entropy-style balancing supplies a smooth initial coupling. Near a hard
 // capacity it converges slowly, so a residual network finishes it exactly.
 for(let k=0;k<80;k++){
  for(let i=0;i<n;i++){const d=a[i].reduce((s,x)=>s+x,0);if(d)for(let j=0;j<n;j++)a[i][j]*=row[i]/d;}
  for(let j=0;j<n;j++){const d=a.reduce((s,r)=>s+r[j],0);if(d)for(let i=0;i<n;i++)a[i][j]*=column[j]/d;}
 }
 for(let k=0;k<1000;k++){
  const excess=a.map((r,i)=>r.reduce((s,x)=>s+x,0)-row[i]);
  const start=excess.findIndex(x=>x>eps);if(start<0)break;
  const parent=Array(2*n).fill(-1),queue=[start];parent[start]=start;let end=-1;
  for(let q=0;q<queue.length&&end<0;q++){
   const node=queue[q];
   if(node<n){
    if(node!==start&&excess[node]<-eps){end=node;break;}
    for(let j=0;j<n;j++)if(a[node][j]>eps&&parent[n+j]<0){parent[n+j]=node;queue.push(n+j);}
   }else for(let i=0;i<n;i++)if(i!==node-n&&parent[i]<0){parent[i]=node;queue.push(i);}
  }
  if(end<0)throw Error('No feasible residual creation path');
  let delta=Math.min(excess[start],-excess[end]),node=end;
  while(node!==start){const p=parent[node];if(p<n)delta=Math.min(delta,a[p][node-n]);node=p;}
  node=end;while(node!==start){const p=parent[node];if(p<n)a[p][node-n]-=delta;else a[node][p-n]+=delta;node=p;}
 }
 for(let i=0;i<n;i++)if(Math.abs(a[i].reduce((s,x)=>s+x,0)-row[i])>1e-8||Math.abs(a.reduce((s,r)=>s+r[i],0)-column[i])>1e-8||a[i][i]!==0)throw Error('Creation transport did not conserve marginals');
 return a;
}

export const deltaNamesN=['sim-v3','sim-v4','seg','naive'];
export const meanN=a=>a.reduce((s,x)=>s+x,0)/a.length;
export const sdN=a=>{const m=meanN(a);return Math.sqrt(meanN(a.map(x=>(x-m)**2)));};
export const sigmoidN=x=>1/(1+Math.exp(-Math.max(-40,Math.min(40,x))));
export function centerN(a,w){const n=w.reduce((s,x)=>s+x,0),m=a.reduce((s,x,i)=>s+x*w[i],0)/n;return a.map(x=>x-m);}
export function relationN(x,y,w=Array(x.length).fill(1)){const a=centerN(x,w),b=centerN(y,w);let xx=0,yy=0,xy=0,n=0;for(let i=0;i<a.length;i++){n+=w[i];xx+=w[i]*a[i]**2;yy+=w[i]*b[i]**2;xy+=w[i]*a[i]*b[i];}return {correlation:xx*yy>1e-20?xy/Math.sqrt(xx*yy):null,slope:xx>1e-10?xy/xx:null,SD:Math.sqrt(xx/n)};}
export function aggregateN(data,sw,tw){return data.map(season=>season.map(c=>{
 const d={};for(const v of deltaNamesN){const a=Array(30).fill(0);for(let j=0;j<20;j++)if(sw[j])for(let i=0;i<30;i++)a[i]+=c.deltas[v][j][i]*sw[j]/20;d[v]=centerN(a,tw);}
 return {...c,x:centerN(c.x,tw),y:centerN(c.y,tw),d,refSD:c.refSD.reduce((s,x,i)=>s+x*sw[i]/20,0)};
}));}
export function fitN(blocks,train,v,tw,fixed=null){
 const moments=Array.from({length:3},()=>({xx:0,xy:0,xd:0,dd:0,dy:0}));
 for(const s of train)for(let k=0;k<3;k++){const c=blocks[s][k],m=moments[k];for(let i=0;i<30;i++){const w=tw[i]/30,x=c.x[i],y=c.y[i],d=c.d[v][i];m.xx+=w*x*x;m.xy+=w*x*y;m.xd+=w*x*d;m.dd+=w*d*d;m.dy+=w*d*y;}}
 let den=0,num=0;for(const m of moments){den+=m.dd-m.xd*m.xd/Math.max(1e-20,m.xx);num+=m.dy-m.xd*m.xy/Math.max(1e-20,m.xx);}
 const b=fixed??(den>1e-10?num/den:0),a=moments.map(m=>(m.xy-b*m.xd)/Math.max(1e-20,m.xx));return {a,b,rankDeficient:den<=1e-10};
}
export function netMetricsN(pred,c,tw){const p=centerN(pred,tw),y=c.y;let mse=0;for(let i=0;i<30;i++)mse+=tw[i]*(p[i]-y[i])**2/30;const rel=relationN(p,y,tw),sy=relationN(y,y,tw).SD;return {netRMSE:Math.sqrt(mse),correlation:rel.correlation,calibrationSlope:rel.slope,SDRatio:rel.SD/sy,correlationWithSimple:relationN(p,c.x,tw).correlation};}
export function winMAEN(pred,c,tw,beta){let n=0;for(let i=0;i<30;i++)n+=tw[i]*Math.abs(c.games[i]*sigmoidN(beta*pred[i])-c.wins[i])/30;return n;}
export function logisticSlopeN(rows,tw){let b=.12;for(let it=0;it<12;it++){let score=0,info=0;for(const {p,c}of rows)for(let i=0;i<30;i++){const q=p[i],prob=sigmoidN(b*q);score+=tw[i]*q*(c.wins[i]-c.games[i]*prob);info+=tw[i]*q*q*c.games[i]*prob*(1-prob);}if(info<1e-12)break;const next=Math.max(.025,Math.min(.5,b+score/info));if(Math.abs(next-b)<1e-8){b=next;break;}b=next;}return b;}
const predict=(c,f,k,v)=>c.x.map((x,i)=>f.a[k]*x+f.b*c.d[v][i]);
export function evaluateN(data,sw=Array(20).fill(1),tw=Array(30).fill(1),includeWins=true){
 const blocks=aggregateN(data,sw,tw),all=[0,1,2,3],folds=[],cells=Array.from({length:4},()=>Array.from({length:3},()=>({versions:{},signals:{},pairs:{}})));
 for(let s=0;s<4;s++)for(let k=0;k<3;k++){
  const c=blocks[s][k],out=cells[s][k],simple=c.x,simplecal=c.x.map(x=>x*c.ms),errorSimple=c.y.map((y,i)=>y-simple[i]),errorCal=c.y.map((y,i)=>y-simplecal[i]);
  out.versions.simple={...netMetricsN(simple,c,tw),winOff:c.simpleWins.reduce((n,x,i)=>n+tw[i]*Math.abs(x-c.wins[i])/30,0)};
  out.versions.simplecal={...netMetricsN(simplecal,c,tw)};
  const trainAnchor=all.filter(j=>j!==s);let xx=0,xy=0;for(const j of trainAnchor)for(let i=0;i<30;i++){xx+=tw[i]*blocks[j][k].x[i]**2;xy+=tw[i]*blocks[j][k].x[i]*blocks[j][k].y[i];}out.versions['anchor-only']=netMetricsN(c.x.map(x=>x*xy/Math.max(1e-20,xx)),c,tw);
  if(includeWins){const train=all.filter(j=>j!==s),beta=logisticSlopeN(train.map(j=>({p:blocks[j][k].x,c:blocks[j][k]})),tw);out.versions.simple.winOn=winMAEN(simple,c,tw,beta);out.versions.simple.linkBeta=beta;}
  for(const v of deltaNamesN)out.signals[v]={simple:relationN(c.d[v],errorSimple,tw),simplecal:relationN(c.d[v],errorCal,tw)};
  for(let a=0;a<4;a++)for(let b=a+1;b<4;b++)out.pairs[deltaNamesN[a]+'/'+deltaNamesN[b]]=relationN(c.d[deltaNamesN[a]],c.d[deltaNamesN[b]],tw).correlation;
 }
 for(const v of deltaNamesN)for(const mode of ['fit','b1']){
  const name=v+'-'+mode;
  for(let s=0;s<4;s++){
   const train=all.filter(j=>j!==s),f=fitN(blocks,train,v,tw,mode==='b1'?1:null);folds.push({delta:v,mode,heldout:data[s][0].season,...f});
   const inner=includeWins?train.map(j=>({s:j,fit:fitN(blocks,train.filter(z=>z!==j),v,tw,mode==='b1'?1:null)})):[];
   for(let k=0;k<3;k++){
    const c=blocks[s][k],p=predict(c,f,k,v),result=netMetricsN(p,c,tw);
    if(includeWins){const beta=logisticSlopeN(inner.map(z=>({p:predict(blocks[z.s][k],z.fit,k,v),c:blocks[z.s][k]})),tw),refT=Math.sqrt(3)/Math.PI*meanN(train.map(j=>blocks[j][k].refSD));result.winOff=winMAEN(p,c,tw,1/refT);result.winOn=winMAEN(p,c,tw,beta);result.linkBeta=beta;result.referenceT=refT;}
    cells[s][k].versions[name]=result;
   }
  }
 }
 const pooled=Array.from({length:3},(_,k)=>{const versions={},signals={},pairs={};for(const name of Object.keys(cells[0][k].versions)){
  const rows=cells.map(s=>s[k].versions[name]);versions[name]=Object.fromEntries(Object.keys(rows[0]).map(key=>[key,key==='netRMSE'?Math.sqrt(meanN(rows.map(r=>r[key]**2))):meanN(rows.map(r=>r[key]))]));
  const yy=meanN(blocks.map(s=>relationN(s[k].y,s[k].y,tw).SD**2)),xx=meanN(rows.map((r,s)=>r.SDRatio**2*relationN(blocks[s][k].y,blocks[s][k].y,tw).SD**2)),xy=meanN(rows.map((r,s)=>r.correlation*r.SDRatio*relationN(blocks[s][k].y,blocks[s][k].y,tw).SD**2)),anchorXX=meanN(blocks.map(s=>relationN(s[k].x,s[k].x,tw).SD**2)),anchorXY=meanN(rows.map((r,s)=>r.correlationWithSimple*r.SDRatio*relationN(blocks[s][k].y,blocks[s][k].y,tw).SD*relationN(blocks[s][k].x,blocks[s][k].x,tw).SD));
  Object.assign(versions[name],{correlation:xy/Math.sqrt(xx*yy),calibrationSlope:xy/xx,SDRatio:Math.sqrt(xx/yy),correlationWithSimple:anchorXY/Math.sqrt(xx*anchorXX)});
 }
 // Signal relation pools within-season centered moments equally, not mean correlations.
 for(const v of deltaNamesN){const X=[],Y=[],Z=[],W=[];for(let s=0;s<4;s++){const c=blocks[s][k];for(let i=0;i<30;i++){X.push(c.d[v][i]);Y.push(c.y[i]-c.x[i]);Z.push(c.y[i]-c.ms*c.x[i]);W.push(tw[i]);}}signals[v]={simple:relationN(X,Y,W),simplecal:relationN(X,Z,W)};}
 for(let a=0;a<4;a++)for(let b=a+1;b<4;b++){const X=[],Y=[],W=[];for(let s=0;s<4;s++)for(let i=0;i<30;i++){X.push(blocks[s][k].d[deltaNamesN[a]][i]);Y.push(blocks[s][k].d[deltaNamesN[b]][i]);W.push(tw[i]);}pairs[deltaNamesN[a]+'/'+deltaNamesN[b]]=relationN(X,Y,W).correlation;}
 return {versions,signals,pairs};});
 return {folds,cells,pooled};
}
export function flattenN(e){const out={};for(const [group,ks]of [...e.cells.map((rows,i)=>['s'+i,rows]),['pooled',e.pooled]])for(let k=0;k<3;k++){
 const c=ks[k],prefix=group+'/K'+[25,41,55][k];for(const [v,z]of Object.entries(c.signals))for(const base of ['simple','simplecal'])for(const metric of ['correlation','slope'])out[prefix+'/signal/'+v+'/'+base+'/'+metric]=z[base][metric];
 for(const [pair,r]of Object.entries(c.pairs))out[prefix+'/deltaCorrelation/'+pair]=r;
 for(const v of deltaNamesN)for(const mode of ['fit','b1']){const name=v+'-'+mode,m=c.versions[name],simp=c.versions.simple,cal=c.versions.simplecal,naive=c.versions['naive-fit'];
  out[prefix+'/compare/'+name+'/net-simplecal']=m.netRMSE-cal.netRMSE;
  out[prefix+'/compare/'+name+'/net-min']=m.netRMSE-Math.min(simp.netRMSE,cal.netRMSE);
  out[prefix+'/compare/'+name+'/net-naive']=m.netRMSE-naive.netRMSE;
  out[prefix+'/compare/'+name+'/net-anchor-only']=m.netRMSE-c.versions['anchor-only'].netRMSE;
  if(Number.isFinite(m.winOn)){out[prefix+'/compare/'+name+'/wins-off-simple']=m.winOff-simp.winOff;out[prefix+'/compare/'+name+'/wins-on-simple']=m.winOn-simp.winOff;out[prefix+'/compare/'+name+'/wins-on-simple-on']=m.winOn-simp.winOn;out[prefix+'/compare/'+name+'/wins-on-off']=m.winOn-m.winOff;}
 }
 out[prefix+'/compare/simple/wins-on-off']=c.versions.simple.winOn-c.versions.simple.winOff;
 }
 for(const f of e.folds)out['fold/'+f.delta+'/'+f.mode+'/'+f.heldout+'/b']=f.b;
 return out;}

export function oldZone(e){return e.actionType==='3pt'?'long':/Restricted Area|In The Paint/.test(e.area??'')?'short':'mid';}
export function readZone(e){
 const old=oldZone(e),text=[e.subType,e.descriptor].join(' '),nearText=/layup|dunk|tip|putback/i.test(text);
 const distance=Number.isFinite(e.shotDistance)&&e.shotDistance>=0?e.shotDistance:null;
 const valid=Number.isFinite(e.x)&&Number.isFinite(e.y)&&e.x>=0&&e.x<=100&&e.y>=0&&e.y<=100;
 const geometry=valid?Math.hypot(Math.min(Math.abs(e.x-5.59),Math.abs(e.x-94.41))*.94,(e.y-50)*.5):null;
 const nearDistance=distance!==null&&distance<=4,nearGeometry=geometry!==null&&geometry<=4;
 if(e.actionType==='3pt')return{zone:'long',old,reason:'three-action',distance,geometry};
 if(e.actionType!=='2pt')throw Error('Expected FG');
 if(/Restricted Area|In The Paint/.test(e.area??''))return{zone:'short',old,reason:'recognized-paint',distance,geometry};
 if(e.area==='Mid-Range'){
  if(nearText&&nearDistance&&nearGeometry)return{zone:'short',old,reason:'three-source-near-basket',distance,geometry};
  if(nearText||nearDistance||nearGeometry)return{zone:'unknown',old,reason:'unresolved-mid-conflict',distance,geometry};
  return{zone:'mid',old,reason:'recognized-mid',distance,geometry};
 }
 return{zone:'unknown',old,reason:'unrecognized-area',distance,geometry};
}

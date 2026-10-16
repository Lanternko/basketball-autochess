export function pathDetails(es){
 const next=es.find(e=>['fg','ft','loss'].includes(e.kind));
 const route=!next?'period_end':next.kind==='fg'?'fg_'+next.zone:next.kind==='ft'?'ft_first':'loss_before_attempt';
 const ix=es.findIndex(e=>e.kind==='fg'),fg=ix<0?null:es[ix];
 const reb=fg&&!fg.made?es.slice(ix+1).find(e=>['fg','ft','loss','reb'].includes(e.kind)):null;
 return {route,lossKind:next?.kind==='loss'?next.lossKind:null,firstFgZone:fg?.zone??null,firstFgMade:fg?.made??null,firstFgPoints:fg?.points??0,firstFgMiss:!!fg&&!fg.made,recovery:fg&&!fg.made?(reb?.kind==='reb'&&reb.own&&!reb.freeThrow?(reb.team?'team':'player'):'none'):null,foulBeforeAttempt:es.slice(0,next?es.indexOf(next):es.length).some(e=>e.kind==='foul')};
}
export function fullCollector(){
 let current=null,rows=[],games=[];
 const close=()=>{if(!current)return;if(!current.special)for(let i=0;i<current.anchors.length;i++){const a=current.anchors[i];rows.push({off:current.off,first:i===0,points:current.points-a.points,fgPoints:current.fg-a.fg,ftPoints:current.ft-a.ft,additionalOreb:current.anchors.length-i-1,...pathDetails(current.events.slice(a.index+1))});}current=null;};
 return {event(e){
  if(e.type==='PERIOD_START'&&e.period===1){close();rows=[];games.push(rows);}
  if(['POSSESSION','PERIOD_END','GAME_END','OVERTIME_LIMIT'].includes(e.type))close();
  if(e.type==='POSSESSION')current={off:e.off,points:0,fg:0,ft:0,anchors:[],events:[],special:false};
  if(!current)return;
  if(e.technical)current.special=true;
  const own=e.off===current.off;let x=null;
  if(['FGM','FGX'].includes(e.type)&&own)x={kind:'fg',zone:e.zone,made:e.type==='FGM',points:e.points??(e.type==='FGM'?(e.zone==='long'?3:2):0)};
  if(['FTM','FTX'].includes(e.type)&&own&&!e.technical)x={kind:'ft'};
  if(['STEAL','TOV','SHOT_CLOCK','DREB','TEAM_DREB'].includes(e.type))x={kind:'loss',lossKind:e.type==='STEAL'?e.kind+'Steal':e.type==='TOV'?e.kind??'turnover':e.type};
  if(['OREB','TEAM_OREB'].includes(e.type))x={kind:'reb',own,team:e.type==='TEAM_OREB',freeThrow:!!e.freeThrow};
  if(e.type==='FOUL')x={kind:'foul'};
  if(x)current.events.push(x);
  if(own){if(e.type==='FGM'){const n=e.points??(e.zone==='long'?3:2);current.points+=n;current.fg+=n;}if(e.type==='FTM'&&!e.technical){current.points++;current.ft++;}if(e.type==='OREB'&&!e.freeThrow)current.anchors.push({points:current.points,fg:current.fg,ft:current.ft,index:current.events.length-1});}
 },finish(){close();return{games};}};
}

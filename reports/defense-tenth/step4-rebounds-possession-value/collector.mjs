// Read-only observation; never draws RNG or changes event data.
export function fullCollector(){
 let game=null,current=null,rows=[],games=[];
 const close=()=>{if(!current)return;if(!current.special)for(let i=0;i<current.anchors.length;i++){const a=current.anchors[i];rows.push({off:current.off,first:i===0,points:current.points-a.points,fgPoints:current.fg-a.fg,ftPoints:current.ft-a.ft,additionalOreb:current.anchors.length-i-1});}current=null;};
 return {event(e){
  if(e.type==='PERIOD_START'&&e.period===1){close();rows=[];games.push(rows);game=games.length-1;}
  if(['POSSESSION','PERIOD_END','GAME_END','OVERTIME_LIMIT'].includes(e.type))close();
  if(e.type==='POSSESSION')current={off:e.off,points:0,fg:0,ft:0,anchors:[],special:false};
  if(!current)return;
  if(e.technical)current.special=true;
  if(e.off===current.off){if(e.type==='FGM'){const n=e.points??(e.zone==='long'?3:2);current.points+=n;current.fg+=n;}if(e.type==='FTM'&&!e.technical){current.points++;current.ft++;}if(e.type==='OREB'&&!e.freeThrow)current.anchors.push({points:current.points,fg:current.fg,ft:current.ft});}
 },finish(){close();return{games};}};
}

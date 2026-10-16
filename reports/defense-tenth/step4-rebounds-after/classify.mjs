export function classify(reb,next){
 const dt=reb.clock-next.clock;if(next.period!==reb.period)return {category:'periodEnd',seconds:null};if(dt<0)return {category:'invalidTime',seconds:null};
 if(next.kind==='fg'){const quick=next.player===reb.player&&next.zone==='short'&&dt<=3;return {category:quick?'immediateProxy':'otherShot',seconds:dt,zone:next.zone,same:next.player===reb.player,made:next.made,points:next.points,official:next.official??false};}
 return {category:next.kind==='loss'?(dt<=3?'earlyLoss':'laterLoss'):next.kind,seconds:dt};
}
export function simCollector(){let pending=null,rows=[],games=[],excluded={ft:0,team:0};let game=-1;
 const close=e=>{if(pending){rows.push({...classify(pending,e),off:pending.off,interrupted:pending.interrupted??false});pending=null;}};
 return {event(e){
 if(e.type==='PERIOD_START'&&e.period===1){game++;rows=[];games.push(rows);}
 if(e.type==='PERIOD_END'||e.type==='GAME_END'){close({...e,kind:'periodEnd'});return;}
 if(e.type==='OREB'){if(e.freeThrow){excluded.ft++;return;}close({...e,kind:'unknown'});pending={...e};return;}
 if(e.type==='TEAM_OREB'){excluded.team++;return;}
 if(!pending)return;
 if(['SUB','SUBSTITUTION','FOUL'].includes(e.type))pending.interrupted=true;
 if(['FGM','FGX'].includes(e.type))close({...e,kind:e.off===pending.off?'fg':'loss',made:e.type==='FGM'});
 else if(['STEAL','TOV','SHOT_CLOCK','DREB','TEAM_DREB'].includes(e.type))close({...e,kind:'loss'});
 else if(e.type==='FOUL'&&e.off!==pending.off&&e.kind!=='technical')close({...e,kind:'foul'});
 else if(['FTM','FTX'].includes(e.type)&&!e.technical)close({...e,kind:e.off===pending.off?'ft':'loss'});
 },finish(){if(pending)close({...pending,kind:'unknown'});return {games,excluded};}};
}

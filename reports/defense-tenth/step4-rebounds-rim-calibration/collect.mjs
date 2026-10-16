export function collector(){
 let miss=null,reb=null,row;const games=[];
 const reset=()=>row={misses:0,immediateClock:0,fgOreb:0,postOrebClock:0,clock:0,natural:0,fgReleases:0,fgFlight:0};reset();
 return {event(e){
 if(e.kind==='gameEnd'){games.push(row);reset();miss=reb=null;return;}
 if(e.kind==='period'){miss=reb=null;return;}
 if(e.kind==='clock'){
  row.clock++;row.natural+=Number(e.natural??false);
  if(miss&&e.period===miss.period&&e.off===miss.off&&miss.time-e.time>=0&&miss.time-e.time<=2)row.immediateClock++;
  if(reb&&e.period===reb.period&&e.off===reb.off&&reb.time>=e.time)row.postOrebClock++;
 }
 if(e.kind==='teamOreb')return;
 if(['fg','ft','foul','reb','turnover','clock'].includes(e.kind)){miss=null;reb=null;}
 if(e.kind==='fg'&&!e.made){row.misses++;miss=e;}
 if(e.kind==='reb'&&e.fgOreb){row.fgOreb++;reb=e;}
 },finish(){return games;}};
}
export function simEvent(e){
 const x={period:e.period,time:e.clock,off:e.off,kind:'other'};
 if(e.type==='GAME_END')x.kind='gameEnd';
 if(['PERIOD_START','PERIOD_END'].includes(e.type))x.kind='period';
 if(['FGX','FGM'].includes(e.type)){x.kind='fg';x.made=e.type==='FGM';}
 if(['FTX','FTM'].includes(e.type))x.kind='ft';
 if(e.type==='FOUL')x.kind='foul';
 if(['TOV','STEAL'].includes(e.type))x.kind='turnover';
 if(e.type==='SHOT_CLOCK'){x.kind='clock';x.natural=e.naturalNoRim??false;}
 if(e.type==='TEAM_OREB')x.kind='teamOreb';
 if(['OREB','DREB','TEAM_DREB'].includes(e.type)){x.kind='reb';x.fgOreb=e.type==='OREB'&&!e.freeThrow;}
 return x;
}
export function realEvent(e,refs){
 const m=/PT(?:(\d+)M)?([\d.]+)S/.exec(e.clock??'');
 const x={period:e.period,time:m?60*Number(m[1]??0)+Number(m[2]):NaN,off:e.teamId,kind:'other'};
 if(e.actionType==='period')x.kind='period';
 if(['2pt','3pt'].includes(e.actionType)){x.kind='fg';x.made=e.shotResult==='Made';}
 if(e.actionType==='freethrow')x.kind='ft';
 if(e.actionType==='foul')x.kind='foul';
 if(e.actionType==='turnover')x.kind=e.subType==='shot clock'?'clock':'turnover';
 if(e.actionType==='rebound'){
  const shot=refs.get(e.shotActionNumber),fg=shot&&['2pt','3pt'].includes(shot.actionType)&&shot.shotResult==='Missed'&&shot.period===e.period;
  const team=!e.personId||(e.qualifiers??[]).includes('team');
  x.kind=team&&e.subType==='offensive'?'teamOreb':'reb';
  x.fgOreb=Boolean(!team&&e.subType==='offensive'&&fg);
 }
 return x;
}

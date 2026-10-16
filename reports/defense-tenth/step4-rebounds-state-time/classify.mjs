export const states=['made','dreb','liveTurnover','deadTurnover','playerOreb','teamOreb','ftOreb','foulRetained'];
const special=e=>/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((e.qualifiers??[]).join(' '));
const final=e=>{const m=/(\d+) of (\d+)/.exec(e.subType??'');return m&&m[1]===m[2];};
const clock=e=>{const m=/PT(?:(\d+)M)?([\d.]+)S/.exec(e.clock??'');return m?60*Number(m[1]??0)+Number(m[2]):NaN;};
function finishEvents(events){
 for(let i=0;i<events.length;i++){
  const e=events[i],following=[];
  for(let j=i+1;j<events.length;j++){const n=events[j];if(n.period!==e.period||n.time!==e.time)break;following.push(n);}
  const ft=following.some(n=>n.kind==='ft'&&n.actor===e.actor);
  if(e.kind==='fg'&&e.made&&!ft){e.end=true;e.state='made';e.owner=1-e.actor;}
  if(e.kind==='ft'&&e.final&&e.made){e.end=true;e.state='made';e.owner=1-e.actor;}
  if(e.kind==='foul'&&e.nonShooting&&!ft){e.state='foulRetained';e.owner=e.actor;}
 }
 return events;
}
export function realEvents(actions,ids){
 const refs=new Map(actions.map(e=>[e.actionNumber,e])),audit={invalidRebound:0,deadFtRebound:0,special:0};
 const events=actions.map(e=>{
  const side=ids.indexOf(e.teamId),x={period:e.period,time:clock(e),actor:side,kind:'other'};
  if(e.actionType==='period'){x.kind=e.subType==='end'?'periodEnd':'periodStart';return x;}
  if(['2pt','3pt'].includes(e.actionType)){x.kind='fg';x.made=e.shotResult==='Made';}
  if(e.actionType==='freethrow'){if(special(e)){audit.special++;return x;}x.kind='ft';x.final=final(e);x.made=e.shotResult==='Made';}
  if(e.actionType==='turnover'){x.kind='turnover';x.end=true;x.state=e.stealPersonId>0?'liveTurnover':'deadTurnover';x.owner=1-side;}
  if(e.actionType==='foul'&&!special(e)&&!/technical|offensive|flagrant/i.test(e.subType??'')){x.kind='foul';x.actor=1-side;x.nonShooting=!/shooting/i.test(e.subType??'');}
  if(e.actionType==='rebound'){
   const shot=refs.get(e.shotActionNumber),isFt=shot?.actionType==='freethrow';
   if(isFt&&(!final(shot)||special(shot))){audit.deadFtRebound++;return x;}
   if(!shot||shot.period!==e.period||shot.shotResult!=='Missed'||(!isFt&&!['2pt','3pt'].includes(shot.actionType))){audit.invalidRebound++;return x;}
   x.kind='rebound';x.owner=side;
   if(e.subType==='defensive'){x.state='dreb';x.end=true;}
   else if(e.subType==='offensive')x.state=isFt?'ftOreb':(!e.personId||(e.qualifiers??[]).includes('team'))?'teamOreb':'playerOreb';
  }
  return x;
 });return {events:finishEvents(events),audit};
}
export function simEvents(raw){return finishEvents(raw.map(e=>{
 const x={period:e.period,time:e.clock,actor:e.off,kind:'other'};
 if(e.type==='PERIOD_END')x.kind='periodEnd';
 if(e.type==='PERIOD_START')x.kind='periodStart';
 if(['FGM','FGX'].includes(e.type)){x.kind='fg';x.made=e.type==='FGM';}
 if(['FTM','FTX'].includes(e.type)&&!e.technical){x.kind='ft';x.final=e.attempt===e.attempts;x.made=e.type==='FTM';}
 if(['STEAL','TOV','SHOT_CLOCK'].includes(e.type)){x.kind='turnover';x.end=true;x.actor=e.type==='STEAL'?1-e.off:e.off;x.state=e.type==='STEAL'?'liveTurnover':'deadTurnover';x.owner=1-x.actor;}
 if(e.type==='FOUL'){x.kind='foul';x.actor=1-e.off;x.nonShooting=['nonShooting','intentional'].includes(e.kind);}
 if(['OREB','TEAM_OREB','DREB','TEAM_DREB'].includes(e.type)){x.kind='rebound';x.owner=e.off;if(e.type.includes('DREB')){x.end=true;x.state='dreb';}else x.state=e.freeThrow?'ftOreb':e.type==='OREB'?'playerOreb':'teamOreb';}
 return x;
}));}
export function measure(events){
 const rows=[],audit={anchors:0,invalidTime:0,ownerMismatch:0,firstCensored:0,segmentCensored:0,fullCensored:0};
 for(let i=0;i<events.length;i++){
  const a=events[i];if(!a.state||a.owner<0||a.owner>1||!Number.isFinite(a.time))continue;audit.anchors++;
  let first=null,segment=null,full=null,firstKind=null,invalid=false;
  for(let j=i+1;j<events.length;j++){
   const n=events[j];if(n.period!==a.period||n.kind==='periodEnd')break;
   const dt=a.time-n.time;if(!Number.isFinite(dt)||dt<-.01){audit.invalidTime++;invalid=true;break;}
   if(['fg','ft','turnover','foul'].includes(n.kind)&&n.actor!==a.owner){audit.ownerMismatch++;break;}
   if(first===null&&(['fg','ft','turnover','foul'].includes(n.kind)||(n.kind==='rebound'&&n.end))){first=dt;firstKind=n.kind;}
   if(segment===null&&(n.end||(n.state&&n.owner===a.owner)))segment=dt;
   if(n.end){full=dt;break;}
  }
  if(invalid)continue;
  if(first===null)audit.firstCensored++;if(segment===null)audit.segmentCensored++;if(full===null)audit.fullCensored++;
  rows.push([a.owner,states.indexOf(a.state),first,segment,full,firstKind]);
 }
 return {rows,audit};
}

export const categories=['passingLive','handlingLive','otherLive','passingDead','handlingDead','offensiveFoul','otherViolation','outUnclassified','unmappedDead','clock','ownershipOther'];
export function realCategory(e){
 const t=e.subType??'unknown',d=(e.descriptor??'').toLowerCase(),live=e.stealPersonId>0;
 if(t==='shot clock')return 'clock';
 if(t==='offensive foul')return live?'otherLive':'offensiveFoul';
 if(t==='bad pass'||t==='inbound'||t==='out-of-bounds'&&d==='bad pass')return live?'passingLive':'passingDead';
 if(t==='lost ball'||t==='out-of-bounds'&&d==='lost ball')return live?'handlingLive':'handlingDead';
 if(t==='out-of-bounds')return live?'otherLive':'outUnclassified';
 const known=['traveling','double dribble','3-second violation','5-second violation','8-second violation','backcourt','discontinue dribble','palming','lane violation','offensive goaltending','illegal assist','basket from below','kicked ball','punched ball','illegal screen','jump ball violation','inbound violation','other'];
 return live?'otherLive':known.includes(t)?'otherViolation':'unmappedDead';
}
export function simCategory(k){return {passSteal:'passingLive',touchSteal:'handlingLive',passOutTov:'passingDead',handlingOutTov:'handlingDead',offensiveFoulTov:'offensiveFoul',otherViolationTov:'otherViolation',unmappedDeadTov:'unmappedDead',SHOT_CLOCK:'clock',DREB:'ownershipOther',TEAM_DREB:'ownershipOther'}[k]??'unmappedDead';}

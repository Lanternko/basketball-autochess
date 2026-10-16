// Observational preparation only. This module never supplies player attributes.
import {mean,variance,sd} from './statistical_summary.js';
export const clockSeconds=e=>{const m=/PT(?:(\d+)M)?([\d.]+)S/.exec(e.clock);if(!m)throw Error('Invalid clock');return Number(m[1]??0)*60+Number(m[2]);};
export const periodSeconds=p=>p<=4?720:300;
export const leadBucket=n=>n<=-20?'<=-20':n<=-10?'-19..-10':n<=-6?'-9..-6':n<=5?'-5..5':n<=9?'6..9':n<=19?'10..19':'>=20';
const sum=a=>a.reduce((n,x)=>n+x,0);
const unique=a=>[...new Set(a)];
const onCourtAction=e=>['2pt','3pt','freethrow','rebound','turnover','steal','block','jumpball'].includes(e.actionType)||e.actionType==='foul'&&!['technical','double technical','bench technical'].includes(e.subType);
const participants=e=>onCourtAction(e)?unique([e.personId,e.assistPersonId,e.stealPersonId,e.blockPersonId,...(e.actionType==='jumpball'?e.personIdsFilter??[]:[])]).filter(x=>x>0):[];
export function reconstructLineups(actions,exposure){
  const owners=new Map(exposure.teams.flatMap(t=>t.players.map(p=>[p.playerId,t.teamId]))),ids=exposure.teams.map(t=>t.teamId);
  const starters=ids.map(id=>exposure.teams.find(t=>t.teamId===id).players.filter(p=>p.starter).map(p=>p.playerId));
  const eventLineups=Array(actions.length),stints=[],errors=[];const seconds=new Map([...owners.keys()].map(id=>[id,0]));
  for(const period of unique(actions.map(e=>e.period)).filter(p=>p>0)){
    const indices=actions.flatMap((e,i)=>e.period===period?[i]:[]),initial=ids.map((id,side)=>{
      if(period===1)return [...starters[side]];
      const seen=new Set(),on=[];
      for(const i of indices){const e=actions[i];if(e.actionType==='substitution'&&e.teamId===id&&!seen.has(e.personId)){seen.add(e.personId);if(e.subType==='out')on.push(e.personId);}
        for(const player of participants(e))if(owners.get(player)===id&&!seen.has(player)){seen.add(player);on.push(player);}}
      return unique(on);
    });
    initial.forEach((a,i)=>{if(a.length!==5)errors.push({period,teamId:ids[i],reason:'ambiguous-period-start',players:a});});
    let lineups=initial.map(a=>new Set(a)),previous=periodSeconds(period),stintStart=previous,stintLineups=initial.map(a=>[...a]),startIndex=indices[0];
    const close=(clock,index)=>{if(stintStart-clock>1e-8||index>startIndex)stints.push({period,startClock:stintStart,endClock:clock,seconds:Math.max(0,stintStart-clock),startIndex,endIndex:index,lineups:stintLineups});};
    for(let cursor=0;cursor<indices.length;cursor++){
      const index=indices[cursor],e=actions[index],clock=clockSeconds(e),dt=previous-clock;
      if(dt<-1e-6)errors.push({period,index,reason:'nonmonotone-clock',dt});
      if(dt>0)for(const lineup of lineups)for(const p of lineup)seconds.set(p,(seconds.get(p)??0)+dt);
      previous=clock;
      if(e.actionType==='substitution'){
        close(clock,index);const batch=[];let last=cursor;
        while(last<indices.length){const x=actions[indices[last]];if(x.actionType!=='substitution'||clockSeconds(x)!==clock)break;batch.push(indices[last]);last++;}
        // Keep event order: a player can enter and leave again at the same clock.
        for(const k of batch){const x=actions[k],side=ids.indexOf(x.teamId);if(side<0)continue;
          if(x.subType==='out'){if(!lineups[side].has(x.personId))errors.push({period,index:k,reason:'out-not-on-court',playerId:x.personId});lineups[side].delete(x.personId);}
          if(x.subType==='in'){if(lineups[side].has(x.personId))errors.push({period,index:k,reason:'in-already-on-court',playerId:x.personId});lineups[side].add(x.personId);}}
        lineups.forEach((a,side)=>{if(a.size!==5)errors.push({period,index,reason:'not-five-after-substitution',teamId:ids[side],players:[...a]});});
        for(const k of batch)eventLineups[k]=lineups.map(a=>[...a]);
        stintStart=clock;stintLineups=lineups.map(a=>[...a]);startIndex=batch.at(-1)+1;cursor=last-1;
      }else{
        eventLineups[index]=lineups.map(a=>[...a]);
        for(const p of participants(e)){const side=ids.indexOf(owners.get(p));if(side>=0&&!lineups[side].has(p))errors.push({period,index,reason:'actor-not-on-court',playerId:p,type:e.actionType});}
      }
    }
    if(previous>0)for(const a of lineups)for(const p of a)seconds.set(p,(seconds.get(p)??0)+previous);
    close(0,indices.at(-1)+1);
  }
  const minuteChecks=exposure.teams.flatMap(t=>t.players.map(p=>({teamId:t.teamId,playerId:p.playerId,boxSeconds:p.seconds,reconstructedSeconds:seconds.get(p.playerId)??0,errorSeconds:(seconds.get(p.playerId)??0)-p.seconds})));
  // Official boxes round individual minutes to whole seconds; do not force fit.
  const mismatches=minuteChecks.filter(p=>Math.abs(p.errorSeconds)>1.1);
  return {valid:errors.length===0&&mismatches.length===0,structurallyValid:errors.length===0,errors,mismatches,minuteChecks,stints,eventLineups,ids,starters};
}
export const blankFactors=()=>({fga:0,fgm:0,longA:0,longM:0,midA:0,midM:0,shortA:0,shortM:0,fta:0,ftm:0,tov:0,liveTov:0,clockTov:0,oreb:0,dreb:0,teamOreb:0,teamDreb:0,reboundOpportunities:0,deadFtReb:0,possessions:0,points:0});
export function realFactorEvent(e){const c=blankFactors(),made=e.shotResult==='Made';
  if(['2pt','3pt'].includes(e.actionType)&&e.isFieldGoal){const zone=e.actionType==='3pt'?'long':/Restricted Area|In The Paint/.test(e.area??'')?'short':'mid';c.fga=1;c.fgm=+made;c[zone+'A']=1;c[zone+'M']=+made;c.points=made?(zone==='long'?3:2):0;}
  if(e.actionType==='freethrow'){c.fta=1;c.ftm=+made;c.points=+made;}
  if(e.actionType==='turnover'){c.tov=1;c.liveTov=+(e.stealPersonId>0);c.clockTov=+(e.subType==='shot clock');}
  if(e.actionType==='rebound'){const offense=e.subType==='offensive',team=e.personId===0||(e.qualifiers??[]).includes('team');c[team?(offense?'teamOreb':'teamDreb'):(offense?'oreb':'dreb')]=1;}
  return c;
}
const specialFt=e=>(e.qualifiers??[]).some(q=>/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test(q));
const finalFt=e=>{const m=/(\d+) of (\d+)/.exec(e.subType??'');return m&&m[1]===m[2];};
export function normalizeRealGame(actions,fixture,lineup){
  const ids=[fixture.homeId,fixture.awayId],possessions=[],segments=[],turnoverTypes={},anomalies=[];let current=null,pending=null,score=[0,0],q3=null;
  const ls=i=>lineup?.eventLineups[i]?ids.map(id=>lineup.eventLineups[i][lineup.ids.indexOf(id)]):null;
  const start=(side,e,index,state='period')=>{current={side,period:e.period,start:pending?.time??periodSeconds(e.period),startIndex:index,points:0,opponentPoints:0,lead:score[side]-score[1-side],state:pending?.state??state,lineups:ls(index),segmentStart:pending?.time??periodSeconds(e.period),segmentState:pending?.state??state,starterSeconds:0,seconds:0};pending=null;};
  const segment=(time)=>{if(current){const duration=current.segmentStart-time;if(duration>=0)segments.push({state:current.segmentState,duration,period:current.period,lead:current.lead});}};
  const end=(e,index,nextState)=>{if(!current)return;const time=clockSeconds(e),nextSide=1-current.side;segment(time);const p={...current,end:time,endIndex:index,duration:current.start-time,signedPoints:current.points-current.opponentPoints};delete p.segmentStart;delete p.segmentState;possessions.push(p);current=null;pending={time,state:nextState,side:nextSide};};
  let previous=null;
  for(let i=0;i<actions.length;i++){
    const e=actions[i],time=clockSeconds(e),side=ids.indexOf(e.teamId);
    if(previous&&e.period===previous.period&&current){const dt=clockSeconds(previous)-time;if(dt>0){const last=ls(i-1);current.seconds+=dt;if(last&&lineup){const starter=lineup.starters[lineup.ids.indexOf(ids[current.side])];current.starterSeconds+=dt*last[current.side].filter(p=>starter.includes(p)).length;}}}
    if(e.actionType==='period'&&e.subType==='start'){if(current)anomalies.push({index:i,reason:'unclosed-period'});current=null;pending=null;}
    const activity=['2pt','3pt','freethrow','turnover','rebound','heave','jumpball'].includes(e.actionType);
    const technical=e.actionType==='freethrow'&&(e.qualifiers??[]).some(q=>/technical/i.test(q));
    const jumpCreditedTurnover=e.actionType==='jumpball'&&actions.slice(i+1,i+5).some(n=>n.actionType==='turnover'&&n.period===e.period&&clockSeconds(n)===time);
    if(activity&&side>=0&&!current&&!technical&&!(e.actionType==='rebound'&&e.subType==='offensive'&&e.shotActionNumber&&actions.find(a=>a.actionNumber===e.shotActionNumber)?.actionType==='freethrow'&&!finalFt(actions.find(a=>a.actionNumber===e.shotActionNumber)))){
      const attack=e.actionType==='rebound'&&e.subType==='defensive'?1-side:e.actionType==='jumpball'&&pending?pending.side:side;start(attack,e,i);
    }
    if(e.actionType==='turnover')turnoverTypes[e.subType??'unknown']=(turnoverTypes[e.subType??'unknown']??0)+1;
    const c=realFactorEvent(e);if(current&&c.points){if(side===current.side)current.points+=c.points;else current.opponentPoints+=c.points;}
    else if(technical&&c.points&&possessions.length){const p=possessions.at(-1);if(side===p.side)p.points+=c.points;else p.opponentPoints+=c.points;p.signedPoints=p.points-p.opponentPoints;}
    score=[Number(e.scoreHome),Number(e.scoreAway)];
    if(e.actionType==='turnover'&&current){if(side!==current.side)anomalies.push({index:i,reason:'turnover-other-owner'});end(e,i,'turnover');}
    if(['2pt','3pt'].includes(e.actionType)&&e.shotResult==='Made'&&current){
      // An and-one continues the same possession; technical/retained FTs do not.
      let andOne=false;for(let j=i+1;j<actions.length;j++){const n=actions[j];if(n.period!==e.period||clockSeconds(n)!==time)break;if(n.actionType==='freethrow'&&n.teamId===e.teamId&&!specialFt(n)&&n.subType==='1 of 1')andOne=true;}
      if(!andOne)end(e,i,'made');
    }
    if(e.actionType==='freethrow'&&finalFt(e)&&e.shotResult==='Made'&&!specialFt(e)&&current)end(e,i,'made');
    if(e.actionType==='rebound'&&current){const shot=actions.find(a=>a.actionNumber===e.shotActionNumber),dead=shot?.actionType==='freethrow'&&(!finalFt(shot)||specialFt(shot));
      if(!dead&&e.subType==='defensive')end(e,i,'dreb');
      else if(!dead&&e.subType==='offensive'){segment(time);current.segmentStart=time;current.segmentState='retained';}
    }
    if(e.actionType==='jumpball'&&!jumpCreditedTurnover&&current&&side!==current.side){end(e,i,'turnover');}
    if(e.actionType==='period'&&e.subType==='end'){if(!current&&pending?.time>0)start(pending.side,e,i);if(current)end(e,i,'period');pending=null;if(e.period===3)q3=score[0]-score[1];}
    previous=e;
  }
  const eventPoints=[0,0];for(const e of actions){const side=ids.indexOf(e.teamId);if(side>=0)eventPoints[side]+=realFactorEvent(e).points;}
  const reconstructed=[0,0];for(const p of possessions){reconstructed[p.side]+=p.points;reconstructed[1-p.side]+=p.opponentPoints;}
  const pointsValid=eventPoints.every((p,i)=>p===score[i]&&reconstructed[i]===p);
  if(!pointsValid)anomalies.push({reason:'score-accounting',eventPoints,reconstructed,final:score});
  return {id:fixture.id,ids,score,q3,possessions,segments,turnoverTypes,anomalies,pointsValid,lineupsValid:lineup?.valid??false};
}
export function normalizeSimGame(game,fixture,pair){
  const possessions=[],segments=[];let current=null,last=null,segmentStart=0,state='period',pendingState='period';let q3=null;
  const close=e=>{if(!current)return;const p={...current,end:e.clock,duration:e.elapsed-current.elapsed,points:e.score[current.side]-current.score[current.side],opponentPoints:e.score[1-current.side]-current.score[1-current.side]};p.signedPoints=p.points-p.opponentPoints;possessions.push(p);segments.push({state,period:p.period,duration:e.elapsed-segmentStart,lead:p.lead});current=null;};
  for(const e of game.events){
    if(current&&last){const dt=e.elapsed-last.elapsed;if(dt>0){current.seconds+=dt;current.starterSeconds+=dt*last.lineups[current.side].filter(i=>i<5).length;}}
    if(e.type==='POSSESSION'){close(e);current={side:e.off,period:e.period,start:e.clock,elapsed:e.elapsed,score:e.score,lead:e.score[e.off]-e.score[1-e.off],state:pendingState,seconds:0,starterSeconds:0,lineups:e.lineups};segmentStart=e.elapsed;state=pendingState;}
    if(['OREB','TEAM_OREB'].includes(e.type)){segments.push({state,period:e.period,duration:e.elapsed-segmentStart,lead:current?.lead??0});segmentStart=e.elapsed;state='retained';}
    if(['DREB','TEAM_DREB'].includes(e.type))pendingState='dreb';
    if(['STEAL','TOV','SHOT_CLOCK'].includes(e.type))pendingState='turnover';
    if(['FGM','FTM'].includes(e.type))pendingState='made';
    if(e.type==='PERIOD_END'){close(e);pendingState='period';if(e.period===3)q3=e.score[0]-e.score[1];}
    last=e;
  }
  return {id:fixture.id,ids:[fixture.homeId,fixture.awayId],score:[game.scoreA,game.scoreB],q3,possessions,segments,pointsValid:true,lineupsValid:true,turnoverTypes:{pass:game.statA.passSteals+game.statB.passSteals,touch:game.statA.touchTov+game.statB.touchTov,'shot clock':game.statA.clockTov+game.statB.clockTov}};
}
const covariance=(a,b)=>{const ma=mean(a),mb=mean(b);return mean(a.map((x,i)=>(x-ma)*(b[i]-mb)));};
export const correlation=(a,b)=>sd(a)*sd(b)>0?covariance(a,b)/(sd(a)*sd(b)):null;
export function varianceAnalysis(games){
  const valid=games.filter(g=>g.pointsValid),rows=valid.flatMap(g=>g.possessions.filter(p=>p.period<=4).map(p=>({...p,gameId:g.id,teamId:g.ids[p.side],lineupsValid:g.lineupsValid})));
  const teamMeans=new Map();for(const id of unique(valid.flatMap(g=>g.ids))){const team=valid.flatMap(g=>g.ids.flatMap((t,i)=>t===id?[g.possessions.filter(p=>p.period<=4&&p.side===i).reduce((n,p)=>n+p.signedPoints,0)]:[]));teamMeans.set(id,mean(team));}
  const allowedMeans=new Map();for(const id of teamMeans.keys()){const x=valid.flatMap(g=>g.ids.flatMap((t,i)=>t===id?[g.possessions.filter(p=>p.period<=4&&p.side===1-i).reduce((n,p)=>n+p.signedPoints,0)]:[]));allowedMeans.set(id,mean(x));}
  const leagueScore=mean([...teamMeans.values()]);
  const records=valid.map(g=>{const p=g.possessions.filter(p=>p.period<=4),N=[0,0],S=[0,0];for(const r of p){N[r.side]++;S[r.side]+=r.signedPoints;}return {id:g.id,N,S,teamOnly:S.map((s,i)=>s-teamMeans.get(g.ids[i])),Y:S.map((s,i)=>s-teamMeans.get(g.ids[i])-allowedMeans.get(g.ids[1-i])+leagueScore),q3:g.q3,q4:S[0]-S[1]-g.q3};});
  const A=records.map(r=>r.Y[0]),B=records.map(r=>r.Y[1]),N=records.map(r=>(r.N[0]+r.N[1])/2),vN=variance(N);
  const betaA=covariance(A,N)/vN,betaB=covariance(B,N)/vN,paceCov=betaA*betaB*vN,scoreCov=covariance(A,B);
  const aVar=variance(A),bVar=variance(B),pointVar=variance(rows.map(p=>p.signedPoints)),meanCount=mean(records.map(r=>sum(r.N))),iid=meanCount*pointVar;
  const teamPPP=new Map(unique(rows.map(r=>r.teamId)).map(id=>{const t=rows.filter(r=>r.teamId===id);return [id,mean(t.map(r=>r.signedPoints))];}));
  const centeredPointVar=mean(rows.map(r=>(r.signedPoints-teamPPP.get(r.teamId))**2)),iidCentered=meanCount*centeredPointVar;
  const paceIndividual=(betaA**2+betaB**2)*vN,paceMargin=(betaA-betaB)**2*vN;
  const residual=variance(A.map((a,i)=>a-B[i]));
  const buckets=Object.fromEntries(unique(rows.map(r=>leadBucket(r.lead))).map(k=>{const r=rows.filter(p=>leadBucket(p.lead)===k),l=r.filter(p=>p.lineupsValid);return [k,{n:r.length,ppp:mean(r.map(p=>p.signedPoints)),duration:mean(r.map(p=>p.duration)),starterShare:sum(l.map(p=>p.starterSeconds))/(5*sum(l.map(p=>p.seconds))),lineupN:l.length}];}));
  return {games:valid.length,excluded:games.filter(g=>!g.pointsValid).map(g=>g.id),regulationPossessions:rows.length,pointsDistribution:Object.fromEntries([...new Set([0,1,2,3,4,...rows.map(p=>p.signedPoints)])].sort((a,b)=>a-b).map(k=>[k,{count:rows.filter(p=>p.signedPoints===k).length,share:rows.filter(p=>p.signedPoints===k).length/rows.length}])),pointMean:mean(rows.map(p=>p.signedPoints)),pointVariance:pointVar,teamCenteredPointVariance:centeredPointVar,meanCombinedPossessions:meanCount,independentSD:Math.sqrt(iid),teamCenteredIndependentSD:Math.sqrt(iidCentered),withinTeamScoreVariance:(variance(records.map(r=>r.teamOnly[0]))+variance(records.map(r=>r.teamOnly[1])))/2,withinTeamScoreCovariance:covariance(records.map(r=>r.teamOnly[0]),records.map(r=>r.teamOnly[1])),strengthAdjustedScoreVariance:(aVar+bVar)/2,scoreCovariance:scoreCov,paceCovariance:paceCov,remainingCovariance:scoreCov-paceCov,meanPossessionCount:mean(N),possessionCountVariance:vN,paceBetas:[betaA,betaB],marginResidualSD:Math.sqrt(residual),decomposition:{iidVariance:iidCentered,individualPaceVariance:paceIndividual,paceCovarianceReduction:-2*paceCov,remainingCovarianceReduction:-2*(scoreCov-paceCov),withinTeamSerialAndHeterogeneityVariance:aVar+bVar-paceIndividual-iidCentered,total:residual},scoreBuckets:buckets,q3Q4Correlation:correlation(records.map(r=>r.q3),records.map(r=>r.q4)),records};
}

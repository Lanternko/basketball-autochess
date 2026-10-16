import {clockSeconds} from '../../../src/defense_pbp_analysis.js';
export function contactEvidence(shot,reb,protocol){
 let yes=false,no=false;const evidence=[];
 for(const [name,e] of [['shot',shot],['rebound',reb]]){
  for(const k of protocol.contactPatterns.structuredFields)if(e&&Object.hasOwn(e,k)){
   const v=e[k];if([true,1,'true'].includes(v)){yes=true;evidence.push(name+'.'+k+'=true');}else if([false,0,'false'].includes(v)){no=true;evidence.push(name+'.'+k+'=false');}
  }
  for(const [field,value] of Object.entries({description:e?.description,descriptor:e?.descriptor,qualifiers:(e?.qualifiers??[]).join(' ')})){
   const text=String(value??'').toLowerCase();const negatives=protocol.contactPatterns.retainText.filter(x=>text.includes(x));const positives=negatives.length?[]:protocol.contactPatterns.resetText.filter(x=>text.includes(x));
   if(negatives.length){no=true;evidence.push(name+'.'+field+':'+negatives.join('|'));}if(positives.length){yes=true;evidence.push(name+'.'+field+':'+positives.join('|'));}
  }
 }
 return {classification:yes&&!no?'reset':no&&!yes?'retain':'unknown',evidence,reason:yes&&no?'contradictory-evidence':yes||no?'explicit-evidence':'no-rim-contact-evidence'};
}
const special=e=>/technical|flagrant|clearpath|awayfromplay|transitiontake/i.test((e.qualifiers??[]).join(' '));
const finalFt=e=>{const m=/(\d+) of (\d+)/.exec(e.subType??'');return m&&m[1]===m[2]&&!special(e);};
export function reconstruct(actions,anchors,protocol,teamIds){
 const fixtureTeams=teamIds??[...new Set(actions.filter(a=>a.teamId>0).map(a=>a.teamId))];
 const wanted=new Map(anchors.map(a=>[a.source.anchorAction,a])),refs=new Map();let state={lo:0,hi:24,derived:false,active:false,owner:null,reason:'period-start-unknown',source:null},prev=null;const rows=[],clockChecks=[],issues=[];
 const unknown=(reason,owner=null)=>{state={lo:0,hi:24,derived:false,active:false,owner,reason,source:null};};
 const fresh=(amount,owner,e,reason)=>{state={lo:amount,hi:amount,derived:true,active:true,owner,reason,source:e.actionNumber};};
 const snapshot=()=>({...state});
 for(let i=0;i<actions.length;i++){
  const e=actions[i],time=clockSeconds(e),type=e.actionType,team=e.teamId||null;
  if(!prev||prev.period!==e.period)unknown('period-start-unknown');
  if(prev&&prev.period===e.period){const dt=prev.time-time;if(dt< -1e-6){issues.push({action:e.actionNumber,reason:'time-reversal',dt});unknown('timestamp-reversal');}else if(state.active){state.lo=state.lo-dt;state.hi=state.hi-dt;}}
  if(['2pt','3pt','turnover','freethrow'].includes(type)&&team){if(state.owner&&state.owner!==team){issues.push({action:e.actionNumber,reason:'ownership-discontinuity',from:state.owner,to:team});unknown('ownership-discontinuity',team);}else if(!state.owner)state.owner=team;}
  // Endpoint labels are checked only after the pre-event state has been frozen.
  if(type==='turnover'&&e.subType==='shot clock')clockChecks.push({action:e.actionNumber,period:e.period,seconds:time,before:snapshot()});
  if(type==='rebound'){
   const shot=refs.get(e.shotActionNumber),isFG=shot&&['2pt','3pt'].includes(shot.actionType),isFT=shot?.actionType==='freethrow'&&finalFt(shot),valid=shot&&shot.period===e.period&&shot.shotResult==='Missed'&&(isFG||isFT),player=e.personId>0&&!(e.qualifiers??[]).includes('team');
   if(valid&&e.subType==='defensive'&&player)fresh(24,team,e,'individual-defensive-rebound24');
   else if(valid&&e.subType==='offensive'){
    const before=snapshot(),contact=isFG?contactEvidence(shot,e,protocol):{classification:'reset',evidence:['live-final-FT-rebound'],reason:'legal-final-FT-reset14'};
    if(isFG&&wanted.has(e.actionNumber)){
     const a=wanted.get(e.actionNumber);rows.push({off:a.off,first:a.first,anchorAction:e.actionNumber,shotAction:e.shotActionNumber,period:e.period,seconds:time,contact,before,retainBranch:{lo:before.lo,hi:before.hi,derived:before.derived},resetBranch:{lo:14,hi:14},validation:{firstKind:a.firstKind,firstSeconds:a.firstSeconds,lossCategory:a.lossCategory,lossAction:a.firstLossAction},ownerMatch:before.owner===team});
    }
    if(contact.classification==='reset')fresh(14,team,e,contact.reason);
    else if(contact.classification==='retain'){state.owner=team;state.active=true;state.reason='explicit-no-rim-carry';}
    else {state={...state,lo:Math.min(before.lo,14),hi:Math.max(before.hi,14),active:true,owner:team,reason:'rim-unknown-reset-or-carry'};}
   }else if(type==='rebound'&&!valid)unknown('invalid-or-dead-rebound-reference',team);
   else if(e.subType==='defensive')unknown('team-defensive-rebound-control-unknown',team);
  }
  if(type==='turnover'){
   const opponents=fixtureTeams.filter(id=>id!==team);
   if(team&&opponents.length===1)fresh(24,opponents[0],e,'official-turnover-next24');else unknown('turnover-owner-unknown');
  }
  if(['2pt','3pt'].includes(type)&&e.shotResult==='Made')unknown('madeFG-inbound-start-unknown');
  if(type==='freethrow')unknown('FT-clock-stopped-next-control-unknown',team);
  if(type==='foul'){
   const text=[e.subType,e.descriptor,...(e.qualifiers??[])].join(' ');
   if(!/technical|flagrant|shooting|offensive|transitiontake|clearpath|awayfromplay/i.test(text)&&['personal','loose ball','looseball'].includes(e.subType)&&state.owner&&team!==state.owner){state={...state,lo:Math.min(state.lo,14),hi:24,active:true,reason:'defensive-foul-location-penalty-unresolved'};}
   else if(!/technical|delay/i.test(text))unknown('foul-reset-or-FT-unresolved',state.owner);
  }
  if(type==='jumpball'||type==='violation')unknown('unresolved-jump-or-violation');
  if(type==='period'&&e.subType==='end')unknown('period-end');
  refs.set(e.actionNumber,e);prev={period:e.period,time};
 }
 for(const [id,a] of wanted)if(!rows.some(r=>r.anchorAction===id)){const e=actions.find(e=>e.actionNumber===id);rows.push({off:a.off,first:a.first,anchorAction:id,shotAction:a.source.shotAction,period:e?.period,seconds:e?clockSeconds(e):null,contact:{classification:'unknown',evidence:[],reason:'chronological-shot-reference-unavailable'},before:{lo:0,hi:24,derived:false,owner:null,reason:'chronological-shot-reference-unavailable'},validation:{firstKind:a.firstKind,firstSeconds:a.firstSeconds,lossCategory:a.lossCategory,lossAction:a.firstLossAction},ownerMatch:false});issues.push({action:id,reason:'anchor-reference-unavailable'});}
 return {rows,clockChecks,issues};
}

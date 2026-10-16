import {pathDetails} from '../step4-rebounds-paths/collector.mjs';
export function detail(es,a){
 const first=es.find(e=>['fg','ft','loss'].includes(e.kind)),fg=es.find(e=>e.kind==='fg'),dt=first?a.clock-first.clock:null,fgdt=fg?a.clock-fg.clock:null;
 const before=first?es.slice(0,es.indexOf(first)):es;
 const boundary=es.find(e=>['fg','ft','loss','foul'].includes(e.kind));
 const kind=!boundary?'periodEnd':boundary.kind==='foul'?(boundary.defensive?(boundary.nonShooting?'nonshoot':'shooting'):'offensiveOrOtherFoul'):boundary.kind;
 const pre=first?es.slice(0,es.indexOf(first)):es;
 const fouls=pre.filter(e=>e.kind==='foul'&&e.defensive&&e.nonShooting).map(e=>a.clock-e.clock);
 return {...pathDetails(es),boundary:kind,boundarySeconds:boundary?a.clock-boundary.clock:null,nonshootBeforeAttempt:fouls.length>0,firstNonshootSeconds:fouls[0]??null,anchorSeconds:a.clock,windowEligible:a.clock>=3,firstSeconds:dt,firstKind:first?.kind??'periodEnd',earlyLoss:first?.kind==='loss'&&dt>=0&&dt<=3,lateLoss:first?.kind==='loss'&&dt>3,earlyFg:first?.kind==='fg'&&dt>=0&&dt<=3,earlyFt:first?.kind==='ft'&&dt>=0&&dt<=3,earlyNonShootingFoul:before.some(e=>e.kind==='foul'&&e.nonShooting&&e.defensive&&a.clock-e.clock>=0&&a.clock-e.clock<=3),quickProxy:!!fg&&fg.player===a.player&&fg.zone==='short'&&fgdt>=0&&fgdt<=3,intent:a.intent??null};
}
export function fullCollector(){
 let current=null,rows=[],games=[];
 const close=()=>{if(!current)return;if(!current.special)for(let i=0;i<current.anchors.length;i++){const a=current.anchors[i];rows.push({off:current.off,first:i===0,points:current.points-a.points,fgPoints:current.fg-a.fg,ftPoints:current.ft-a.ft,additionalOreb:current.anchors.length-i-1,...detail(current.events.slice(a.index+1),a)});}current=null;};
 return {duration(x){const a=current?.anchors.at(-1);if(a&&a.intent===null)a.intent=x.putback?'putback':'restart';},event(e){
  if(e.type==='PERIOD_START'&&e.period===1){close();rows=[];games.push(rows);}
  if(['POSSESSION','PERIOD_END','GAME_END','OVERTIME_LIMIT'].includes(e.type))close();
  if(e.type==='POSSESSION')current={off:e.off,points:0,fg:0,ft:0,anchors:[],events:[],special:false};
  if(!current)return;if(e.technical)current.special=true;const own=e.off===current.off;let x=null;
  if(['FGM','FGX'].includes(e.type)&&own)x={kind:'fg',zone:e.zone,made:e.type==='FGM',points:e.points??(e.type==='FGM'?(e.zone==='long'?3:2):0),player:e.player};
  if(['FTM','FTX'].includes(e.type)&&own&&!e.technical)x={kind:'ft'};
  if(['STEAL','TOV','SHOT_CLOCK','DREB','TEAM_DREB'].includes(e.type))x={kind:'loss',lossKind:e.type==='STEAL'?e.kind+'Steal':e.type==='TOV'?e.kind??'turnover':e.type};
  if(['OREB','TEAM_OREB'].includes(e.type))x={kind:'reb',own,team:e.type==='TEAM_OREB',freeThrow:!!e.freeThrow};
  if(e.type==='FOUL')x={kind:'foul',defensive:!own,nonShooting:['nonShooting','intentional'].includes(e.kind)};
  if(x)current.events.push({...x,clock:e.clock});
  if(own){if(e.type==='FGM'){const n=e.points??(e.zone==='long'?3:2);current.points+=n;current.fg+=n;}if(e.type==='FTM'&&!e.technical){current.points++;current.ft++;}if(e.type==='OREB'&&!e.freeThrow)current.anchors.push({points:current.points,fg:current.fg,ft:current.ft,index:current.events.length-1,clock:e.clock,player:e.player,intent:null});}
 },finish(){close();return{games};}};
}

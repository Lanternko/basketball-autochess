import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const root='reports/defense-third';fs.mkdirSync(root,{recursive:true});
const zone=e=>e.actionType==='3pt'||e.area?.includes('3')||e.area==='Backcourt'?'long':e.area==='Mid-Range'?'mid':['Restricted Area','In The Paint (Non-RA)'].includes(e.area)?'short':null;
const counts=Object.fromEntries(['long','mid','short','unknown'].map(k=>[k,{fga:0,fgm:0,madeFoul:0,missFoul:0,recordedMissFoul:0}]));
const unresolved=[];let games=0,ordinaryFTA=0,allFTA=0;
for(const s of read('data/defense-a-source/manifest.json').sources){
  const actions=read(s.file).data.game.actions;games++;
  for(const e of actions){if(e.isFieldGoal===1&&['2pt','3pt'].includes(e.actionType)){const c=counts[zone(e)??'unknown'];c.fga++;c.fgm+=e.shotResult==='Made';}if(e.actionType==='freethrow'){allFTA++;if(!e.qualifiers?.some(q=>/technical|flagrant|clearpath/i.test(q)))ordinaryFTA++;}}
  for(let i=0;i<actions.length;i++){
    const e=actions[i];if(e.actionType!=='foul'||e.descriptor!=='shooting')continue;
    const shots=actions.slice(Math.max(0,i-16),i).filter(x=>x.period===e.period&&x.clock===e.clock&&x.personId===e.foulDrawnPersonId&&['2pt','3pt'].includes(x.actionType));
    const shot=shots.at(-1),n=Number(e.qualifiers?.find(x=>/^[123]freethrow$/.test(x))?.[0]);
    const made=shot?.shotResult==='Made'&&n===1;
    let z=made?zone(shot):n===3?'long':zone(e);
    if(!made&&n!==2&&n!==3){unresolved.push({id:s.id,action:e.actionNumber,reason:'shooting foul without 1/2/3 FT classification'});continue;}
    if(!z)unresolved.push({id:s.id,action:e.actionNumber,reason:'missing foul zone'});
    const c=counts[z??'unknown'];c[made?'madeFoul':'missFoul']++;
    if(!made&&shot?.shotResult==='Missed'&&shot.isFieldGoal===1)c.recordedMissFoul++;
  }
}
for(const c of Object.values(counts)){
  c.unrecordedMissFoul=c.missFoul-c.recordedMissFoul;c.opportunities=c.fga+c.unrecordedMissFoul;
  c.madeAndFouledRate=c.madeFoul/c.opportunities;c.missedAndFouledRate=c.missFoul/c.opportunities;
  c.foulGivenMake=c.madeFoul/c.fgm;c.foulGivenMiss=c.unrecordedMissFoul/(c.fga-c.fgm+c.unrecordedMissFoul);
}
const report={games,counts,unresolved,ordinaryFTA,allFTA,definition:'Opportunities = recorded FGA + unrecorded shooting-foul misses. Conditional qMiss excludes recorded foul-miss anomalies. Paint merges Restricted Area and In The Paint. Unknown zone is retained and excluded from zone fitting.',inverse:'m = r / [r+(1-r)(1-qMiss)]; r = m(1-qMiss)/(1-m*qMiss). qMake changes FT outcomes but not the FGA denominator.',sources:{manifest:hash('data/defense-a-source/manifest.json')},code:hash('scripts/audit_defense_third_fouls.js')};
fs.writeFileSync(root+'/foul-audit.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({games,counts,unresolved:unresolved.length},null,2));

import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {calendarTruth,pairedCalendar,simpleCalendar} from '../src/defense_seventh_scoreboard.js';
const root='reports/defense-seventh',season=process.argv[2],result={season,cutoffs:{}};
for(const k of [25,41,55]){
 const c=read(`${root}/${season}/calendar-${k}/config.json`),truth=calendarTruth(c),a=loadSeventh(season+'-calendar-'+k+'-v4'),b=loadSeventh(season+'-calendar-'+k+'-v3'),simple=simpleCalendar(c),fixed=a.map(r=>({...structuredClone(simple.run),seed:r.seed})),pairedV3=pairedCalendar(a,b,truth),pairedSimple=pairedCalendar(a,fixed,truth),summary=summarizeFifth(a,0,a.map((_,i)=>i),truth);
 result.cutoffs[k]={date:c.date,GPTrainingRange:[Math.min(...Object.values(c.teamGP)),Math.max(...Object.values(c.teamGP))],v3:summarizeFifth(b,0,b.map((_,i)=>i),truth),v4:summary,simple:{...simple.summary,exponent:simple.exponent,definition:simple.method},pairedV3,pairedSimple,significance:{netVsV3:pairedV3.netRMSE.ci95[1]<0,winsVsV3:pairedV3.winMAE.ci95[1]<0,netVsSimple:pairedSimple.netRMSE.ci95[1]<0,winsVsSimple:pairedSimple.winMAE.ci95[1]<0},meanEfficiencyBias:summary.global.simulated.offensiveRatingProxy-summary.global.observed.offensiveRatingProxy};
 // Synthetic counts encode only the comparator's margin and win prediction.
 // Its other box/global/variance metrics are not meaningful measurements.
 result.cutoffs[k].simple.global=null;result.cutoffs[k].simple.teams=result.cutoffs[k].simple.teams.map(t=>({id:t.id,name:t.name,net:t.net,wins:t.wins,observed:t.observed}));
 for(const key of ['residualSD','defenseCorrelation','defenseSDRatio']){result.cutoffs[k].simple.metrics[key]=null;delete pairedSimple[key];}
 console.log(season,k,JSON.stringify({v3:result.cutoffs[k].v3.metrics,v4:summary.metrics,simple:result.cutoffs[k].simple.metrics,net:pairedV3.netRMSE,wins:pairedV3.winMAE,netSimple:pairedSimple.netRMSE,winSimple:pairedSimple.winMAE,meanBias:result.cutoffs[k].meanEfficiencyBias}));
}
fs.writeFileSync(root+'/'+season+'-calendar-assessment.json',JSON.stringify(result,null,2)+'\n');

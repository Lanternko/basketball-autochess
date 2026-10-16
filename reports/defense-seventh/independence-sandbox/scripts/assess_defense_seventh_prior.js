import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {calendarTruth,pairedCalendar} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
const root='reports/defense-seventh',result={definition:'Independent prior experiment. Calendar-cutoff comparisons are conditional on future active lists/starters. Preseason0 is a separate true forecast with assumed future availability, starters, rotation and TBD schedule; its uncertainty includes Monte Carlo availability draws.',cutoffs:{}};
for(const k of [25,41,55]){
 const c=read(`${root}/2025-26/calendar-${k}/config.json`),truth=calendarTruth(c),a=loadSeventh('2025-26-calendar-'+k+'-prior'),b=loadSeventh('2025-26-calendar-'+k+'-v4'),paired=pairedCalendar(a,b,truth),summary=summarizeFifth(a,0,a.map((_,i)=>i),truth);result.cutoffs[k]={date:c.date,summary,pairedV4:paired,significance:{net:paired.netRMSE.ci95[1]<0,wins:paired.winMAE.ci95[1]<0}};console.log('PRIOR',k,JSON.stringify({metrics:summary.metrics,net:paired.netRMSE,wins:paired.winMAE}));
}
if(fs.existsSync(root+'/2025-26-preseason-0-seeds.json')){
 const c={...read(root+'/2025-26/calendar-25/config.json'),date:'2025-10-20'},truth=calendarTruth(c),a=loadSeventh('2025-26-preseason-0');result.preseason={summary:summarizeFifth(a,0,a.map((_,i)=>i),truth),rules:read(root+'/prior/preseason-0/rules.json'),coverage:read(root+'/prior/preseason-0/coverage.json')};console.log('ZERO',JSON.stringify(result.preseason.summary.metrics));
}
fs.writeFileSync(root+'/prior-assessment.json',JSON.stringify(result,null,2)+'\n');

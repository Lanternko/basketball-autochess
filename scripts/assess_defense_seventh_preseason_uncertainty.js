import fs from 'node:fs';
import {read} from './defense_io.js';
import {loadSeventh} from './run_defense_seventh.js';
import {calendarTruth,pairedCalendar} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth,prepare,metricKeys} from '../src/defense_fifth_scoreboard.js';
import {makeRng} from '../src/rng.js';
import {sd} from '../src/statistical_summary.js';
const root='reports/defense-seventh',c={...read(root+'/2025-26/calendar-25/config.json'),date:'2025-10-20'},truth=calendarTruth(c),a=loadSeventh('2025-26-preseason-0'),past=read(root+'/2024-25/calendar-82/config.json'),before=calendarTruth({...past,date:'2024-10-01'}),teams=before.teams;
let lo=0,hi=40;const loss=x=>teams.reduce((s,t)=>{const p=1/(1+Math.exp(-x*Math.log(t.stats.pts/t.opponent.pts)));return s-t.wins*Math.log(p)-(82-t.wins)*Math.log(1-p);},0);for(let i=0;i<70;i++){const x=lo+(hi-lo)/3,y=hi-(hi-lo)/3;if(loss(x)<loss(y))hi=y;else lo=x;}const exponent=(lo+hi)/2;
const run={seed:0,teams:truth.teams.map(t=>{const p=teams.find(p=>p.id===t.id);return {id:t.id,name:t.name,games:82,wins:82/(1+(p.opponent.pts/p.stats.pts)**exponent),stats:{...t.stats,pts:t.opponent.pts+p.net*82},opponent:t.opponent};})},fixed=a.map(r=>({...structuredClone(run),seed:r.seed}));prepare(a);const all=a.map((_,i)=>i),rng=makeRng(20261209),samples=Object.fromEntries(metricKeys.map(k=>[k,[]]));
for(let n=0;n<2000;n++){const draw=all.map(()=>Math.floor(rng()*all.length)),m=summarizeFifth(a,0,draw,truth).metrics;for(const k of metricKeys)samples[k].push(m[k]);}
const uncertainty=Object.fromEntries(metricKeys.map(k=>{const x=samples[k].sort((a,b)=>a-b);return [k,{standardError:sd(x),ci95:[x[50],x[1950]]}];})),simple=summarizeFifth(fixed,0,all,truth);for(const k of ['residualSD','defenseCorrelation','defenseSDRatio'])simple.metrics[k]=null;simple.global=null;
const paired=pairedCalendar(a,fixed,truth);for(const k of ['residualSD','defenseCorrelation','defenseSDRatio'])delete paired[k];
fs.writeFileSync(root+'/preseason-uncertainty.json',JSON.stringify({uncertainty,simple:{metrics:simple.metrics,exponent,definition:'Previous2024-25 full team net margin and training-season fitted Pythagorean exponent; evaluation comparator only, no team numbers in player simulator inputs.'},pairedSimple:paired,scope:'Seed bootstrap includes assumed availability randomness and engine randomness. Does not quantify uncertainty in injuries, rotation rules, roster changes or abilities.'},null,2)+'\n');console.log('Preseason CI and previous-team comparator saved',JSON.stringify(simple.metrics));

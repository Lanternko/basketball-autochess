import fs from 'node:fs';
import readline from 'node:readline';
import {read,table,hash} from './defense_io.js';
import {calendarTruth,simpleCalendar} from '../src/defense_seventh_scoreboard.js';
import {summarizeFifth} from '../src/defense_fifth_scoreboard.js';
import {mean} from '../src/statistical_summary.js';
import {slope} from '../src/defense_scoreboard.js';
import {cLabel} from './run_defense_eighth_c_versions.js';
export const cConfig=(s,k)=>`reports/defense-seventh/${s}/calendar-${k}/config.json`;
export function cManifest(s,k,v){
 if(['v3','v4'].includes(v))return `reports/defense-seventh/${s}-calendar-${k}-${v}-seeds.json`;
 if(v==='v5'&&['2024-25','2025-26'].includes(s)){const c=read('reports/defense-eighth/b/v5-freeze.json').c[k];return `reports/defense-seventh/${s}-eighth-b-calendar-${k}-c${c.toFixed(6).replace('.','p')}-seeds.json`;}
 if(s==='2024-25'&&['v1','v3-signals-off'].includes(v))return `reports/defense-seventh/${s}-eighth-a-calendar-${k}-${v}-seeds.json`;
 return `reports/defense-seventh/${cLabel(s,k,v)}-seeds.json`;
}
export const countProxy=s=>s.fga-s.oreb+s.tov+.44*s.fta;
export function moments(matches,ids){
 const scored=new Map(ids.map(id=>[id,[]])),allowed=new Map(ids.map(id=>[id,[]]));for(const g of matches)for(let i=0;i<2;i++){const id=i?g.awayId:g.homeId;scored.get(id).push(g.regulationScore[i]);allowed.get(id).push(g.regulationScore[1-i]);}
 const sc=new Map([...scored].map(([id,a])=>[id,mean(a)])),al=new Map([...allowed].map(([id,a])=>[id,mean(a)])),lm=mean([...sc.values()]),out=new Map(ids.map(id=>[id,{n:0,sum:0,sum2:0}]));
 for(const g of matches){const e=(g.regulationScore[0]-sc.get(g.homeId)-al.get(g.awayId)+lm)-(g.regulationScore[1]-sc.get(g.awayId)-al.get(g.homeId)+lm);for(const id of [g.homeId,g.awayId]){const m=out.get(id);m.n+=.5;m.sum+=e*.5;m.sum2+=e*e*.5;}}
 return out;
}
export function loadCSeeds(manifestFile,truth,sources){
 const mf=read(manifestFile),league=mf.extra.cardFile?read(mf.extra.cardFile):read(mf.extra.bundle).league,valid=new Set(league.validGameIds??[]);sources[manifestFile]=hash(manifestFile);
 for(const [file,h]of Object.entries(mf.sources))if(hash(file)!==h)throw Error('Manifest source changed '+file);
 const seeds=mf.files.map((f,i)=>{if(f.seed!==20261012+i||hash(f.file)!==f.sha256)throw Error('Changed/unpaired seed '+f.file);const run=read(f.file),summary=summarizeFifth([run],0,[0],truth),ms=moments(run.matches.filter(g=>!valid.size||valid.has(g.id)),summary.teams.map(t=>t.id)),own=new Map(run.teams.map(t=>[t.id,t]));
 return summary.teams.map(t=>{const o=own.get(t.id),r=t.observed;return {id:t.id,name:t.name,net:t.net,wins:t.wins,points:o.stats.pts,proxy:(countProxy(o.stats)+countProxy(o.opponent))/2,residualMoment:ms.get(t.id),observed:{net:r.net,wins:r.wins,points:r.stats.pts,proxy:(countProxy(r.stats)+countProxy(r.opponent))/2}};});});
 if(seeds.length!==20)throw Error('Not20 seeds');return seeds;
}
export function cSimple(c,truth){
 const simple=simpleCalendar(c),l=read(c.leagueFile),logs=table(c.paths['data/season-source/team-games.json']),lookup=new Map(logs.map(r=>[r.GAME_ID+'/'+r.TEAM_ID,r])),train=l.schedule.filter(g=>g.date<=c.date),dates=[...new Set(train.map(g=>g.date))].sort(),split=dates[Math.floor((dates.length-1)/2)];
 const stats=l.teams.map(t=>{const gs=train.filter(g=>[g.homeId,g.awayId].includes(t.id)),phase=early=>{const a=gs.filter(g=>(g.date<=split)===early);return {games:a.length,net:mean(a.map(g=>lookup.get(g.id+'/'+t.id).PTS-lookup.get(g.id+'/'+(g.homeId===t.id?g.awayId:g.homeId)).PTS))};};return {id:t.id,early:phase(true),late:phase(false)};});
 const raw=slope(stats.map(t=>t.early.net),stats.map(t=>t.late.net)),multiplier=Math.max(0,Math.min(1,raw)),trainTruth=calendarTruth(c,'train');
 const simpleRows=simple.summary.teams.map(t=>({id:t.id,name:t.name,net:t.net,wins:t.wins,observed:{net:t.observed.net,wins:t.observed.wins}})),shrink=simpleRows.map(t=>{const pre=trainTruth.teams.find(x=>x.id===t.id),post=truth.teams.find(x=>x.id===t.id);return {...t,net:multiplier*t.net,wins:post.games/(1+(pre.opponent.pts/pre.stats.pts)**(simple.exponent*multiplier))};});
 return {simple:Array.from({length:20},()=>simpleRows),shrink:Array.from({length:20},()=>shrink),training:{multiplier,rawSlope:raw,split,trainingChecks:stats,exponent:simple.exponent}};
}
export async function realCResidual(c){const league=read(c.leagueFile),schedule=new Map(league.schedule.filter(g=>g.date>c.date).map(g=>[g.id,g])),gs=[];for await(const line of readline.createInterface({input:fs.createReadStream(c.realGames),crlfDelay:Infinity})){if(!line)continue;const g=JSON.parse(line),f=schedule.get(g.id);if(!f||!g.pointsValid)continue;const score=[0,0];for(const p of g.possessions)if(p.period<=4)score[p.side]+=p.signedPoints;gs.push({homeId:f.homeId,awayId:f.awayId,regulationScore:score});}const m=moments(gs,league.teams.map(t=>t.id)),n=[...m.values()].reduce((s,x)=>s+x.n,0),sum=[...m.values()].reduce((s,x)=>s+x.sum,0),sum2=[...m.values()].reduce((s,x)=>s+x.sum2,0);return {games:gs.length,SD:Math.sqrt(sum2/n-(sum/n)**2),definition:'Observed regulation signed possession points, points-valid PBP, same team-scored/team-allowed mean adjustment; lineup failures do not gate score evaluation.'};}

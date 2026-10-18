import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {calendarTruth,simpleCalendar} from '../src/defense_seventh_scoreboard.js';
import {seasonsN,cutoffsN,configN,seedsN} from '../src/defense_ninth_rosters.js';
const root='reports/defense-ninth/development',spec=read(root+'/prereg.json'),ms=read('reports/defense-eighth/c/prereg-supplement.json').outputCalibration.ms,sources={};
if(hash(root+'/prereg.json')!==fs.readFileSync(root+'/prereg.sha256','utf8').trim())throw Error('Prereg changed');
for(const [p,h]of Object.entries(spec.sourceHashes))if(hash(p)!==h)throw Error('Frozen/input changed '+p);
const readChecked=(p,h)=>{if(h&&hash(p)!==h)throw Error('Changed run '+p);sources[p]=hash(p);return read(p);};
const data=seasonsN.map(season=>cutoffsN.map(k=>{
 const c=readChecked(configN(season,k)),train=calendarTruth(c,'train'),post=calendarTruth(c),simple=simpleCalendar(c),ids=post.teams.map(t=>t.id).sort((a,b)=>a-b),get=(a,id)=>a.find(t=>t.id===id),deltas=Object.fromEntries(['sim-v3','sim-v4','seg','naive'].map(v=>[v,[]])),refSD=[],se=[],audit=[];
 for(const version of ['v3','v4']){
  const actualMF=readChecked(`reports/defense-seventh/${season}-calendar-${k}-${version}-seeds.json`),ctrlMF=readChecked(`${root}/${season}-K${k}-${version}.json`);
  if(ctrlMF.preregHash!==hash(root+'/prereg.json'))throw Error('Unregistered ctrl');
  for(let j=0;j<20;j++){
   const f=actualMF.files[j],g=ctrlMF.files[j];if(f.seed!==seedsN[j]||g.seed!==f.seed)throw Error('Seed pairing');
   const a=readChecked(f.file,f.sha256),b=readChecked(g.file,g.sha256),old=new Map(a.matches.map(x=>[x.id,x]));if(a.matches.length!==b.matches.length)throw Error('Fixtures differ');
   const rows=ids.map(id=>{const aa=get(a.teams,id),bb=get(b.teams,id);if(aa.games!==bb.games)throw Error('Games differ');return (aa.stats.pts-aa.opponent.pts)/aa.games-bb.net;});deltas['sim-'+version].push(rows);
   for(const z of b.matches){const o=old.get(z.id);if(!o||o.homeId!==z.homeId||o.awayId!==z.awayId)throw Error('Fixtures changed');}
   if(version==='v3'){
    refSD.push(a.analysis.marginResidualSD);
    for(const v of ['seg','naive']){const sums=new Map(ids.map(id=>[id,{sum:0,n:0}]));for(const z of b.analytic){for(const [id,sign]of [[z.homeId,1],[z.awayId,-1]]){const t=sums.get(id);t.sum+=sign*z[v];t.n++;}}deltas[v].push(ids.map(id=>sums.get(id).sum/sums.get(id).n));}
    audit.push(b.analyticAudit);
   }
  }
 }
 return {season,k,date:c.date,ids,names:ids.map(id=>get(post.teams,id).name),x:ids.map(id=>get(train.teams,id).net),y:ids.map(id=>get(post.teams,id).net),games:ids.map(id=>get(post.teams,id).games),wins:ids.map(id=>get(post.teams,id).wins),simpleWins:ids.map(id=>get(simple.summary.teams,id).wins),ms:ms[k],deltas,refSD,audit};
}));
fs.writeFileSync(root+'/dataset.json',JSON.stringify({preparedAt:new Date().toISOString(),preregHash:hash(root+'/prereg.json'),label:'四季開發季，已看過答案',data,sources},null,2)+'\n');console.log('DATASET all24 counterfactual ensembles,12 analytic ensembles,20 paired seeds');

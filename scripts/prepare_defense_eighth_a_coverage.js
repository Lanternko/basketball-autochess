import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {makeRng} from '../src/rng.js';
const root='reports/defense-eighth/a/coverage';fs.mkdirSync(root,{recursive:true});
const league=read('data/season-league.json'),sample=read('reports/defense-b1/defensive-samples.json'),exclude=new Set(['lineupFailed','uncertainPossessionGames','counterMismatchGames','missingPbp'].flatMap(k=>sample[k].map(x=>typeof x==='string'?x:x.id))),strict=league.schedule.map(g=>g.id).filter(id=>!exclude.has(id)).sort(),target=1091;
if(strict.length!==1188||league.schedule.length!==1230)throw Error('Coverage assumptions changed');
const rules={createdAt:new Date().toISOString(),target,fullGames:1230,sourceStrict:strict.length,maskSeeds:[20261081,20261082,20261083],definition:'Three outcome-independent uniform subsets without replacement of1091 from1188 strict2025 games. Full-season masks determined by game IDs and RNG only; each calendar training sample intersects its fixed mask. Re-estimate B1 factors, old cards, and joint role ability with frozen methods; preserve all originally strict heldout stints as the common test sample. Offline model/card aggregation only; no simulation and no league calibration rerun. Same cutoff tracking reused (individual tracking and body/identity metadata do not become missing). Does not imitate non-random reasons why2024 games failed audit.'};
if(!fs.existsSync(root+'/rules.json'))fs.writeFileSync(root+'/rules.json',JSON.stringify(rules,null,2)+'\n');
for(const seed of rules.maskSeeds){
 const rng=makeRng(seed),a=[...strict];for(let i=a.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[a[i],a[j]]=[a[j],a[i]];}
 const ids=a.slice(0,target).sort(),keep=new Set(ids);fs.writeFileSync(`${root}/mask-${seed}.json`,JSON.stringify({seed,kept:ids,excluded:strict.filter(id=>!keep.has(id))},null,2)+'\n');
 for(const k of [25,41,55]){
  const old=read(`reports/defense-seventh/2025-26/calendar-${k}/config.json`),dir=`${root}/mask-${seed}/calendar-${k}`;fs.mkdirSync(dir,{recursive:true});const c=structuredClone(old);c.root=dir;c.modelOutput=dir+'/factors';c.leagueOutput=dir+'/v3-league.json';c.foulMeansOutput=dir+'/foul-means.json';c.trainGames=old.trainGames.filter(id=>keep.has(id));
  for(const p of Object.keys(c.paths))if(p.endsWith('/engine-signals.json'))c.paths[p]=dir+'/train-games.json';else if(p.includes('card-values-pre'))c.paths[p]=dir+'/card-values.json';
  fs.writeFileSync(dir+'/train-games.json',JSON.stringify({trainGames:c.trainGames})+'\n');fs.writeFileSync(dir+'/foul-means.json','{}\n');
  c.coverage={seed,sourceConfig:`reports/defense-seventh/2025-26/calendar-${k}/config.json`,sourceTrainingGames:old.trainGames.length,keptTrainingGames:c.trainGames.length,fullSeasonKept:target,fullSeasonTotal:1230,maskHash:hash(`${root}/mask-${seed}.json`)};
  fs.writeFileSync(dir+'/config.json',JSON.stringify(c,null,2)+'\n');
 }
}
console.log('COVERAGE MASKS READY',rules.maskSeeds);

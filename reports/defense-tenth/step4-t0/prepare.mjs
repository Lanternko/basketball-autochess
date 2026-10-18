import fs from 'node:fs';
import readline from 'node:readline';
import {execFileSync} from 'node:child_process';
import {read,table,hash} from '../../../scripts/defense_io.js';
import * as C from '../../../src/constants.js';
import {fifthInputs} from '../../../src/defense_fifth_jobs.js';
const d='reports/defense-tenth/step4-t0',protocol=read(d+'/protocol.json');
const sum=(a,k)=>a.reduce((s,r)=>s+(r[k]??0),0),safe=(a,b)=>b>0?a/b:0;
const attr=p=>Math.max(40,Math.min(99,p<50?40+(p-1)*30/49:70+(p-50)*29/49));
const rank=(v,a)=>attr(100*(a.filter(x=>x<v).length+.5*a.filter(x=>x===v).length)/a.length);
function inverse(v,c){for(let i=1;i<c.length;i++){const[a,b]=c[i-1],[x,y]=c[i];if(v>=Math.min(b,y)&&v<=Math.max(b,y))return Math.max(40,Math.min(99,a+(v-b)/(y-b)*(x-a)));}return Math.abs(v-c[0][1])<Math.abs(v-c.at(-1)[1])?40:99;}
const keys=['MIN','PTS','FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','PF'];
function totals(logs,byTeam=false){const m=new Map();for(const r of logs){const id=byTeam?r.TEAM_ID+'/'+r.PLAYER_ID:r.PLAYER_ID,q=m.get(id)??{playerId:r.PLAYER_ID,name:r.PLAYER_NAME,GP:0};q.GP++;for(const z of keys)q[z]=(q[z]??0)+(r[z]??0);m.set(id,q);}return m;}
function mergeTracking(season,kind){
 const file=`reports/defense-tenth/step4-t2/raw/${season}/0-${kind}.json`,doc=read(file),rows=table(file),groups=Map.groupBy(rows,r=>r.CLOSE_DEF_PERSON_ID),out=[];
 for(const rs of groups.values()){const q={...rs[0]},nk=kind==='three'?'FG3A':'FGA_LT_06',mk=kind==='three'?'FG3M':'FGM_LT_06',pk=kind==='three'?'FG3_PCT':'LT_06_PCT',bk=kind==='three'?'NS_FG3_PCT':'NS_LT_06_PCT';q[nk]=sum(rs,nk);q[mk]=sum(rs,mk);q[pk]=safe(q[mk],q[nk]);q[bk]=safe(rs.reduce((s,r)=>s+(r[bk]??0)*r[nk],0),q[nk]);q.PLUSMINUS=q[pk]-q[bk];q.GP=Math.max(...rs.map(r=>r.GP));out.push(q);}
 const headers=doc.data.resultSets[0].headers;return {doc:{...doc,data:{resultSets:[{name:'MergedIndividualDefense',headers,rowSet:out.map(r=>headers.map(k=>r[k]))}]},provenance:{source:file,sha256:hash(file),duplicates:rows.length-out.length}},rows:out};
}
if(hash(d+'/protocol.json')!==fs.readFileSync(d+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
for(const season of protocol.seasons){
 const root=d+'/'+season;fs.mkdirSync(root+'/tracking',{recursive:true});
 if(season==='2025-26'){
  const b=fifthInputs({cutoff:0});b.options.seasonMinuteTargets=false;b.options.neutralContests=false;
  fs.writeFileSync(root+'/bundle.json',JSON.stringify(b)+'\n');continue;
 }
 const base=`data/defense-seventh/${season}`,league=structuredClone(read(base+'/league.json')),logs=table(base+'/player-games.json'),all=totals(logs),inTeam=totals(logs,true),rows=[...all.values()],pool=rows.filter(q=>q.GP>=30&&q.MIN/q.GP>=20),advanced=new Map(table(`reports/defense-tenth/step4-t2/raw/${season}/0-advanced.json`).map(q=>[q.PLAYER_ID,q])),meta=new Map(league.teams.flatMap(t=>t.roster).map(q=>[q.playerId,q]));
 const shots=new Map(),manifest=read(base+'/manifest.json');
 for(const src of manifest.sources)for(const e of read(src.file).data.game.actions)if(e.isFieldGoal===1&&['2pt','3pt'].includes(e.actionType)){const q=shots.get(e.personId)??{},z=e.actionType==='3pt'?'long':e.area==='Mid-Range'?'mid':'short';q[z+'A']=(q[z+'A']??0)+1;q[z+'M']=(q[z+'M']??0)+(e.shotResult==='Made');shots.set(e.personId,q);}
 const tracking={};for(const kind of ['three','rim']){const t=mergeTracking(season,kind);tracking[kind]=new Map(t.rows.map(r=>[r.CLOSE_DEF_PERSON_ID,r]));fs.writeFileSync(root+'/tracking/'+kind+'.json',JSON.stringify(t.doc)+'\n');}
 const priors={long:sum(rows,'FG3M')/sum(rows,'FG3A'),ft:sum(rows,'FTM')/sum(rows,'FTA'),short:sum([...shots.values()],'shortM')/sum([...shots.values()],'shortA'),mid:sum([...shots.values()],'midM')/sum([...shots.values()],'midA')};
 const size=q=>{const m=meta.get(q.playerId);return m.heightInches+m.bodyWeight/10;},sizePool=pool.filter(q=>meta.get(q.playerId)?.bodyWeight>0),missing=[];
 for(const t of league.teams){t.roster.sort((a,b)=>(inTeam.get(t.id+'/'+b.playerId)?.MIN??0)-(inTeam.get(t.id+'/'+a.playerId)?.MIN??0)||a.playerId-b.playerId);for(const p of t.roster){const b=all.get(p.playerId),r=inTeam.get(t.id+'/'+p.playerId),s=shots.get(p.playerId)??{},a=advanced.get(p.playerId);if(!b||!r)throw Error('Missing observed card '+p.playerId);
  for(const z of ['long','mid','short','ft']){const n=z==='long'?b.FG3A:z==='ft'?b.FTA:s[z+'A']??0,m=z==='long'?b.FG3M:z==='ft'?b.FTM:s[z+'M']??0,curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT,ft:C.CURVE_FT}[z];p[z]=inverse((m+100*priors[z])/(n+100),curve);}
  for(const[k,f]of Object.entries({drive:q=>safe(q.FTA,q.FGA),tovSkill:q=>-safe(q.TOV,q.FGA+.44*q.FTA+q.AST+q.TOV),stamina:q=>safe(q.MIN,q.GP)}))p[k]=rank(f(b),pool.map(f));
  for(const [k,f]of [['pass','AST_PCT'],['rebound','REB_PCT']]){p[k]=a?rank(a[f],pool.filter(q=>advanced.has(q.playerId)).map(q=>advanced.get(q.playerId)[f])):70;if(!a)missing.push({id:p.playerId,name:p.name,field:k});}
  p.physique=p.bodyWeight>0?rank(size(b),sizePool.map(size)):70;
  for(const[k,kind,curve,nk]of [['onBall','three',C.CURVE_DEF_3PT,'FG3A'],['help','rim',C.CURVE_DEF_RIM,'FGA_LT_06']]){const v=tracking[kind].get(p.playerId),n=v?.[nk]??0;p[k]=n>0?inverse(v.PLUSMINUS*n/(n+200),curve):70;if(!n)missing.push({id:p.playerId,name:p.name,field:k});}
  p.offBall=p.screen=p.handle=p.breakDbl=70;p.observed=Object.fromEntries(['GP',...keys].map(k=>[k,r[k]]));p.seasonMinutesPerGame=Math.max(.01,r.MIN/r.GP);p.shotProfile={threeRate:safe(r.FG3A,r.FGA),freeThrowsPerAttempt:safe(r.FTA,r.FGA),sourceSeason:season};p.defenseMeasurement={steals:b.STL,minutes:b.MIN};p.offenseMeasurement={attempts:r.FGA,freeThrows:r.FTA,turnovers:r.TOV,minutes:r.MIN};
 }}
 league.priorRate=sum(rows,'STL')/sum(rows,'MIN');league.validGameIds=manifest.sources.map(s=>s.id);league.provenance={recipe:'Original full-season v3 individual cards, no stint results. Historical PBP shot zones and cached metadata; official AST_PCT/REB_PCT. Same-season answer-side reconstruction.',priors,missing,pbpGames:manifest.sources.length};
 fs.writeFileSync(root+'/v3-league.json',JSON.stringify(league)+'\n');
 const foulSum={};for(const t of league.teams)for(const p of t.roster){const s=shots.get(p.playerId)??{};for(const z of ['long','mid','short']){const v=foulSum[z]??=[0,0];v[0]+=(s[z+'A']??0)*p.shotProfile.freeThrowsPerAttempt;v[1]+=s[z+'A']??0;}}
 fs.writeFileSync(root+'/foul-means.json',JSON.stringify({pre82:Object.fromEntries(Object.entries(foulSum).map(([z,v])=>[z,v[0]/v[1]]))})+'\n');
 const date=league.schedule.map(g=>g.date).sort().at(-1),allTrainGames=league.schedule.map(g=>g.id),prep=read(`reports/defense-seventh/${season}/stints/defensive-samples.json`),bad=new Set(['lineupFailed','uncertainPossessionGames','counterMismatchGames','missingPbp'].flatMap(k=>prep[k].map(x=>typeof x==='string'?x:x.id))),trainGames=allTrainGames.filter(id=>!bad.has(id));
 const sources=league.teams.flatMap(t=>[['long','three'],['short','rim']].map(([zone,kind])=>({teamId:t.id,zone,date,file:root+'/tracking/'+kind+'.json',sha256:hash(root+'/tracking/'+kind+'.json')})));
 fs.writeFileSync(root+'/tracking/manifest.json',JSON.stringify({sources,failures:[],note:'Full-season league-wide individual tracking copied into team context for prior construction; duplicated player rows merged. No fabricated team-specific DFG.'})+'\n');
 const c={season,k:82,date,root,leagueFile:root+'/v3-league.json',leagueOutput:root+'/v3-league.json',foulMeansOutput:root+'/foul-means.json',modelOutput:root+'/factors',exposure:base+'/game-exposure.json',realGames:`reports/defense-seventh/${season}/stints/real-games.jsonl`,trainGames:allTrainGames,strictGames:trainGames,allTrainGames,teamGP:Object.fromEntries(league.teams.map(t=>[t.id,82])),paths:{'data/season-league.json':root+'/v3-league.json','data/season-source/player-games.json':base+'/player-games.json','data/season-source/team-games.json':base+'/team-games.json','reports/defense-b1/defensive-samples.json':`reports/defense-seventh/${season}/stints/defensive-samples.json`,'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`,'data/defense-a-source/manifest.json':base+'/manifest.json','data/defense-fifth-source/pre82/manifest.json':root+'/tracking/manifest.json','data/defense-third-source/manifest.json':root+'/tracking/manifest.json'}};
 fs.writeFileSync(root+'/config.json',JSON.stringify(c,null,2)+'\n');
 console.log('PREPARED',season,league.teams.flatMap(t=>t.roster).length,'strict',trainGames.length,'missing',missing.length);
}
fs.writeFileSync(d+'/prepared.json',JSON.stringify({at:new Date().toISOString(),protocolSHA:hash(d+'/protocol.json')},null,2)+'\n');

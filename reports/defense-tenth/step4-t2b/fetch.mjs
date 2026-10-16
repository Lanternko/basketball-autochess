import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-t2b',read=f=>JSON.parse(fs.readFileSync(f,'utf8')),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const p=read(root+'/protocol.json');if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol SHA');
const players=read('reports/defense-tenth/step4-t2/players.json');
const table=f=>{const x=read(f).data.resultSets,t=Array.isArray(x)?x[0]:x;return t.rowSet.map(r=>Object.fromEntries(t.headers.map((k,i)=>[k,r[i]])));};
const base={LeagueID:'00',PerMode:'Totals',SeasonType:'Regular Season',CloseDefDistRange:'',College:'',Conference:'',Country:'',DateFrom:'',DateTo:'',Division:'',DraftPick:'',DraftYear:'',DribbleRange:'',GameSegment:'',GeneralRange:'',Height:'',LastNGames:'0',Location:'',Month:'0',OpponentTeamID:'0',Outcome:'',PORound:'',Period:'0',PlayerExperience:'',PlayerPosition:'',SeasonSegment:'',ShotClockRange:'',ShotDistRange:'',StarterBench:'',TeamID:'0',TouchTimeRange:'',VsConference:'',VsDivision:'',Weight:''};
const jobs=[];
function job(season,team,kind,date=''){
 const [yr,mo,day]=date.split('-'),dateParam=date?`${mo}/${day}/${yr}`:'';
 const params={...base,Season:season,TeamID:String(team),GeneralRange:p.acquisition.categories[kind],DateFrom:dateParam,DateTo:dateParam};
 const file=`${root}/raw/${season}/${team}-${kind}${date?'-'+date:''}.json`;
 jobs.push({season,team,kind,date,file,url:'https://stats.nba.com/stats/leaguedashplayerptshot?'+new URLSearchParams(params)});
}
for(const season of p.seasons){
 for(const team of [0,...Object.keys(players[season].teams).map(Number).sort()])for(const kind of ['all','catch','pull'])job(season,team,kind);
 for(const c of p.cases.filter(c=>c.season===season)){
  const tid=Number(Object.keys(players[season].teams).find(k=>players[season].teams[k].name===c.team));
  const logs=table(season==='2025-26'?'data/season-source/team-games.json':`data/defense-seventh/${season}/team-games.json`);
  const dates=[...new Set(logs.filter(x=>x.TEAM_ID===tid).map(x=>x.GAME_DATE.slice(0,10)))].sort();
  if(dates.length!==82)throw Error('Date count '+season+' '+tid);
  for(const date of dates)for(const kind of ['all','catch','pull'])job(season,tid,kind,date);
 }
}
let next=0,done=0;const sources=[],failures=[];
await Promise.all(Array.from({length:4},async()=>{while(next<jobs.length){const j=jobs[next++];try{
 let d;if(fs.existsSync(j.file))d=read(j.file);else{
  let error;for(let attempt=0;attempt<3;attempt++)try{
   const r=await fetch(j.url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(20000)});
   if(!r.ok)throw Error('HTTP '+r.status);d={...j,data:await r.json(),fetchedAt:new Date().toISOString()};break;
  }catch(e){error=e;}if(!d)throw error;
  const sets=Array.isArray(d.data.resultSets)?d.data.resultSets:[d.data.resultSets];
  if(!sets[0]?.headers?.includes('FGA'))throw Error('Unknown/invalid schema');
  fs.mkdirSync(j.file.slice(0,j.file.lastIndexOf('/')),{recursive:true});fs.writeFileSync(j.file,JSON.stringify(d)+'\n');
 }
 const t=Array.isArray(d.data.resultSets)?d.data.resultSets[0]:d.data.resultSets;
 sources.push({...j,rows:t.rowSet.length,headers:t.headers,sha256:hash(j.file)});
 }catch(e){failures.push({...j,error:String(e)});}
 if(++done%30===0)console.log('FETCH',done+'/'+jobs.length,'success',sources.length,'fail',failures.length);
}}));
fs.writeFileSync(root+'/fetch-manifest.json',JSON.stringify({protocolSHA:hash(root+'/protocol.json'),completedAt:new Date().toISOString(),jobs:jobs.length,sources,failures},null,2)+'\n');
console.log('FETCH COMPLETE',sources.length,failures.length);

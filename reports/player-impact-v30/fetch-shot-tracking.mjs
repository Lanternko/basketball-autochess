import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/player-impact-v30',seasons=process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26'];
const measures=['Drives','CatchShoot','PullUpShot'];
const jobs=seasons.flatMap(season=>measures.map(measure=>({season,measure})));
const results=[];let next=0;
await Promise.all(Array.from({length:3},async()=>{while(next<jobs.length){
 const j=jobs[next++],file=`${root}/raw/${j.season}/${j.measure}.json`;
 const params={LeagueID:'00',Season:j.season,SeasonType:'Regular Season',PerMode:'Totals',PlayerOrTeam:'Player',PtMeasureType:j.measure,TeamID:'0',LastNGames:'0',Month:'0',OpponentTeamID:'0',PaceAdjust:'N',PlusMinus:'N',Rank:'N',Period:'0',DateFrom:'',DateTo:'',Conference:'',Division:'',GameSegment:'',Location:'',Outcome:'',PORound:'',PlayerExperience:'',PlayerPosition:'',SeasonSegment:'',StarterBench:'',VsConference:'',VsDivision:'',College:'',Country:'',DraftPick:'',DraftYear:'',Height:'',Weight:''};
 const url='https://stats.nba.com/stats/leaguedashptstats?'+new URLSearchParams(params);
 try{
  let doc;
  if(fs.existsSync(file))doc=JSON.parse(fs.readFileSync(file));
  else{
   const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(20000)});
   if(!r.ok)throw Error('HTTP '+r.status);
   doc={...j,url,fetchedAt:new Date().toISOString(),data:await r.json()};
  }
  const rs=Array.isArray(doc.data.resultSets)?doc.data.resultSets[0]:doc.data.resultSets;
  if(!rs?.headers?.includes('PLAYER_ID')||!rs.rowSet.length)throw Error('Invalid player tracking table');
  if(doc.season!==j.season||doc.measure!==j.measure)throw Error('Wrong cached scope');
  fs.mkdirSync(`${root}/raw/${j.season}`,{recursive:true});
  if(!fs.existsSync(file))fs.writeFileSync(file,JSON.stringify(doc)+'\n');
  const entry={...j,file,url,rows:rs.rowSet.length,headers:rs.headers,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')};results.push(entry);
  console.log(JSON.stringify({season:j.season,measure:j.measure,rows:entry.rows,headers:entry.headers}));
 }catch(e){results.push({...j,url,error:String(e)});console.log(JSON.stringify({...j,error:String(e)}));}
}}));
const output=root+'/shot-tracking-fetch-'+seasons.join('_')+'.json';
if(fs.existsSync(output))throw Error('Preserve existing fetch manifest');
fs.writeFileSync(output,JSON.stringify({jobs:results,failures:results.filter(r=>r.error)},null,2));

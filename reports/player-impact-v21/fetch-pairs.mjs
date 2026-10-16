import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/player-impact-v21',seasons=process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26'],rows=[];
await Promise.all(seasons.map(async season=>{
 const file=`${root}/raw/${season}/passing-pairs-league.json`,probe=`${root}/raw/${season}/passing-pairs-league-probe.json`;
 const params={PlayerID:'0',TeamID:'0',Season:season,SeasonType:'Regular Season',PerMode:'Totals',LeagueID:'00',LastNGames:'0',Month:'0',OpponentTeamID:'0',DateFrom:'',DateTo:'',Location:'',Outcome:'',SeasonSegment:'',VsConference:'',VsDivision:''};
 const url='https://stats.nba.com/stats/playerdashptpass?'+new URLSearchParams(params);
 try{
  let doc;
  if(fs.existsSync(file))doc=JSON.parse(fs.readFileSync(file));
  else if(fs.existsSync(probe))doc=JSON.parse(fs.readFileSync(probe));
  else{const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error('HTTP '+r.status);doc={season,playerId:0,url,data:await r.json(),fetchedAt:new Date().toISOString()};}
  const sets=doc.data.resultSets;
  if(doc.season!==season||!sets?.some(s=>s.name==='PassesMade'&&s.rowSet.length>1000)||!sets.some(s=>s.name==='PassesReceived'))throw Error('Missing league pair scope');
  fs.mkdirSync(`${root}/raw/${season}`,{recursive:true});if(!fs.existsSync(file))fs.writeFileSync(file,JSON.stringify(doc)+'\n');
  rows.push({season,file,url:doc.url,rows:sets.map(s=>({name:s.name,rows:s.rowSet.length})),sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
  console.log(JSON.stringify(rows.at(-1)));
 }catch(e){rows.push({season,error:String(e)});console.log(JSON.stringify(rows.at(-1)));}
}));
const manifest=root+'/pairs-fetch'+(process.argv.slice(2).length?'-retry-'+seasons.join('_'):'')+'.json';
if(fs.existsSync(manifest))throw Error('Keep prior manifest');
fs.writeFileSync(manifest,JSON.stringify({jobs:rows,failures:rows.filter(r=>r.error)},null,2));

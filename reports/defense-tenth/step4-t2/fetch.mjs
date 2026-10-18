import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-t2',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const p=read(root+'/protocol.json');if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol hash mismatch');
const table=f=>{const t=read(f).data.resultSets[0];return t.rowSet.map(r=>Object.fromEntries(t.headers.map((h,i)=>[h,r[i]])));};
const common={LeagueID:'00',SeasonType:'Regular Season',PerMode:'Totals',LastNGames:'0',Month:'0',OpponentTeamID:'0',PaceAdjust:'N',PlusMinus:'N',Rank:'N',Period:'0',DateFrom:'',DateTo:'',Conference:'',Division:'',GameSegment:'',Location:'',Outcome:'',PORound:'',PlayerExperience:'',PlayerPosition:'',SeasonSegment:'',ShotClockRange:'',StarterBench:'',VsConference:'',VsDivision:'',College:'',Country:'',DraftPick:'',DraftYear:'',Height:'',Weight:''};
const kinds=['rim','three','matchups','hustle','advanced'],jobs=[];
for(const season of p.seasons){
  const logs=table(season==='2025-26'?'data/season-source/player-games.json':`data/defense-seventh/${season}/player-games.json`),byPlayer=Map.groupBy(logs,r=>r.PLAYER_ID);
  const moverTeams=[...new Set([...byPlayer.values()].filter(rs=>new Set(rs.filter(r=>r.MIN>0).map(r=>r.TEAM_ID)).size>1).flatMap(rs=>rs.filter(r=>r.MIN>0).map(r=>r.TEAM_ID)))].sort();
  for(const team of [0,...moverTeams])for(const kind of kinds){
    const endpoint=kind==='matchups'?'leagueseasonmatchups':kind==='hustle'?'leaguehustlestatsplayer':kind==='advanced'?'leaguedashplayerstats':'leaguedashptdefend';
    const params=kind==='matchups'?{LeagueID:'00',Season:season,SeasonType:'Regular Season',PerMode:'Totals',DefPlayerID:'',DefTeamID:team?String(team):'',OffPlayerID:'',OffTeamID:''}:{...common,Season:season,TeamID:String(team),MeasureType:kind==='advanced'?'Advanced':'Base',...(kind==='rim'||kind==='three'?{DefenseCategory:kind==='rim'?'Less Than 6Ft':'3 Pointers'}:{})};
    // The matchup API uses the same Season string but has no date filter.
    if(kind==='matchups')params.Season=season;
    const file=`${root}/raw/${season}/${team}-${kind}.json`,url='https://stats.nba.com/stats/'+endpoint+'?'+new URLSearchParams(params);
    jobs.push({season,team,kind,endpoint,file,url});
  }
}
let next=0,done=0;const sources=[],failures=[];
await Promise.all(Array.from({length:4},async()=>{while(next<jobs.length){const j=jobs[next++];try{let d;
  if(fs.existsSync(j.file))d=read(j.file);else{let error;for(let attempt=0;attempt<=p.acquisition.retries;attempt++)try{const response=await fetch(j.url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(p.acquisition.timeoutMS)});if(!response.ok)throw Error('HTTP '+response.status);d={...j,data:await response.json(),fetchedAt:new Date().toISOString()};break;}catch(e){error=e;}if(!d)throw error;
    const sets=Array.isArray(d.data.resultSets)?d.data.resultSets:[d.data.resultSets];if(!sets.some(s=>s?.rowSet?.length))throw Error('Empty dataset');fs.mkdirSync(j.file.slice(0,j.file.lastIndexOf('/')),{recursive:true});fs.writeFileSync(j.file,JSON.stringify(d)+'\n');}
  const sets=Array.isArray(d.data.resultSets)?d.data.resultSets:[d.data.resultSets];sources.push({...j,sha256:hash(j.file),rows:sets.reduce((n,s)=>n+(s?.rowSet?.length??0),0),headers:sets[0]?.headers});
 }catch(e){failures.push({...j,error:String(e)});}if(++done%20===0)console.log('FETCH',done+'/'+jobs.length,'success',sources.length,'fail',failures.length);}}));
fs.writeFileSync(root+'/fetch-manifest.json',JSON.stringify({registeredProtocolSHA:hash(root+'/protocol.json'),completedAt:new Date().toISOString(),jobs:jobs.length,sources,failures},null,2)+'\n');console.log('COMPLETE',sources.length,failures.length);

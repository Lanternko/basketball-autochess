import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const root=new URL('../',import.meta.url), directory=new URL('data/defense-source/',root);
const league=JSON.parse(await fs.readFile(new URL('data/season-league.json',root)));
await fs.mkdir(new URL('boxes/',directory),{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function fetchPage(id){
  const url='https://www.nba.com/game/'+id+'/box-score';
  const response=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw new Error('NBA page HTTP '+response.status);
  const html=await response.text(),match=html.match(/<script id="__NEXT_DATA__" type="application\/json">(.*?)<\/script>/s);
  if(!match)throw new Error('Missing NBA page data');
  const game=JSON.parse(match[1]).props.pageProps.game;
  return {url,fetchedAt:new Date().toISOString(),season:league.season,extraction:'__NEXT_DATA__.props.pageProps.game box score fields',sourceHtmlSha256:sha(html),
    data:{game:{gameId:game.gameId,homeTeamId:game.homeTeamId,awayTeamId:game.awayTeamId,homeTeam:game.homeTeam,awayTeam:game.awayTeam}}};
}
async function fetchJson(url){
  let last;
  for(let attempt=0;attempt<2;attempt++)try{
    const response=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(20000)});
    if(!response.ok)throw new Error('HTTP '+response.status);
    return {url,fetchedAt:new Date().toISOString(),season:league.season,data:await response.json()};
  }catch(e){last=e;}
  throw new Error(url+': '+last.message);
}
const base=JSON.parse(await fs.readFile(new URL('data/benchmark-source/teams.json',root)));
const advancedUrl=new URL(base.url);advancedUrl.searchParams.set('MeasureType','Advanced');
let advanced;
try{advanced=JSON.parse(await fs.readFile(new URL('advanced-teams.json',directory)));}catch(e){if(e.code!=='ENOENT')throw e;}
advanced??=await fetchJson(advancedUrl.href);
if(advanced.data.resultSets?.[0]?.rowSet?.length!==30)throw new Error('Incomplete advanced teams');
await fs.writeFile(new URL('advanced-teams.json',directory),JSON.stringify(advanced)+'\n');
const sources=[],games=[],failures=[];let next=0,done=0;
const minutes=value=>{
  if(value==='')return 0;
  const iso=/^PT(\d+)M([\d.]+)S$/.exec(value);if(iso)return Number(iso[1])*60+Number(iso[2]);
  if(!/^\d+:\d{2}(\.\d+)?$/.test(value))throw new Error('Invalid NBA minutes '+value);
  const [m,s]=value.split(':').map(Number);return 60*m+s;
};
async function worker(){
  while(next<league.schedule.length){
    const fixture=league.schedule[next++],file='boxes/'+fixture.id+'.json',path=new URL(file,directory);
    let doc;
    try{doc=JSON.parse(await fs.readFile(path));}catch(e){if(e.code!=='ENOENT')throw e;}
    if(!doc){
      const url='https://cdn.nba.com/static/json/liveData/boxscore/boxscore_'+fixture.id+'.json';
      try{
        const response=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(8000)});
        if(!response.ok)throw new Error('CDN HTTP '+response.status);
        doc={url,fetchedAt:new Date().toISOString(),season:league.season,data:await response.json()};
      }catch(e){
        try{doc=await fetchPage(fixture.id);}catch(error){failures.push({id:fixture.id,error:error.message});continue;}
      }
      if((doc.data.boxScoreTraditional??doc.data.game)?.gameId!==fixture.id)throw new Error('Wrong box score '+fixture.id);
      await fs.writeFile(path,JSON.stringify(doc)+'\n');
    }
    let box=doc.data.boxScoreTraditional??doc.data.game;
    const scoresMatch=b=>[b.homeTeam,b.awayTeam].every(t=>t.players.reduce((n,p)=>n+p.statistics.points,0)===fixture.observed[(fixture.homeId===t.teamId?'home':'away')+'Score']);
    if(!scoresMatch(box)){
      doc=await fetchPage(fixture.id);box=doc.data.game;
      await fs.writeFile(path,JSON.stringify(doc)+'\n');
    }
    if(doc.season!==league.season||box.gameId!==fixture.id)throw new Error('Mixed box score');
    const teamRows=[box.homeTeam,box.awayTeam].map(t=>({teamId:t.teamId,players:t.players.map(p=>({
      playerId:p.personId,seconds:minutes(p.statistics.minutes),starter:p.starter!==undefined?p.starter==='1':!!p.position,position:p.position,
      points:p.statistics.points,plusMinus:p.statistics.plusMinusPoints}))}));
    for(const t of teamRows){
      const side=fixture.homeId===t.teamId?'home':fixture.awayId===t.teamId?'away':null;
      if(!side)throw new Error('Wrong teams');
      const appeared=new Set(fixture[side+'PlayerIds']);
      if(t.players.some(p=>p.seconds>0&&!appeared.has(p.playerId)))throw new Error('Unexpected appearance');
      if([...appeared].some(id=>!t.players.some(p=>p.playerId===id)))throw new Error('Missing appearance');
      if(t.players.filter(p=>p.starter).length!==5)throw new Error('Missing official starters '+fixture.id);
      if(t.players.reduce((n,p)=>n+p.points,0)!==fixture.observed[side+'Score'])throw new Error('Box score differs from snapshot '+fixture.id);
      const total=t.players.reduce((n,p)=>n+p.seconds,0);
      if(Math.abs(total/5-(2880+Math.round((total/5-2880)/300)*300))>2)throw new Error('Invalid observed five-player time');
    }
    games.push({id:fixture.id,designatedHomeId:box.homeTeamId??box.homeTeam.teamId,designatedAwayId:box.awayTeamId??box.awayTeam.teamId,teams:teamRows});
    sources.push({file:'defense-source/'+file,url:doc.url,fetchedAt:doc.fetchedAt,sha256:sha(await fs.readFile(path))});
    done++;if(done%100===0)console.log('Official boxes '+done+'/1230');
  }
}
await Promise.all(Array.from({length:3},worker));
if(failures.length){await fs.writeFile(new URL('fetch-failures.json',directory),JSON.stringify(failures,null,2));throw new Error('Incomplete official boxes: '+failures.length+' failures. Rerun resumes cached files.');}
sources.sort((a,b)=>a.file.localeCompare(b.file));games.sort((a,b)=>a.id.localeCompare(b.id));
sources.push({file:'defense-source/advanced-teams.json',url:advanced.url,fetchedAt:advanced.fetchedAt,sha256:sha(await fs.readFile(new URL('advanced-teams.json',directory)))});
await fs.writeFile(new URL('game-exposure.json',directory),JSON.stringify({schemaVersion:1,season:league.season,
  methodology:'Official game minutes to seconds and G/F/C starter positions. Does not contain substitution times. DNP players retained in source; simulation availability remains observed appearances.',sources,games},null,2)+'\n');
console.log('Saved 1230 official minute/starter records and 30 advanced team rows');

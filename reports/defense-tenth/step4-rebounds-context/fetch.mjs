import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-rebounds-context';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const p=read(root+'/protocol.json');
if(sha(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Changed protocol');
const lock=root+'/fetch-code-registration.json';
if(!fs.existsSync(lock))fs.writeFileSync(lock,JSON.stringify({at:new Date().toISOString(),sha256:sha(root+'/fetch.mjs')},null,2)+'\n');
if(read(lock).sha256!==sha(root+'/fetch.mjs'))throw Error('Changed fetch code');
const common={LeagueID:'00',SeasonType:'Regular Season',PerMode:'Totals',PlayerOrTeam:'Player',LastNGames:'0',Month:'0',OpponentTeamID:'0',TeamID:'0',GameScope:'',Location:'',Outcome:'',PORound:'0',PlayerExperience:'',PlayerPosition:'',SeasonSegment:'',StarterBench:'',VsConference:'',VsDivision:'',College:'',Conference:'',Country:'',Division:'',DraftPick:'',DraftYear:'',Height:'',Weight:'',PtMeasureType:'Rebounding'};
let next=0;const sources=[],failures=[];
await Promise.all(Array.from({length:p.acquisition.concurrency},async()=>{
 while(next<p.acquisition.jobs.length){const j=p.acquisition.jobs[next++],q=new URLSearchParams({...common,Season:j.season,DateFrom:j.DateFrom,DateTo:j.DateTo}),url=p.acquisition.endpoint+'?'+q;
  try{let doc;
   if(fs.existsSync(j.file))doc=read(j.file);else{
    let last;
    for(let a=0;a<p.acquisition.attempts;a++)try{
     const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(p.acquisition.timeoutMS)});
     if(!r.ok)throw Error('HTTP '+r.status);
     doc={...j,url,fetchedAt:new Date().toISOString(),data:await r.json()};break;
    }catch(e){last=String(e);}
    if(!doc)throw Error(last);
    fs.mkdirSync(root+'/raw',{recursive:true});fs.writeFileSync(j.file,JSON.stringify(doc)+'\n');
   }
   const t=doc.data.resultSets?.[0];if(!t?.rowSet?.length)throw Error('Empty/malformed table');
   sources.push({...j,url,rows:t.rowSet.length,sha256:sha(j.file)});
  }catch(e){failures.push({...j,url,error:String(e)});}
  console.log(JSON.stringify({done:sources.length+failures.length,total:p.acquisition.jobs.length,failures:failures.length}));
 }
}));
fs.writeFileSync(root+'/fetch-manifest.json',JSON.stringify({at:new Date().toISOString(),protocolSHA256:sha(root+'/protocol.json'),sources,failures},null,2)+'\n');

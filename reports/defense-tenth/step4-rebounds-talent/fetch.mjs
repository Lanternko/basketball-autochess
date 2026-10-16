import fs from 'node:fs';
import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-rebounds-talent';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const p=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
const lock=root+'/fetch-code-registration.json';
if(!fs.existsSync(lock))fs.writeFileSync(lock,JSON.stringify({at:new Date().toISOString(),sha256:hash(root+'/fetch.mjs')},null,2)+'\n');
if(read(lock).sha256!==hash(root+'/fetch.mjs'))throw Error('Fetch code changed');
const jobs=[];
for(const year of p.acquisition.combineYears)for(const kind of p.acquisition.endpoints){
 const q=new URLSearchParams({LeagueID:'00',SeasonYear:String(year)});
 jobs.push({kind,year,file:`${root}/raw/combine/${year}-${kind}.json`,url:`https://stats.nba.com/stats/${kind}?${q}`});
}
const common={LeagueID:'00',SeasonType:'Regular Season',PerMode:'Totals',PlayerOrTeam:'Player',LastNGames:'0',Month:'0',OpponentTeamID:'0',TeamID:'0',DateFrom:'',DateTo:'',GameScope:'',Location:'',Outcome:'',PORound:'0',PlayerExperience:'',PlayerPosition:'',SeasonSegment:'',StarterBench:'',VsConference:'',VsDivision:'',College:'',Conference:'',Country:'',Division:'',DraftPick:'',DraftYear:'',Height:'',Weight:''};
for(const season of p.seasons)for(const kind of p.acquisition.tracking){
 const q=new URLSearchParams({...common,Season:season,PtMeasureType:kind});
 jobs.push({kind,season,file:`${root}/raw/tracking/${season}-${kind}.json`,url:`https://stats.nba.com/stats/leaguedashptstats?${q}`});
}
let next=0,done=0;const sources=[],failures=[];
const save=()=>fs.writeFileSync(root+'/fetch-manifest.json',JSON.stringify({at:new Date().toISOString(),protocolSHA256:hash(root+'/protocol.json'),jobs:jobs.length,done,sources,failures},null,2)+'\n');
await Promise.all(Array.from({length:p.acquisition.concurrency},async()=>{
 while(next<jobs.length){const j=jobs[next++];try{
  let doc;
  if(fs.existsSync(j.file))doc=read(j.file);else{
   let last;
   for(let attempt=0;attempt<p.acquisition.attempts;attempt++)try{
    const response=await fetch(j.url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(p.acquisition.timeoutMS)});
    if(!response.ok)throw Error('HTTP '+response.status);
    const data=await response.json();
    if(!data.resultSets&&!data.resultSet)throw Error('No NBA resultSets');
    doc={...j,fetchedAt:new Date().toISOString(),data};break;
   }catch(e){last=String(e);}
   if(!doc)throw Error(last);
   fs.mkdirSync(j.file.slice(0,j.file.lastIndexOf('/')),{recursive:true});fs.writeFileSync(j.file,JSON.stringify(doc)+'\n');
  }
  const raw=doc.data.resultSets??doc.data.resultSet,sets=Array.isArray(raw)?raw:[raw];
  if(!sets.every(s=>Array.isArray(s.headers)&&Array.isArray(s.rowSet)))throw Error('Bad NBA table');
  sources.push({...j,sha256:hash(j.file),rows:sets.reduce((s,t)=>s+t.rowSet.length,0),headers:sets[0].headers,fetchedAt:doc.fetchedAt});
 }catch(e){failures.push({...j,error:String(e)});}
 done++;save();if(done%4===0||done===jobs.length)console.log(JSON.stringify({done,total:jobs.length,success:sources.length,fail:failures.length}));
 }
}));
save();console.log(JSON.stringify({complete:true,sources:sources.length,failures:failures.length}));

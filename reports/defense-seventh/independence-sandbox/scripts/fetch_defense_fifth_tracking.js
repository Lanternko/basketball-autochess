import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const cutoff=Number(process.argv[2]??25);const directory='data/defense-fifth-source/pre'+cutoff,league=read('data/season-league.json');fs.mkdirSync(directory,{recursive:true});
const count={},dates={};for(const g of league.schedule.slice().sort((a,b)=>a.date.localeCompare(b.date)||a.id.localeCompare(b.id)))for(const id of [g.homeId,g.awayId]){count[id]=(count[id]??0)+1;if(count[id]===cutoff)dates[id]=g.date;}
const jobs=league.teams.flatMap(t=>['long','short'].map(zone=>({teamId:t.id,zone,date:dates[t.id]}))),sources=[],failures=[];let next=0;
await Promise.all(Array.from({length:4},async()=>{while(next<jobs.length){const j=jobs[next++],file=directory+'/'+j.teamId+'-'+j.zone+'-pre'+cutoff+'.json';
  const query=new URLSearchParams({LeagueID:'00',Season:'2025-26',SeasonType:'Regular Season',PerMode:'Totals',MeasureType:'Base',TeamID:String(j.teamId),LastNGames:'0',Month:'0',OpponentTeamID:'0',PaceAdjust:'N',PlusMinus:'N',Rank:'N',Period:'0',DefenseCategory:j.zone==='long'?'3 Pointers':'Less Than 6Ft',DateFrom:'',DateTo:j.date});
  const url='https://stats.nba.com/stats/leaguedashptdefend?'+query;
  try{let raw;if(fs.existsSync(file))raw=read(file);else{const response=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(12000)});if(!response.ok)throw Error('HTTP '+response.status);raw={...j,url,fetchedAt:new Date().toISOString(),data:await response.json()};fs.writeFileSync(file,JSON.stringify(raw)+'\n');}
    const set=Array.isArray(raw.data.resultSets)?raw.data.resultSets[0]:raw.data.resultSets;if(!set?.rowSet?.length)throw Error('Empty tracking response');
    // Refuse APIs silently ignoring date filters.
    if(set.headers.includes('GP')&&set.rowSet.some(r=>r[set.headers.indexOf('GP')]>cutoff))throw Error('GP>cutoff: date/team filter not honored');
    sources.push({...j,file,url,sha256:hash(file),rows:set.rowSet.length});
  }catch(e){failures.push({...j,url,error:String(e)});}
}}));
fs.writeFileSync(directory+'/manifest.json',JSON.stringify({sources,failures,cutoffs:dates},null,2)+'\n');console.log(JSON.stringify({sources:sources.length,failures:failures.length,firstFailure:failures[0]}));

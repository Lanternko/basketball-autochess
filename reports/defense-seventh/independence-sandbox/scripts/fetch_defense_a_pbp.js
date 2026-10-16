import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const root=new URL('../',import.meta.url),dir=new URL('data/defense-a-source/pbp/',root);
await fs.mkdir(dir,{recursive:true});
const league=JSON.parse(await fs.readFile(new URL('data/season-league.json',root)));
let next=0,done=0;const sources=[],failures=[];
async function worker(){while(next<league.schedule.length){
  const fixture=league.schedule[next++],file=fixture.id+'.json',path=new URL(file,dir);
  try{
    let doc;try{doc=JSON.parse(await fs.readFile(path));}catch(e){if(e.code!=='ENOENT')throw e;}
    if(!doc)for(let attempt=0;attempt<3;attempt++){
      try{const url='https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_'+fixture.id+'.json';
        const response=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0',Referer:'https://www.nba.com/'},signal:AbortSignal.timeout(10000)});
        if(!response.ok)throw new Error('HTTP '+response.status);
        doc={url,fetchedAt:new Date().toISOString(),data:await response.json()};break;
      }catch(e){if(attempt===2)throw e;}
    }
    const game=doc.data.game;if(game.gameId!==fixture.id||!Array.isArray(game.actions)||game.actions.length<100)throw new Error('Invalid PBP');
    const final=[...game.actions].reverse().find(a=>a.scoreHome!==''&&a.scoreAway!=='');
    if(Number(final.scoreHome)!==fixture.observed.homeScore||Number(final.scoreAway)!==fixture.observed.awayScore)throw new Error('Final score mismatch');
    if(!doc.validation)doc.validation={finalScoreMatches:true,actions:game.actions.length};
    await fs.writeFile(path,JSON.stringify(doc)+'\n');
    sources.push({id:fixture.id,file:'data/defense-a-source/pbp/'+file,url:doc.url,sha256:crypto.createHash('sha256').update(await fs.readFile(path)).digest('hex')});
  }catch(e){failures.push({id:fixture.id,error:e.message});}
  done++;if(done%100===0)console.log('PBP '+done+'/1230');
}}
await Promise.all(Array.from({length:6},worker));
sources.sort((a,b)=>a.id.localeCompare(b.id));
await fs.writeFile(new URL('data/defense-a-source/manifest.json',root),JSON.stringify({season:league.season,scope:'A3 rebound event audit only; no reconstruction of observed substitution stints',sources,failures},null,2)+'\n');
console.log(JSON.stringify({complete:sources.length,failures}));

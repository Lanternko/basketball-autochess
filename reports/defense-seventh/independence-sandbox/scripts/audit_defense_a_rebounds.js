import fs from 'node:fs';
import assert from 'node:assert/strict';
import {read,hash} from './defense_io.js';
const manifest=read('data/defense-a-source/manifest.json');
const buckets=Object.fromEntries(['long','mid','short','ftFinal','ftOther'].map(k=>[k,{misses:0,playerOff:0,playerDef:0,teamOff:0,teamDef:0,unresolved:0,periodEnd:0}]));
const box={teamGames:0,richTeamGames:0,fgMiss:0,ftMiss:0,playerOff:0,playerDef:0,teamOff:0,teamDef:0};
let teamEvents=0,unlinkedRebounds=0,duplicateLinks=0;const perGame=[];
for(const source of manifest.sources){
  assert.equal(hash(source.file),source.sha256);
  const game=read(source.file).data.game,actions=game.actions;
  const rebounds=new Map();
  for(const event of actions.filter(a=>a.actionType==='rebound')){
    if(!event.shotActionNumber){unlinkedRebounds++;continue;}
    if(rebounds.has(event.shotActionNumber)){duplicateLinks++;continue;}
    rebounds.set(event.shotActionNumber,event);if(!event.personId)teamEvents++;
  }
  const counts={fgMiss:0,ftMiss:0,playerOff:0,playerDef:0,teamOff:0,teamDef:0,ftOther:0};
  for(const shot of actions.filter(a=>a.shotResult==='Missed'&&(a.isFieldGoal||a.actionType==='freethrow'))){
    let zone;
    if(shot.actionType==='freethrow'){
      const parts=/^(\d+) of (\d+)$/.exec(shot.subType??'');
      const final=parts&&parts[1]===parts[2]&&!shot.qualifiers?.includes('technical')&&!shot.qualifiers?.includes('flagrant');
      zone=final?'ftFinal':'ftOther';counts.ftMiss++;if(!final)counts.ftOther++;
    }else{zone=shot.actionType==='3pt'?'long':/Restricted Area|In The Paint/.test(shot.area??'')?'short':'mid';counts.fgMiss++;}
    const bucket=buckets[zone];bucket.misses++;
    const rebound=rebounds.get(shot.actionNumber);
    if(!rebound){bucket.unresolved++;continue;}
    const key=(rebound.personId?'player':'team')+(rebound.teamId===shot.teamId?'Off':'Def');
    bucket[key]++;counts[key]++;
    if(rebound.clock==='PT00M00.00S')bucket.periodEnd++;
  }
  const doc=read('data/defense-source/boxes/'+source.id+'.json').data;
  const teams=[(doc.game??doc.boxScoreTraditional).homeTeam,(doc.game??doc.boxScoreTraditional).awayTeam];
  for(const team of teams){const s=team.statistics;box.teamGames++;
    box.fgMiss+=s.fieldGoalsAttempted-s.fieldGoalsMade;box.ftMiss+=s.freeThrowsAttempted-s.freeThrowsMade;
    box.playerOff+=s.reboundsOffensive;box.playerDef+=s.reboundsDefensive;
    if(Number.isFinite(s.reboundsTeamOffensive)){box.richTeamGames++;box.teamOff+=s.reboundsTeamOffensive;box.teamDef+=s.reboundsTeamDefensive;}
  }
  perGame.push({id:source.id,...counts});
}
const rates={};
for(const key of ['long','mid','short','ftFinal']){
  const b=buckets[key],resolved=b.playerOff+b.playerDef+b.teamOff+b.teamDef;
  rates[key]={teamProbability:(b.teamOff+b.teamDef)/resolved,teamOffShare:b.teamOff/(b.teamOff+b.teamDef),
    playerOffShare:b.playerOff/(b.playerOff+b.playerDef),denominator:resolved};
  assert.ok(resolved/b.misses>.98,'Too many unresolved '+key);
}
const result={schemaVersion:1,scope:'Rebound event audit; no lineup reconstruction; three mismatched final-score games excluded.',
  coverage:{games:manifest.sources.length,total:1230,excluded:manifest.failures},buckets,rates,box,teamEvents,unlinkedRebounds,duplicateLinks,perGame,
  conclusion:'The engine awards a player rebound for every reboundable miss; real missed shots also resolve to team/out-of-bounds rebounds. Box team OREB includes non-final FT dead-ball bookkeeping and cannot all be treated as extending possessions. PBP classifies these separately.',
  provenance:{sources:{'data/defense-a-source/manifest.json':hash('data/defense-a-source/manifest.json')},
    code:{'scripts/audit_defense_a_rebounds.js':hash('scripts/audit_defense_a_rebounds.js')}}};
fs.mkdirSync(new URL('../reports/defense-a/',import.meta.url),{recursive:true});
fs.writeFileSync(new URL('../reports/defense-a/rebound-audit.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({coverage:result.coverage,buckets,rates,box,unlinkedRebounds,duplicateLinks},null,2));

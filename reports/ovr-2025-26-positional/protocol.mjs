import fs from 'node:fs';
import {inputs,positions} from '../ovr-2025-26-latest/runtime.mjs';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';

export const ROOT='reports/ovr-2025-26-positional';
export const unknown=['offBall','screen','handle','breakDbl'];
const measured=ATTRIBUTES.filter(k=>!unknown.includes(k));
const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;

// Preserve the measured positional shape, while keeping unknown fields neutral.
// This is an arithmetic attribute mean, not an assumption about simulated OVR.
export function centered(card,target=70){
  let lo=-150,hi=150;
  for(let n=0;n<60;n++){
    const shift=(lo+hi)/2;
    if(mean(measured.map(k=>Math.max(0,Math.min(120,card[k]+shift))))<target)lo=shift;else hi=shift;
  }
  return {...card,...Object.fromEntries(measured.map(k=>[k,Math.max(0,Math.min(120,card[k]+(lo+hi)/2))])),
    ...Object.fromEntries(unknown.map(k=>[k,target]))};
}

export function positionalInputs(){
  const x=inputs(),byId=new Map(x.players.map(p=>[p.playerId,p]));
  const bundle=JSON.parse(fs.readFileSync('reports/defense-tenth/step4-t0/2025-26/bundle.json'));
  const votes=new Map();let usable=0,skipped=0,exactFive=0,broadThree=0;
  const assistRate=id=>{const p=byId.get(id);return p.observed.AST/p.observed.MIN;};
  // Most cached official live boxes supply PG/SG/SF/PF/C. Older traditional
  // boxes only supply G/F/C; split those guards by assists/minute, forwards by
  // height. Keep the proxy and fallback coverage visible.
  for(const game of bundle.exposure.games)for(const team of game.teams){
    const starters=team.players.filter(p=>p.starter&&p.seconds>0);
    let ordered,source;
    if(starters.length===5&&positions.every(pos=>starters.filter(p=>p.position===pos).length===1)){
      ordered=positions.map(pos=>starters.find(p=>p.position===pos));source='exact';exactFive++;
    }else{
      const groups=Object.fromEntries(['G','F','C'].map(g=>[g,starters.filter(p=>p.position===g)]));
      if(groups.G.length!==2||groups.F.length!==2||groups.C.length!==1){skipped++;continue;}
      groups.G.sort((a,b)=>assistRate(b.playerId)-assistRate(a.playerId)||a.playerId-b.playerId);
      groups.F.sort((a,b)=>byId.get(a.playerId).heightInches-byId.get(b.playerId).heightInches||a.playerId-b.playerId);
      ordered=[...groups.G,...groups.F,...groups.C];source='proxy';broadThree++;
    }
    usable++;
    ordered.forEach((p,i)=>{
      const v=votes.get(p.playerId)??{seconds:[0,0,0,0,0],starts:0,exactStarts:0};
      v.seconds[i]+=p.seconds;v.starts++;if(source==='exact')v.exactStarts++;votes.set(p.playerId,v);
    });
  }
  const roles=x.players.map(p=>{
    const v=votes.get(p.playerId),slot=v?v.seconds.indexOf(Math.max(...v.seconds)):positions.indexOf(p.pos);
    return {playerId:p.playerId,name:p.name,position:positions[slot],slot,
      source:v?'modal-official-starter-role':'existing-height-band-fallback',starts:v?.starts??0,exactStarts:v?.exactStarts??0,
      lowConfidence:!v||v.starts<5,secondsBySlot:v?.seconds??[0,0,0,0,0]};
  });
  const roleMap=new Map(roles.map(r=>[r.playerId,r]));
  const profiles=positions.map((pos,slot)=>{
    const ps=x.players.filter(p=>roleMap.get(p.playerId).slot===slot&&!roleMap.get(p.playerId).lowConfidence),minutes=ps.reduce((s,p)=>s+p.observed.MIN,0);
    const weighted=k=>ps.reduce((s,p)=>s+p[k]*p.observed.MIN,0)/minutes;
    const total=k=>ps.reduce((s,p)=>s+p.observed[k],0);
    const raw={name:'平均'+pos,playerId:-1000-slot,pos,courtPosition:pos,heightInches:weighted('heightInches'),
      ...Object.fromEntries(ATTRIBUTES.map(k=>[k,weighted(k)])),
      offenseMeasurement:{minutes,attempts:total('FGA'),freeThrows:total('FTA'),turnovers:total('TOV')},
      defenseMeasurement:{minutes,steals:total('STL')},
      shotProfile:{threeRate:total('FG3A')/total('FGA'),freeThrowsPerAttempt:total('FTA')/total('FGA'),sourceSeason:'2025-26'},
      individualOreb:{share:ps.reduce((s,p)=>s+p.individualOreb.share*p.observed.MIN,0)/minutes}};
    const profile=centered(raw);
    return {...profile,profileMetadata:{players:ps.length,minutes,rawMean:mean(ATTRIBUTES.map(k=>raw[k])),
      normalizedMean:mean(ATTRIBUTES.map(k=>profile[k])),unknownFields:unknown,
      auxiliaryPolicy:'Position-pooled observed volume/shot/steal rates and minute-weighted OREB share, not normalized by attribute mean.'}};
  });
  return {...x,roles,roleMap,profiles,roleAudit:{usableStarterTeamGames:usable,exactFivePositionTeamGames:exactFive,broadThreePositionTeamGames:broadThree,skippedStarterTeamGames:skipped,
    fallbackPlayers:roles.filter(r=>r.source.includes('fallback')).length,lowConfidencePlayers:roles.filter(r=>r.lowConfidence).length}};
}

export function lineup(x,player,slot,kind='positional'){
  const base=kind==='flat'?x.base:{name:'各位置平均70隊友',season:'2025-26',roster:x.profiles};
  return {...base,roster:base.roster.map((p,i)=>i===slot?{...player,pos:positions[i],courtPosition:positions[i]}:p)};
}

export const representativeIds=[1629674,201939,1628983,203999,1641705,203507,1629029,1630162,
  1628378,1629627,203991,1628436,1628389,1627759,201142,2544,1629008,1626156,1630163,1628386];

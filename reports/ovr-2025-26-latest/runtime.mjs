import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
import {inverse} from '../../scripts/export_defense_sixth_cards.js';
import {ATTRIBUTES} from '../../src/strength_benchmark.js';

export const ROOT='reports/ovr-2025-26-latest';
export const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
export const positions=['PG','SG','SF','PF','C'];
export async function gameEngine({memoized=false}={}){
  // Load the adopted adapter verbatim, exposing its game export rather than its season runner.
  const filename='reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs';
  let source=fs.readFileSync(filename,'utf8');
  const before='cached=(await import(encode(s))).runDefenseSeason;return cached;';
  if(source.split(before).length!==2)throw Error('Adopted adapter export drift');
  source=source.replace(before,'cached=(await import(gu)).simulateDefenseFourthGame;return cached;');
  if(memoized){
    // These inputs depend only on the fixed matchup, shooter, assist and shot state.
    // No RNG calls are cached. Only valid for fatigue/substitutions disabled.
    const injection=`
      if(g.split('const probability = (i,a=null,forced=false) => {').length!==2)throw Error('Probability cache anchor drift');
      g=g.replace('const probability = (i,a=null,forced=false) => {',
        'const probability = (i,a=null,forced=false) => { const cacheKey=off+\":\"+i+\":\"+a+\":\"+forced+\":\"+(putback!==null); if(opt.ovrCache?.has(cacheKey))return opt.ovrCache.get(cacheKey);');
      g=g.replace('return fourthProbability(os[i],','const cachedProbability=fourthProbability(os[i],');
      g=g.replace('},ds,opt);\\n    };','},ds,opt); if(opt.ovrCache)opt.ovrCache.set(cacheKey,cachedProbability); return cachedProbability;\\n    };');
      const lineupAnchor='const lineups = () => sides.map(s=>s.lineup.map(i=>opt.fatigue?M.applyStamina(s.roster[i],1-s.energy[i]):s.roster[i]));';
      if(g.split(lineupAnchor).length!==2)throw Error('Fixed lineup cache anchor drift');
      g=g.replaceAll('M.teammateContext(','cachedContext(');
      g=g.replace(lineupAnchor,\`const fixedLineups=sides.map(s=>s.lineup.map(i=>s.roster[i]));
        const lineups=()=>fixedLineups;
        const contexts=fixedLineups.map(ls=>ls.map((_,i)=>M.teammateContext(ls,i)));
        const cachedContext=(ls,i)=>contexts[fixedLineups.indexOf(ls)][i];\`);
    `;
    const anchor="  const gu=encode(g),s=";
    if(source.split(anchor).length!==2)throw Error('Adapter compilation anchor drift');
    source=source.replace(anchor,injection+'\n'+anchor);
  }
  const adapter=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
  return adapter.experimentalSeason();
}
export function inputs(){
  const b=read('reports/defense-tenth/step4-t0/2025-26/bundle.json');
  const cal=read('reports/defense-tenth/step4-rebounds-oreb/2025-26/calibration-oreb.json').selected;
  const oreb=read('reports/defense-tenth/step4-rebounds-oreb/2025-26/cards.json').players;
  const options={...b.options,...cal.options};
  delete options.defenseSignals;delete options.rotationCurve;
  for(const k of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])options[k]=false;
  Object.assign(options,{seasonMinuteTargets:false,neutralContests:false,individualOrebCard:true,individualOrebAllocation:true,
    putbackTiming:true,putbackCDF:read('reports/defense-tenth/step4-rebounds-putback-time/putback-cdf.json').cdf,
    clockRecalibration:true,splitTurnoverTiming:true,
    pace:read('reports/defense-tenth/step4-rebounds-turnover-time/2025-26/calibration.json').selected.pace});
  options.timingCDF={...options.timingCDF,...read('reports/defense-tenth/step4-rebounds-turnover-time/2025-26/turnover-cdf.json').states};
  // OVR controls equal exposure and position; the adopted probability/timing paths remain enabled.
  Object.assign(options,{fatigue:false,substitutions:false,foulOut:99,minuteTargets:false,observedTargets:false,
    excludeZeroTargets:false,maxOvertimes:0,quarterSeconds:216,replay:false});
  const players=new Map(),membership=new Map(),teamCards=new Map();
  for(const t of b.league.teams)for(const raw of t.roster){
    const p=structuredClone(raw);
    for(const z of ['long','mid','short']){
      const curve={long:C.CURVE_3PT,mid:C.CURVE_MID,short:C.CURVE_SHORT}[z];
      const v=Math.max(.001,Math.min(.999,M.interpolate(p[z],curve)));
      p[z]=Math.max(0,Math.min(120,inverse(1/(1+Math.exp(-Math.log(v/(1-v))-cal.shotDelta)),curve)));
    }
    p.individualOreb=oreb[p.playerId];
    if(!p.individualOreb)throw Error('Missing OREB card '+p.playerId);
    teamCards.set(t.id+'/'+p.playerId,p);
    if(players.has(p.playerId)){
      const other=players.get(p.playerId);
      for(const k of ATTRIBUTES)if(other[k]!==p[k])throw Error('Trade card mismatch '+p.playerId+' '+k);
      if(JSON.stringify(other.defenseMeasurement)!==JSON.stringify(p.defenseMeasurement))throw Error('Trade defense measurement mismatch');
      for(const k of Object.keys(other.observed))other.observed[k]+=p.observed[k];
    }else players.set(p.playerId,structuredClone(p));
    const list=membership.get(p.playerId)??[];list.push(t.name);membership.set(p.playerId,list);
  }
  for(const p of players.values()){
    const s=p.observed;
    p.offenseMeasurement={minutes:s.MIN,attempts:s.FGA,freeThrows:s.FTA,turnovers:s.TOV};
    p.shotProfile={...p.shotProfile,threeRate:s.FGA?s.FG3A/s.FGA:p.shotProfile.threeRate,
      freeThrowsPerAttempt:s.FGA?s.FTA/s.FGA:p.shotProfile.freeThrowsPerAttempt};
  }
  const minutes=new Map();
  for(const game of b.exposure.games)for(const t of game.teams)for(const p of t.players){
    const key=t.teamId+'/'+p.playerId;minutes.set(key,(minutes.get(key)??0)+p.seconds/60);
  }
  const opponents=b.league.teams.map(t=>({id:t.id,name:t.name,season:b.league.season,
    roster:[...t.roster].sort((a,b)=>(minutes.get(t.id+'/'+b.playerId)??0)-(minutes.get(t.id+'/'+a.playerId)??0)||a.playerId-b.playerId).slice(0,5)
      .map(p=>teamCards.get(t.id+'/'+p.playerId)).sort((a,b)=>a.heightInches-b.heightInches||a.playerId-b.playerId)
      .map((p,i)=>({...p,pos:positions[i],courtPosition:positions[i]}))}));
  const all=[...players.values()];
  const totals=Object.fromEntries(['MIN','FGA','FTA','TOV','STL','FG3A'].map(k=>[k,all.reduce((s,p)=>s+p.observed[k],0)]));
  const shares=Object.values(oreb);
  const neutral={name:'中性基準',playerId:-1,...Object.fromEntries(ATTRIBUTES.map(k=>[k,70])),
    offenseMeasurement:{minutes:totals.MIN,attempts:totals.FGA,freeThrows:totals.FTA,turnovers:totals.TOV},
    defenseMeasurement:{minutes:totals.MIN,steals:totals.STL},
    shotProfile:{threeRate:totals.FG3A/totals.FGA,freeThrowsPerAttempt:totals.FTA/totals.FGA,sourceSeason:'2025-26'},
    individualOreb:{share:shares.reduce((s,p)=>s+p.oreb,0)/shares.reduce((s,p)=>s+p.opportunities,0)}};
  const base={name:'四名全70隊友',season:'2025-26',roster:positions.map((pos,i)=>({...neutral,playerId:-100-i,pos,courtPosition:pos}))};
  const anchors=[40,70,99].map(v=>({...neutral,name:'全'+v,playerId:-v,...Object.fromEntries(ATTRIBUTES.map(k=>[k,v]))}));
  return {options,players:all.sort((a,b)=>a.playerId-b.playerId),opponents,base,anchors,membership:Object.fromEntries(membership)};
}
export function probe(base,player,slot){return {...base,roster:base.roster.map((p,i)=>i===slot?{...player,pos:p.pos,courtPosition:p.pos}:p)};}

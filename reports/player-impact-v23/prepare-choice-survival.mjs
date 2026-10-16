import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v22/input.mjs';
import {terminalDefenseProbabilities} from '../player-impact-v21/model.mjs';
import {spaceProbability} from '../player-impact-v22/model.mjs';
import {observedFoulInputs} from '../player-impact-v5/model.mjs';
import {attemptMakeProbability} from '../../src/defense_probability.js';
import {exposureDefenseProbabilities} from '../player-impact-v20/model.mjs';
import {rotationEnergyStep,periodEnergyRecovery} from '../../src/source_rotation_energy.js';
import {measuredContext} from '../../src/measured_creation_context.js';
import {pressureSignal} from '../../src/defense_probability.js';
import * as M from '../../src/probability_model.js';
import * as C from '../../src/constants.js';
const root='reports/player-impact-v23',read=f=>JSON.parse(fs.readFileSync(f)),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-choice-survival.json`;if(fs.existsSync(output))throw Error('Preserve source contexts');
 const b=loadInput(season),teams=new Map(b.league.teams.map(t=>[t.id,new Map(t.roster.map(p=>[p.playerId,p]))]));
 const src=read(`${root}/${season}-putback-choices.json`),valid=new Map(src.games.map(g=>[g.id,g])),games=new Map(),sums=new Map();
 const file=season==='2025-26'?'reports/defense-b1/stints.jsonl':`reports/defense-seventh/${season}/stints/stints.jsonl`;
 for(const line of fs.readFileSync(file,'utf8').trim().split('\n')){const s=JSON.parse(line);if(!valid.has(s.id)||s.seconds<0)continue;const rows=games.get(s.id)??[];rows.push(s);games.set(s.id,rows);}
 const mf=(season==='2025-26'?'data/defense-a-source':`data/defense-seventh/${season}`)+'/manifest.json',paths=new Map(read(mf).sources.map(s=>[s.id,s.file]));let count=0,strictSeconds=0;const outputGames=[],excluded={tooLate:0,intentionalFoul:0,runClock:0},unreachableFastShots=[];const fixtures=new Map(b.league.schedule.map(g=>[g.id,g]));
 for(const[id,rows]of games){
  const energies=new Map(),events=valid.get(id).rows,actions=events.length?read(paths.get(id)).data.game.actions:[],joined=new Set(),outputRows=[];let lastPeriod=1;const fixture=fixtures.get(id);
  rows.sort((a,b)=>a.period-b.period||b.startClock-a.startClock||b.endClock-a.endClock);
  for(const s of rows){
   strictSeconds+=s.seconds*10;
   if(s.period>lastPeriod){for(const[k,e]of energies)energies.set(k,periodEnergyRecovery(e,s.period-lastPeriod));lastPeriod=s.period;}
   const active=s.teams.map(t=>{const ids=new Set(t.players),lineup=new Map();for(const[pid,p]of teams.get(t.teamId)){const key=t.teamId+':'+pid,e=energies.get(key)??1,step=rotationEnergyStep(e,s.seconds,ids.has(pid),p.stamina);energies.set(key,step.end);if(ids.has(pid))lineup.set(pid,M.applyStamina(p,1-step.mean));}return t.players.map(pid=>lineup.get(pid));});
   for(const e of events)if(s.startIndex<=e.index&&e.index<s.endIndex){
    if(joined.has(e.index))throw Error('Overlapping event source stints');joined.add(e.index);
    const side=s.teams.findIndex(t=>t.teamId===e.teamId),os=active[side],ds=active[1-side],i=os.findIndex(p=>p.playerId===e.playerId);if(i<0)throw Error('Putback actor outside lineup');
    const p=os[i],clock=actions[e.index].clock.match(/PT(?:(\d+)M)?([\d.]+)S/),secs=Number(clock[1]??0)*60+Number(clock[2]);
    const tr=ls=>C.weightedTop(ls.map(p=>p.rebound*(1-C.PHYS_REB_WEIGHT)+p.physique*C.PHYS_REB_WEIGHT),C.COMPOSITE.teamRebound);
    const action=actions[e.index];let h=Number(action.scoreHome),a=Number(action.scoreAway);if(!Number.isFinite(h)||!Number.isFinite(a))throw Error('Missing source score');const lead=e.teamId===fixture.homeId?h-a:a-h;
    const reason=secs<=.3?'tooLate':action.period>=4&&secs<=27&&lead>0&&lead<=6?'intentionalFoul':action.period>=4&&secs<=14&&lead>0?'runClock':null;
    if(reason){excluded[reason]++;if(e.recordedFastPutback)unreachableFastShots.push({game:id,index:e.index,playerId:e.playerId,reason});continue;}
    const opts={assist:null,forced:secs<1.5,putback:true,contextScale:b.options.contextScale??1,contextLongScale:1,contextShortScale:b.options.contextShortScale,turnoverScale:b.options.turnoverScale??1,turnoverMode:b.options.turnoverMode,pressureAttribute:pressureSignal(ds,b.options.stealPriorRate).attribute};
    const opt={...b.options,contextScale:1,creationPolicy:'rotation-space',contextLongScale:1};
    const base=terminalDefenseProbabilities(p,measuredContext(os,i),ds[i],M.helpDefense(ds),tr(os),tr(ds),M.teamPhysique(ds),opts,ds,opt),q=spaceProbability(base,p,true,opt),foul=observedFoulInputs(q,p,opt,attemptMakeProbability);
    const survival=(1-opt.nonShootingFoulRate)*(1-q.pTovTouch)*foul.short.recorded;
    if(!(survival>0&&survival<1))throw Error('Invalid recorded-FGA conditional survival');
    outputRows.push([p.playerId,e.recordedFastPutback,survival]);
    const sum=sums.get(p.playerId)??{rebounds:0,fastFga:0,survivalSum:0};sum.rebounds++;sum.fastFga+=e.recordedFastPutback;sum.survivalSum+=survival;sums.set(p.playerId,sum);count++;

   }
  }
  if(joined.size!==events.length)throw Error('Unmapped source putback events');outputGames.push({id,fold:Number(BigInt(id)%5n),rows:outputRows});
 }
 if(count+Object.values(excluded).reduce((s,n)=>s+n,0)!==src.totals.fgReboundOpportunities)throw Error('Source opportunity coverage mismatch');
 const cards=Object.fromEntries(src.cards?Object.keys(src.cards).map(pid=>[pid,sums.get(Number(pid))??{rebounds:0,fastFga:0,survivalSum:0}]):[]);
 const out={season,design:'Recorded same-player fast short FGA incidence = putback branch selection times source-model survival of nonshooting contact, terminal TOV and unrecorded shooting foul miss. Contexts use v22 actual opposing five and rotation mean energy. Full-source defender/shot card covariates: descriptive conditional reconstruction, not causal or blind prediction. Exclude only states where current endgame/clock engine cannot attempt a PB; preserve excluded actual fast shots separately as model-policy mismatch. No runtime parameter changed.',rowFields:['playerId','recordedFastPutback','sourceRecordedFgaSurvival'],count,excluded,unreachableFastShots,cards,games:outputGames,hashes:Object.fromEntries([`${root}/prepare-choice-survival.mjs`,`${root}/${season}-putback-choices.json`,file,'reports/player-impact-v22/input.mjs','reports/player-impact-v22/model.mjs','reports/player-impact-v21/model.mjs'].map(f=>[f,hash(f)]))};
 fs.writeFileSync(output,JSON.stringify(out));console.log(JSON.stringify({season,count,excluded,unreachableFastShots:unreachableFastShots.length}));
}

import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const cache=new Map(),url=f=>pathToFileURL(path.resolve(f)).href;
export async function impactEngine(version,{game=false,memoized=false}={}){
 const key=JSON.stringify([version,game,memoized]);if(cache.has(key))return cache.get(key);
 if(!['threat-flow','threat-creation','threat-space'].includes(version))throw Error('Unknown creation model');
 let source=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
 const patches=[];
 const replace=(from,to)=>patches.push(`{const a=${JSON.stringify(from)};if(g.split(a).length!==2)throw Error('Impact source anchor drift: '+a);g=g.replace(a,${JSON.stringify(to)});}`);
 {
  // Move this closure ahead of handler selection. It does not capture hi.
  patches.push(`{const start=g.indexOf('    const probability = (i,a=null,forced=false) => {'),end=g.indexOf('    const best = (i,a,forced=false) => {',start);if(start<0||end<0)throw Error('Probability closure drift');const p=g.slice(start,end);g=g.slice(0,start)+g.slice(end);const anchor='    let hi=putback===null?';if(g.split(anchor).length!==2)throw Error('Selection anchor drift');g=g.replace(anchor,p+'    const creationPlan=putback===null?opportunityPlan(ls[off],probability,pressureSignal(ls[1-off],opt.stealPriorRate).relative,opt.creationPolicy):null;\\n'+anchor);}`);
  replace("volumeWeights(ls[off]):M.handlingWeights(ls[off])","creationPlan.weights:M.handlingWeights(ls[off])");
  replace('M.shootRate(p.ev,passesLeft)','(passesLeft===C.MAX_PASSES?creationPlan.rows[hi].shoot:1)');
  replace('M.passOpenRate(ls[off][hi],M.teammateContext(ls[off],hi),pressureDefender)','1');
  replace('M.interceptRate(ls[off][hi],pressureDefender,M.teammateContext(ls[off],hi))*(opt.turnoverCategories?opt.passTurnoverScale:1)','creationPlan.rows[hi].intercept');
  replace("volumeWeights(ls[off],'shot').map((w,i)=>i===hi?0:w)",'creationPlan.rows[hi].receivers');
  patches.push(`g="import {opportunityPlan,contestHelp,spaceProbability,observedFoulInputs} from '${url('reports/player-impact-v13/model.mjs')}';\\n"+g;`);
 }
 if([].includes(version)){
  replace('ds[i],M.helpDefense(ds),tr(os)','ds[i],contestHelp(ds),tr(os)');
 }
 {
  replace('return fourthProbability(os[i],','const originalProbability=fourthProbability(os[i],');
  replace('},ds,opt);\n    };','},ds,opt); return spaceProbability(originalProbability,os[i],putback!==null,opt);\n    };');
  patches.push(`{const start=g.indexOf('    const foulInputs=Object.fromEntries(zones.map(z=>{'),end=g.indexOf('    // p.zone describes recorded FGA.',start);if(start<0||end<0)throw Error('Foul input anchor drift');g=g.slice(0,start)+'    const foulInputs=observedFoulInputs(p,ls[off][hi],opt,attemptMakeProbability);\\n'+g.slice(end);}`);
 }
 // Keep the already verified conditional DREB/BLK allocation for candidates.
 // Control remains byte-for-byte comparable in all team/player counters.
 if(version!=='control'){
  replace("reboundWeights(ls[side],{zone,side:offensive?'offense':'defense',shooterIndex:offensive?slot:-1,freeThrow},opt)","(offensive?reboundWeights(ls[side],{zone,side:'offense',shooterIndex:slot,freeThrow},opt):measuredRecipientWeights(ls[side],'dreb'))");
  replace('blocker=D.lineup[pickWeighted(bp.weights,rng())]',"blocker=D.lineup[pickWeighted(measuredRecipientWeights(ls[1-off],'blk'),rng())]");
  patches.push(`g="import {measuredRecipientWeights} from '${url('src/individual_box_allocation.js')}';\\n"+g;`);
 }
 replace('    if (opt.eventObserver) opt.eventObserver(',`    if(opt.onCourtObserver&&['FGM','FGX','GAME_END'].includes(type))opt.onCourtObserver({type,side,zone:extra.zone,playerId:player===null?null:sides[side].roster[player].playerId,assistPlayerId:extra.assist===null||extra.assist===undefined?null:sides[side].roster[extra.assist].playerId,teams:sides.map((s,i)=>({teamId:i?teamB.id:teamA.id,lineup:s.lineup.map(j=>s.roster[j].playerId),active:s.roster.filter(p=>!p.injured&&(p.targetMinutes??1)>0).map(p=>p.playerId)}))});\n    if (opt.eventObserver) opt.eventObserver(`);
 if(memoized){
  if(!game)throw Error('Memoization only allowed for fixed-lineup game probes');
  replace('const probability = (i,a=null,forced=false) => {','const probability = (i,a=null,forced=false) => { const cacheKey=off+":"+i+":"+a+":"+forced+":"+(putback!==null); if(opt.ovrCache?.has(cacheKey))return opt.ovrCache.get(cacheKey);');
  replace('const originalProbability=fourthProbability(os[i],','const originalProbability=fourthProbability(os[i],');
  replace('return spaceProbability(originalProbability,os[i],putback!==null,opt);','const cachedProbability=spaceProbability(originalProbability,os[i],putback!==null,opt); if(opt.ovrCache)opt.ovrCache.set(cacheKey,cachedProbability); return cachedProbability;');
  patches.push(`g=g.replaceAll('M.teammateContext(','cachedContext(');`);
  replace('const lineups = () => sides.map(s=>s.lineup.map(i=>opt.fatigue?M.applyStamina(s.roster[i],1-s.energy[i]):s.roster[i]));',`const fixedLineups=sides.map(s=>s.lineup.map(i=>s.roster[i]));
 const lineups=()=>fixedLineups;
 const contexts=fixedLineups.map(ls=>ls.map((_,i)=>M.teammateContext(ls,i)));
 const cachedContext=(ls,i)=>contexts[fixedLineups.indexOf(ls)][i];`);
 }
 patches.push(`g=g.replaceAll('M.teammateContext(', 'measuredContext(');g="import {measuredContext} from '${url('src/measured_creation_context.js')}';\\n"+g;`);
 const anchor='  const gu=encode(g),s=';if(source.split(anchor).length!==2)throw Error('Adapter export anchor');
 source=source.replace(anchor,patches.join('\n')+'\n'+anchor);
 if(game)source=source.replace('cached=(await import(encode(s))).runDefenseSeason;return cached;','cached=(await import(gu)).simulateDefenseFourthGame;return cached;');
 const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 const run=await mod.experimentalSeason();cache.set(key,run);return run;
}

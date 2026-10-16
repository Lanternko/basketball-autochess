import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const cache=new Map(),url=f=>pathToFileURL(path.resolve(f)).href;
export async function impactEngine(version,{game=false,memoized=false}={}){
 const key=JSON.stringify([version,game,memoized]);if(cache.has(key))return cache.get(key);
 if(!['control','creation-flow','creation-flow-balanced'].includes(version))throw Error('Unknown creation model');
 let source=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
 const patches=[];
 const replace=(from,to)=>patches.push(`{const a=${JSON.stringify(from)};if(g.split(a).length!==2)throw Error('Impact source anchor drift: '+a);g=g.replace(a,${JSON.stringify(to)});}`);
 if(version!=='control'){
  replace("volumeWeights(ls[off]):M.handlingWeights(ls[off])","creationHandlerWeights(ls[off]):M.handlingWeights(ls[off])");
  replace('M.shootRate(p.ev,passesLeft)','creationShootProbability(ls[off][hi],passesLeft,C.MAX_PASSES)');
  const probs=version==='creation-flow-balanced'?",ls[off].map((_,i)=>{const a=probability(i,assist),b=probability(i);const p=a.ev>=b.ev?a:b;return p.FG3M+p.MIDM+p.RIMM;})":'';
  replace("volumeWeights(ls[off],'shot').map((w,i)=>i===hi?0:w)",`creationReceiverWeights(ls[off],hi${probs})`);
  patches.push(`g="import {creationHandlerWeights,creationShootProbability,creationReceiverWeights} from '${url('src/shot_creation_model.js')}';\\n"+g;`);
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
  replace('return fourthProbability(os[i],','const cachedProbability=fourthProbability(os[i],');
  replace('},ds,opt);\n    };','},ds,opt); if(opt.ovrCache)opt.ovrCache.set(cacheKey,cachedProbability); return cachedProbability;\n    };');
  patches.push(`g=g.replaceAll('M.teammateContext(','cachedContext(');`);
  replace('const lineups = () => sides.map(s=>s.lineup.map(i=>opt.fatigue?M.applyStamina(s.roster[i],1-s.energy[i]):s.roster[i]));',`const fixedLineups=sides.map(s=>s.lineup.map(i=>s.roster[i]));
 const lineups=()=>fixedLineups;
 const contexts=fixedLineups.map(ls=>ls.map((_,i)=>M.teammateContext(ls,i)));
 const cachedContext=(ls,i)=>contexts[fixedLineups.indexOf(ls)][i];`);
 }
 const anchor='  const gu=encode(g),s=';if(source.split(anchor).length!==2)throw Error('Adapter export anchor');
 source=source.replace(anchor,patches.join('\n')+'\n'+anchor);
 if(game)source=source.replace('cached=(await import(encode(s))).runDefenseSeason;return cached;','cached=(await import(gu)).simulateDefenseFourthGame;return cached;');
 const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
 const run=await mod.experimentalSeason();cache.set(key,run);return run;
}

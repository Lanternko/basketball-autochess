import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href;
const encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const link=(s,base,map={})=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${map[f]??url(path.resolve(base,f))}${q}`);
let cached;
export async function experimentalSeason(){
  if(cached)return cached;
  let g=fs.readFileSync('src/defense_fourth_game.js','utf8');
  const anchor='    const offensive=rng()<chance, side=';
  if(g.split(anchor).length!==2)throw Error('Rebound instrumentation anchor drift');
  g=g.replace(anchor,`    if(!freeThrow&&(opt.individualOrebCard||opt.leagueOrbLogit))chance=reboundChance(os,ds,{zone,shooterIndex:slot,oldChance:chance,options:opt});\n${anchor}`);
  const weights='opportunityReboundWeights(ls[side],{zone,side:offensive?\'offense\':\'defense\',shooterIndex:offensive?slot:-1})';
  if(g.split(weights).length!==2)throw Error('Rebound recipient anchor drift');
  g=g.replace(weights,"reboundWeights(ls[side],{zone,side:offensive?'offense':'defense',shooterIndex:offensive?slot:-1,freeThrow},opt)");
  const ret='    return {end:!offensive,dead:false,putback:offensive && !freeThrow && rng()<M.putbackRate(ls[side][index],M.helpDefense(ds))?player:null};';
  if(g.split(ret).length!==2)throw Error('Putback trace anchor drift');
  g=g.replace(ret,`    if(opt.allocationObserver){const cfg={zone,side:'offense',shooterIndex:slot,freeThrow};const ow=opportunityReboundWeights(os,cfg),nw=reboundWeights(os,cfg,{individualOrebAllocation:true}),h=M.helpDefense(ds);opt.allocationObserver({offensive,freeThrow,oldExpected:ow.reduce((s,w,i)=>s+w*M.putbackRate(os[i],h),0),newExpected:nw.reduce((s,w,i)=>s+w*M.putbackRate(os[i],h),0),selectedExpected:offensive?M.putbackRate(ls[side][index],h):0});}\n${ret}`);
  g=`import {reboundChance,reboundWeights} from '${url('reports/defense-tenth/step4-rebounds-allocation/model.mjs')}';\n`+link(g,'src');
  const gu=encode(g),s=link(fs.readFileSync('src/defense_fourth_season.js','utf8'),'src',{'./defense_fourth_game.js':gu});
  cached=(await import(encode(s))).runDefenseSeason;return cached;
}

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
  g=g.replace(anchor,`    if(!freeThrow&&(opt.individualDrebCard||opt.leagueOrbLogit))chance=reboundChance(os,ds,{zone,shooterIndex:slot,oldChance:chance,options:opt});\n${anchor}`);
  const weights='opportunityReboundWeights(ls[side],{zone,side:offensive?\'offense\':\'defense\',shooterIndex:offensive?slot:-1})';
  if(g.split(weights).length!==2)throw Error('Rebound recipient anchor drift');
  g=g.replace(weights,"reboundWeights(ls[side],{zone,side:offensive?'offense':'defense',shooterIndex:offensive?slot:-1},opt)");
  g=`import {reboundChance,reboundWeights} from '${url('reports/defense-tenth/step4-rebounds/model.mjs')}';\n`+link(g,'src');
  const gu=encode(g),s=link(fs.readFileSync('src/defense_fourth_season.js','utf8'),'src',{'./defense_fourth_game.js':gu});
  cached=(await import(encode(s))).runDefenseSeason;return cached;
}

import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
// Diagnostic-only modules in memory. No engine/frozen file is written.
export async function auditEngine(kind='fourth',{neutralTwoP=false}={}){
 const url=f=>pathToFileURL(path.resolve('src',f)).href;
 const encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
 const relink=(s,map={})=>s.replace(/from\s+(['"])(\.\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${map[f.slice(2)]??url(f.slice(2))}${q}`);
 let model=fs.readFileSync('src/probability_model.js','utf8');
 if(neutralTwoP)model=model.replace('(1-threeRate)*C.HALFCOURT_ZONE_SHARE.mid/twoPrior','(1-threeRate)*.5').replace('(1-threeRate)*C.HALFCOURT_ZONE_SHARE.short/twoPrior','(1-threeRate)*.5');
 const mu=encode(relink(model)),pu=encode(relink(fs.readFileSync('src/defense_probability.js','utf8'),{'probability_model.js':mu})),eu=encode(relink(fs.readFileSync('src/defense_fourth_effects.js','utf8'),{'probability_model.js':mu,'defense_probability.js':pu}));
 let game=fs.readFileSync(`src/defense_${kind}_game.js`,'utf8');
 game=game.replaceAll('M.teammateContext(', 'auditContext(');
 const point=game.indexOf('  if(opt.empiricalTiming');
 if(point<0)throw Error('No engine instrumentation anchor');
 game=game.slice(0,point)+`  const auditContext=(ls,i)=>{const c=M.teammateContext(ls,i);if(!ls.some(p=>opt.auditIds?.includes(p.playerId)))return c;if(opt.auditNeutralCreation)c.create=70;if(opt.auditNoSpacing){c.spacing=70;c.gravity=70;}return c;};\n`+game.slice(point);
 game=game.replace('const offensive=rng()<chance, side=', 'const offensive=(rng()<chance)&&!(opt.auditNoOreb&&off===0), side=');
 game=game.replace('const offensive=reboundRng()<rate.teamOffShare,side=', 'const offensive=(reboundRng()<rate.teamOffShare)&&!(opt.auditNoOreb&&off===0),side=');
 const gu=encode(relink(game,{'probability_model.js':mu,'defense_probability.js':pu,'defense_fourth_effects.js':eu}));
 return (await import(gu))[kind==='fourth'?'simulateDefenseFourthGame':'simulateDefenseFifthGame'];
}

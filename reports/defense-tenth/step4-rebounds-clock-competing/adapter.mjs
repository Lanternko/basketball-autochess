import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href;
const encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const link=(s,base)=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${url(path.resolve(base,f))}${q}`);

import {rimClockSource as baseSource} from '../step4-rebounds-rim-clock/adapter.mjs';
export function rimClockSource(source) {
 let g=baseSource(source);
 const replace=(a,b)=>{if(g.split(a).length!==2)throw Error('Competing clock source drift: '+a);g=g.replace(a,b);};
 replace("  let origin='period'", "  let postClockPending=false;const postClockRng=makeRng(opt.seed^0x2610C10C);\n  let origin='period'");
 replace("    if (opt.eventObserver) opt.eventObserver({type,period,clock:clock/10,off:side,player,...extra});", "    if (opt.eventObserver) opt.eventObserver({type,period,clock:clock/10,shotClock:shotClock/10,off:side,player,...extra});");
 replace('    if (offensive) resetReboundClock();', '    if (offensive) {resetReboundClock();if(!freeThrow)postClockPending=true;}');
 replace('    let ls=lineups(), O=sides[off], D=sides[1-off];', `    let ls=lineups(), O=sides[off], D=sides[1-off];
    const deadline=deadlineDecision({pending:postClockPending,periodTicks:clock,shotTicks:shotClock,enabled:opt.postOrebDeadline??false,probability:opt.postOrebClockProbability??0,rng:postClockRng});
    postClockPending=false;
    if(deadline.eligible)emit('CLOCK_TRIAL',off,null,{path:'postOreb'});
    if(deadline.violation){
      advance(shotClock,"Violation");const player=O.lineup[0];
      record(off,player,'tov');record(off,player,'deadTov');record(off,player,'clockTov');
      emit('SHOT_CLOCK',off,player,{independent:false,timeoutSource:'postOreb'});
      origin=opt.splitTurnoverTiming?'deadTurnover':'turnover';
      return {end:true,dead:true,putback:null};
    }`);
 replace('      shotClock=240;possessions++;', '      postClockPending=false;shotClock=240;possessions++;');
 replace('      plannedViolation=opt.independentClock&&clock>shotClock&&violationRng()<opt.clockViolationProbability;', `      if(clock>shotClock)emit('CLOCK_TRIAL',off,null,{path:'fresh'});
      plannedViolation=opt.independentClock&&clock>shotClock&&violationRng()<(opt.competingFreshClock?opt.freshClockProbability:opt.clockViolationProbability);`);
 return `import {deadlineDecision} from '${url('reports/defense-tenth/step4-rebounds-clock-competing/deadline.mjs')}';\n`+g;
}

let cached;
async function load() {
  if(cached)return cached;
  let s=fs.readFileSync('reports/defense-tenth/step4-rebounds-turnover-time/adapter.mjs','utf8');
  const anchor='  g=splitTurnoverSource(g);';
  if(s.split(anchor).length!==2)throw Error('Baseline adapter drift');
  s=s.replace(anchor,anchor+'\n  g=rimClockSource(g);');
  const built='  const gu=encode(g),s=';
  if(s.split(built).length!==2)throw Error('Baseline import drift');
  s=s.replace(built,'  const gu=encode(g);builtGame=(await import(gu)).simulateDefenseFourthGame;const s=');
  s=`import {rimClockSource} from '${url('reports/defense-tenth/step4-rebounds-clock-competing/adapter.mjs')}';\nlet builtGame;\n`+link(s,'reports/defense-tenth/step4-rebounds-turnover-time');
  s+='\nexport async function getGame(){await experimentalSeason();return builtGame;}';
  cached=await import(encode(s));return cached;
}
export async function experimentalSeason(){return (await load()).experimentalSeason();}
export async function experimentalGame(){return (await load()).getGame();}

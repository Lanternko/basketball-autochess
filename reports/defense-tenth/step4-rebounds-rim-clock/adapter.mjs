import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href;
const encode=s=>'data:text/javascript;base64,'+Buffer.from(s).toString('base64');
const link=(s,base)=>s.replace(/from\s+(['"])(\.\.?\/[^'"]+)\1/g,(_,q,f)=>`from ${q}${url(path.resolve(base,f))}${q}`);

export function rimClockSource(source) {
  let g=source.replaceAll('\r\n','\n');
  const replace=(a,b)=>{if(g.split(a).length!==2)throw Error('Rim-clock source drift: '+a);g=g.replace(a,b);};
  replace("  if(opt.empiricalTiming&&!opt.timingCDF)","  if(opt.rimContactClock&&typeof opt.rimContactResolver!=='function')throw Error('Explicit rimContactResolver required');\n  if(opt.empiricalTiming&&!opt.timingCDF)");
  replace("  let origin='period'", "  const rimContactRng=makeRng(opt.seed^0x392DA715);\n  let origin='period'");
  replace('  const rebound = (shooter, zone, freeThrow=false) => {',`  const naturalClockLoss=(shooter,where)=>{
    record(off,shooter,'tov');record(off,shooter,'deadTov');record(off,shooter,'clockTov');
    emit('SHOT_CLOCK',off,shooter,{independent:false,naturalNoRim:true,where});
    origin=opt.splitTurnoverTiming?'deadTurnover':'turnover';
    return {end:true,dead:true,putback:null};
  };
  const rebound = (shooter, zone, freeThrow=false, rimContact=null) => {
    const beforeFlight=shotClock;`);
  replace('    if (!freeThrow) advance(3+Math.floor(timeRng()*10),"Flight");',`    if (!freeThrow) {
      const flight=3+Math.floor(timeRng()*10);
      advance(opt.rimContactClock&&!rimContact?Math.min(flight,shotClock):flight,"Flight");
    }`);
  replace("    record(off,null,'reboundChances');",`    if(opt.rimContactClock&&!freeThrow&&!rimContact&&shotClock===0) return naturalClockLoss(shooter,'flight');
    const resetReboundClock=()=>{
      if(!opt.rimContactClock){shotClock=140;return;}
      const before=shotClock,transition=offensiveReboundClock({remainingTicks:shotClock,periodTicks:clock,rimContact,freeThrow});
      shotClock=transition.clockTicks;
      emit('REBOUND_CLOCK',off,shooter,{freeThrow,rimContact:freeThrow?null:rimContact,clockBeforeFlight:beforeFlight/10,clockBefore:before/10,clockAfter:shotClock/10,reset:transition.reset});
    };
    record(off,null,'reboundChances');`);
  replace('      if(offensive)shotClock=140;','      if(offensive)resetReboundClock();');
  replace('    if (offensive) shotClock=140;','    if (offensive) resetReboundClock();');
  replace('    let ls=lineups(), O=sides[off], D=sides[1-off];',`    if(opt.rimContactClock&&shotClock===0)return naturalClockLoss(sides[off].lineup[0],'next-opportunity');
    let ls=lineups(), O=sides[off], D=sides[1-off];`);
  const event="    emit(made?'FGM':'FGX',off,shooter,{zone,points:made?points:0,assist:made&&usedAssist?passer:null,blocker});";
  replace(event,`    let rimContact=null;
    if(opt.rimContactClock&&!made){
      rimContact=resolveContact(opt.rimContactResolver,{zone,blocked:blocker!==null,putback:putback!==null,period,gameSeconds:clock/10,shotClockSeconds:shotClock/10},rimContactRng);
      emit('RIM_CONTACT_STATE',off,shooter,{zone,blocked:blocker!==null,rimContact});
    }
${event}`);
  replace('    return rebound(shooter,zone);','    return rebound(shooter,zone,false,rimContact);');
  return `import {offensiveReboundClock,resolveContact} from '${url('reports/defense-tenth/step4-rebounds-rim-clock/rule.mjs')}';\n`+g;
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
  s=`import {rimClockSource} from '${url('reports/defense-tenth/step4-rebounds-rim-clock/adapter.mjs')}';\nlet builtGame;\n`+link(s,'reports/defense-tenth/step4-rebounds-turnover-time');
  s+='\nexport async function getGame(){await experimentalSeason();return builtGame;}';
  cached=await import(encode(s));return cached;
}
export async function experimentalSeason(){return (await load()).experimentalSeason();}
export async function experimentalGame(){return (await load()).getGame();}

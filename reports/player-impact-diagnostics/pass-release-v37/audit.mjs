// Observe the exact archived Jokic healthy games without changing a random draw.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {source,workloadTeam,opponentTeam,options} from '../../player-impact-v29/benchmark.mjs';
const root='reports/player-impact-diagnostics/pass-release-v37',read=f=>JSON.parse(fs.readFileSync(f)),sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),id=203999,hashes={},versions=[];
assert.ok(!fs.existsSync(root+'/audit.json'));
for(const version of ['v30','v37']){
 const base=`reports/player-impact-${version}`,protocol=read(base+'/ovr-probe-protocol.json');
 for(const[p,h]of Object.entries(protocol.hashes))assert.equal(sha(p),h,p);
 const {ovrInput}=await import(`../../player-impact-${version}/ovr-input.mjs`),x=await ovrInput(),p=x.players.find(p=>p.playerId===id),slot=x.roleMap.get(id).slot,cap=source().capMinutes;
 const checkpoint=read(base+'/ovr-probe-checkpoint.json'),prior=checkpoint.rows.find(r=>r.result.playerId===id).result.arms.find(a=>a.arm==='supportedHealthy');
 let code=fs.readFileSync(base+'/engine.mjs','utf8');
 const anchor=" const anchor='  const gu=encode(g),s=';";assert.equal(code.split(anchor).length,2);
 const before='    p=best(hi,assist,shotClock<20||clock<15);',after=before+" opt.releaseAudit?.({off,shooterId:O.roster[shooter].playerId,passerId:passer===null?null:O.roster[passer].playerId,usedAssist,ev:p.ev});";
 code=code.replace(anchor,` replace(${JSON.stringify(before)},${JSON.stringify(after)});\n`+anchor);
 const {impactEngine}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')),run=await impactEngine('rotation-space',{game:true});
 const totals={games:0,passes:0,releasePotential:0,releaseUsesAssist:0,releaseRejectsAssist:0,creditedAssists:0,playerAst:0,minutes:0},receivers={};
 const receiver=pid=>receivers[pid]??=( {playerId:pid,passes:0,releases:0,usesAssist:0,rejectsAssist:0,creditedAssists:0} );
 for(const g of prior.games){
  const a=workloadTeam(x,p,slot,prior.minutes,cap,g.phase),b=opponentTeam(x,x.opponents[g.opponent],cap,g.phase);
  for(const pair of g.pair){
   const side=pair.side,teams=side?[b.team,a.team]:[a.team,b.team],schedules=side?[b.schedule,a.schedule]:[a.schedule,b.schedule],opt=options(x,g.seed,schedules);
   opt.releaseAudit=e=>{if(e.off!==side||e.passerId!==id)return;totals.releasePotential++;const r=receiver(e.shooterId);r.releases++;if(e.usedAssist){totals.releaseUsesAssist++;r.usesAssist++;}else{totals.releaseRejectsAssist++;r.rejectsAssist++;}};
   opt.eventObserver=e=>{
    if(e.off!==side)return;const roster=teams[side].roster;
    if(e.type==='PASS'&&roster[e.from]?.playerId===id){totals.passes++;receiver(e.playerId).passes++;}
    if(e.type==='FGM'&&e.assist!==null&&e.assist!==undefined&&roster[e.assist]?.playerId===id){totals.creditedAssists++;receiver(e.playerId).creditedAssists++;}
   };
   const result=run(...teams,opt),tag=side?'B':'A',stats=result['players'+tag][slot];
   assert.equal(side?result.scoreB-result.scoreA:result.scoreA-result.scoreB,pair.margin);
   for(const[k,v]of Object.entries(pair.playerStats))assert.equal(stats[k],v,`${version} ${g.opponent} ${g.i} ${side} ${k}`);
   assert.ok(Math.abs(stats.seconds/60-pair.playerMinutes)<1e-8);totals.games++;totals.playerAst+=stats.ast;totals.minutes+=stats.seconds/60;
  }
 }
 assert.equal(totals.creditedAssists,totals.playerAst);assert.equal(totals.releasePotential,totals.releaseUsesAssist+totals.releaseRejectsAssist);
 versions.push({version,name:p.name,minutesPerGame:prior.minutes,totals,receivers:Object.values(receivers)});
 for(const f of [base+'/engine.mjs',base+'/ovr-input.mjs',base+'/ovr-probe-checkpoint.json',base+'/ovr-probe-protocol.json'])hashes[f]=sha(f);
 for(const[p,h]of Object.entries(protocol.hashes))assert.equal(sha(p),h,p);
 console.log(JSON.stringify({version,...totals,astPerWorkloadGame:totals.playerAst/totals.games}));
}
hashes[root+'/audit.mjs']=sha(root+'/audit.mjs');
fs.writeFileSync(root+'/audit.json',JSON.stringify({passed:true,scope:'Exploratory release-path observation of one selected player, all archived supportedHealthy seeds/opponents/seats. Every observed game exactly reproduces its archived margin, all13 player counters and minutes; observer adds no random draw or return mutation. This is a conditional model mechanism diagnostic, not causal NBA data, full OVR or proof all decrease is caused by one step.',versions,hashes},null,2));

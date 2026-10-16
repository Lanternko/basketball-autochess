import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {offensiveReboundProbability,opportunityReboundWeights,REBOUND_RULES} from '../../../src/rebound_block_model.js';
import {simulateDefenseFourthGame} from '../../../src/defense_fourth_game.js';
import {makeRng,pickWeighted} from '../../../src/rng.js';

const root='reports/defense-tenth/step4-rebounds-opportunity';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const save=(f,x)=>fs.writeFileSync(root+'/'+f,JSON.stringify(x,null,2)+'\n');
const hashObject=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sum=a=>a.reduce((s,x)=>s+x,0);
const clone=structuredClone;
const protocol=read(root+'/protocol.json');
assert.equal(sha(root+'/protocol.json'),fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0]);
for(const [f,h] of Object.entries(protocol.inputHashes))assert.equal(sha(f),h,f);
const lock=root+'/analysis-code-registration.json';
if(!fs.existsSync(lock))fs.writeFileSync(lock,JSON.stringify({at:new Date().toISOString(),sha256:sha(root+'/analyze.mjs')},null,2)+'\n');
assert.equal(read(lock).sha256,sha(root+'/analyze.mjs'));

const positions=['PG','SG','SF','PF','C'],zones=['short','mid','long'];
const neutral=()=>positions.map((pos,i)=>({name:'Neutral '+pos,playerId:-(i+1),pos,courtPosition:pos,
  ...Object.fromEntries(['long','mid','short','drive','tovSkill','pass','ft','rebound','onBall','help','stamina','physique','offBall','screen','handle','breakDbl'].map(k=>[k,70]))}));
const anchor=neutral();anchor[4].rebound=99;anchor[4].physique=90;
const rolePG=clone(anchor);rolePG[4].courtPosition='PG';
const posPG=clone(anchor);posPG[4].pos='PG';
const swapped=clone(anchor);swapped[0].courtPosition='C';swapped[4].courtPosition='PG';
const helper=neutral();helper[4].boxOut=99;helper[4].boxOutHelp=99;
const near=neutral().map(p=>({...p,reboundStartDistanceFeet:0}));
const far=neutral().map(p=>({...p,reboundStartDistanceFeet:30}));
const crash0=neutral().map(p=>({...p,crashIntent:0}));
const crash1=neutral().map(p=>({...p,crashIntent:1}));
const cases=[];
for(let k=0;k<=5;k++){
  const variants=[];
  for(let mask=0;mask<32;mask++)if(mask.toString(2).replaceAll('0','').length===k)
    variants.push(neutral().map((p,i)=>({...p,rebound:(mask>>i)&1?99:70})));
  cases.push({name:'stack'+k,variants});
}
cases.push(...Object.entries({anchorC:anchor,anchorPG:rolePG,anchorPosOnlyPG:posPG,anchorSwapPG:swapped,
  boxOutHigh:helper,distanceNear:near,distanceFar:far,crash0,crash1}).map(([name,v])=>({name,variants:[v]})));
const topCards=[];
function table(f){const s=read(f).data.resultSets[0];return s.rowSet.map(row=>Object.fromEntries(s.headers.map((h,i)=>[h,row[i]])));}
for(const season of protocol.seasons){
  const b=read(`reports/defense-tenth/step4-t0/${season}/bundle.json`),by=new Map();
  for(const t of b.league.teams)for(const p of t.roster){
    const prev=by.get(p.playerId);
    if(!prev)by.set(p.playerId,{card:clone(p),totalMinutes:p.observed.MIN,largestStint:p.observed.MIN});
    else {prev.totalMinutes+=p.observed.MIN;if(p.observed.MIN>prev.largestStint){prev.card=clone(p);prev.largestStint=p.observed.MIN;}}
  }
  const advanced=new Map(table(`reports/defense-tenth/step4-t2/raw/${season}/0-advanced.json`).map(r=>[r.PLAYER_ID,r]));
  const selected=[...by.values()].filter(p=>p.totalMinutes>=1000&&Number.isFinite(advanced.get(p.card.playerId)?.OREB_PCT))
    .sort((a,b)=>advanced.get(b.card.playerId).OREB_PCT-advanced.get(a.card.playerId).OREB_PCT||a.card.playerId-b.card.playerId).slice(0,5);
  assert.equal(selected.length,5);
  cases.push({name:'realTop5-'+season,variants:[selected.map(r=>r.card)]});
  topCards.push({season,players:selected.map(p=>({playerId:p.card.playerId,name:p.card.name,pos:p.card.pos,
    courtPosition:p.card.courtPosition,totalMinutes:p.totalMinutes,orebPct:advanced.get(p.card.playerId).OREB_PCT,
    rebound:p.card.rebound,physique:p.card.physique}))});
}

function state(off,def,zone,shooterIndex){
  const settings={zone,shooterIndex};
  const p=offensiveReboundProbability(off,def,settings);
  const ow=opportunityReboundWeights(off,{...settings,side:'offense'});
  const dw=opportunityReboundWeights(def,{zone,side:'defense'});
  const joint=[...ow.map(w=>p*w),...dw.map(w=>(1-p)*w)];
  const error=Math.abs(sum(joint)-1);
  assert.ok(error<protocol.rules.conservationTolerance);
  assert.ok(joint.every(v=>v>=0&&v<=1));
  return {p,ow,dw,joint,error};
}
function summarize(states){
  const joint=Array.from({length:10},(_,i)=>mean(states.map(s=>s.joint[i])));
  const p=mean(states.map(s=>s.p));
  return {offShare:p,offIndividual:joint.slice(0,5),defIndividual:joint.slice(5),
    offConditional:joint.slice(0,5).map(x=>x/p),defConditional:joint.slice(5).map(x=>x/(1-p)),
    massError:Math.abs(sum(joint)-1),minOffShare:Math.min(...states.map(s=>s.p)),maxOffShare:Math.max(...states.map(s=>s.p))};
}
const kernels=[];
for(const c of cases){
  const states=[];
  for(const lineup of c.variants)for(const zone of zones)for(let shooterIndex=0;shooterIndex<5;shooterIndex++)
    states.push(state(lineup,neutral(),zone,shooterIndex));
  const seedRows=[];
  for(const seed of protocol.seeds){
    const rng=makeRng(seed),counts=Array(10).fill(0);let oreb=0;
    for(let i=0;i<protocol.opportunitiesPerSeed;i++){
      const vi=Math.floor(rng()*c.variants.length),zi=Math.floor(rng()*3),si=Math.floor(rng()*5);
      const s=states[vi*15+zi*5+si],offensive=rng()<s.p,recipient=pickWeighted(offensive?s.ow:s.dw,rng());
      counts[(offensive?0:5)+recipient]++;oreb+=offensive;
    }
    assert.equal(sum(counts),protocol.opportunitiesPerSeed);
    seedRows.push({seed,offShare:oreb/protocol.opportunitiesPerSeed,counts});
  }
  const sampleMean=mean(seedRows.map(s=>s.offShare));
  const seedSD=Math.sqrt(sum(seedRows.map(s=>(s.offShare-sampleMean)**2))/(seedRows.length-1));
  const se=seedSD/Math.sqrt(seedRows.length);
  kernels.push({name:c.name,variants:c.variants.length,exact:summarize(states),
    sampling:{opportunities:protocol.opportunitiesPerSeed*protocol.seeds.length,offShare:sampleMean,seedSD,seedSE:se,
      mean95MonteCarloOnly:[sampleMean-2.093*se,sampleMean+2.093*se]},seedRows});
}
const roleDetail=[];
for(const [name,lineup] of Object.entries({anchorC:anchor,anchorPG:rolePG,anchorPosOnlyPG:posPG,anchorSwapPG:swapped})){
  for(const zone of zones)for(const shooterIndex of [-1,4]){
    roleDetail.push({name,zone,shooterIndex,asOffense:state(lineup,neutral(),zone,shooterIndex),
      asDefense:state(neutral(),lineup,zone,shooterIndex)});
  }
}
const exact=name=>kernels.find(c=>c.name===name).exact;
assert.deepEqual(exact('stack0'),exact('boxOutHigh'));
assert.deepEqual(exact('stack0'),exact('distanceNear'));
assert.deepEqual(exact('stack0'),exact('distanceFar'));
assert.deepEqual(exact('stack0'),exact('crash0'));
assert.deepEqual(exact('stack0'),exact('crash1'));
assert.deepEqual(exact('anchorC'),exact('anchorPosOnlyPG'));
save('kernel-results.json',{at:new Date().toISOString(),protocolSHA256:sha(root+'/protocol.json'),
  label:protocol.label,rules:REBOUND_RULES,topCards,kernels,roleDetail});
console.log('Kernel complete',kernels.length,'cases');

const bundle=read('reports/defense-tenth/step4-t0/2025-26/bundle.json');
const opt={...bundle.options,fatigue:false,substitutions:false,foulOut:99,minuteTargets:false,
  stateRotation:false,seasonMinuteTargets:false,neutralContests:false,replay:true};
for(const key of ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'])opt[key]=false;
delete opt.defenseSignals;
const gameCases={neutral:neutral(),allStrong:neutral().map(p=>({...p,rebound:99})),
  anchorC:anchor,anchorPG:rolePG,anchorPosOnlyPG:posPG,boxOutHigh:helper,distanceFar:far};
const games=[];
for(const [name,roster] of Object.entries(gameCases))for(const seed of protocol.seeds){
  const result=simulateDefenseFourthGame({name,roster:clone(roster)}, {name:'neutral',roster:neutral()}, {...opt,seed});
  let pending=null,terminal=0,orphan=0,fgMisses=0,ftMisses=0,unresolved=0,maxPossOrebs=0;
  const possessionOrebs=new Map();
  for(const e of result.events){
    if(e.type==='FGX'){pending={kind:'fg',poss:e.poss};fgMisses++;}
    if(e.type==='FTX'&&!e.technical&&e.attempt===e.attempts){pending={kind:'ft',poss:e.poss};ftMisses++;}
    if(['OREB','DREB','TEAM_OREB','TEAM_DREB'].includes(e.type)){
      if(!pending||pending.poss!==e.poss)orphan++;
      pending=null;terminal++;
      if(e.type==='OREB')possessionOrebs.set(e.poss,(possessionOrebs.get(e.poss)??0)+1);
    }
    if(e.type==='PERIOD_END'&&pending){unresolved++;pending=null;}
  }
  maxPossOrebs=Math.max(0,...possessionOrebs.values());
  const stats=[result.statA,result.statB];
  const chances=sum(stats.map(s=>s.reboundChances));
  const recovered=sum(stats.map(s=>s.oreb+s.dreb+s.teamOreb+s.teamDreb));
  assert.equal(recovered,chances,name+' ledger');assert.equal(terminal,chances);assert.equal(orphan,0);
  assert.equal(sum(stats.map(s=>s.periodMiss)),unresolved);
  assert.equal(terminal+unresolved,fgMisses+ftMisses);
  const payload={scoreA:result.scoreA,scoreB:result.scoreB,statA:result.statA,statB:result.statB,
    playersA:result.playersA,playersB:result.playersB,events:result.events};
  // Player display pos can change without changing actual event/stat mechanics.
  const mechanicsPayload=clone(payload);for(const side of ['playersA','playersB'])for(const p of mechanicsPayload[side])delete p.pos;
  games.push({name,seed,complete:result.complete,chances,recovered,terminal,orphan,unresolved,fgMisses,ftMisses,maxPossOrebs,
    mechanicsSHA256:hashObject(mechanicsPayload),statA:result.statA,statB:result.statB});
}
for(const name of ['boxOutHigh','distanceFar'])for(const g of games.filter(x=>x.name===name))
  assert.equal(g.mechanicsSHA256,games.find(x=>x.name==='neutral'&&x.seed===g.seed).mechanicsSHA256,name+' ignored metadata');
const gameParity=Object.fromEntries(['boxOutHigh','distanceFar','anchorPosOnlyPG'].map(name=>[name,
  games.filter(x=>x.name===name).filter(g=>g.mechanicsSHA256!==games.find(x=>x.name===(name==='anchorPosOnlyPG'?'anchorC':'neutral')&&x.seed===g.seed).mechanicsSHA256).map(g=>g.seed)]));
save('game-audit.json',{at:new Date().toISOString(),protocolSHA256:sha(root+'/protocol.json'),
  diagnosticOptions:{signalsOff:true,noMap:true,fatigue:false,substitutions:false,foulOut:99,minuteTargets:false},
  parityMismatchSeeds:gameParity,totalGames:games.length,totalChances:sum(games.map(g=>g.chances)),
  maxOrebsInOnePossession:Math.max(...games.map(g=>g.maxPossOrebs)),games});
console.log('Games complete',games.length,'opportunities',sum(games.map(g=>g.chances)));

const hustle=[];
for(const season of protocol.seasons){
  const rows=table(`reports/defense-tenth/step4-t2/raw/${season}/0-hustle.json`);
  const invalid=rows.filter(r=>r.BOX_OUT_PLAYER_TEAM_REBS<r.BOX_OUT_PLAYER_REBS||r.BOX_OUT_PLAYER_TEAM_REBS>r.BOX_OUTS);
  const add=k=>sum(rows.map(r=>r[k]??0));
  hustle.push({season,rows:rows.length,uniquePlayers:new Set(rows.map(r=>r.PLAYER_ID)).size,
    offBoxouts:add('OFF_BOXOUTS'),defBoxouts:add('DEF_BOXOUTS'),boxouts:add('BOX_OUTS'),
    teamRecoveryCredits:add('BOX_OUT_PLAYER_TEAM_REBS'),ownRecoveryCredits:add('BOX_OUT_PLAYER_REBS'),
    teammateRecoveryCredits:add('BOX_OUT_PLAYER_TEAM_REBS')-add('BOX_OUT_PLAYER_REBS'),
    invalid:invalid.map(r=>({id:r.PLAYER_ID,name:r.PLAYER_NAME,boxouts:r.BOX_OUTS,
      team:r.BOX_OUT_PLAYER_TEAM_REBS,own:r.BOX_OUT_PLAYER_REBS})),
    label:'Player box-out credits; not deduplicated team possessions. Recovery counts are not split into offensive/defensive contexts.'});
}
save('hustle-summary.json',{at:new Date().toISOString(),rows:hustle});
console.log('Hustle complete',hustle.map(r=>({season:r.season,teammateCredits:r.teammateRecoveryCredits,invalid:r.invalid.length})));

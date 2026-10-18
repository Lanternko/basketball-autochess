import {simulateGame} from './simulation_engine.js';
import {BASELINE} from './teams.js';

export const ATTRIBUTES=['long','mid','short','drive','tovSkill','pass','ft','rebound','onBall','help','stamina','physique','offBall','screen','handle','breakDbl'];
export function validateLeague(league) {
  if (league.teams?.length!==30 || new Set(league.teams.map(t=>t.id)).size!==30) throw new Error('Exactly 30 unique teams required');
  for (const t of league.teams) {
    if (t.season!==league.season || t.roster.length!==5 || new Set(t.roster.map(p=>p.playerId)).size!==5) throw new Error('Invalid season/roster');
    for (const p of t.roster) if (!ATTRIBUTES.every(k=>Number.isFinite(p[k])&&p[k]>=0&&p[k]<=150)) throw new Error('Invalid attributes');
    if (new Set(t.roster.map(p=>ATTRIBUTES.map(k=>p[k]).join(','))).size<2) throw new Error('Uniform teams are not a league');
  }
}
export function probe(player,slot) {
  if (!Number.isInteger(slot)||slot<0||slot>4) throw new RangeError('Invalid slot');
  return {...BASELINE,name:player.name,roster:BASELINE.roster.map((p,i)=>i===slot?{...player,pos:p.pos,courtPosition:p.pos}:p)};
}
export function flatPlayer(value) {return {name:`全${value}`,pos:'PG',...Object.fromEntries(ATTRIBUTES.map(k=>[k,value]))};}
export function winToOvr(win,anchors) {
  const {low,mid,high}=anchors;
  if (![win,low,mid,high].every(Number.isFinite)||low<0||high>1||!(low<mid&&mid<high)||win<0||win>1) throw new RangeError('Invalid win-rate anchors');
  const value=win>=mid?70+29*(win-mid)/(high-mid):40+30*(win-low)/(mid-low);
  return Math.round(Math.max(0,Math.min(99,value)));
}
const bounded=(x)=>Math.max(0,Math.min(1,x));
// Stratified independent seeds. Two seating orders form ONE observation; they
// must never be counted as two independent Bernoulli samples.
export function summarizeStrata(strata) {
  if (!strata.length || strata.some(s=>s.length<2||s.some(v=>!Number.isFinite(v)||v<0||v>1))) throw new RangeError('Need >=2 bounded samples in each stratum');
  const means=strata.map(s=>s.reduce((a,b)=>a+b,0)/s.length);
  const mean=means.reduce((a,b)=>a+b,0)/means.length;
  const variance=strata.reduce((v,s,i)=>v+s.reduce((a,x)=>a+(x-means[i])**2,0)/(s.length-1)/s.length,0)/strata.length**2;
  const se=Math.sqrt(variance),halfWidth95=1.96*se;
  const weightSquares=strata.reduce((v,s)=>v+1/s.length,0)/strata.length**2;
  const hoeffding=Math.sqrt(Math.log(40)*weightSquares/2);
  return {winRate:mean,standardError:se,halfWidth95,ci95:[bounded(mean-halfWidth95),bounded(mean+halfWidth95)],
    conservative95:[bounded(mean-hoeffding),bounded(mean+hoeffding)],
    independentPairs:strata.reduce((n,s)=>n+s.length,0),games:2*strata.reduce((n,s)=>n+s.length,0)};
}
export function measureStrength(lineups,opponents,{samples=32,seed=20260919,...rules}={}) {
  if (!Number.isSafeInteger(samples)||samples<2 || !Number.isSafeInteger(seed)) throw new RangeError('Invalid sampling plan');
  const strata=[],margins=[];
  for (let opponent=0;opponent<opponents.length;opponent++) for(let slot=0;slot<lineups.length;slot++) {
    const outcomes=[],net=[];
    for(let i=0;i<samples;i++) {
      // Disjoint seed IDs across strata; same seed plan across all candidates.
      const gameSeed=(seed+Math.imul(opponent*5+slot,1000003)+Math.imul(i,7919))>>>0;
      const options={mode:'fixed',possessions:30,fatigue:false,...rules,seed:gameSeed};
      const a=simulateGame(lineups[slot],opponents[opponent],options);
      const b=simulateGame(opponents[opponent],lineups[slot],options);
      outcomes.push(((a.scoreA>a.scoreB?1:a.scoreA===a.scoreB?.5:0)+(b.scoreB>b.scoreA?1:b.scoreA===b.scoreB?.5:0))/2);
      net.push((a.scoreA-a.scoreB+b.scoreB-b.scoreA)/2);
    }
    strata.push(outcomes);margins.push(net.reduce((a,b)=>a+b,0)/net.length);
  }
  return {...summarizeStrata(strata),meanMargin:margins.reduce((a,b)=>a+b,0)/margins.length,stratumWinRates:strata.map(s=>s.reduce((a,b)=>a+b,0)/s.length)};
}
export function rankTeams(rows) {
  const sorted=[...rows].sort((a,b)=>b.winRate-a.winRate||a.id-b.id);
  return sorted.map(r=>{
    const higher=rows.filter(p=>p.winRate>r.winRate).length;
    const equal=rows.filter(p=>p.winRate===r.winRate).length;
    const rank=1+higher+(equal-1)/2;
    return {...r,rank,pr:100*(rows.length-rank)/rows.length,
      rankInterval95:[1+rows.filter(p=>p.conservative95[0]>r.conservative95[1]).length,
        rows.length-rows.filter(p=>p.conservative95[1]<r.conservative95[0]).length]};
  });
}

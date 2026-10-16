import {simulateDefenseAGame} from './defense_a_game.js';
import {observedLineup} from './minute_budget.js';
import {NBA_DEFENSE_V1} from './defense_presets.js';
import {mean,variance,sd} from './statistical_summary.js';
export const VARIANCE_CONFIGS={baseline:{},noFatigue:{fatigue:false},noFoulOut:{foulOut:99},
  noEndgame:{endgameStrategies:false},noMinuteTargets:{minuteTargets:false},
  allFourOff:{fatigue:false,foulOut:99,endgameStrategies:false,minuteTargets:false},
  fixedFive:{fatigue:false,foulOut:99,endgameStrategies:false,minuteTargets:false,substitutions:false}};
export function varianceJob(inputs,job){
  if(!VARIANCE_CONFIGS[job.variant])throw new Error('Unknown variance intervention');
  // One actual NBA game roster, copied identically to both sides. Choose the
  // median team by observed net purely to define a representative diagnostic.
  const ordered=inputs.actual.slice().sort((a,b)=>(a.ppg-a.opponentPPG)-(b.ppg-b.opponentPPG));
  const id=ordered[15].id,team=inputs.league.teams.find(t=>t.id===id);
  const fixture=inputs.league.schedule.find(g=>g.homeId===id||g.awayId===id);
  const obs=inputs.exposure.games.find(g=>g.id===fixture.id).teams.find(t=>t.teamId===id);
  const pair=observedLineup(team,fixture[fixture.homeId===id?'homePlayerIds':'awayPlayerIds'],obs);
  const options={...NBA_DEFENSE_V1,stealPriorRate:inputs.priorRate,...VARIANCE_CONFIGS[job.variant]};
  const results=[],points=[[],[]],counts=[0,0],starter={leading20:{seconds:0,starterSeconds:0},close5:{seconds:0,starterSeconds:0}};
  for(let index=0;index<job.games;index++){
    const seed=(810013+Math.imul(index+1,7919))>>>0;
    const game=simulateDefenseAGame(pair,pair,{...options,seed,replay:true});
    let current=null,last=null;const regulation=[0,0];
    const endPoss=score=>{if(!current)return;const delta=(score[0]-current.score[0])-(score[1]-current.score[1]);
      points[current.off].push(delta);counts[current.off]++;};
    for(const event of game.events){
      if(event.type==='POSSESSION'){
        endPoss(event.score);current=event.period<=4?{off:event.off,score:event.score}:null;
      }
      if(event.type==='PERIOD_END'&&event.period===4){endPoss(event.score);current=null;regulation[0]=event.score[0];regulation[1]=event.score[1];}
      if(last&&event.period<=4){const dt=event.elapsed-last.elapsed;
        for(const side of [0,1]){const lead=last.score[side]-last.score[1-side];
          const bucket=lead>=20?starter.leading20:Math.abs(lead)<=5?starter.close5:null;
          if(bucket){bucket.seconds+=dt;bucket.starterSeconds+=dt*last.lineups[side].filter(i=>i<5).length;}
        }
      }
      last=event;
    }
    endPoss(game.events.at(-1).score);
    results.push({seed,margin:game.scoreA-game.scoreB,regulationMargin:regulation[0]-regulation[1],overtimes:game.overtimes,
      scoreA:game.scoreA,scoreB:game.scoreB,regulationPoss:game.events.filter(e=>e.type==='POSSESSION'&&e.period<=4).length});
  }
  const theoreticalVariance=counts.reduce((n,count,side)=>n+count/job.games*variance(points[side]),0);
  const finalSD=sd(results.map(r=>r.margin)),regulationSD=sd(results.map(r=>r.regulationMargin));
  return {variant:job.variant,team:pair.name,fixture:fixture.id,games:job.games,options,
    finalSD,regulationSD,theoreticalIndependentSD:Math.sqrt(theoreticalVariance),
    excessRegulationVariance:regulationSD**2-theoreticalVariance,
    theoreticalDefinition:'Observed per-possession signed point variance by attacking side, times mean regulation possession count. IID counterfactual; conditional on this roster and variant, not independent NBA evidence.',
    meanRegulationPoss:mean(results.map(r=>r.regulationPoss)),sd95Approx:[finalSD-1.96*finalSD/Math.sqrt(2*(job.games-1)),finalSD+1.96*finalSD/Math.sqrt(2*(job.games-1))],
    starterExposure:Object.fromEntries(Object.entries(starter).map(([key,b])=>[key,{...b,share:b.seconds?b.starterSeconds/(5*b.seconds):null}])),
    possessionMean:points.map(mean),possessionVariance:points.map(variance),results};
}

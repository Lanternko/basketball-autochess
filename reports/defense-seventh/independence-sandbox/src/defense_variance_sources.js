// Keep signed possession increments for margin IID theory, but use actual team
// scores for score variance/covariance (opposing technical FTs are real points).
import {varianceAnalysis as possessionAnalysis} from './defense_pbp_analysis.js';
import {mean,variance,sd} from './statistical_summary.js';
const covariance=(a,b)=>{const ma=mean(a),mb=mean(b);return mean(a.map((v,i)=>(v-ma)*(b[i]-mb)));};
export function varianceAnalysis(games){
  const base=possessionAnalysis(games),valid=games.filter(g=>g.pointsValid);
  const raw=valid.map(g=>{const N=[0,0],S=[0,0];for(const p of g.possessions.filter(p=>p.period<=4)){N[p.side]++;S[p.side]+=p.points;S[1-p.side]+=p.opponentPoints;}
    return {id:g.id,ids:g.ids,N,S:g.regulationScore??S,pointLedgerScore:S,q3:g.q3};});
  const ids=[...new Set(raw.flatMap(r=>r.ids))],teamMeans=new Map(),allowedMeans=new Map(),perTeam=[];
  for(const id of ids){const scores=raw.flatMap(r=>r.ids.flatMap((t,i)=>t===id?[r.S[i]]:[])),allowed=raw.flatMap(r=>r.ids.flatMap((t,i)=>t===id?[r.S[1-i]]:[]));teamMeans.set(id,mean(scores));allowedMeans.set(id,mean(allowed));perTeam.push({teamId:id,games:scores.length,mean:mean(scores),scoreVariance:variance(scores)});}
  const league=mean([...teamMeans.values()]);
  const records=raw.map(r=>({...r,teamOnly:r.S.map((s,i)=>s-teamMeans.get(r.ids[i])),Y:r.S.map((s,i)=>s-teamMeans.get(r.ids[i])-allowedMeans.get(r.ids[1-i])+league),q4:r.S[0]-r.S[1]-r.q3}));
  const a=records.map(r=>r.Y[0]),b=records.map(r=>r.Y[1]),n=records.map(r=>(r.N[0]+r.N[1])/2),vn=variance(n),ba=covariance(a,n)/vn,bb=covariance(b,n)/vn;
  const cov=covariance(a,b),paceCov=ba*bb*vn,scoreVar=(variance(a)+variance(b))/2;
  const ia=(ba**2+bb**2)*vn,total=variance(a.map((s,i)=>s-b[i])),q3=records.map(r=>r.q3),q4=records.map(r=>r.q4);
  return {...base,perTeam,withinTeamScoreVariance:perTeam.reduce((s,t)=>s+t.games*t.scoreVariance,0)/perTeam.reduce((s,t)=>s+t.games,0),
    sideCenteredWithinTeamScoreVariance:(variance(records.map(r=>r.teamOnly[0]))+variance(records.map(r=>r.teamOnly[1])))/2,
    withinTeamScoreCovariance:covariance(records.map(r=>r.teamOnly[0]),records.map(r=>r.teamOnly[1])),strengthAdjustedScoreVariance:scoreVar,scoreCovariance:cov,paceCovariance:paceCov,remainingCovariance:cov-paceCov,paceBetas:[ba,bb],marginResidualSD:Math.sqrt(total),
    decomposition:{iidVariance:base.decomposition.iidVariance,individualPaceVariance:ia,paceCovarianceReduction:-2*paceCov,remainingCovarianceReduction:-2*(cov-paceCov),withinTeamSerialAndHeterogeneityVariance:scoreVar*2-ia-base.decomposition.iidVariance,total},
    q3Q4Correlation:covariance(q3,q4)/(sd(q3)*sd(q4)),scoreLedgerDifferences:records.filter(r=>r.S.some((s,i)=>s!==r.pointLedgerScore[i])).map(r=>({id:r.id,score:r.S,ledger:r.pointLedgerScore})),records};
}

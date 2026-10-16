import {terminalDefenseProbabilities as previousTerminal,exposureDefenseProbabilities} from '../player-impact-v47/model.mjs';
export {exposureDefenseProbabilities};
export function offensiveMakePlan(p,handler,offense,putback){
 const m=handler.offensiveLineupMeasurement;
 if(!m||putback)return p;
 if(!p.finePlan||!Array.isArray(offense)||offense.length!==5||new Set(offense.map(p=>p.playerId)).size!==5||!offense.some(p=>p.playerId===handler.playerId)||offense.some(p=>!p.offensiveLineupMeasurement))throw Error('Missing five-player offensive lineup');
 const makeEta={...p.finePlan.makeEta};
 for(const z of ['ra','paint','mid'])makeEta[z]+=m.shooterDelta[z]+offense.filter(p=>p.playerId!==handler.playerId).reduce((s,p)=>s+p.offensiveLineupMeasurement.teammateLogits[z],0);
 return {...p,finePlan:{...p.finePlan,makeEta}};
}
export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){return offensiveMakePlan(previousTerminal(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt),handler,opts.offensiveLineup,opts.putback);}

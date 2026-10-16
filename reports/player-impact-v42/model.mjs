import {terminalDefenseProbabilities as previousTerminal,exposureDefenseProbabilities as previousExposure} from '../player-impact-v41/model.mjs';
import {recordedZoneChoice,applyRecordedZone} from './choice-model.mjs';
export function terminalDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt){
 const q=previousTerminal(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup,opt);
 if(opts.putback)return q;
 return {...q,defensiveZone:recordedZoneChoice(handler,lineup)};
}
export function exposureDefenseProbabilities(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup){
 const q=previousExposure(handler,ctx,defender,help,oreb,dreb,phys,opts,lineup);
 return opts.putback?q:applyRecordedZone(q,recordedZoneChoice(handler,lineup));
}

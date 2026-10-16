import fs from 'node:fs';
import {reliabilityAdjustedContribution} from '../../src/player_reliability.js';
const root='reports/player-impact-v29',read=f=>JSON.parse(fs.readFileSync(root+'/'+f)),summary=read('pilot-summary.json'),source=read('workload-source.json');
const players=summary.players.map(p=>{
 const healthy=p.arms.find(a=>a.arm==='supportedHealthy'),history=Object.values(source.players[p.playerId].history);
 return {playerId:p.playerId,name:p.name,position:p.position,healthyLoadMinutes:healthy.minutes,healthyPairedMargin:healthy.pairedMargin,
  reliabilitySensitivity:[0,.05,.10].map(coefficient=>({coefficient,...reliabilityAdjustedContribution(healthy.pairedMargin.mean,history,coefficient)}))};
});
const result={design:'Selected prototype policy: measure healthy contribution at supported source workload, then discount only positive matched-baseline contribution by at most 10% using the second-highest adequately covered season of explicit injury/illness listed-game rates. One isolated injury season gives zero deduction; negative contribution receives no absence bonus. Do not change per-game rotation for reliability. Coefficients 0/0.05/0.10 are uncalibrated preference sensitivity, not medical predictions or a final OVR. Original recurrent-minute arms retained as diagnostics only, not the selected policy.',players};
fs.writeFileSync(root+'/reliability-policy.json',JSON.stringify(result,null,2));
console.log(JSON.stringify({players:players.length,policy:'discount-positive-contribution-only'}));

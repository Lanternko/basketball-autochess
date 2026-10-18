import {read} from '../scripts/defense_io.js';
// Pure common-league switch. No player/team key, observed future count or score.
export function forecastClockOptions(enabled,cutoff=0){
 if(!enabled||!cutoff)return {};
 return {forecastClock:true,...read('reports/defense-fifth/clock-calibration-pre'+cutoff+'.json').selected};
}
export function fifthFinalOptions(cutoff=0){
 const s=read('reports/defense-fifth/selection.json');
 return forecastClockOptions(s.valid.includes('clock-41'),cutoff);
}

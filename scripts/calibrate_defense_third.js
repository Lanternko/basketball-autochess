import fs from 'node:fs';
import {runThirdJobs} from '../src/defense_third_pool.js';
import {globalDefenseMetrics} from '../src/defense_third_season.js';
const history=[];let selected={pace:.836,foulScale:1,passTurnoverScale:1.65,touchTurnoverScale:1.25,touchLiveShare:.4};
for(let round=0;round<4;round++){
  const run=(await runThirdJobs([{preset:'combined',seed:731019,options:selected}]))[0],m=globalDefenseMetrics(run);
  const sums=k=>run.teams.reduce((n,t)=>n+t.stats[k],0)/2460;
  const r={round,options:{...selected},metrics:m,pass:sums('passSteals'),touch:sums('touchSteals'),deadNoClock:m.deadTurnovers-m.clockTurnovers};history.push(r);console.log(JSON.stringify(r));
  // Fit only measured event class counts and box possession count, never team strength/wins.
  const passScale=selected.passTurnoverScale*5.1365118174/r.pass;
  const touchLive=3.2799511002,dead=5.4189079055;
  selected={...selected,pace:selected.pace*102.5544390244/m.possessionsProxy,
    passTurnoverScale:passScale,touchTurnoverScale:selected.touchTurnoverScale*(touchLive+dead)/(r.touch+r.deadNoClock),
    touchLiveShare:Math.min(.95,selected.touchLiveShare*(touchLive/(touchLive+dead))/(r.touch/(r.touch+r.deadNoClock))),
    clockViolationProbability:run.options.clockViolationProbability*.673594132/m.clockTurnovers};
  fs.writeFileSync('reports/defense-third/calibration.json',JSON.stringify({seed:731019,scope:'Full 1230 fixtures. Fits observed category counts and box possessions only; no wins/team ID/OVR, no shooting-accuracy tuning.',selected,history},null,2)+'\n');
}

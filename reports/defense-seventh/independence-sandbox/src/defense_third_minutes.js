import {observedLineup} from './minute_budget.js';
export function thirdLineup(team,active,exposure,season=false){
  const result=observedLineup(team,active,exposure);if(!season)return result;
  const weights=result.roster.map(p=>Math.max(0,p.seasonMinutesPerGame??0));
  const targets=weights.map(()=>0);let remaining=240,free=weights.map((_,i)=>i);
  while(free.length){const sum=free.reduce((n,i)=>n+weights[i],0),scale=remaining/(sum||free.length);
    const capped=free.filter(i=>(sum?weights[i]:1)*scale>48);
    if(!capped.length){for(const i of free)targets[i]=(sum?weights[i]:1)*scale;break;}
    for(const i of capped){targets[i]=48;remaining-=48;}free=free.filter(i=>!capped.includes(i));
  }
  return {...result,roster:result.roster.map((p,i)=>({...p,targetMinutes:targets[i]}))};
}

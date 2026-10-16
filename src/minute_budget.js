const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};

// Decompose a feasible minute budget into five simultaneous players using
// McNaughton's preemptive scheduling construction. This is an exposure control,
// not a reconstruction of coaching substitutions or observed lineup stints.
export function minuteBudgetSchedule(roster, seconds=2880) {
  assert(Number.isFinite(seconds)&&seconds>0,'Invalid schedule duration');
  const targets=roster.map(p=>p.targetMinutes*60);
  assert(targets.length>=5&&targets.every(n=>Number.isFinite(n)&&n>=0&&n<=seconds+1e-7),'Invalid minute targets');
  assert(Math.abs(targets.reduce((a,b)=>a+b,0)-5*seconds)<1e-5,'Minute targets must total five-player time');
  const starterWindow=Math.max(0,Math.min(15,...targets.slice(0,5),seconds-Math.max(0,...targets.slice(5))));
  const remaining=targets.map((n,i)=>n-(i<5?starterWindow:0));
  const width=seconds-starterWindow,slots=Array.from({length:5},()=>[]);
  if(starterWindow>0)slots.forEach((s,i)=>s.push({start:0,end:starterWindow,player:i}));
  let slot=0,time=0;
  remaining.forEach((n,player)=>{
    while(n>1e-7){
      const take=Math.min(n,width-time);
      if(take>1e-7)slots[slot].push({start:starterWindow+time,end:starterWindow+time+take,player});
      time+=take;n-=take;
      if(time>=width-1e-7){slot++;time=0;}
    }
  });
  const boundaries=[...new Set([0,seconds,...slots.flatMap(s=>s.flatMap(p=>[p.start,p.end]))])].sort((a,b)=>a-b);
  const stints=[];
  for(let i=0;i<boundaries.length-1;i++){
    const start=boundaries[i],end=boundaries[i+1];if(end-start<1e-7)continue;
    const mid=(start+end)/2,lineup=slots.map(s=>s.find(p=>mid>=p.start&&mid<p.end)?.player);
    assert(lineup.every(Number.isInteger)&&new Set(lineup).size===5,'Infeasible minute decomposition');
    stints.push({start,end,lineup});
  }
  return stints;
}

export function observedLineup(team, playerIds, exposure) {
  const appeared=new Set(playerIds), measured=new Map(exposure.players.map(p=>[p.playerId,p]));
  const roster=team.roster.filter(p=>appeared.has(p.playerId)).map(p=>({...p,observedGameSeconds:measured.get(p.playerId)?.seconds,
    officialStarter:measured.get(p.playerId)?.starter,officialPosition:measured.get(p.playerId)?.position}));
  assert(roster.length===appeared.size&&roster.every(p=>Number.isFinite(p.observedGameSeconds)),'Missing game exposure');
  const starters=roster.filter(p=>p.officialStarter),bench=roster.filter(p=>!p.officialStarter);
  assert(starters.length===5,'Need five observed starters');
  const order={PG:0,SG:1,G:1,SF:2,PF:3,F:3,C:4};
  starters.sort((a,b)=>order[a.officialPosition]-order[b.officialPosition]||a.heightInches-b.heightInches||a.playerId-b.playerId);
  starters.forEach(p=>{p.pos=p.courtPosition=p.officialPosition;});
  bench.forEach(p=>{if(Object.hasOwn(order,p.officialPosition))p.pos=p.courtPosition=p.officialPosition;});
  bench.sort((a,b)=>b.observedGameSeconds-a.observedGameSeconds||a.playerId-b.playerId);
  const players=[...starters,...bench];
  let lo=0,hi=2880/Math.min(...players.filter(p=>p.observedGameSeconds>0).map(p=>p.observedGameSeconds));
  for(let i=0;i<80;i++){
    const scale=(lo+hi)/2;
    if(players.reduce((n,p)=>n+Math.min(2880,p.observedGameSeconds*scale),0)<14400)lo=scale;else hi=scale;
  }
  // Allocate integer tenths of a second so the simulation clock can meet targets.
  const ticks=players.map(p=>Math.min(28800,p.observedGameSeconds*(lo+hi)/2*10));
  const floor=ticks.map(Math.floor),rank=ticks.map((n,i)=>({i,fraction:n-floor[i]})).sort((a,b)=>b.fraction-a.fraction||a.i-b.i);
  let missing=144000-floor.reduce((a,b)=>a+b,0);
  for(const {i} of rank)if(missing>0&&floor[i]<28800){floor[i]++;missing--;}
  assert(missing===0,'Cannot quantize minute targets');
  players.forEach((p,i)=>{p.targetMinutes=floor[i]/600;});
  return {...team,roster:players};
}

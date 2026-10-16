export function rotationCollector(){
 const games=new Map();let intervals=0;
 const person=(t,id)=>t.players[id]??={seconds:0,phase:Array(24).fill(0),stints:[]};
 return {interval(e){
  if(!(e.seconds>0))return;intervals++;let game=games.get(e.gameId);if(!game){game={id:e.gameId,teams:{}};games.set(e.gameId,game);}
  for(const side of e.teams){let t=game.teams[side.teamId];if(!t)t=game.teams[side.teamId]={teamId:side.teamId,players:{},pairs:{},lastLineup:[],lastStart:{},end:0};
   if(new Set(side.lineup).size!==5||side.lineup.some(id=>!side.active.includes(id)))throw Error('Illegal five-player lineup');
   const ticks=Math.round(e.seconds*10);t.end=Math.round((e.start+e.seconds)*10);
   for(const id of t.lastLineup)if(!side.lineup.includes(id)){person(t,id).stints.push(Math.round(e.start*10)-t.lastStart[id]);delete t.lastStart[id];}
   for(const id of side.lineup){const p=person(t,id);if(!t.lastLineup.includes(id))t.lastStart[id]=Math.round(e.start*10);p.seconds+=ticks;
    if(e.period<=4)for(let b=Math.max(0,Math.floor(e.start/120));b<Math.min(24,Math.ceil((e.start+e.seconds)/120));b++)p.phase[b]+=Math.round(10*Math.max(0,Math.min(e.start+e.seconds,(b+1)*120)-Math.max(e.start,b*120)));
   }
   if(e.period<=4)for(let a=0;a<5;a++)for(let b=a+1;b<5;b++){const x=side.lineup[a],y=side.lineup[b],key=x<y?x+'/'+y:y+'/'+x;t.pairs[key]=(t.pairs[key]??0)+ticks;}
   t.lastLineup=side.lineup;
  }
 },finish(teams){
  const totals=new Map();
  for(const game of games.values())for(const t of Object.values(game.teams)){
   for(const id of t.lastLineup)person(t,id).stints.push(t.end-t.lastStart[id]);
   if(Math.abs(Object.values(t.players).reduce((s,p)=>s+p.seconds,0)-5*t.end)>1)throw Error('Rotation time accounting');
   for(const[id,p]of Object.entries(t.players))totals.set(t.teamId+'/'+id,(totals.get(t.teamId+'/'+id)??0)+p.seconds);
   delete t.lastLineup;delete t.lastStart;
  }
  for(const t of teams)for(const p of t.players)if(Math.abs((totals.get(t.id+'/'+p.playerId)??0)-10*p.stats.seconds)>.1)throw Error('Rotation/player seconds mismatch');
  return {intervals,ticksPerSecond:10,games:[...games.values()]};
 }};
}

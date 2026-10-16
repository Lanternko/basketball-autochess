const keys=['fga','fgm','longA','longM','midA','midM','shortA','shortM'];
const blank=()=>Object.fromEntries(keys.map(k=>[k,0]));
export function defenseCollector(){
 const players=new Map();let game=null,games=0,total=blank();
 const person=id=>{if(!players.has(id))players.set(id,{playerId:id,on:blank(),off:blank(),onSeconds:0,offSeconds:0});return players.get(id);};
 return {event(e){
  game??=e.teams.map(()=>({counts:blank(),on:new Map()}));
  if(e.type==='GAME_END'){
   for(let side=0;side<2;side++)for(const id of e.teams[side].active){const p=person(id),on=game[side].on.get(id)??blank();for(const k of keys){p.on[k]+=on[k];p.off[k]+=game[side].counts[k]-on[k];}p.offSeconds+=e.elapsed;}
   game=null;games++;return;
  }
  if(!['FGM','FGX'].includes(e.type))return;
  const side=1-e.side,c=blank();c.fga=1;c.fgm=Number(e.type==='FGM');c[e.zone+'A']=1;c[e.zone+'M']=c.fgm;
  for(const k of keys){game[side].counts[k]+=c[k];total[k]+=c[k];}
  if(e.teams[side].lineup.length!==5)throw Error('Defense observer needs five players');
  for(const id of e.teams[side].lineup){const on=game[side].on.get(id)??blank();for(const k of keys)on[k]+=c[k];game[side].on.set(id,on);}
 },finish(teams){
  if(game)throw Error('Unclosed defense observer game');
  for(const t of teams)for(const p of t.players){const r=person(p.playerId);r.onSeconds+=p.stats.seconds;r.offSeconds-=p.stats.seconds;}
  for(const k of keys)if([...players.values()].reduce((s,p)=>s+p.on[k],0)!==5*total[k])throw Error('Defense observer five-player conservation '+k);
  if(total.fga!==teams.reduce((s,t)=>s+t.stats.fga,0)||total.fgm!==teams.reduce((s,t)=>s+t.stats.fgm,0))throw Error('Defense observer team ledger');
  return {games,total,players:[...players.values()]};
 }};
}

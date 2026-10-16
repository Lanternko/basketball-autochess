const KEYS=['fga','fgm','fg3a','fg3m','opp_fga','opp_fgm','opp_fg3a','opp_fg3m'];
const blank=()=>Object.fromEntries(KEYS.map(k=>[k,0]));
export function onCourtCollector(){
 const sums=new Map();let game=null,games=0;
 const person=id=>{if(!sums.has(id))sums.set(id,{playerId:id,on:blank(),sameGame:blank(),own:{fga:0,fgm:0,fg3a:0,fg3m:0}});return sums.get(id);};
 return {event(e){
  game??=e.teams.map(t=>({id:t.teamId,stats:blank()}));
  if(e.type==='GAME_END'){
   for(let i=0;i<2;i++)for(const id of e.teams[i].active){const p=person(id);for(const k of KEYS)p.sameGame[k]+=game[i].stats[k];}
   game=null;games++;return;
  }
  const c={fga:1,fgm:Number(e.type==='FGM'),fg3a:Number(e.zone==='long'),fg3m:Number(e.type==='FGM'&&e.zone==='long')};
  for(let i=0;i<2;i++){
   const prefix=i===e.side?'':'opp_';
   for(const [k,v]of Object.entries(c))game[i].stats[prefix+k]+=v;
   if(e.teams[i].lineup.length!==5)throw Error('On-court observer requires five players');
   for(const id of e.teams[i].lineup){const p=person(id);for(const [k,v]of Object.entries(c))p.on[prefix+k]+=v;}
  }
  const p=person(e.playerId);for(const [k,v]of Object.entries(c))p.own[k]+=v;
 },finish(){
  if(game)throw Error('Unclosed on-court game');
  return {games,players:[...sums.values()].map(p=>({...p,off:Object.fromEntries(KEYS.map(k=>[k,p.sameGame[k]-p.on[k]])),teammates:Object.fromEntries(['fga','fgm','fg3a','fg3m'].map(k=>[k,p.on[k]-p.own[k]]))}))};
 }};
}

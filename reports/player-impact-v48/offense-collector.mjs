import {fineZones,coarseOf} from '../player-impact-v45/model.mjs';
const keys=['fga','fgm',...fineZones.flatMap(z=>[z+'A',z+'M'])],blank=()=>Object.fromEntries(keys.map(k=>[k,0]));
export function offenseCollector(seed){
 const players=new Map();let game=null,games=0,total=blank(),state=seed>>>0;
 const random=()=>{state=(state+0x6D2B79F5)>>>0;let t=state;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
 const person=id=>{if(!players.has(id))players.set(id,{playerId:id,on:blank(),off:blank(),own:blank(),byShooter:{},onSeconds:0,offSeconds:0});return players.get(id);};
 return {event(e){
  game??=e.teams.map(()=>({counts:blank(),on:new Map()}));
  if(e.type==='GAME_END'){
   for(let side=0;side<2;side++)for(const id of e.teams[side].active){const p=person(id),on=game[side].on.get(id)??blank();for(const k of keys){p.on[k]+=on[k];p.off[k]+=game[side].counts[k]-on[k];}p.offSeconds+=e.elapsed;}
   game=null;games++;return;
  }
  if(!['FGM','FGX'].includes(e.type)||e.putback)return;
  const plan=e.finePlan;if(!plan)throw Error('Missing fine source plan');const made=e.type==='FGM',zs=fineZones.filter(z=>coarseOf[z]===e.zone),weights=zs.map(z=>plan.zone[z]*(made?plan.make[z]:1-plan.make[z])),den=weights.reduce((s,x)=>s+x,0);if(!(den>0))throw Error('No fine posterior support');let draw=random()*den,i=0;while(i<weights.length-1&&draw>=weights[i])draw-=weights[i++];
  const z=zs[i],c=blank();c.fga=1;c.fgm=Number(made);c[z+'A']=1;c[z+'M']=Number(made);const side=e.side;if(!e.teams[side].lineup.includes(e.playerId))throw Error('Shooter must be on court');
  for(const k of keys){total[k]+=c[k];game[side].counts[k]+=c[k];person(e.playerId).own[k]+=c[k];}
  for(const pid of e.teams[side].lineup){const on=game[side].on.get(pid)??blank();for(const k of keys)on[k]+=c[k];game[side].on.set(pid,on);}
  for(const pid of e.teams[side].active){const arm=e.teams[side].lineup.includes(pid)?'on':'off',p=person(pid),s=p.byShooter[e.playerId]??={on:blank(),off:blank()};for(const k of keys)s[arm][k]+=c[k];}
 },finish(teams){
  if(game)throw Error('Unclosed game');for(const t of teams)for(const p of t.players){const r=person(p.playerId);r.onSeconds+=p.stats.seconds;r.offSeconds-=p.stats.seconds;}
  for(const k of keys){if([...players.values()].reduce((s,p)=>s+p.on[k],0)!==5*total[k])throw Error('Five-player on ledger');if([...players.values()].reduce((s,p)=>s+p.own[k],0)!==total[k])throw Error('Own shot ledger');for(const p of players.values())for(const arm of ['on','off'])if(Object.values(p.byShooter).reduce((s,r)=>s+r[arm][k],0)!==p[arm][k])throw Error('By-shooter ledger');}
  return {games,freshOnly:true,total,players:[...players.values()].map(p=>({...p,teammates:Object.fromEntries(keys.map(k=>[k,p.on[k]-p.own[k]]))}))};
 }};
}

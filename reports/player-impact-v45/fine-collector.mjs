import {fineZones,coarseOf} from './model.mjs';
const keys=['fga','fgm',...fineZones.flatMap(z=>[z+'A',z+'M'])];
const blank=()=>Object.fromEntries(keys.map(k=>[k,0]));
export function fineCollector(seed){
 const players=new Map();let game=null,games=0,total=blank(),rngState=seed>>>0;
 // Independent observation RNG: fine labels never perturb game outcomes.
 const random=()=>{rngState=(rngState+0x6D2B79F5)>>>0;let t=rngState;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
 const person=id=>{if(!players.has(id))players.set(id,{playerId:id,on:blank(),off:blank(),onSeconds:0,offSeconds:0});return players.get(id);};
 return {event(e){
  game??=e.teams.map(()=>({counts:blank(),on:new Map()}));
  if(e.type==='GAME_END'){
   for(let side=0;side<2;side++)for(const id of e.teams[side].active){const p=person(id),on=game[side].on.get(id)??blank();for(const k of keys){p.on[k]+=on[k];p.off[k]+=game[side].counts[k]-on[k];}p.offSeconds+=e.elapsed;}
   game=null;games++;return;
  }
  if(!['FGM','FGX'].includes(e.type)||e.putback)return;
  const plan=e.finePlan;if(!plan)throw Error('Missing fresh fine probability plan');
  const made=e.type==='FGM',candidates=fineZones.filter(z=>coarseOf[z]===e.zone),weights=candidates.map(z=>plan.zone[z]*(made?plan.make[z]:1-plan.make[z])),den=weights.reduce((s,x)=>s+x,0);
  if(!(den>0))throw Error('No fine posterior support');let draw=random()*den,index=0;while(index<weights.length-1&&draw>=weights[index])draw-=weights[index++];
  const zone=candidates[index],side=1-e.side,c=blank();c.fga=1;c.fgm=Number(made);c[zone+'A']=1;c[zone+'M']=Number(made);
  for(const k of keys){game[side].counts[k]+=c[k];total[k]+=c[k];}
  for(const id of e.teams[side].lineup){const on=game[side].on.get(id)??blank();for(const k of keys)on[k]+=c[k];game[side].on.set(id,on);}
 },finish(teams){
  if(game)throw Error('Unclosed fine game');for(const t of teams)for(const p of t.players){const r=person(p.playerId);r.onSeconds+=p.stats.seconds;r.offSeconds-=p.stats.seconds;}
  for(const k of keys)if([...players.values()].reduce((s,p)=>s+p.on[k],0)!==5*total[k])throw Error('Fine five-player ledger '+k);
  if(total.fga!==fineZones.reduce((s,z)=>s+total[z+'A'],0)||total.fgm!==fineZones.reduce((s,z)=>s+total[z+'M'],0))throw Error('Fine zone count ledger');
  return {games,total,players:[...players.values()],freshOnly:true,labelMethod:'Sample fine zone conditional on coarse zone and made/miss from the modeled joint probability, with independent observer RNG. Fine label does not separately drive rebound/foul geometry.'};
 }};
}

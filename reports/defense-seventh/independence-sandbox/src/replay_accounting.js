// Read-only event accounting: no new random draws or changes to the engine.
export function replayAccounting(game, teams) {
  if (!game.events?.length||!game.complete) throw new Error('Need a complete replay');
  const blank=()=>({seconds:0,pointsFor:0,pointsAgainst:0,plusMinus:0});
  const players=teams.map(t=>t.roster.map(blank));
  const buckets=teams.map(()=>Object.fromEntries(Array.from({length:6},(_,i)=>[i,blank()])));
  const shai=teams.map(()=>({on:blank(),off:blank()}));
  let previous=null, score=[0,0];
  const bucket=(lineup)=>lineup.filter(i=>i>=5).length;
  for (const event of game.events) {
    if (!event.lineups?.every((lineup,side)=>lineup.length===5&&new Set(lineup).size===5&&lineup.every(i=>Number.isInteger(i)&&i>=0&&i<players[side].length))) throw new Error('Invalid replay lineup');
    if (previous) {
      const dt=event.elapsed-previous.elapsed;
      if (dt<0) throw new Error('Non-monotonic replay clock');
      for (const side of [0,1]) {
        const lineup=previous.lineups[side];
        for (const i of lineup) players[side][i].seconds+=dt;
        buckets[side][bucket(lineup)].seconds+=dt;
        const key=lineup.some(i=>teams[side].roster[i].playerId===1628983)?'on':'off';
        shai[side][key].seconds+=dt;
      }
    }
    const changes=event.score.map((points,side)=>points-score[side]);
    if (changes.some(n=>n<0)) throw new Error('Non-monotonic replay score');
    for (const side of [0,1]) {
      const pf=changes[side],pa=changes[1-side],lineup=event.lineups[side];
      const key=lineup.some(i=>teams[side].roster[i].playerId===1628983)?'on':'off';
      for (const row of [...lineup.map(i=>players[side][i]),buckets[side][bucket(lineup)],shai[side][key]]) {
        row.pointsFor+=pf;row.pointsAgainst+=pa;row.plusMinus+=pf-pa;
      }
    }
    score=[...event.score];previous=event;
  }
  if (score[0]!==game.scoreA||score[1]!==game.scoreB) throw new Error('Replay final score mismatch');
  for (const side of [0,1]) {
    const margin=score[side]-score[1-side],reported=game[side===0?'playersA':'playersB'];
    if (players[side].reduce((n,p)=>n+p.plusMinus,0)!==5*margin) throw new Error('Plus-minus conservation failed');
    players[side].forEach((p,i)=>{if(Math.abs(p.seconds-reported[i].seconds)>.11)throw new Error('Replay minutes mismatch');});
    if (Math.abs(Object.values(buckets[side]).reduce((n,b)=>n+b.seconds,0)-game.gameSeconds)>.11) throw new Error('Stint duration mismatch');
    if (Object.values(buckets[side]).reduce((n,b)=>n+b.plusMinus,0)!==margin) throw new Error('Stint margin mismatch');
  }
  return {players,buckets,shai};
}

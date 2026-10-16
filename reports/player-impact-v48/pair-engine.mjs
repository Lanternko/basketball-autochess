import fs from 'node:fs';
// Observation-only callback at exactly the interval credited to player seconds.
export async function impactEngine(version,options={}){
 let s=fs.readFileSync('reports/player-impact-v47/engine.mjs','utf8');
 const modAnchor="\n const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));";
 const gameAnchor=" const anchor='  const gu=encode(g),s=';";
 const dt='    clock-=dt; shotClock=Math.max(0,shotClock-dt); elapsed+=dt;';
 const observed=dt+"\n    opt.pairMinuteObserver?.({seconds:dt/10,teams:sides.map(s=>({lineup:s.lineup.map(i=>s.roster[i].playerId),active:s.roster.filter(p=>!p.injured&&(p.targetMinutes??1)>0).map(p=>p.playerId)}))});";
 const finalPatch=`replace(${JSON.stringify(dt)},${JSON.stringify(observed)});\n`;
 const in45=`{const a=${JSON.stringify(gameAnchor)};if(s.split(a).length!==2)throw Error('Pair game anchor');s=s.replace(a,${JSON.stringify(finalPatch)}+a);}\n`;
 const in47=`{const a=${JSON.stringify(modAnchor)};if(s.split(a).length!==2)throw Error('Pair v45 anchor');s=s.replace(a,${JSON.stringify(in45)}+a);}\n`;
 if(s.split(modAnchor).length!==2)throw Error('Pair v47 anchor');s=s.replace(modAnchor,in47+modAnchor);
 return (await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'))).impactEngine(version,options);
}

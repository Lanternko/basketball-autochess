import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const url=f=>pathToFileURL(path.resolve(f)).href,cache=new Map();
export async function impactEngine(version,options={}){
 const key=JSON.stringify([version,options]);if(cache.has(key))return cache.get(key);
 let s=fs.readFileSync('reports/player-impact-v47/engine.mjs','utf8');
 const modAnchor="\n const mod=await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));",gameAnchor=" const anchor='  const gu=encode(g),s=';";
 const changes=[
  ['const rotate = (forced=false, protectedPlayer=null, protectedSide=-1) => {','const rotate = (forced=false, protectedPlayer=null, protectedSide=-1) => {\n    if(measuredRotate({sides,period,clock,elapsed,opt,protectedPlayer,protectedSide,emit}))return;'],
  ['    clock-=dt; shotClock=Math.max(0,shotClock-dt); elapsed+=dt;','    clock-=dt; shotClock=Math.max(0,shotClock-dt); elapsed+=dt;\n    observeRotationInterval(sides,dt/10,opt);\n    opt.rotationIntervalObserver?.({seconds:dt/10,start:elapsed/10-dt/10,period,gameId:opt.rotationGameId,teams:sides.map(s=>({teamId:s.rotationTeamId,lineup:s.lineup.map(i=>s.roster[i].playerId),active:s.roster.filter(p=>!p.injured&&(p.targetMinutes??1)>0).map(p=>p.playerId)}))});'],
  ['return { roster:t.roster, lineup:eligible.slice(0,5),','return { rotationTeamId:t.id,roster:t.roster, lineup:eligible.slice(0,5),'],
 ];
 const gameImport=`g=${JSON.stringify(`import {measuredRotate,observeRotationInterval} from '${url('src/measured_rotation.js')}';\n`)}+g;`;
 const patch=changes.map(([a,b])=>`replace(${JSON.stringify(a)},${JSON.stringify(b)});`).join('\n')+`\npatches.push(${JSON.stringify(gameImport)});\n`;
 const in45=`{const a=${JSON.stringify(gameAnchor)};if(s.split(a).length!==2)throw Error('Rotation game anchor');s=s.replace(a,${JSON.stringify(patch)}+a);const from="url('reports/player-impact-team-clock/season-source.mjs')";if(s.split(from).length!==2)throw Error('Rotation season import');s=s.replace(from,"url('reports/player-impact-v49/season-source.mjs')");}\n`;
 const in47=`{const a=${JSON.stringify(modAnchor)};if(s.split(a).length!==2)throw Error('Rotation v45 anchor');s=s.replace(a,${JSON.stringify(in45)}+a);}\n`;
 if(s.split(modAnchor).length!==2)throw Error('Rotation v47 anchor');s=s.replace(modAnchor,in47+modAnchor);
 const run=await(await import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'))).impactEngine(version,options);cache.set(key,run);return run;
}

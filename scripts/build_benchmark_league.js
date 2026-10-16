import fs from 'node:fs';
import crypto from 'node:crypto';
import * as C from '../src/constants.js';
const root = new URL('../data/benchmark-source/',import.meta.url);
const sources = [];
function read(name) {
  const bytes = fs.readFileSync(new URL(name+'.json',root));
  const doc = JSON.parse(bytes);
  if (doc.season !== '2025-26') throw new Error('Mixed source seasons');
  sources.push({file:`benchmark-source/${name}.json`,url:doc.url,fetchedAt:doc.fetchedAt,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
  const set = Array.isArray(doc.data.resultSets) ? doc.data.resultSets[0] : doc.data.resultSets;
  if (name==='shots') return set.rowSet.map(r=>({PLAYER_ID:r[0],shortM:r[6]+r[9],shortA:r[7]+r[10],midM:r[12],midA:r[13]}));
  return set.rowSet.map(r=>Object.fromEntries(set.headers.map((h,i)=>[h,r[i]])));
}
const teamRows=read('teams'), base=read('base');
const maps=Object.fromEntries(['advanced','bio','shots','defense-long','defense-rim'].map(k=>[k,new Map(read(k).map(r=>[r.PLAYER_ID??r.CLOSE_DEF_PERSON_ID,r]))]));
const pool=base.filter(r=>r.GP>=30&&r.MIN/r.GP>=20);
const percentile=(x,values)=>100*(values.filter(v=>v<x).length+.5*values.filter(v=>v===x).length)/values.length;
const attr=p=>Math.max(40,Math.min(99,p<50?40+(p-1)*30/49:70+(p-50)*29/49));
const rank=(r,f)=>attr(percentile(f(r),pool.map(f)));
const safe=(a,b)=>b>0?a/b:0;
function inverse(p,curve) {
  for (let i=1;i<curve.length;i++) {
    const [x0,y0]=curve[i-1], [x1,y1]=curve[i];
    if (p>=Math.min(y0,y1)&&p<=Math.max(y0,y1)) return Math.max(40,Math.min(99,x0+(p-y0)/(y1-y0)*(x1-x0)));
  }
  return Math.abs(p-curve[0][1])<Math.abs(p-curve.at(-1)[1])?40:99;
}
const shrink=(m,a,mean,prior=100)=>(m+mean*prior)/(a+prior);
function card(row,slot) {
  const id=row.PLAYER_ID, b=base.find(p=>p.PLAYER_ID===id);
  const a=maps.advanced.get(id), bio=maps.bio.get(id), shot=maps.shots.get(id);
  if (!b||!a||!bio||!shot) throw new Error(`Missing source ${id}`);
  const def=(kind,curve)=>{
    const d=maps[kind].get(id);
    if (!d) throw new Error(`Missing tracking ${id}/${kind}`);
    return inverse(d.PCT_PLUSMINUS*d.D_FGA/(d.D_FGA+200),curve);
  };
  const p={name:row.PLAYER_NAME,playerId:id,pos:['PG','SG','SF','PF','C'][slot],courtPosition:['PG','SG','SF','PF','C'][slot],
    long:inverse(shrink(b.FG3M,b.FG3A,.3639),C.CURVE_3PT),
    mid:inverse(shrink(shot.midM,shot.midA,.4216),C.CURVE_MID),
    short:inverse(shrink(shot.shortM,shot.shortA,.5782),C.CURVE_SHORT),
    ft:inverse(shrink(b.FTM,b.FTA,.78),C.CURVE_FT),
    drive:rank(b,r=>safe(r.FTA,r.FGA)),
    tovSkill:rank(b,r=>-safe(r.TOV,r.FGA+.44*r.FTA+r.AST+r.TOV)),
    pass:rank(b,r=>maps.advanced.get(r.PLAYER_ID).AST_PCT),
    rebound:rank(b,r=>maps.advanced.get(r.PLAYER_ID).REB_PCT),
    stamina:rank(b,r=>r.MIN/r.GP),
    physique:rank(b,r=>{const v=maps.bio.get(r.PLAYER_ID);return Number(v.PLAYER_HEIGHT_INCHES)+Number(v.PLAYER_WEIGHT)/10;}),
    onBall:def('defense-long',C.CURVE_DEF_3PT),help:def('defense-rim',C.CURVE_DEF_RIM),
    offBall:70,screen:70,handle:70,breakDbl:70,
    shotProfile:{threeRate:safe(row.FG3A,row.FGA),freeThrowsPerAttempt:safe(row.FTA,row.FGA),sourceSeason:'2025-26'},
    teamMinutes:row.MIN,teamGames:row.GP};
  return p;
}
const teams=teamRows.sort((a,b)=>a.TEAM_ID-b.TEAM_ID).map(t=>{
  const rows=read(`team-${t.TEAM_ID}`).sort((a,b)=>b.MIN-a.MIN||a.PLAYER_ID-b.PLAYER_ID).slice(0,5);
  // Fixed role assignment: increasing measured height, then decreasing AST rate.
  rows.sort((a,b)=>maps.bio.get(a.PLAYER_ID).PLAYER_HEIGHT_INCHES-maps.bio.get(b.PLAYER_ID).PLAYER_HEIGHT_INCHES||safe(b.AST,b.MIN)-safe(a.AST,a.MIN)||a.PLAYER_ID-b.PLAYER_ID);
  return {id:t.TEAM_ID,name:t.TEAM_NAME,season:'2025-26',benchmarkKind:'same-season-fixed-five',roster:rows.map(card)};
});
if (teams.length!==30) throw new Error('Expected 30 teams');
const result={schemaVersion:1,season:'2025-26',rotation:'Top five team-specific total minutes; all five play the full fixed-possession game, no bench substitutions. This is conditional fixed-five PR, not full-rotation NBA team PR.',
  methodology:{ability:'Full-season player totals including all traded-team stints; selection and tendencies use team-specific totals. No team wins, net rating, usage targets or card costs enter ratings.',
    shooting:'Inverse engine accuracy curves after 100-attempt league-prior shrinkage, bounded 40..99; FT curve unchanged.',
    defense:'Tracked opponent percentage difference shrunk by D_FGA/(D_FGA+200), inverse defense curves, bounded 40..99.',
    other:'Rank within GP>=30 and MPG>=20 pool, attribute PR1/50/99 -> 40/70/99.',
    unknown:'offBall, screen, handle and breakDbl set to neutral 70: unmeasured, not fabricated individual ratings.',
    roles:'Height ascending assigns PG/SG/SF/PF/C; AST/min and player ID break ties. This is an explicit role convention, not official starting positions.'},sources,teams};
fs.writeFileSync(new URL('../data/benchmark-league.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(`Built ${teams.length} teams / ${teams.flatMap(t=>t.roster).length} cards from ${sources.length} snapshots`);

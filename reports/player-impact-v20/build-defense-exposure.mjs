import fs from 'node:fs';
import crypto from 'node:crypto';
import {loadInput} from '../player-impact-v19/input.mjs';
const root='reports/player-impact-v20',hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const table=file=>{const doc=JSON.parse(fs.readFileSync(file)),sets=doc.data.resultSets,s=Array.isArray(sets)?sets[0]:sets;return s.rowSet.map(r=>Object.fromEntries(s.headers.map((k,i)=>[k,r[i]])));};
for(const season of process.argv.slice(2).length?process.argv.slice(2):['2022-23','2023-24','2024-25','2025-26']){
 const output=`${root}/${season}-defense-exposure.json`;if(fs.existsSync(output))throw Error('Preserve source defense exposure');
 const b=loadInput(season),players=new Map();for(const t of b.league.teams)for(const p of t.roster){const s=players.get(p.playerId)??{minutes:0,fga:0,fg3a:0,name:p.name};s.minutes+=p.observed.MIN;s.fga+=p.observed.FGA;s.fg3a+=p.observed.FG3A;players.set(p.playerId,s);}
 const counts={long:new Map(),short:new Map()},files=new Map();
 if(season==='2025-26'){files.set('data/benchmark-source/defense-long.json','long');files.set('data/benchmark-source/defense-rim.json','short');}
 else{const m=JSON.parse(fs.readFileSync(`reports/defense-tenth/step4-t0/${season}/tracking/manifest.json`));for(const s of m.sources){if(files.has(s.file)&&files.get(s.file)!==s.zone)throw Error('Tracking scope conflict');files.set(s.file,s.zone);}}
 for(const[file,zone]of files)for(const r of table(file)){const pid=r.CLOSE_DEF_PERSON_ID??r.PLAYER_ID;if(counts[zone].has(pid))throw Error('Duplicate global tracking row; never sum replicated manifest entries');const n=r[zone==='long'?'FG3A':'FGA_LT_06']??r.D_FGA??0;counts[zone].set(pid,{attempts:n,difference:r.PLUSMINUS??r.PCT_PLUSMINUS});}
 const total=[...players.values()].reduce((s,p)=>({minutes:s.minutes+p.minutes,fga:s.fga+p.fga,fg3a:s.fg3a+p.fg3a}),{minutes:0,fga:0,fg3a:0}),shot=JSON.parse(fs.readFileSync(`reports/player-impact-v6/${season}-cards.json`));
 const zones=['mid','short'].map(z=>Object.values(shot.cards).reduce((s,p)=>s+(p.freshShotCounts?.[z+'A']??0)+(p.putbackProxyCounts?.[z+'A']??0),0)),shortFraction=zones[1]/(zones[0]+zones[1]),teamMinutes=total.minutes/5;
 const leagueAttemptsPerTeamMinute={long:total.fg3a/teamMinutes,short:(total.fga-total.fg3a)*shortFraction/teamMinutes};
 const priorRates=Object.fromEntries(['long','short'].map(z=>[z,[...players].reduce((s,[id])=>s+(counts[z].get(id)?.attempts??0),0)/total.minutes]));
 const cards=Object.fromEntries([...players].map(([id,p])=>[id,{minutes:p.minutes,...Object.fromEntries(['long','short'].map(z=>[z,{attempts:counts[z].get(id)?.attempts??0,rawDifference:counts[z].get(id)?.difference??null,sourceMissing:!counts[z].has(id),rate:((counts[z].get(id)?.attempts??0)+240*priorRates[z])/(p.minutes+240)}]))}]));
 const out={season,design:'Closest-defender tracking FGA per player minute; use rate times FG-percentage difference, divided by team-zone FGA per team minute. 240-minute league activity prior (same as steal/allocation exposure prior), unchanged existing defense attributes and200-FGA difference shrinkage. Rim<6ft contributions divided by full short-zone FGA, so not all short shots treated as rim contests. Global tracking files deduplicated across replicated team manifest entries. No names/ranks/on-off/simulation residual fit. Tracking difference is descriptive, not proven causal.',priorMinutes:240,priorRates,leagueAttemptsPerTeamMinute,teamMinutes,shortFraction,cards,sources:{...Object.fromEntries([...files.keys()].map(f=>[f,hash(f)])),[`reports/player-impact-v6/${season}-cards.json`]:hash(`reports/player-impact-v6/${season}-cards.json`),codeSHA256:hash(root+'/build-defense-exposure.mjs')}};
 fs.writeFileSync(output,JSON.stringify(out,null,2));console.log(JSON.stringify({season,players:players.size,files:files.size,priorRates,leagueAttemptsPerTeamMinute}));
}

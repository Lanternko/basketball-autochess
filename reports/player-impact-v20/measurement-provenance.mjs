import fs from 'node:fs';
import {loadInput} from './input.mjs';
import {ovrInput} from './ovr-input.mjs';
const season='2025-26',b=loadInput(season),x=await ovrInput(season);
const players=[...new Map(b.league.teams.flatMap(t=>t.roster).map(p=>[p.playerId,p])).values()];
const unknown=['offBall','screen','handle','breakDbl'];
for(const p of players)for(const k of unknown)if(p[k]!==70)throw Error('Unknown skills cannot be represented as measured');
const notes={
 unknownSkills:'All four remain neutral70; no new measured ballhandling, off-ball movement, screens or double-team escape data was obtained.',
 speed:'Missing. Spacing uses observed3PM/min and production/role proxies; it does not measure running speed or prove speed caused a shot-quality change.',
 shooting:'Source fresh FGM/FGA by zone with100-attempt league prior, retained shared league projection and actual fresh-FGA-weighted source context. Same-season reconstruction, not an independent forecast.',
 assists:'Source AST/min converted to delivery opportunities using source-implied receiver FG success; transport has no self-pass and conserves terminal opportunities. Success reference remains the earlier v18 approximation.',
 turnovers:'Source box turnover-skill ratio and measured pass-steal activity feed separate touch/pass processes. No dribbling tracking is available; neutral handle is not a measured dribbling grade.',
 steals:'Observed STL/min with240-minute league prior determines pressure/activity, independently of closest-defender FG contest ratings.',
 blocks:'Conditional blocked-miss recipient uses measured BLK/min; existing team blocked-miss mechanism retained. Allocation accuracy alone does not prove incremental team defense.',
 rebounds:'Existing team OREB probability retained; individual DREB recipient correction retained. Neither player shares nor team totals alone establish causal replacement value.',
 contests:'Closest-defended FGA/player-minute times conditional FG difference, divided by team-zone FGA/team-minute. Six-foot rim counts do not cover every short shot; midrange remains a proxy. Descriptive association, not causal defense.',
 stamina:'Exported grade is based on observed minutes per game. It is a role proxy, not measured physiology. Equal-duration OVR disables fatigue/substitution.',
 physique:'Height/weight derived percentile remains in separate shot/rebound mechanisms; v20 changes contest exposure, not the physique prior.',
 ovr:'One natural position, four distinct mean70 positional teammates,30 fixed opponent lineups, both seating orders,14.4 minutes. Auxiliary rates use declared positional pools. Current31-player sample is not a Top50 or an anchored0–99 rating.'
};
const rows=players.map(p=>({playerId:p.playerId,name:p.name,minutes:p.defenseExposureMeasurement.minutes,
 role:x.roleMap.get(p.playerId),missingMeasurements:p.missingMeasurements,unknownSkills:Object.fromEntries(unknown.map(k=>[k,p[k]])),
 sourceFreshShots:p.opportunityMeasurement.freshShotCounts,
 shootingPriorAttempts:p.shootingMeasurement.priorAttempts,
 sourceZoneAttempts:p.shootingMeasurement.sourceZoneAttempts,
 sourceCreation:p.creationSuccessMeasurement,
 productionProxies:p.creationContextMeasurement,
 sourceContests:p.defenseExposureMeasurement}));
fs.writeFileSync('reports/player-impact-v20/2025-26-measurement-provenance.json',JSON.stringify({season,players:rows.length,notes,rows},null,2));
console.log(JSON.stringify({players:rows.length,unknownSkills:unknown,allUnknownsNeutral70:true,roleAudit:x.roleAudit}));

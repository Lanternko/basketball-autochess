import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash} from '../scripts/defense_io.js';
import {verifyC} from '../scripts/run_defense_eighth_c_versions.js';
import {prepareCGroup,combinedC,bootstrapC,confirmationC} from '../src/defense_eighth_c_statistics.js';
import {measureEighth} from '../src/defense_eighth_analysis.js';
import {cConfig,cSimple} from '../scripts/defense_eighth_c_data.js';
import {calendarTruth} from '../src/defense_seventh_scoreboard.js';
const p=verifyC(),rows=Array.from({length:30},(_,i)=>({id:i,net:(i-14.5)*.8+(i%3),wins:15+i*.4,observed:{net:i-14.5,wins:15+i*.5}})),g=prepareCGroup({v3:Array(20).fill(rows),v4:Array(20).fill([...rows].reverse())}),m=combinedC([g]);
for(const k of ['netRMSE','netCorrelation','netSDRatio','calibrationSlope','winMAE','winRMSE'])assert(Math.abs(m.v3[k]-measureEighth(rows)[k])<1e-10,k);
assert(Math.abs(m.v3.netRMSE**2-m.v3.oracleRMSE**2-(m.v3.observedNetSD*m.v3.netSDRatio)**2*(m.v3.calibrationSlope-1)**2)<1e-10,'Oracle plus dispersion decomposition');
const paired=bootstrapC([g,g],[{id:'b',left:'v4',right:'v3'}],{B:100});for(const v of Object.values(paired.pairs.b))if(v?.ci95){assert(Math.abs(v.estimate)<1e-12);assert.deepEqual(v.ci95,[0,0]);assert.deepEqual(v.ci998,[0,0]);}
const mk=(lo,hi,wlo=lo,whi=hi)=>({netRMSE:{ci95:[lo,hi],ci998:[wlo,whi]},winMAE:{ci95:[-1,1],ci998:[-2,2]}}),comp={id:'b',netOnly:false},cells=rs=>Object.fromEntries([25,41,55].map((k,i)=>[k,{pairs:{b:rs[i]}}]));
assert.equal(confirmationC(cells([mk(-2,-1),mk(-2,-1),mk(-1,1)]),comp,'improvement').grade,'跨季確認');assert.equal(confirmationC(cells([mk(-2,-1,-2,1),mk(-1,1),mk(-1,1)]),comp,'improvement').grade,'單點成立');assert.equal(confirmationC(cells([mk(-1,1),mk(-1,1),mk(-1,1)]),comp,'improvement').grade,'分不出');
// Comparator adapter must exactly reproduce all already-frozen development rows.
const a=read('reports/defense-eighth/a/analysis.json');for(const s of p.developmentSeasons)for(const k of p.cutoffs){const c=read(cConfig(s,k)),d=cSimple(c,calendarTruth(c));for(const v of ['simple','shrink'])for(const r of d[v][0]){const old=a.seasons[s][k].models[v].teams.find(t=>t.id===r.id);assert(Math.abs(r.net-old.net)<1e-12);assert(Math.abs(r.wins-old.wins)<1e-12);}}
if(process.argv.includes('--artifacts')){
 const root='reports/defense-eighth/c',a=read(root+'/assessment.json'),q=read(root+'/quality.json'),audit=read(root+'/execution-audit.json');assert.equal(a.preregHash,hash(root+'/prereg-supplement.json'));assert.equal(a.v5FreezeHash,p.v5FreezeHash);assert.equal(a.groups.blind.seasons.length,2);assert.equal(a.groups.four.seasons.length,4);
 assert.equal(audit.preregHash,a.preregHash);assert.equal(audit.v5FreezeHash,p.v5FreezeHash);for(const s of p.blindSeasons){assert(audit.downloadChronology[s].allAfterRegistration);assert(Date.parse(audit.downloadChronology[s].earliestFetchedAt)>Date.parse(p.registeredAt));}
 for(const [file,h]of Object.entries(audit.sourceHashes))assert.equal(hash(file),h,file);
 for(const [s,qs]of Object.entries(q.seasons)){assert.equal(qs.regularGames,1230);assert.equal(qs.failureCount+qs.strictUsableGames,1230);assert.equal(qs.byTeam.reduce((sum,t)=>sum+t.missing,0),2*qs.failureCount);assert.equal(qs.byMonth.reduce((sum,t)=>sum+t.missing,0),qs.failureCount);if(s==='2023-24')assert.equal(qs.tournament.championship.inRegularSchedule,false);}
 for(const group of Object.values(a.groups))for(const cell of Object.values(group.cutoffs)){assert.equal(cell.bootstrap.B,20000);for(const c of p.comparisons)for(const x of Object.values(cell.pairs[c.id]))if(x?.ci95){assert(x.ci998[0]<=x.ci95[0]);assert(x.ci998[1]>=x.ci95[1]);}for(const v of ['v4cal','simplecal']){assert.equal(cell.versions[v].winMAE,null);assert.equal(cell.versions[v].winRMSE,null);}}
 for(const [s,cells]of Object.entries(a.seasons))for(const [k,cell]of Object.entries(cells)){assert(Math.abs(cell.versions.v4cal.netCorrelation-cell.versions.v4.netCorrelation)<1e-10);assert(Math.abs(cell.versions.simplecal.netCorrelation-cell.versions.simple.netCorrelation)<1e-10);assert(Math.abs(cell.versions.v4cal.calibrationSlope-cell.versions.v4.calibrationSlope/p.outputCalibration.m4[k])<1e-10);const d=read(`${root}/ablation/${s}/calendar-${k}/diagnostic.json`);assert(Math.abs(d.covarianceSum-1)<1e-10);assert.deepEqual(d.seeds,p.seeds.slice(0,3));}
 for(const [file,h]of Object.entries(a.sources))assert.equal(hash(file),h,file);
 const report=read(root+'/closeout.json');assert.equal(report.nextBatchStarted,false);for(const [file,h]of Object.entries({...report.sources,...report.outputHashes}))assert.equal(hash(file),h,file);assert.equal(report.reportCode,hash('scripts/report_defense_eighth_c.js'));
}
console.log('C0/frozen hashes, population statistics, pairing, calibration-only columns, multiplicity and frozen comparator parity passed');

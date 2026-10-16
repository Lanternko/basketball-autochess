// Read-only execution audit; no forecast or registration is modified here.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {read,hash} from './defense_io.js';
import {verifyC} from './run_defense_eighth_c_versions.js';
import {cConfig,cManifest} from './defense_eighth_c_data.js';
const root='reports/defense-eighth/c',p=verifyC(),out={auditedAt:new Date().toISOString(),preregHash:hash(root+'/prereg-supplement.json'),registeredAt:p.registeredAt,v5FreezeHash:p.v5FreezeHash,downloadChronology:{},cells:{},sourceHashes:{}};
for(const s of p.blindSeasons){
 const dir=`data/defense-seventh/${s}`,files=['team-games.json','player-games.json','bio.json',...['boxes','pbp'].flatMap(d=>fs.readdirSync(dir+'/'+d).filter(f=>f.endsWith('.json')).map(f=>d+'/'+f))],times=files.map(f=>{const doc=read(dir+'/'+f);assert.equal(doc.season,s);assert(Date.parse(doc.fetchedAt)>Date.parse(p.registeredAt),f+' predates C0');return doc.fetchedAt;}).sort();
 out.downloadChronology[s]={rawDocuments:files.length,earliestFetchedAt:times[0],latestFetchedAt:times.at(-1),allAfterRegistration:true,basicSources:Object.fromEntries(files.slice(0,3).map(f=>[dir+'/'+f,hash(dir+'/'+f)])),pbpManifestHash:hash(dir+'/manifest.json')};
}
for(const s of [...p.developmentSeasons,...p.blindSeasons]){out.cells[s]={};for(const k of p.cutoffs){
 const cf=cConfig(s,k),c=read(cf),league=read(c.leagueFile),byID=new Map(league.schedule.map(g=>[g.id,g]));
 for(const id of [...c.trainGames,...c.allTrainGames])assert(byID.get(id)?.date<=c.date,'Training date leak '+s+'/'+k+'/'+id);
 const ability=read(c.root+'/ability-model-forward.json'),factors=read(c.root+'/factors/engine-signals.json'),tracking=read(c.root+'/tracking/manifest.json');
 for(const id of [...ability.trainGames,...factors.trainGames])assert(c.trainGames.includes(id),'Estimator sample leak '+s+'/'+k+'/'+id);
 assert.equal(tracking.date,c.date);for(const x of tracking.sources){assert.equal(new URL(x.url).searchParams.get('DateTo'),c.date);assert.equal(hash(x.file),x.sha256);}
 const versions={};for(const v of ['v1','v3-signals-off','v3','v4','v5']){
  const file=cManifest(s,k,v),m=read(file);assert.deepEqual(m.files.map(f=>f.seed),p.seeds);assert.equal(m.extra.calendarDate,c.date);
  for(const [src,h]of Object.entries(m.sources))assert.equal(hash(src),h,'Changed manifest source '+src);
  const label=m.label,calFiles=Object.keys(m.extra).length?fs.readdirSync('reports/defense-seventh').filter(f=>f.startsWith('cal-'+label+'-')&&f.endsWith('-seeds.json')):[];
  for(const f of calFiles){const cal=read('reports/defense-seventh/'+f);assert.equal(cal.extra.phase,'train');assert.equal(cal.extra.calendarDate,c.date);for(const i of cal.extra.indices)assert(c.trainGames.includes(league.schedule[i].id));}
  if(v==='v5'){
   const cardRoot=m.extra.cardFile.slice(0,m.extra.cardFile.lastIndexOf('/')),scaled=read(cardRoot+'/ability-model-forward.json'),factor=read('reports/defense-eighth/b/v5-freeze.json').c[k];
   assert.equal(scaled.eighthResidualScale.multiplier,factor);
   // JSON stores -0 as 0; preserve exact numeric equality without treating
   // that serialization-only sign change as a change to the frozen model.
   assert(scaled.models.role.offenseResidual.every((x,i)=>x===ability.models.role.offenseResidual[i]*factor),'v5 residual is not the frozen scalar multiple');
   const restored=structuredClone(scaled);delete restored.eighthResidualScale;restored.models.role.offenseResidual=ability.models.role.offenseResidual;assert.deepEqual(restored,ability,'v5 changed a non-residual input');
  }
  versions[v]={manifest:file,sha256:hash(file),trainingCalibrationManifests:calFiles.length,calibration:m.extra.calibration};
 }out.cells[s][k]={date:c.date,strictTrainGames:c.trainGames.length,allTrainGames:c.allTrainGames.length,configHash:hash(cf),versions};
}}
for(const s of [...p.developmentSeasons,...p.blindSeasons])for(const k of p.cutoffs){const file=`${root}/ablation/${s}/calendar-${k}/diagnostic.json`,d=read(file);assert.equal(d.preregHash,out.preregHash);assert(Math.abs(d.covarianceSum-1)<1e-10);for(const x of Object.values(d.ablations)){const m=read(x.manifest);assert.deepEqual(m.files.map(f=>f.seed),p.diagnostics.ablation.seeds);assert.deepEqual(m.extra.calibration,d.calibration);assert.equal(hash(m.extra.cardFile),x.cardHash);}out.sourceHashes[file]=hash(file);}
for(const f of ['scripts/audit_defense_eighth_c_execution.js','scripts/run_defense_eighth_c_versions.js','scripts/diagnose_defense_eighth_c_ablation.js','scripts/assess_defense_eighth_c.js','scripts/defense_eighth_c_data.js','src/defense_eighth_c_statistics.js'])out.sourceHashes[f]=hash(f);
verifyC();fs.writeFileSync(root+'/execution-audit.json',JSON.stringify(out,null,2)+'\n');console.log('C chronology, training dates, paired seeds, frozen hashes and ablation calibration audit passed');

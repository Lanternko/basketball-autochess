import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
import {root,verify} from './run.mjs';
verify();const p=read(root+'/protocol.json'),issues=[],protectedFiles=read(root+'/protected-before.json');
if(hash(root+'/protected-before.json')!==p.protectedManifestSHA)issues.push('protected manifest changed');
for(const group of [protectedFiles,p.inputHashes,p.codeHashes])for(const [f,h]of Object.entries(group))if(!fs.existsSync(f)||hash(f)!==h)issues.push('changed '+f);
const parity=read(root+'/parity.json');if(parity.results.length!==4||parity.results.some(r=>r.games!==1230||!r.teamPlayerStatsIdentical))issues.push('parity');
const m=read(root+'/run-manifest.json');if(m.files.length!==160)issues.push('run count');
for(const j of m.files){if(hash(j.file)!==j.sha256)issues.push('run hash '+j.file);const r=read(j.file);if(r.matches.length!==1230||r.teams.some(t=>t.games!==82))issues.push('game count '+j.file);if(['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal'].some(k=>r.options[k])||r.options.defenseSignals)issues.push('stint signal '+j.file);if(r.options.individualDrebCard!==(j.version==='dreb'))issues.push('switch '+j.file);if(r.options.seasonMinuteTargets||r.options.neutralContests)issues.push('minutes/contests '+j.file);}
const a=read(root+'/analysis.json');for(const c of a.cells)for(const t of c.teams)if(!Number.isFinite(t.O+t.D)||Math.abs(t.O+t.D-t.netError)>1e-8)issues.push('O+D '+c.season+'/'+t.id);
const result={finishedAt:new Date().toISOString(),protocolSHA:hash(root+'/protocol.json'),protectedFiles:Object.keys(protectedFiles).length,parityGames:4920,fullEvaluationSeasons:m.files.length,fullEvaluationGames:m.files.length*1230,jointBootstrapReplicates:read(root+'/joint-intervals.json').replicates,issues};fs.writeFileSync(root+'/completion-audit.json',JSON.stringify(result,null,2)+'\n');
const files=['protocol.json','coverage.json','parity.json','run-manifest.json','analysis.json','joint-intervals.json','decision.json','report.md','completion-audit.json'];fs.writeFileSync(root+'/deliverable-hashes.json',JSON.stringify(Object.fromEntries(files.map(f=>[f,hash(root+'/'+f)])),null,2)+'\n');console.log(JSON.stringify(result));if(issues.length)process.exitCode=1;

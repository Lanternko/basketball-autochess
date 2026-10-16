import assert from 'node:assert/strict';
import fs from 'node:fs';
import {read,hash} from '../scripts/defense_io.js';
import {buildV5} from '../scripts/build_defense_eighth_v5_cards.js';
import {seventhInputs,executeSeventhJob} from '../src/defense_seventh_jobs.js';
import {blindVerdict,jointBlindEnvelope,jointBlindPair} from '../src/defense_eighth_blind_evaluation.js';
const ci=(a,b)=>({ci95:[a,b]});
assert.equal(blindVerdict(ci(-2,-1),ci(-1,1)).answer,'成立');assert.equal(blindVerdict(ci(-1,1),ci(.2,1)).answer,'不成立');assert.equal(blindVerdict(ci(-1,1),ci(-1,1)).answer,'分不出');assert(blindVerdict(ci(-2,-1),ci(.2,1)).tradeoff);
const rows=Array.from({length:30},(_,i)=>({id:i,net:i-15,wins:20+i,observed:{net:i-15,wins:20+i}})),g={v5:Array.from({length:20},()=>rows),simple:Array.from({length:20},()=>rows),shrink:Array.from({length:20},()=>rows)};const identical=jointBlindEnvelope([g,g],'v5',{B:100});assert.equal(identical.netRMSE.estimate,0);assert.deepEqual(identical.netRMSE.ci95,[0,0]);assert.equal(identical.verdict.answer,'分不出');
// Franchise alignment must survive different row order in another season/model.
const varied=Array.from({length:20},(_,s)=>rows.map((r,i)=>({...r,net:r.net+(s%3-1)*(i%2?1:-1),wins:r.wins+(s%5-2)}))),ordered={v5:varied,simple:varied.map(rs=>[...rs].reverse())};
const aligned=jointBlindPair([ordered,{v5:varied.map(rs=>[...rs].reverse()),simple:varied}],'v5','simple',{B:100});for(const x of Object.values(aligned)){assert.equal(x.estimate,0);assert.deepEqual(x.ci95,[0,0]);}
// c=1 exact numerical card and game parity; all output is isolated under b/tests.
const cf='reports/defense-seventh/2025-26/calendar-41/config.json',out='reports/defense-eighth/b/tests/c1';await buildV5(cf,1,{output:out});
const old=read('reports/defense-seventh/2025-26/calendar-41/pre41-v4-league.json'),now=read(out+'/pre41-v5-league.json');assert.deepEqual(now.teams,old.teams);assert.deepEqual(now.seventhSignals,old.seventhSignals);
const original=read('reports/defense-seventh/2025-26-calendar-41-v4-seeds.json').extra,job={...original,label:'parity',seed:20261012,indices:[1000,1001]},a=executeSeventhJob(job),b=executeSeventhJob({...job,cardFile:out+'/pre41-v5-league.json'});assert.deepEqual(a.matches,b.matches);
if(process.argv.includes('--artifacts')){
 const root='reports/defense-eighth/b',rules=read(root+'/development-rules.json'),selection=read(root+'/selection.json'),assessment=read(root+'/assessment.json'),players=read(root+'/players.json'),freeze=read(root+'/v5-freeze.json');
 assert.equal(freeze.blindDataPresent,false);assert.equal(freeze.previousRulesCancelled,true);for(const[file,h]of Object.entries(freeze.sources))assert.equal(hash(file),h,file);
 assert.equal(fs.readFileSync(root+'/v5-freeze.sha256','utf8').split(/\s+/)[0],hash(root+'/v5-freeze.json'));
 for(const k of rules.cutoffs){assert(selection.cutoffs[k].c>=0&&selection.cutoffs[k].c<=1);assert.equal(freeze.c[k],selection.cutoffs[k].c);for(const season of rules.developmentSeasons){const cell=assessment.seasons[season][k],file=cell.v5Manifest,manifest=read(file),dir=cell.v5Dir,model=read(dir+'/ability-model-forward.json'),source=read(`reports/defense-seventh/${season}/calendar-${k}/ability-model-forward.json`),cal=read(dir+'/calibration-v5.json'),c=selection.cutoffs[k].c;assert.equal(manifest.files.length,20);assert.deepEqual(model.models.role.priorOffense,source.models.role.priorOffense);assert.deepEqual(model.models.role.priorDefenseAllowed,source.models.role.priorDefenseAllowed);assert.deepEqual(model.models.role.defenseResidual,source.models.role.defenseResidual);assert.deepEqual(model.models.plain,source.models.plain);assert.deepEqual(model.models.role.offenseResidual,source.models.role.offenseResidual.map(v=>v*c));assert(cal.history.length<=5);assert(cal.seeds.every((s,i)=>s===20260101+i));for(const f of manifest.files)assert.equal(hash(f.file),f.sha256);for(const[key,h]of Object.entries(cell.inputHashes))assert.equal(hash(key),h);assert.equal(players.seasons[season][k].playerGate,players.seasons[season][k].FGGap<=.3);}}
 assert.equal(freeze.teamStrengthOnly,players.teamStrengthOnly);assert(!fs.existsSync('data/defense-seventh/2023-24/league.json'));assert(!fs.existsSync('data/defense-seventh/2022-23/league.json'));
}
console.log('eighth B: multiplier-only projection, c1 parity, precommitted C4 decisions and artifacts passed');

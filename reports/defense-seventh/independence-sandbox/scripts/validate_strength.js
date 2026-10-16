import fs from 'node:fs';
import crypto from 'node:crypto';
import {TEAMS} from '../src/teams.js';
import {STABLE_POSSESSIONS} from '../src/calibration_presets.js';
import {validateLeague,measureStrength,rankTeams,probe,flatPlayer,winToOvr} from '../src/strength_benchmark.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const league=read('../data/benchmark-league.json');validateLeague(league);
const teamSamples=Number(process.env.TEAM_SAMPLES??128),playerSamples=Number(process.env.PLAYER_SAMPLES??32);
const seed=Number(process.env.STRENGTH_SEED??20260919);
const leagueContext=read('../data/league-context.json').contexts.find(c=>c.season===league.season&&c.type==='Regular Season');
const rules={mode:'fixed',possessions:30,fatigue:false,blocks:true,reboundModel:'opportunity',leagueReboundShare:leagueContext.orebShare,...STABLE_POSSESSIONS};
const sourceFiles=['src/simulation_engine.js','src/probability_model.js','src/constants.js','src/rebound_block_model.js','src/strength_benchmark.js','src/calibration_presets.js','src/rng.js','src/teams.js','data/benchmark-league.json'];
const hashes=Object.fromEntries(sourceFiles.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+p,import.meta.url))).digest('hex')]));
const checkpoint=new URL(`../reports/strength-checkpoint-${seed}.json`,import.meta.url);
const fingerprint=crypto.createHash('sha256').update(JSON.stringify({hashes,rules,teamSamples,playerSamples,seed})).digest('hex');
let progress={fingerprint,teams:[],players:[],anchors:[]};
if(fs.existsSync(checkpoint)) {const p=JSON.parse(fs.readFileSync(checkpoint));if(p.fingerprint===fingerprint)progress=p;}
const save=()=>fs.writeFileSync(checkpoint,JSON.stringify(progress,null,2)+'\n');
for(const team of league.teams) {
 if(progress.teams.some(t=>t.id===team.id))continue;
 const result=measureStrength([team],league.teams,{...rules,samples:teamSamples,seed});
 progress.teams.push({id:team.id,name:team.name,...result});save();console.log('Team',team.name,result.winRate.toFixed(3));
}
for(const value of [40,70,99]) {
 if(progress.anchors.some(p=>p.value===value))continue;
 const p=flatPlayer(value),result=measureStrength(Array.from({length:5},(_,i)=>probe(p,i)),league.teams,{...rules,samples:playerSamples,seed});
 progress.anchors.push({value,...result});save();console.log('Anchor',value,result.winRate.toFixed(3));
}
for(const [team,t] of Object.entries(TEAMS))for(const p of t.roster) {
 if(progress.players.some(r=>r.team===team&&r.name===p.name))continue;
 const result=measureStrength(Array.from({length:5},(_,i)=>probe(p,i)),league.teams,{...rules,samples:playerSamples,seed});
 progress.players.push({team,name:p.name,...result});save();console.log('Player',p.name,result.winRate.toFixed(3));
}
const anchors=Object.fromEntries(['low','mid','high'].map((k,i)=>[k,progress.anchors.find(p=>p.value===[40,70,99][i]).winRate]));
const teams=rankTeams(progress.teams);
const players=progress.players.map(p=>({...p,ovr:winToOvr(p.winRate,anchors),ovrConditionalCI95:p.ci95.map(v=>winToOvr(v,anchors))})).sort((a,b)=>b.winRate-a.winRate);
const monotonic=players.every((p,i)=>i===0||p.ovr<=players[i-1].ovr);
const precision=[...teams,...players,...progress.anchors].every(p=>p.halfWidth95<=.02);
const samplePlanComplete=teamSamples>=128&&playerSamples>=32;
const anchorSeparation=progress.anchors[0].conservative95[1]<progress.anchors[1].conservative95[0]&&progress.anchors[1].conservative95[1]<progress.anchors[2].conservative95[0];
const result={schemaVersion:1,scope:league.rotation,season:league.season,seed,teamSamples,playerSamples,rules,hashes,fingerprint,
 exposure:{possessionsPerSide:30,referencePace:100,equivalentMinutes:14.4,interpretation:'Equal possession exposure expressed as minutes at fixed pace; not a clock-driven game.'},
 sampling:'Uniform fixed pool of all 30 teams, including self for identical schedule; ties count half. Seat-swapped games are one cluster. Player slots equally weighted. 95% normal stratified intervals plus distribution-free Hoeffding bounds; not model-error intervals.',
 uncertainty:'OVR intervals condition on fitted anchors; anchor uncertainty reported separately. Team rank intervals use marginal conservative intervals and are not simultaneous confidence regions.',
 acceptance:{monotonic,precision,anchorSeparation,samplePlanComplete,targetHalfWidth:.02,passed:monotonic&&precision&&anchorSeparation&&samplePlanComplete},anchors:progress.anchors,mapping:anchors,
 pr90:teams.filter(t=>t.rank===3),teams,players};
fs.writeFileSync(new URL('../reports/strength-validation.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
const pct=x=>(x*100).toFixed(2);
fs.writeFileSync(new URL('../reports/strength-validation.md',import.meta.url),['# 固定五人球隊 PR 與勝率 OVR 驗證','',`同季 ${league.season} 30隊。seed=${seed}；每方30回合，無疲勞，固定全聯盟對手池與平衡先後手。`, '', `驗收：勝率映射單調=${monotonic}；全部95%抽樣區間半寬≤2pp=${precision}。`, '',league.rotation,'','中性未量測屬性、資料與建卡規則見 data/benchmark-league.json。此結果只驗證指定模型基準，不證明 NBA 真實排名或所有陣容單調。', '', 'PR = 100 × (30 − 中間名次) / 30；第三名為 PR90。CI 重疊者不宣稱排名已確定。和局計半勝；兩個先後手為一組抽樣單位。', '', '| 球隊 | PR | 勝率 | 95% CI | 保守名次範圍* | 場數 |','|---|---:|---:|---:|---:|---:|',...teams.map(t=>`| ${t.name} | ${t.pr.toFixed(1)} | ${pct(t.winRate)}% | ${t.ci95.map(pct).join('–')}% | ${t.rankInterval95.join('–')} | ${t.games} |`),'','*以各隊邊際 Hoeffding 區間作保守比較，不是同時涵蓋所有名次的95%區間。','','| 球員 | OVR | 勝率 | 95% CI | 場數 |','|---|---:|---:|---:|---:|',...players.map(p=>`| ${p.name} | ${p.ovr} | ${pct(p.winRate)}% | ${p.ci95.map(pct).join('–')}% | ${p.games} |`),'',`勝率錨點：${JSON.stringify(anchors)}。全40→40、全70→70、全99→99，分段線性後取整數；費用不進入公式。`, '', '完整資料包含各對手／槽位勝率、淨分差診斷、原始碼雜湊及區間。OVR區間以固定估計錨點換算，不包含錨點本身的不確定性。',''].join('\n'));
console.log(JSON.stringify(result.acceptance));
if(!result.acceptance.passed)process.exitCode=1;

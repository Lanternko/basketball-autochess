import fs from 'node:fs';
import crypto from 'node:crypto';
import {TEAMS} from '../src/teams.js';
import {STABLE_POSSESSIONS} from '../src/calibration_presets.js';
import {buildPer36Report} from '../src/per36_report.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const reference=read('../data/reference-seasons.json'),league=read('../data/league-context.json');
const selection=read('../reports/possession-calibration.json');
for(const [k,v] of Object.entries(selection.best.config))if(STABLE_POSSESSIONS[k]!==v)throw new Error('Preset differs from selected configuration');
if(!selection.passed)throw new Error('Primary calibration gate failed');
const metrics=['pts','usage','reb','tov'];
const errors=rows=>Object.fromEntries(metrics.map(k=>[k,rows.flatMap(r=>r.players).reduce((s,p)=>s+Math.abs(k==='usage'?p.error.usageProxyPercentagePoints:p.simulated[k]-p.real[k]),0)/20]));
const blocks=[];
for(let block=0;block<30;block++) {
 const seed=20270219+block*200003;
 const run=options=>['CLE','LAL','OKC','NYK'].map(key=>buildPer36Report(TEAMS[key],reference.teams[key],{n:100,seed,leagueReboundShare:league.contexts.find(c=>c.season===TEAMS[key].season&&c.type==='Regular Season').orebShare,...options}));
 const baseline=errors(run({})),candidate=errors(run(STABLE_POSSESSIONS));
 blocks.push({seed,baseline,candidate,delta:Object.fromEntries(metrics.map(k=>[k,candidate[k]-baseline[k]]))});
 if(block%5===4)console.log('Paired uncertainty blocks',block+1);
}
const intervals=Object.fromEntries(metrics.map(k=>{
 const xs=blocks.map(b=>b.delta[k]),mean=xs.reduce((a,b)=>a+b,0)/xs.length;
 const se=Math.sqrt(xs.reduce((s,x)=>s+(x-mean)**2,0)/(xs.length-1)/xs.length);
 return [k,{meanDelta:mean,standardError:se,ci95:[mean-2.04523*se,mean+2.04523*se]}];
}));
const modelFiles=['src/simulation_engine.js','src/probability_model.js','src/constants.js','src/calibration_presets.js','src/rebound_block_model.js','src/per36_report.js','src/rng.js','src/teams.js','data/reference-seasons.json','data/league-context.json'];
const hashes=Object.fromEntries(modelFiles.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(new URL('../'+p,import.meta.url))).digest('hex')]));
const result={schemaVersion:1,preset:STABLE_POSSESSIONS,hashes,blocks,intervals,
 interpretation:'Paired mean change of 100-game-block MAE over the same 20 players, 30 independent blocks, t(29) intervals. This is not a confidence interval on NBA model validity or exactly the pooled 2000-game MAE. Negative means improvement. Multiple metrics are exploratory, not simultaneous intervals.'};
fs.writeFileSync(new URL('../reports/possession-uncertainty.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
fs.writeFileSync(new URL('../reports/possession-uncertainty.md',import.meta.url),['# 球權校準配對不確定性','',
 '30 個獨立 seed 批次，各批每隊每版本100場，兩版本使用同seed；固定20名球員。報告「每批MAE變化的平均」及 t(29) 95%區間，不等於2000場池化MAE的區間，也不包含NBA模型偏差。多指標區間未作同時推論校正。','',
 '| 指標 | 新−舊平均 MAE | 95% CI |','|---|---:|---:|',...metrics.map(k=>`| ${k} | ${intervals[k].meanDelta.toFixed(4)} | ${intervals[k].ci95.map(v=>v.toFixed(4)).join(' ～ ')} |`),'',
 '負數表示改善；包含0者不宣稱顯著改善。使用同季整季usage代理且既有卡表曾擬合此目標，不能把抽樣穩定性当作獨立預測準確度。',''].join('\n'));
console.log(intervals);

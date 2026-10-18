// Presentation/metadata only: analytical estimates, rules, ranks and intervals
// are read from registered analysis; never recomputed or selected here.
import fs from 'node:fs';
import {read,hash} from '../../../scripts/defense_io.js';
const d='reports/defense-tenth/step4-t0',fit=[];
for(const season of ['2022-23','2023-24','2024-25']){
 const c=read(d+'/'+season+'/config.json'),m=read(c.modelOutput+'/engine-signals.json');
 const finite=Object.values(m.effects).flat().every(Number.isFinite)&&Object.values(m.centers).every(Number.isFinite);
 if(!finite||m.trainGames.length!==c.strictGames.length||m.trainGames.some(g=>!c.strictGames.includes(g)))throw Error('Full-factor audit '+season);
 fit.push({season,strictGames:c.strictGames.length,fittedGames:m.trainGames.length,finite,source:c.modelOutput+'/engine-signals.json',sha256:hash(c.modelOutput+'/engine-signals.json'),heldoutAssessment:'Unavailable: full-season fitting has no holdout. Legacy estimator offline-model.json empty-test zeros/NaN are not accuracy results.',legacyFixedStrictMetadata:season!=='2023-24'?'offline-model strictGames has stale hardcoded1188; config and actual fitted training IDs are authoritative':'validation adapter corrected this metadata'});
}
fs.writeFileSync(d+'/fit-audit.json',JSON.stringify(fit,null,2)+'\n');
let report=fs.readFileSync(d+'/report.md','utf8');
report=report.replace('python scripts/estimate_defense_seventh_factors.py reports/defense-tenth/step4-t0/2023-24/config.json random','python reports/defense-tenth/step4-t0/full-factor-adapter-v3.py reports/defense-tenth/step4-t0/2023-24/config.json\nnode reports/defense-tenth/step4-t0/zero-minute-adapter.mjs');
report=report.replace('node scripts/build_defense_seventh_bundle.js reports/defense-tenth/step4-t0/2023-24/config.json','node scripts/build_defense_seventh_bundle.js reports/defense-tenth/step4-t0/2023-24/config-positive-minutes.json');
report=report.replace('node reports/defense-tenth/step4-t0/audit.mjs','node reports/defense-tenth/step4-t0/publish.mjs\nnode reports/defense-tenth/step4-t0/audit.mjs\nnode reports/defense-tenth/step4-t0/audit-supplement.mjs');
report+='\n## 執行期資料驗證修正（不改估計／評分規則）\n\n';
report+='2023–24交易球員可在兩隊合計出賽超過82場，原按單隊82場檢查全聯盟tracking的assert失敗。validation-supplement-v3.json於重試前登記逐球員官方GP核對；沒有刪除那些人，沒有修改ridge、特徵、卡、機率或評分規則。前兩個驗證adapter的路徑／重複計數問題均保留，v2在估計前取消，沒有產生排名成績。\n\n';
report+='同季Justin Jackson兩次極短出賽官方MIN四捨五入為0，既有volume rater要求正分母。zero-minute-supplement.json於2023–24校正與評分前登記：只把0分母換成已下載box合計41.1秒=0.685分鐘；原始MIN=0、所有計數與屬性保留。沒有以球隊或球員身份修補能力。zero-minute-corrections.json保留逐欄紀錄。\n\n';
report+='三季模型全季fit沒有holdout；舊腳本輸出的空測試零值／NaN不當成資料外成績。2022–23／2024–25該舊診斷metadata仍寫固定1188，實際fit IDs分別為1079／1091；fit-audit.json核對實際訓練ID及所有係數。這是報告metadata限制，不是改樣本或改模型。\n\n';
const original=read('reports/defense-tenth/step4-t1/analysis.json').cells.find(c=>c.task==='task1'&&c.season==='2025-26'&&c.version==='v1');
report+=`原2025–26 v1全季同口徑參考：net RMSE ${original.metrics.netRMSE.toFixed(3)}、Spearman ${original.metrics.Spearman.toFixed(3)}、勝場MAE ${original.metrics.winsMAE.toFixed(3)}；net失敗為${original.failures.filter(f=>f.axis==='net').map(f=>f.name+' '+f.actualRank+'→'+f.predictedRank).join('、')}。其餘歷史v1本項未新增。\n`;
fs.writeFileSync(d+'/report.md',report);
// Keep all table rows adjacent; move the per-team explanatory paragraphs below.
const text=fs.readFileSync(d+'/failures.md','utf8'),sections=text.split(/(?=\n## )/),fixed=sections.map(s=>{if(!s.startsWith('\n## '))return s;const lines=s.split('\n'),rows=lines.filter(x=>x.startsWith('|')),rest=lines.filter(x=>!x.startsWith('|')&&x.trim()),title=rest.shift();return['',title,'',...rows,'',...rest.flatMap(x=>[x,''])].join('\n');}).join('\n');fs.writeFileSync(d+'/failures.md',fixed+'\n');
console.log('Published metadata/format supplement; no analytical changes');

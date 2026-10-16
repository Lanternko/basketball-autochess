import fs from 'node:fs';
const file=new URL('../reports/possession-calibration.json',import.meta.url);
const report=JSON.parse(fs.readFileSync(file));
// Older development output used holdout labels before all four teams had been
// inspected. Normalize the labels; do not misrepresent that exploratory work.
for(const v of report.validation) {
 if(v.groups.training){v.groups.historical=v.groups.training;delete v.groups.training;}
 if(v.groups.heldOut){v.groups.modern=v.groups.heldOut;delete v.groups.heldOut;}
}
fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');
const rows=report.validation.flatMap(v=>Object.entries(v.groups).map(([k,g])=>`| ${v.seed} / ${k} | ${['pts','usage','reb','tov'].map(m=>`${g.baseline[m].toFixed(3)} → ${g.candidate[m].toFixed(3)}`).join(' | ')} | ${g.passed} |`));
fs.writeFileSync(new URL('../reports/possession-calibration.md',import.meta.url),[
 '# 球權與包夾校準','',`四隊整體四指標不退步：${report.passed?'通過':'未通過'}。`, '',
 'CLE/LAL/OKC/NYK 均參與開發；不再稱其中任何一隊為留出資料。先前探索曾查看多組參數與舊 seed；最終選參與新 seed 驗證分開保存。此驗證衡量固定模型的抽樣穩定性，不是獨立 NBA 預測。','',
 `最終選參：seed=${report.trainingSeed}，每隊 ${report.trainingN} 場，共 ${report.candidates.length} 組共用參數。先篩選 PTS／usage／REB／TOV 均不退步的候選，再比較事前定義的加權誤差；新seed不參與選參。`, '',
 `採用參數：${JSON.stringify(report.best.config)}。兩個驗證seed，每隊每版本 ${report.validation[0].n} 場。`, '',
 '雙方使用相同 n／seed／pace、同季籃板比例、固定全70對手、無疲勞。沒有修改卡表、罰球命中曲線，沒有輸入真實 usage 或出手量。全70只是診斷對手，不叫球隊PR50。', '',
 '| seed / 組別 | PTS MAE 舊→新 | usage MAE pp 舊→新 | REB MAE 舊→新 | TOV MAE 舊→新 | 全指標不退步 |','|---|---:|---:|---:|---:|---|',...rows,'',
 '模型新增：未包夾 EV 與放空代價決定固定混合包夾機率；處理／傳球能力決定受壓失誤；EV 與抽樣共用持球失誤機率；順下接球機會使用擋拆相對無球的優勢和身材。共用失誤底值補足原模型低估，仍是待追蹤資料驗證的假設。', '',
 '球員整季 USG 正規化只是五人 usage 代理，既有卡表也曾用它校準，不能把降低代理誤差稱為公式真實性證明。包夾率不是實際抽樣包夾事件率。GSW 不參與選參；正式遊戲與 timed 模式預設維持原行為，新設定以 stable-v1 明確選用。','',
 '配對批次的誤差變化區間見 possession-uncertainty.md；籃板改善幅度很小，應連同區間與尚缺罰球籃板的限制解讀。',''].join('\n'));

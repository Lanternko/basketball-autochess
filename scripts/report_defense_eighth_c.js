import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {verifyC} from './run_defense_eighth_c_versions.js';
const root='reports/defense-eighth/c',p=verifyC(),a=read(root+'/assessment.json'),q=read(root+'/quality.json'),audit=read(root+'/execution-audit.json'),names={a:'防守訊號：v3−signals-off',b:'v4−v3',c:'v5−v4',d:'v4−較強simple/shrink',e:'v5−較強simple/shrink',f:'v4cal−v4',g:'simplecal−simple',h:'v4cal−min(simple,simplecal)'},f=(x,n=3)=>Number.isFinite(x)?(Math.abs(x)<1e-12?0:x).toFixed(n):'—',ci=(x,key='ci95')=>x?`${f(x.estimate)} [${x[key].map(z=>f(z)).join(', ')}]`:'—（無預測）';
const confirmed=p.comparisons.filter(c=>a.confirmations[c.id].improvement.grade==='跨季確認').map(c=>names[c.id]),single=p.comparisons.filter(c=>a.confirmations[c.id].improvement.grade==='單點成立').map(c=>names[c.id]);
const worsened=p.comparisons.filter(c=>a.confirmations[c.id].worsening.grade==='跨季確認').map(c=>names[c.id]);
const headline=`階段C完成。兩盲測季合併，達到「跨季確認」的改善項目：${confirmed.length?confirmed.join('；'):'沒有'}。${worsened.length?`跨季確認的退步：${worsened.join('；')}。`:''}${single.length?`單點成立：${single.join('；')}，不得宣稱改善；30多個檢定中預期約1–2個偶然通過。`:''}v5凍結內容、c(K)、m4／ms與判準保持原樣。正式基準維持v3，完成C後停下。`;
const md=['# 第八批階段C：兩個盲測季','',headline,'','## 已驗證事實：C4八筆比較','',
'結論只由2023–24與2022–23合併的球隊＋seed聯合区間決定。五筆原比較保留netRMSE／winsMAE的OR判準，三筆輸出校準只看netRMSE。每K的成立／不成立／分不出使用95%；確認等級另依預先登記的兩K95%或任一K99.8%規則。其他端點顯著退步仍列為代價。','',
'| 比較 | K25 | K41 | K55 | 改善確認等級 | 退步確認等級 |','|---|---|---|---|---|---|'];
for(const c of p.comparisons){const x=a.confirmations[c.id];md.push(`| ${names[c.id]} | ${p.cutoffs.map(k=>a.groups.blind.cutoffs[k].pairs[c.id].verdict.answer).join(' | ')} | ${x.improvement.grade} | ${x.worsening.grade} |`);}
md.push('', '若同一比較在不同K或不同端點出現相反方向，兩種確認等級都會列出；不隱藏取捨。各端點自己的確認等級保存在assessment.json。單點成立一律註明「30多個檢定中預期約1–2個偶然通過」。這是指定的確認規則，並非宣稱控制整體錯誤率為5%。','',
'| 比較 | K | net差值 [95%] | net差值 [99.8%] | wins MAE差值 [95%] | wins MAE差值 [99.8%] | 分不出時區間寬度 net／wins |','|---|---:|---:|---:|---:|---:|---|');
for(const c of p.comparisons)for(const k of p.cutoffs){const x=a.groups.blind.cutoffs[k].pairs[c.id],w=x.verdict.widths;md.push(`| ${c.id} | ${k} | ${ci(x.netRMSE)} | ${ci(x.netRMSE,'ci998')} | ${ci(x.winMAE)} | ${ci(x.winMAE,'ci998')} | ${x.verdict.answer==='分不出'?`${f(w.netRMSE)} / ${f(w.winMAE)}`:'—'} |`);}
md.push('', '誤差差值均為左−右，負值較好。「較強對照」每次重抽重新取合併誤差較低者；net與wins可選不同對照，選擇不餵入模型。八筆比較所有可定義指標的兩種區間另列 [paired-intervals.md](paired-intervals.md)。','',
'## C3主表','',
'各季內去均值、季間等權；net／wins／事後理想RMSE以季別MSE合併後開根號，其餘列季別數值平均。相關、校準斜率、SD都是逐隊20seed平均後計算，母體SD。聯盟效率偏差先在每季合併計數，計分為100×PTS／雙方平均(FGA−OREB+TOV+0.44FTA)，再等權合併。單場殘差是凍結的本季球隊得分／失分均值調整，非官方效率。','',
'理想縮放RMSE=σy√(1−r²)與答案倍率均用了後段真實答案，只作事後上限；答案倍率與校準斜率是同一量。合併時逐季算理想MSE再合併，不能把平均r與平均σ直接代入公式。v4cal／simplecal只提供球隊net，沒有勝場、單場事件或效率預測；空白不代表0。每季完整表與共同截止日另見 [season-tables.md](season-tables.md)。','');
for(const [groupName,group]of Object.entries(a.groups)){
 md.push(`### ${groupName}：${group.seasons.join('、')}`, '',groupName==='four'?'四季主表包含參與倍率選擇的兩個開發季；推論仍以兩盲測季合併為準。':'排除覆蓋不足的敏感度表僅在門檻觸發時另列；兩盲測季原樣合併是C4判讀來源。','');
 if(group.unavailable){md.push(group.unavailable,'');continue;}
 for(const k of p.cutoffs){md.push(`K=${k}`,'','| 版本 | net RMSE | r | 校準斜率 | SD比 | 殘差單場SD | wins MAE | wins RMSE | 效率偏差 | 理想縮放RMSE（事後） | 答案倍率（事後） |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');for(const [v,m]of Object.entries(group.cutoffs[k].versions))md.push(`| ${v} | ${['netRMSE','netCorrelation','calibrationSlope','netSDRatio','residualSD','winMAE','winRMSE','efficiencyBias','oracleRMSE','calibrationSlope'].map(key=>f(m[key])).join(' | ')} |`);const rs=group.seasons.map(s=>a.seasons[s][k].realResidual.SD);md.push('',`同口徑真實後段殘差SD（季別等權平均）：${f(rs.reduce((s,x)=>s+x,0)/rs.length)}。`,'');}
}
md.push('## C0與凍結稽核','',`補充登記時間：${p.registeredAt}（UTC）。[prereg-supplement.json](prereg-supplement.json) 的 [SHA-256](prereg-supplement.sha256)：${hash(root+'/prereg-supplement.json')}。v5規格SHA-256仍為${p.v5FreezeHash}。下載前檢查兩季資料目錄不存在；原v5來源雜湊均通過核對。`,'',
'| K | m4原值 | ms原值 | 凍結c(K) |','|---:|---:|---:|---:|');
const b=read('reports/defense-eighth/b/v5-freeze.json');for(const k of p.cutoffs)md.push(`| ${k} | ${p.outputCalibration.m4[k]} | ${p.outputCalibration.ms[k]} | ${b.c[k]} |`);
md.push('', 'C0保留原B4的jointBootstrap欄位（5000次）供來源追溯；本批執行採補充規定bootstrap.replicates=20000及confirmation規則，產物逐格驗證實際次數。原每K的OR判準保留，新確認等級依C0補充規定。');
md.push('', '20seed為20261012–20261031。聯合bootstrap20,000次，RNG20261082；跨季共用franchise與seed抽樣，95%取2.5／97.5百分位，99.8%取0.1／99.9百分位。數值倍率、模型選擇與判準未因盲測結果修改。','',
'## C1資料品質與缺場','', '| 球季 | 嚴格可用／1230 | 覆蓋率 | 85%門檻 | 陣容有效球員分鐘MAE（秒） | 嚴格缺場 |','|---|---:|---:|---|---:|---:|');
for(const [s,x]of Object.entries(q.seasons))md.push(`| ${s} | ${x.strictUsableGames} | ${f(x.strictCoverage*100,2)}% | ${x.coverageInsufficient?'覆蓋不足':'通過'} | ${f(x.minuteValidation.meanAbsoluteSeconds,4)} | ${x.failureCount} |`);
md.push('',`下載時序稽核：${Object.entries(audit.downloadChronology).map(([s,x])=>`${s}最早抓取${x.earliestFetchedAt}`).join('；')}，均晚於C0登記。訓練日期、20seed配對、消融沿用原校準及來源雜湊見 [execution-audit.json](execution-audit.json)。`);
md.push('',a.coverageInsufficientSeasons.length?`覆蓋不足球季：${a.coverageInsufficientSeasons.join('、')}；原樣照跑，排除該季的合併表另列。`:'四季均≥85%，「排除覆蓋不足球季」門檻未觸發。','',
'兩盲測季皆取得1230場box及1230場PBP，嚴格缺場由原陣容／分鐘、回合與計數稽核產生，未手改。完整失敗原因、每隊／每月及隊×月分布見 [quality.json](quality.json) 與 [quality.md](quality.md)。','',
'2023–24依NBA官方Regular Season leaguegamelog建立1230場、各隊82場賽程；季中錦標賽決賽0062300001不在賽程，其餘錦標賽例行賽場次保留。NBA亦明定只有決賽不計入例行賽：[NBA官方公告](https://pr.nba.com/nba-announces-group-play-schedule-for-inaugural-in-season-tournament/)。稽核保存八強／四強日期的場次清單。','',
'## C5診斷：事後探索，不作驗收','', '| 球季 | K | v4答案倍率 | simple答案倍率 | v4／simple | 開發m4／ms |','|---|---:|---:|---:|---:|---|');
for(const [s,cs]of Object.entries(a.exploration.oracle))for(const [k,x]of Object.entries(cs))md.push(`| ${s} | ${k} | ${f(x.v4)} | ${f(x.simple)} | ${f(x.ratio)} | ${f(x.m4)} / ${f(x.ms)} |`);
md.push('', '此表顯示季間倍率變動，盲測答案倍率沒有用來重估m4、ms或c。與開發季0.874／0.807／0.731及1.001／0.830／0.721並列檢查，點估計接近與否不作預測成績或驗收結論。','',
'| 盲測季 | K | v4／simple | 開發季比值範圍 | 是否在範圍內／超出量 |','|---|---:|---:|---|---|');
for(const s of p.blindSeasons)for(const k of p.cutoffs){const dev=p.developmentSeasons.map(d=>a.exploration.oracle[d][k].ratio),lo=Math.min(...dev),hi=Math.max(...dev),x=a.exploration.oracle[s][k].ratio;md.push(`| ${s} | ${k} | ${f(x)} | ${f(lo)}–${f(hi)} | ${x<lo?'低於範圍 '+f(lo-x):x>hi?'高於範圍 '+f(x-hi):'範圍內'} |`);}
md.push('', '範圍內外只是描述既有兩季倍率的移動量，沒有新增「接近」的驗收門檻。','',
'### v4分散來源：3seed逐項關閉','', '各消融保留原v4訓練期聯盟校準，不重估常數。變異為30隊3seed平均net的母體變異。邊際占比=(V全開−V關閉)/V全開，可為負，也不必合计100%；未把交互作用或3seed雜訊藏成能力占比。協方差記帳占比Cov(net,net−消融net)/Var(net)加上殘餘項在代數上合計100%，同樣不是因果占比。','',
'| 球季 | K | 全開net變異 | 進攻先驗邊際占比 | 進攻殘差 | 防守訊號 | 分鐘分配 |','|---|---:|---:|---:|---:|---:|---:|');
for(const s of [...p.developmentSeasons,...p.blindSeasons])for(const k of p.cutoffs){const d=read(`${root}/ablation/${s}/calendar-${k}/diagnostic.json`);md.push(`| ${s} | ${k} | ${f(d.allVariance)} | ${Object.values(d.ablations).map(x=>f(x.marginalShare*100,1)+'%').join(' | ')} |`);}
md.push('', '| 球季 | K | 進攻先驗協方差記帳 | 進攻殘差 | 防守訊號 | 分鐘分配 | 殘餘 | 合計 |','|---|---:|---:|---:|---:|---:|---:|---:|');
for(const s of [...p.developmentSeasons,...p.blindSeasons])for(const k of p.cutoffs){const d=read(`${root}/ablation/${s}/calendar-${k}/diagnostic.json`);md.push(`| ${s} | ${k} | ${Object.values(d.ablations).map(x=>f(x.covarianceContribution*100,1)+'%').join(' | ')} | ${f(d.covarianceRemainder*100,1)}% | ${f(d.covarianceSum*100,1)}% |`);}
md.push('', '消融的net變化RMS、全部協方差記帳占比、原預測與卡片／seed來源保存在ablation/<season>/calendar-K/diagnostic.json。防守消融照登記關閉五個訊號開關，也會關掉shortFG通道內的角色防守投影效果；C0文字稱該效果未涵蓋是語意誤述。實際開關照登記執行，未改預先登記或任何主比較；本項只能解讀成部署防守訊號合計的消融。','',
'## 推測、失敗項目與限制','',
'已驗證事實是主表數值、兩種聯合區間、確認等級及稽核結果。消融只揭示模型內部的邊際反應，尚不能將盲測誤差因果歸給某一種球員資訊。','',
'v1沿用A階段的舊事件機制；新犯規／失誤類別／獨立違例旋鈕不能在v1產生相同反應，校準紀錄仍完整保存，未加入新機制使其對齊。v3對v1同時改了記帳與事件，不能當作純防守訊號增益；純訊號比較是(a) v3對signals-off。','',
'失敗與未完成的驗證：確認退步、單點成立及未能確認改善的項目如C4表，不拿點估計補成成功。「分不出」代表區間不足以辨別方向，不等於已證實無效。v5仍沿B階段只作球隊強度層，個人FG門檻未過，這批沒有修改球員卡。輸出層校準不提供勝場預測。資料品質嚴格缺場全部公布，未手改。','',
'聯合區間含球隊與Monte Carlo seed抽樣，未涵蓋重新建卡、球季抽樣或逐場賽果的額外重抽；兩個新球季仍是有限盲測樣本。日曆測試已知未來實際出賽名單／先發，能力、分鐘目標及聯盟常數只用截止日前資料，屬條件式預測。四季主表含開發選擇資料，改善宣稱只看兩盲測季與跨季確認規則。','',
'截止日稽核的範圍：比賽表現、陣容區段、tracking與校準樣本依截止日篩選。靜態球員身份、身高／體重及體型排名沿用凍結流程取得的該季bio；API沒有歷史發布時間，不能由本次稽核證明這份體型快照在截止日已發布。這是凍結輸入的時間戳限制，未因此回頭修改版本，也未把bio中的整季表現欄位當作能力估計資料。','',
'與估算不符之處：開發倍率仍精確重現，盲測倍率差異見C5表，不用開发估算代替盲測量測。C0防守消融說明的一處通道歸因誤述已明列，主版本、規則與登記檔均未改。','',
'## 重跑指令與停止點','', '```powershell','node scripts/fetch_defense_seventh_season.js 2023-24','node scripts/fetch_defense_seventh_season.js 2022-23','node scripts/prepare_defense_seventh_season.js 2023-24','node scripts/prepare_defense_seventh_season.js 2022-23','node scripts/audit_defense_eighth_c_quality.js','node scripts/campaign_defense_eighth_c.js 2023-24','node scripts/campaign_defense_eighth_c.js 2022-23','node scripts/campaign_defense_eighth_c_development.js','node scripts/diagnose_defense_eighth_c_ablation.js 2023-24','node scripts/diagnose_defense_eighth_c_ablation.js 2022-23','node scripts/assess_defense_eighth_c.js','node scripts/report_defense_eighth_c.js','node test/defense_eighth_c.js --artifacts','```','',
'C0與v5凍結檔拒絕覆寫；完整快取可重用。不能因結果改版本、倍率、資料或判準。完成C後停下，不開始下一批。','');
const append=['# C階段：所有可定義指標的成對聯合區間',''];for(const [name,g]of Object.entries(a.groups))for(const [k,cell]of Object.entries(g.cutoffs)){append.push(`## ${name} K${k}`,'','| 比較 | 指標 | 差值 [95%] | 差值 [99.8%] |','|---|---|---:|---:|');for(const c of p.comparisons)for(const [key,x]of Object.entries(cell.pairs[c.id]))if(x?.ci95)append.push(`| ${names[c.id]} | ${key} | ${ci(x)} | ${ci(x,'ci998')} |`);append.push('');}
const quality=['# C階段資料稽核：完整缺場與分布',''];for(const [s,x]of Object.entries(q.seasons)){quality.push(`## ${s}`,'',`${x.strictUsableGames}/1230，${f(x.strictCoverage*100,2)}%。`,'','| 球隊 | 嚴格缺場 |','|---|---:|');for(const t of x.byTeam)quality.push(`| ${t.name} | ${t.missing} |`);quality.push('','| 月份 | 例行賽場次 | 嚴格缺場 |','|---|---:|---:|');for(const m of x.byMonth)quality.push(`| ${m.month} | ${m.total} | ${m.missing} |`);quality.push('','| GameID | 日期 | 主隊ID | 客隊ID | 原稽核原因 |','|---|---|---:|---:|---|');for(const g of x.failures)quality.push(`| ${g.id} | ${g.date} | ${g.homeId} | ${g.awayId} | ${Object.keys(g.reasons).join(', ')} |`);quality.push('','完整原始錯誤與隊×月交叉表見quality.json。','');}
const seasonsMD=['# 各季完整表（單季描述；驗收只看兩盲測季聯合區間）',''];
const hypothesisIndex=md.indexOf('## 推測、失敗項目與限制');md[hypothesisIndex]='## 推測（未驗證，不作驗收）';
md.splice(hypothesisIndex+2,0,'新球季中，關閉先驗的變異反應最大；關閉殘差在2023–24減少變異、在2022–23反而增加變異。可能是殘差在部分球季抵銷先驗的極端值，或屬性投影與輪替交互作用，使殘差倍率無法直接控制球隊分散。本次只量到模型內反應，沒有把先驗估計誤差與投影誤差分開，不能當成已證實的失敗原因。','');
const failureIndex=md.findIndex(x=>x.startsWith('失敗與未完成的驗證：'));md.splice(failureIndex,0,'## 失敗與未解決項目','');
const limitIndex=md.findIndex(x=>x.startsWith('聯合區間含球隊'));md.splice(limitIndex,0,'## 限制','');
const estimateIndex=md.findIndex(x=>x.startsWith('與估算不符之處：'));md.splice(estimateIndex,0,'## 與估算不符之處','');
md.splice(estimateIndex+3,0,'','事後比值：2023–24為0.837／0.758／0.761，2022–23為0.678／0.696／0.606。沒有穩定重現兩個開發季的比值範圍；尤其2022–23三個K都更低。這是事後描述，不新增接近程度的驗收門檻，也不重估凍結倍率。','');
const drift=p.blindSeasons.flatMap(s=>p.cutoffs.map(k=>({s,k,delta:a.seasons[s][k].versions.v4.efficiencyBias}))).filter(x=>Math.abs(x.delta)>.5),noteIndex=md.indexOf('## 失敗與未解決項目');
if(drift.length)md.splice(noteIndex+2,0,`額外失敗觀察：盲測v4聯盟效率偏差超過±0.5的格子為${drift.map(x=>`${x.s} K${x.k}: ${f(x.delta)}`).join('；')}分／百回合。這不是C4新增否決門檻，但不能說聯盟均值已穩定跨季對齊；v4cal沒有事件或效率輸出，去均值縮放也不修正這些偏差。這一批保留漂移，不回頭調參。`,'');
for(const [s,cells]of Object.entries(a.seasons))for(const [k,cell]of Object.entries(cells)){
 seasonsMD.push(`## ${s} K${k}`,'',`共同日曆截止日${cell.date}；全例行賽訓練${cell.allTrainingGames}場、嚴格陣容訓練${cell.trainingGames}場。各隊已打${Math.min(...Object.values(cell.teamGP))}–${Math.max(...Object.values(cell.teamGP))}場。${p.developmentSeasons.includes(s)?'開發季，已看過答案。':'凍結後盲測季。'}`,'','| 版本 | net RMSE | r | 校準斜率 | SD比 | 殘差單場SD | wins MAE | wins RMSE | 效率偏差 | 理想縮放RMSE（事後） | 答案倍率（事後） |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|');
 for(const [v,m]of Object.entries(cell.versions))seasonsMD.push(`| ${v} | ${['netRMSE','netCorrelation','calibrationSlope','netSDRatio','residualSD','winMAE','winRMSE','efficiencyBias','oracleRMSE','calibrationSlope'].map(key=>f(m[key])).join(' | ')} |`);seasonsMD.push('',`同口徑真實後段殘差SD：${f(cell.realResidual.SD)}（${cell.realResidual.games}場points-valid PBP）。`,'');
}
const reportCommandIndex=md.indexOf('node scripts/report_defense_eighth_c.js');if(reportCommandIndex>=0)md.splice(reportCommandIndex,0,'node scripts/audit_defense_eighth_c_execution.js');
fs.writeFileSync(root+'/closeout.md',md.join('\n').replaceAll('区','區').replaceAll('计','計').replaceAll('发','發')+'\n');fs.writeFileSync(root+'/paired-intervals.md',append.join('\n')+'\n');fs.writeFileSync(root+'/quality.md',quality.join('\n')+'\n');fs.writeFileSync(root+'/season-tables.md',seasonsMD.join('\n')+'\n');
fs.writeFileSync(root+'/closeout.json',JSON.stringify({headline,stage:'C',baseline:'nba-defense-v3',nextBatchStarted:false,confirmed,worsened,single,sources:Object.fromEntries(['prereg-supplement.json','assessment.json','quality.json','execution-audit.json'].map(f=>[root+'/'+f,hash(root+'/'+f)])),outputHashes:Object.fromEntries(['closeout.md','paired-intervals.md','quality.md','season-tables.md'].map(f=>[root+'/'+f,hash(root+'/'+f)])),reportCode:hash('scripts/report_defense_eighth_c.js')},null,2)+'\n');console.log(headline);

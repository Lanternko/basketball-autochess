import fs from 'node:fs';
const root='reports/defense-tenth/step4-t1';
const read=p=>JSON.parse(fs.readFileSync(p));
const a=read(root+'/analysis.json'),p=read(root+'/protocol.json'),real=read(root+'/real-diagnostics.json');
const n=(v,d=3)=>v===null||v===undefined?'—':v.toFixed(d);
const source=(t)=>t==='task1'?'任務一：同季全季':'任務二：A2 前季卡／答案側診斷';
const columns='| 球季 | 版本 | net RMSE | Spearman | 勝場 MAE | 勝場 RMSE | 校準斜率 | SD 比 | net／勝場失敗數 |\n|---|---|---:|---:|---:|---:|---:|---:|---:|';
const metricRow=c=>`| ${c.season} | ${c.version} | ${n(c.metrics.netRMSE)} | ${n(c.metrics.Spearman)} | ${n(c.metrics.winsMAE)} | ${n(c.metrics.winsRMSE)} | ${n(c.metrics.calibrationSlope)} | ${n(c.metrics.SDRatio)} | ${c.failures.filter(f=>f.axis==='net').length}／${c.failures.filter(f=>f.axis==='wins').length} |`;
const failures=['# T1 全部失敗隊','', '每個版本／球季按兩條軸分開列。攻守誤差均為各季各版本去均值的場均分；正值高估該端強度，負值低估。前五／倒五依該軸真實排名判斷；平均同順位。歸因不能豁免失敗。'];
for(const c of a.cells){
  failures.push('',`## ${source(c.task)} · ${c.season} · ${c.version}`,'', '| 軸 | 球隊 | 類型 | 真實→預測名次 | net 誤差 | 進攻 O | 防守 D | 勝場誤差 | 歸因 |','|---|---|---|---:|---:|---:|---:|---:|---|');
  if(!c.failures.length)failures.push('| — | 無失敗隊 | 通過兩軸 | — | — | — | — | — | — |');
  for(const f of c.failures)failures.push(`| ${f.axis} | ${f.name} | ${f.type} | ${f.actualRank}→${f.predictedRank} | ${n(f.netError,2)} | ${n(f.O,2)}（${f.offenseDirection}） | ${n(f.D,2)}（${f.defenseDirection}） | ${n(f.winsError,2)} | ${f.status} |`);
  for(const f of c.failures.filter(f=>f.flags.length)){
    failures.push('',`- ${f.name}（${f.axis}）：`+f.flags.map(flag=>flag.category==='缺前季個人樣本'?`缺前季卡占真實分鐘 ${n(flag.share*100,1)}%；L2 名次 ${flag.L2Rank}，誤差 ${n(flag.L2Error,2)}；未同時達到消除誤排與解釋一半。`:`接戰 ${flag.closeGames} 場、勝率 ${n(flag.closeWinRate*100,1)}%，實際−淨勝分期望勝場 ${n(flag.contribution,2)}；反事實名次 ${flag.counterfactualActualRank}，仍不足以解釋。`).join(' '));
  }
}
fs.writeFileSync(root+'/failures.md',failures.join('\n')+'\n');
const errors=['# T1 全部逐隊攻守誤差','', 'O=模擬得分−真實得分；D=真實失分−模擬失分。主欄各自去聯盟均值，O+D=去均值net誤差。原始欄保留共同偏差，不把共同失分變化誤認成個人防守能力。'];
for(const c of a.cells){
  errors.push('',`## ${c.task} ${c.season} ${c.version}`,'',`聯盟共同 O=${n(c.metrics.offenseBias)}，D=${n(c.metrics.defenseStrengthBias)} 分／場。`,'','| 球隊 | net 真實→預測名次 | 勝場真實→預測名次 | net 誤差 | O | D | 原始 O | 原始 D |','|---|---:|---:|---:|---:|---:|---:|---:|');
  for(const t of c.teams)errors.push(`| ${t.name} | ${t.actualNetRank}→${t.netRank} | ${t.actualWinsRank}→${t.winsRank} | ${n(t.netError,2)} | ${n(t.O,2)} | ${n(t.D,2)} | ${n(t.rawO,2)} | ${n(t.rawD,2)} |`);
}
fs.writeFileSync(root+'/team-errors.md',errors.join('\n')+'\n');
const diagnostics=['# T1 客觀異常指標','', '僅為評分答案與反事實診斷，從未回寫預測。接戰／勝場轉換不等同證明隨機運氣；clutch 指標不等同球員能力。'];
for(const [season,j] of Object.entries(real)){
  diagnostics.push('',`## ${season}`,'',`PBP 稽核 ${j.validGames}/${j.games}；不合格／缺場 ${j.failures.length} 場，完整清單見 real-diagnostics.json。`,'','| 球隊 | 有效場次 | clutch分鐘 | clutch net/48 | 其餘net/48 | clutch影響/場 | 接戰勝/場 | 實際−期望勝場 | 觸發異常 |','|---|---:|---:|---:|---:|---:|---:|---:|---|');
  for(const t of j.teams)diagnostics.push(`| ${t.name} | ${t.validGames}/${t.games} | ${n(t.clutchMinutes,1)} | ${n(t.clutchNetPer48,2)} | ${n(t.nonclutchNetPer48,2)} | ${n(t.clutchImpact,2)} | ${t.closeWins}/${t.closeGames} | ${n(t.winExcess,2)} | ${[t.clutchFlag?'末段':'',t.luckFlag?'轉換':''].filter(Boolean).join('、')||'無'} |`);
}
fs.writeFileSync(root+'/real-diagnostics.md',diagnostics.join('\n')+'\n');
const task1=a.cells.filter(c=>c.task==='task1'),task2=a.cells.filter(c=>c.task==='task2');
const failedRows=a.cells.flatMap(c=>c.failures),uniqueFailTeams=new Set(a.cells.flatMap(c=>c.failures.map(f=>[c.task,c.season,c.version,f.id].join('/'))));
const report=[
'# 第十批第四步 T1：新及格線重新評分', '',
'**T1 完成並停下。2025–26 的凍結 v3 通過兩條排名線；v1 不通過。A2 的 L1、L2 在三季均未通過。純卡的四季「全季同季重現」仍缺輸出，不能由截止後測試代替；因此尚不能判定純卡完成任務一，也不能由 L2 宣稱換隊可用。** 全部為已看過答案的既有結果，未跑任何新模擬。', '',
`事前登記 ${p.registeredAt}；protocol SHA-256：\`${a.protocolHash}\`。A/A2 與 src 998 個既有檔案在登記前封存檔案雜湊；完成後逐檔核對，見 completion-audit.json。`, '',
'## 規則與口徑', '',
'net 排名為主要球隊強弱評分，另以勝場排名獨立套同門檻：真實前五預測第11名起失敗；真實倒五預測第20名以內失敗。先取20 seed平均再排名；同值使用平均順位。版本總及格要求兩條軸均無失敗。歸因不免除失敗。net RMSE按30隊去均值；Spearman不是Pearson。', '',
'歸因規則先寫死：末五分鐘且前一事件分差≤5，至少40分鐘、PBP覆蓋≥85%、末段與其餘net/48差至少10、整季影響至少0.75分／場；接戰最終差≤5、至少15場、勝率偏離50%至少15個百分點、實際與得失分期望差至少3勝；缺前季樣本占真實分鐘至少10%。旗標還必須方向吻合、能消除該軸誤排且降低至少50%誤差，才記支持解釋。教練／戰術一律不當解釋。這些門檻是預先登記的診斷約定，不等同统计顯著性。', '',
'期望勝場固定用得失分的14次方換算；這是此次登記的診斷慣例，沒有對答案選指數，也沒有修改任何模型勝場。clutch影響用相同隊其餘時間的得分差率替換末段，缺PBP的賽季影響按有效場數外推。這些是觀察／答案側反事實，不能證明因果或證明都是運氣。', '',
'## 已驗證：任務一', '',columns,...task1.map(metricRow),'',
'| 球季 | 純卡全季 | 凍結 v3 | v1 | simple 全季 |','|---|---|---|---|---|',
...p.seasons.map(s=>`| ${s} | 缺 | ${s==='2025-26'?'有：通過':'缺'} | ${s==='2025-26'?'有：失敗':'缺'} | 缺 |`),'',
'所要求16格只有2格有合格範圍的既有輸出。2022–23／2023–24／2024–25 v1與v3只有K25/41/55截止後結果；四季純卡也只有截止後結果，缺「全季當季卡＋五訊號全關/no-map＋全季20 seed」。simple既有結果使用截止前或前季net預測後段；沒有同季全季simple預測，直接複製全年答案得到零誤差不是預測，本次沒有創造這種結果。缺格不是失敗，也不是通過。', '',
'2025–26全季v1/v3採真實逐場名單與分鐘軟目標，並非精確逐秒換人重播；重讀既有20 seed確認平均球員逐場分鐘誤差v1為1.400、v3為1.480分鐘。v3還含區段估計防守訊號，通過不能冒稱純卡通過。全部使用當季資料，因此也不是跨季獨立驗證。', '',
'## 已驗證：任務二的既有診斷', '',columns,...task2.map(metricRow),'',
'L1沿用前季卡，新人／無前季樣本仍是統一先驗；L2只把這些人替換為目標季個人卡。L2排除了「沒有新人真實卡」這個輸入問題，卻不是只針對換隊球員的獨立檢定，也沒有把所有老球員改成當季卡。兩版已知目標季逐場出賽與分鐘，但採預先排定賽程、依球隊場次序號映射曝光，與真實對手順序不完全一致。這限制了直接判斷「任何換隊都可用」。', '',
'| 球季 | 雷霆真實 net 名次 | v1全季 | v3全季 | L1 net/勝場名次 | L2 net/勝場名次 |','|---|---:|---:|---:|---:|---:|',
...task2.filter(c=>c.version==='L1').map(c=>{const l2=task2.find(x=>x.season===c.season&&x.version==='L2');return `| ${c.season} | ${c.okc.actualNetRank} | ${c.season==='2025-26'?task1[0].okc.netRank:'缺'} | ${c.season==='2025-26'?task1[1].okc.netRank:'缺'} | ${c.okc.netRank}/${c.okc.winsRank} | ${l2.okc.netRank}/${l2.okc.winsRank} |`; }),'',
'## 失敗隊與歸因', '',
`合計 ${uniqueFailTeams.size} 個版本×球季×失敗隊、${failedRows.length} 筆軸別失敗，**全部仍有「無法解釋」的殘餘**：不是沒有客觀訊號，而是沒有通過本次事前登記的完整歸因門檻。已量出的部分贡献照樣列出。完整清單與攻防方向見 [failures.md](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step4-t1/failures.md)，30隊全量誤差見 [team-errors.md](D:/Projects/CODING/basketball-autochess/reports/defense-tenth/step4-t1/team-errors.md)。`, '',
'- 2025–26 v1：溜馬被高估，主要防守D +5.64；尼克被低估，防守D −6.84、進攻O +1.63。兩者未觸發能解釋誤排的末段／接戰旗標。',
'- 2023–24 雷霆：L1新球員先驗占22.95%真實分鐘，L2 net改善6.29分／場、名次24→14；這是缺樣本確實造成部分損失的模式內證據，仍有−6.43分／場誤差、仍失敗，不能當成完整歸因。',
'- 2025–26 L2：尼克O +1.88、D −7.99；塞爾提克O +3.50、D −8.67；溜馬O +5.38、D +4.33。防守誤差方向可量出，尚沒有可攜防守能力的客觀原因支持；不填「體系／教練」。',
'- 2024–25爵士L1：接戰20場只贏5場，實際比得失分期望少3.13勝；但模型仍高估17.65勝，這項不足以消除誤排或解釋一半。', '',
'## 推測與不能推出的結論', '',
'部分強隊低估集中在防守，例如尼克與塞爾提克；這支持下一項盤點防守訊號，但不能單憑誤差反推出護框／嚇阻／對位哪一欄缺失。L2仍錯也不能直接歸因相性，因為老球員能力仍沿用前季、曝光與對手映射亦有差異。', '',
'排名門檻通過只表示未把兩端球隊嚴重排錯，不表示數值準確：v3全季仍有2.555分net RMSE、5.070勝MAE。既有v1/v3全季比較主要只曾提供seed條件區間，本次未拿它宣稱普遍顯著改善；A2已有球隊＋seed聯合區間原樣附於analysis.json。', '',
'## PBP稽核與失敗項目', '',
'| 球季 | 有效PBP／全季場次 | 完整失敗／缺場數 |','|---|---:|---:|',
...Object.entries(real).map(([s,j])=>`| ${s} | ${j.validGames}/${j.games} | ${j.failures.length} |`),'',
'完整場次失敗理由保存在real-diagnostics.json；包含缺PBP、時鐘／比分回退或不符官方box，不手動修補。按隊的覆蓋與末段／接戰計數見real-diagnostics.md；來源逐檔SHA見source-audit.json。每隊覆蓋均須另過85%才可歸因。', '',
'本項沒有補齊缺少的全季模擬、沒有改卡、沒有改引擎、沒有開始T2／T3／T4。', '',
'## 重跑', '',
'在專案根目錄執行（只有重新讀取既有資料與評分）：', '',
'```powershell', 'node reports/defense-tenth/step4-t1/analyze.mjs','node reports/defense-tenth/step4-t1/report.mjs','node reports/defense-tenth/step4-t1/audit.mjs','```', '',
'register.mjs只建立新protocol，已有登記時會拒絕覆蓋，不應再次執行。T1完成後停下。'
];
fs.writeFileSync(root+'/report.md',report.join('\n')+'\n');
console.log('Reports saved',uniqueFailTeams.size,'failure teams',failedRows.length,'axis rows');

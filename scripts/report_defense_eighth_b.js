import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const root='reports/defense-eighth/b',rules=read(root+'/development-rules.json'),selection=read(root+'/selection.json'),assessment=read(root+'/assessment.json'),players=read(root+'/players.json'),freeze=read(root+'/v5-freeze.json'),ks=rules.cutoffs,seasons=rules.developmentSeasons;
const f=(x,n=3)=>Number.isFinite(x)?x.toFixed(n):'—',ci=x=>`${f(x.estimate)} [${x.ci95.map(v=>f(v)).join(', ')}]`;
const unreachable=ks.filter(k=>!selection.cutoffs[k].targetWithinMappedRange);
const verdict=x=>x.ci95[1]<0?'顯著改善':x.ci95[0]>0?'顯著退步':'分不出';
const pairedSummary=ks.map(k=>{const p=assessment.combined[k].pairs['v5-minus-v4'];return `${k}場的netRMSE／winsMAE：${verdict(p.netRMSE)}／${verdict(p.winMAE)}`;}).join('；');
const headline=`階段 B 完成並凍結v5：c(25)=${f(freeze.c[25],6)}、c(41)=${f(freeze.c[41],6)}、c(55)=${f(freeze.c[55],6)}。兩開發季合併的v5對v4聯合區間判讀：${pairedSummary}。${unreachable.length?`${unreachable.join('／')}場切分的simple斜率超出實測分段對應的可達範圍；只縮進攻殘差的校準機制未達該目標。`:''}${players.teamStrengthOnly?'個人FG門檻未全過，v5只作球隊強度層，不作已驗證球員卡。':'兩個開發季的個人FG門檻全過，仍待盲測。'}所有本批成績均為「開發季，已看過答案」；正式基準維持v3。2023–24／2022–23尚未下載，階段C未開始。`;
const md=['# 第八批修訂：階段 B 凍結v5','',headline,'','## 已驗證事實：B1答案倍率比值','',
'答案倍率是真實後段net對預測net的斜率。比值只驗算兩個開發季已知結果，不是預測成績，不直接套成球員殘差倍率。','',
'| 開發季 | K | v4答案倍率／simple | v3答案倍率／simple |','|---|---:|---:|---:|'];
for(const s of seasons)for(const k of ks){const x=selection.oracleRatios[s][k];md.push(`| ${s} | ${k} | ${f(x.v4)} | ${f(x.v3)} |`);}
md.push('', '你的估算重現：2024–25 v4為0.874／0.807／0.731，2025–26為1.001／0.830／0.721；與0.87／0.81／0.73及1.00／0.83／0.72只有四捨五入差異。', '',
'## B2固定倍率、實際對應與校準','',
'每個K一個c，兩季共用，既不按隊、球員，也不按季指定。唯一能力差異是role模型offenseResidual乘c，先驗、防守殘差、分鐘、B1及引擎保持v4流程；乘c後依原訓練分鐘去均值，沿用原投影。倍率1與v4能力卡及測試比分完全一致，開關關閉即c=1。','',
'先固定規則再測：c=0／0.5／1各20seed；1重用凍結v4。測試各倍率時，仍用v4同一訓練期聯盟校正方法（3seed、最多5輪），數值重估但方法不變。從實際30隊預測向量建立分段線性對應，再搜尋c讓兩季平均校準斜率最靠近兩季平均simple斜率。10001格全域搜尋＋80步局部黃金搜尋，c取六位小數；只看斜率差距，不以netRMSE、勝場或個人數據挑選。選定後只驗證一次完整20seed，未因驗證結果再改c。','',
'| K | 選定c | pooled v4斜率 | pooled simple目標 | 對應預估v5斜率 | 實跑v5斜率 | 實跑−目標 |','|---:|---:|---:|---:|---:|---:|---:|');
for(const k of ks){const s=selection.cutoffs[k],a=assessment.combined[k];md.push(`| ${k} | ${f(s.c,6)} | ${f(s.v4Slope)} | ${f(s.targetSimpleSlope)} | ${f(s.mappedSelectedSlope)} | ${f(a.actualV5Slope)} | ${f(a.achievedGap)} |`);}
md.push('', '「合併斜率」沿A2採每季斜率等權平均；不是把60隊直接混成一個含跨季均值的迴歸。聯盟層級倍率c(K)來自兩開發季的事後meta校準；每季能力卡及事件聯盟常數仍由截止日前資料估計。對應預估最接近目標不等於最終引擎精確達到目標；實跑差距照實列出。','',
'| K | c∈[0,1]的對應斜率範圍 | simple目標在範圍內 |','|---:|---:|---|');
for(const k of ks){const x=selection.cutoffs[k];md.push(`| ${k} | ${x.mappedRange.map(v=>f(v)).join('–')} | ${x.targetWithinMappedRange?'是':'否：此開關不足以達標'} |`);}
md.push('',
'| 開發季 | K | c0斜率 | c0.5斜率 | c1斜率 | 半點與端點線性中點net差RMS | 占端點net變化RMS | c0／0.5／1對v4的球隊倍率 |','|---|---:|---:|---:|---:|---:|---:|---|');
for(const k of ks)for(const x of selection.cutoffs[k].seasons){const n=x.nonlinearity;md.push(`| ${x.season} | ${k} | ${f(x.summaries[0].calibrationSlope)} | ${f(x.summaries[.5].calibrationSlope)} | ${f(x.summaries[1].calibrationSlope)} | ${f(n.midpointRMS)} | ${f(n.relativeMidpointError*100,1)}% | ${[0,.5,1].map(c=>f(n.teamScaleRegression[c])).join(' / ')} |`);}
md.push('', '殘差c不是球隊總net的倍率：先驗與防守保留。投影邊界、非線性出手反應、重新估出的聯盟常數及模擬抽樣是可能使對應偏離直線的來源，尚未逐項歸因。半點RMS中也含有限20seed雜訊，不能全部稱為結構非線性；所以採實測向量分段對應，而不是直接使用B1答案比值。','',
'| 開發季 | K | 進攻先驗SD（logPPP） | 可縮放進攻殘差SD（logPPP） |','|---|---:|---:|---:|');
for(const k of ks)for(const x of selection.cutoffs[k].seasons)md.push(`| ${x.season} | ${k} | ${f(x.abilitySpread.priorOffenseSD,4)} | ${f(x.abilitySpread.offenseResidualSD,4)} |`);
md.push('', '以上是訓練分鐘加權的球員值母體SD；證實可縮放的殘差遠小於保留的先驗，但不是球隊誤差的因果分解。沒有證據把所有過度分散歸給這個殘差，也沒有改縮先驗或防守來湊目標。','',
'## B3：開發季，已看過答案','',
'下列均不構成新球季預測驗收。20seed同20261012–31；誤差為30隊去均值RMSE與剩餘實際場數勝場誤差。相關／斜率／SD採逐隊平均，聯盟偏差採合併計數。所有成對結論只用球隊＋seed聯合5000次bootstrap。','',
'| 開發季 | K | 版本 | net RMSE | r | 校準斜率 | SD比 | wins MAE | wins RMSE |','|---|---:|---|---:|---:|---:|---:|---:|---:|');
for(const s of seasons)for(const k of ks)for(const v of ['v3','v4','v5','simple','shrink']){const m=assessment.seasons[s][k].versions[v].metrics;md.push(`| ${s} | ${k} | ${v} | ${['netRMSE','netCorrelation','calibrationSlope','netSDRatio','winMAE','winRMSE'].map(z=>f(m[z])).join(' | ')} |`);}
md.push('', '| 開發季 | K | v5−v4 net RMSE [聯合95%] | v5−v4 wins MAE [聯合95%] | v5−較強對照net [聯合95%] | v5−較強對照wins [聯合95%] |','|---|---:|---:|---:|---:|---:|');
for(const s of seasons)for(const k of ks){const p=assessment.seasons[s][k].pairs;md.push(`| ${s} | ${k} | ${ci(p['v5-minus-v4'].netRMSE)} | ${ci(p['v5-minus-v4'].winMAE)} | ${ci(p['v5-minus-stronger'].netRMSE)} | ${ci(p['v5-minus-stronger'].winMAE)} |`);}
md.push('', '| 開發季合併K | v5−v4 net RMSE [聯合95%] | v5−v4 wins MAE [聯合95%] | v5−較強對照net [聯合95%] | v5−較強對照wins [聯合95%] |','|---:|---:|---:|---:|---:|');
for(const k of ks){const p=assessment.combined[k].pairs;md.push(`| ${k} | ${ci(p['v5-minus-v4'].netRMSE)} | ${ci(p['v5-minus-v4'].winMAE)} | ${ci(p['v5-minus-stronger'].netRMSE)} | ${ci(p['v5-minus-stronger'].winMAE)} |`);}
md.push('', '這次「較強簡單對照」以合併誤差較低者作包絡，每次重抽也重新取兩者較低誤差；net與wins可各自不同。兩對照個別成對區間仍完整保存。這比固定點估計贏家再抽樣多涵蓋對照選擇的變動，沒有把選擇餵進預測器。模型及c沒有在bootstrap內重估，開發選擇偏差不在CI內。','',
'### 個人FG與邊界：開發季，已看過答案','', '| 開發季 | K | v3 FG加權MAE | v4 FG加權MAE | v5 FG加權MAE | v5−v3（pp） | ≤0.3門檻 | v3／v4／v5邊界人數 |','|---|---:|---:|---:|---:|---:|---|---|');
for(const s of seasons)for(const k of ks){const p=players.seasons[s][k];md.push(`| ${s} | ${k} | ${f(p.v3.metrics.FG.MAE)} | ${f(p.v4.metrics.FG.MAE)} | ${f(p.v5.metrics.FG.MAE)} | ${f(p.FGGap)} | ${p.playerGate?'通過':'失敗'} | ${['v3','v4','v5'].map(v=>p[v].bounds.length).join(' / ')} |`);}
md.push('', 'FG是百分點MAE，按後段真實分鐘加權；交易球員以playerID合併。邊界是實際部署並套訓練期聯盟校正後，任一能力屬性碰0／120的唯一球員數；完整名單、PTS/FGA/3P/AST/REB誤差都在 [players.json](players.json)。門檻只判定用途，沒有為了通過再改c。','',
players.teamStrengthOnly?'**個人門檻未全過：v5只當球隊強度層，不當已驗證球員卡或可靠OVR。**':'個人門檻全過；這仍只是開發季，不能替代新球季玩家能力驗證。','',
'## B4凍結與階段C預先判準','',`v5凍結時間：${freeze.frozenAt}。完整規則、c、程式／估計流程來源雜湊見 [v5-freeze.json](v5-freeze.json)，規格檔本身的 [SHA-256](v5-freeze.sha256) 為 ${hash(root+'/v5-freeze.json')}。凍結前確認兩個新球季的data／report目錄均不存在；原v4及以前來源也逐一核對。之後不得依盲測結果修改v5。`,'',
'- C1沿現有抓取與重建稽核，公布2023–24／2022–23嚴格樣本與完整失敗清單，不手改。','- C2每季共同日曆25／41／55，v1／v3-signals-off／v3／v4／v5／simple／shrink，同20seed。simple/shrink沿A規則，能力與聯盟常數只用該季截止日前資料；v5 c表不重新估計。','- C3四季合併作主表，另列兩盲測季合併；各季內去均值，等權合併，franchise與seed跨季配對抽樣。','- C4每個K分別回答五筆比較：v3−signals-off、v4−v3、v5−v4、v4−較強簡單對照、v5−較強簡單對照。只由兩盲測季合併聯合CI回答；不另加舊的「至少兩個切分」成功規則。','- 成立：netRMSE或winsMAE至少一項CI上界<0；其他指標若顯著退步必須同列，OR判準不隱藏代價。','- 不成立：沒有顯著改善，且至少一項CI下界>0。','- 分不出：兩項均跨0，列出兩個區間寬度，不用點估計宣稱改善。','- C5僅檢查新球季答案倍率比是否接近開發季，事後比值不進入v5。','',
'原B1訓練內估斜率與C2成功標準已作廢；此版不使用它們。兩個新球季沒有下載、沒有開盲測。','',
'## 推測、失敗項目、與估算不符之處','',
'推測：保留先驗與防守後，縮小進攻殘差可能改善過度分散，但也可能損失排序資訊；開發季同時用於選c，改善不代表一般化。實測對應中包含模擬雜訊與結構非線性，尚不能分開歸因。','',
'失敗／限制：個人FG門檻與實跑斜率目標差距如上表，不用聯盟後段常數、球隊補丁或再次選c修補。不可達範圍指預定的c∈[0,1]分段實測對應，不是證明任何引擎倍率都無效。盲測尚未做，沒有跨季成功結論。聯合區間仍不含估卡、選c、球季抽樣與名單假設的不確定性。日曆測試沿用已知逐場實際出賽名單／先發的條件式設定，能力、分鐘目標與聯盟常數只用訓練期資料；不代表真正季前預測。','',
'估算核對：B1與你的估算只有四捨五入差异；B1倍率比不是殘差c，兩者不應當作同一個量。','',
'## 重跑指令與停止點','', '```powershell','node scripts/campaign_defense_eighth_b_anchors.js','node scripts/select_defense_eighth_v5.js   # 首次選定；存在selection時拒絕覆寫','node scripts/campaign_defense_eighth_b_final.js','node scripts/assess_defense_eighth_b_players.js','node scripts/assess_defense_eighth_b.js','node scripts/freeze_defense_eighth_v5.js   # 已凍結時拒絕覆寫','node scripts/report_defense_eighth_b.js','node test/defense_eighth_b.js --artifacts','node test/defense_seventh.js','```','',
'完整快取存在時不要再次跑selection或freeze，直接重跑final／assessment／report；不改已凍結內容。真正重跑來源與種子時應另建診斷目錄，不能覆寫凍結選擇。完成B後停下。','');
const appendix=['# 開發季，已看過答案：v5所有成對聯合區間',''];
for(const s of [...seasons,'combined'])for(const k of ks){const cell=s==='combined'?assessment.combined[k]:assessment.seasons[s][k];appendix.push(`## ${s} ${k}`,'','| 比較 | 指標 | 差值與聯合95% |','|---|---|---:|');for(const [name,p]of Object.entries(cell.pairs))for(const [key,x]of Object.entries(p))if(x?.ci95)appendix.push(`| ${name} | ${key} | ${ci(x)} |`);appendix.push('');}
fs.writeFileSync(root+'/paired-intervals.md',appendix.join('\n')+'\n');fs.writeFileSync(root+'/closeout.md',md.join('\n').replaceAll('异','異')+'\n');
fs.writeFileSync(root+'/closeout.json',JSON.stringify({headline,stage:'B',CStarted:false,baseline:'nba-defense-v3',developmentOnly:true,freeze:root+'/v5-freeze.json',sources:Object.fromEntries([root+'/v5-freeze.json',root+'/assessment.json',root+'/players.json','scripts/report_defense_eighth_b.js'].map(p=>[p,hash(p)]))},null,2)+'\n');console.log(headline);

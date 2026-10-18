import fs from 'node:fs';
import {read,hash} from './defense_io.js';
const root='reports/defense-eighth/a',r=read(root+'/analysis.json'),ks=[25,41,55],seasons=['2024-25','2025-26'];
const f=(x,n=3)=>Number.isFinite(x)?x.toFixed(n):'—',interval=(x,mode='joint')=>x?`${f(x.estimate)} [${x[mode].ci95.map(v=>f(v)).join(', ')}]`:'—';
function pair(x,a,b){if(x.pairs[a+'-minus-'+b])return x.pairs[a+'-minus-'+b];const d=x.pairs[b+'-minus-'+a];return Object.fromEntries(Object.entries(d).map(([k,v])=>[k,{...v,estimate:v.estimate===null?null:-v.estimate,...Object.fromEntries(['seed','team','joint','historicalSeed'].filter(m=>v[m]).map(m=>[m,{...v[m],ci95:v[m].ci95.map(n=>n===null?null:-n).reverse()}]))}]));}
const better=x=>x.joint.ci95[1]<0,worse=x=>x.joint.ci95[0]>0,status=x=>better(x)?'顯著改善':worse(x)?'顯著退步':'差異不顯著';
const diagnosis=Object.fromEntries(ks.map(k=>[k,read(`${root}/coverage/diagnosis-${k}.json`)]));
for(const k of ks)for(const v of ['v1','v3-signals-off'])if(!r.seasons['2024-25'][k].models[v])throw Error('Missing complete A5 control '+k+v);
const headline='階段 A 完成，正式基準維持 v3。納入球隊＋seed重抽後，2024–25的v4對v3與兩個簡單對照在淨勝分／勝場均未達顯著差異；第七批只看seed的顯著改善／退步不能照搬。2025–26的v4對v3仍在三個切分顯著改善，但對較強簡單對照的優勢均不顯著。兩季合併對v3的淨勝分只有41場切分顯著改善，勝場MAE三個切分均顯著改善；不能由合併結果聲稱2024單季已成功。B／C尚未開始，未下載2023–24。';
const md=['# 第八批：階段 A','',headline,'','## 已驗證事實與判讀口徑','',
'沿用第七批20seed（20261012–20261031）與共同日曆截止日。A1–A3重用原逐場模擬輸出，沒有重跑v3／v4。A4只重估與離線加總，A5新增v1及v3只關防守訊號的20seed模擬。原版／v1／v2／v3／v4凍結來源未變更。', '',
'相關、SD與去均值RMSE對30隊等權；每次重抽重新計算樣本均值及SD。既有seed區間保留原2000次結果，新seed／球隊／聯合區間5000次。球隊重抽在所有版本同步抽30隊（有放回）；聯合區間再同步重抽20seed。兩季合併時同一NBA franchise一起抽，並在各季內去均值，兩季等權；RMSE先平均MSE再開根號，其餘平均季指標。不混合25／41／55，以免重複計入重疊後段。所有結論以聯合區間為主。', '',
'球隊抽樣補上「效果是否只集中在少數隊」的不確定性，仍未涵蓋重新估卡、球季抽樣、場次相依、受傷／交易假設或模型選擇。NBA30隊並非獨立隨機樣本，球隊間共同比賽的相關亦未完全保留；這是敏感度區間，不是跨季保證。', '',
'單場殘差SD的球隊區間以每場兩端球隊的重抽次數平均作權重，保留原逐場強度扣除；不重估強度。簡單對照無單場生成機制，防守相關與殘差SD記為無資料。', '',
'## A1：淨勝分誤差的兩種精確拆解','',
'令真實SD為σy、預測SD為σx、相關為r。主要拆解：RMSE²＝2σxσy(1−r)＋(σx−σy)²，分別是相關與SD差兩部分。表內列各自平方根；兩列平方相加才等於總RMSE²，不能直接相加。','',
'另一個用來量收縮空間的拆解：RMSE²＝σy²(1−r²)＋(σx−rσy)²。理想收縮倍率β＝rσy／σx，理想RMSE＝σy√(1−r²)。**β與理想RMSE用了後段真實答案，是事後線性校準上限，不是預測成績，也不是不可突破的模型雜訊下限。** 正倍率收縮不改相關；SD比接近1不代表校準正確。','',
'| 季 | K | 版本 | RMSE | r | 真實／預測SD | 相關項√MSE | SD差項√MSE | 理想收縮RMSE | 答案倍率β |','|---|---:|---|---:|---:|---:|---:|---:|---:|---:|'];
for(const s of seasons)for(const k of ks)for(const v of ['v3','v4','simple','shrink']){const d=r.seasons[s][k].models[v].decomposition;md.push(`| ${s} | ${k} | ${v} | ${f(d.centeredRMSE)} | ${f(d.correlation)} | ${f(d.observedSD)} / ${f(d.simulatedSD)} | ${f(d.correlationRMSE)} | ${f(d.sdGapRMSE)} | ${f(d.oracleShrunkRMSE)} | ${f(d.oracleMultiplier)} |`);}
md.push('', '你的2024–25估算重現：v4為4.289／4.835／5.626，簡單對照4.145／4.675／5.437；與4.29／4.84／5.63及4.14／4.68／5.43只有約0.005～0.007的近似／四捨五入差異。用本批精確值四捨五入到兩位，simple是4.14／4.67／5.44。','',
'2024–25即使答案校正v4的分散，其理想RMSE仍比simple多0.144／0.161／0.189；因此分散能解決部分問題，排序差異仍存在。這是描述性上限差，不自行推導成顯著差異或下一批可實現收益。','',
'## A2：含球隊抽樣的成對比較','', '| 季 | K | v4−v3 RMSE [聯合95%] | v4−v3 MAE [聯合95%] | 較強net對照 | v4−對照 RMSE [聯合95%] | 較強wins對照 | v4−對照 MAE [聯合95%] |','|---|---:|---:|---:|---|---:|---|---:|');
for(const s of seasons)for(const k of ks){const x=r.seasons[s][k],p=pair(x,'v4','v3'),bn=x.strongerBenchmarkByMetric.netRMSE,bw=x.strongerBenchmarkByMetric.winMAE;md.push(`| ${s} | ${k} | ${interval(p.netRMSE)} | ${interval(p.winMAE)} | ${bn} | ${interval(pair(x,'v4',bn).netRMSE)} | ${bw} | ${interval(pair(x,'v4',bw).winMAE)} |`);}
md.push('', '較強對照逐指標取兩個事前建立預測器中實測誤差較低者，只用來訂較嚴的評分標竿；可能net與wins不同。這個事後比較包絡不是部署時可用的選擇器，也沒有隱藏落敗對照。完整兩對照及各版本所有成對結果均附上。','',
'| 兩季合併K | v4−v3 RMSE [聯合95%] | v4−v3 MAE [聯合95%] | v4−simple RMSE [聯合95%] | v4−simple MAE [聯合95%] | v4−shrink RMSE [聯合95%] |','|---:|---:|---:|---:|---:|---:|');
for(const k of ks){const x=r.combined[k],p=pair(x,'v4','v3'),q=pair(x,'v4','simple'),z=pair(x,'v4','shrink');md.push(`| ${k} | ${interval(p.netRMSE)} | ${interval(p.winMAE)} | ${interval(q.netRMSE)} | ${interval(q.winMAE)} | ${interval(z.netRMSE)} |`);}
md.push('', '第七批判讀更新：2024–25的55切分「淨勝分顯著退步」與25切分「勝場顯著改善」在聯合區間均不再顯著；2025–26「顯著贏簡單对照」亦不成立。這不是數字改善，而是把原來遺漏的球隊不確定性補回。對v3的2025改善仍成立。','',
'既有seed、重算seed、球隊與聯合區間全部並列於 [成對區間附表](paired-intervals.md)；含六個主指標及殘差SD、防守相關／SD比、勝場斜率等，JSON附標準誤。','',
'## A3：只用訓練資料的簡單收縮對照','',
'固定規則：截止日前完整日期取中點，前段每隊場均淨勝分預測後段每隊場均淨勝分；合併30隊估一個OLS斜率並限制[0,1]。完整訓練期net乘該係數；勝場用相同倍率收縮Pythagorean得失分log比，指數仍只從完整訓練資料估計。沒有用測試表現選倍率、按隊調參或選額外切點。','',
'| 季 | K | 訓練內分段日 | 收縮倍率 | 原simple RMSE / MAE | shrink RMSE / MAE | shrink−simple RMSE [聯合95%] | shrink−simple MAE [聯合95%] |','|---|---:|---|---:|---:|---:|---:|---:|');
for(const s of seasons)for(const k of ks){const x=r.seasons[s][k],a=x.models.simple.metrics,b=x.models.shrink.metrics,p=pair(x,'shrink','simple');md.push(`| ${s} | ${k} | ${x.shrinkRule.split} | ${f(x.shrinkRule.multiplier)} | ${f(a.netRMSE)} / ${f(a.winMAE)} | ${f(b.netRMSE)} / ${f(b.winMAE)} | ${interval(p.netRMSE)} | ${interval(p.winMAE)} |`);}
md.push('', '收縮不是跨季通用改善：2024的25／41net點估計變好、55變差；2025的25稍好，41／55反而明显變差。上表與附表列出聯合區間，點估計不等於顯著改善。固定倍率的真實校準與訓練內斜率不同，支持階段B必須用卡→較晚場次的真正時間順向預測來量，不能拿答案β套入。','',
'## A4：隨機覆蓋率抽薄與離線重估','',
'先寫三個固定seed（20261081–83），各從1188個嚴格2025場次均勻無放回保留1091個，總覆蓋1091／1230＝88.70%；每個切分只用其截止日前與遮罩交集。重估B1、舊卡、角色joint模型及v4投影，保留原1188嚴格資料的共同後段作評分。跟隨凍結流程，模型的投影分鐘權重使用截止日前全部box分鐘，追蹤截止日資料亦保留。沒有重跑遊戲或校正時鐘。', '',
'以下是**投影卡線性加總**對共同後段真實區段的攻守淨效率（分／百回合），不是模擬淨勝分。固定原先真實後段區段陣容與曝光作診斷，聯盟效率截距不作後段擬合；完整joint含防守殘差的離線結果另存JSON，但v4部署仍關閉完整防守殘差。','',
'| K | full訓練場數 | 遮罩訓練場數 | full r | 抽薄r範圍 | Δr範圍 | full斜率 | 抽薄斜率範圍 | Δ斜率範圍 | full RMSE | 抽薄RMSE範圍 |','|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|');
const range=a=>`${f(Math.min(...a))}～${f(Math.max(...a))}`;
for(const k of ks){const d=diagnosis[k],a=d.models.full,b=Object.entries(d.models).filter(([key])=>key!=='full').map(([,v])=>v);md.push(`| ${k} | ${a.trainingGames} | ${b.map(v=>v.trainingGames).join(' / ')} | ${f(a.deployedLinear.correlation)} | ${range(b.map(v=>v.deployedLinear.correlation))} | ${range(b.map(v=>v.delta.deployedLinear.correlation))} | ${f(a.deployedLinear.calibrationSlope)} | ${range(b.map(v=>v.deployedLinear.calibrationSlope))} | ${range(b.map(v=>v.delta.deployedLinear.calibrationSlope))} | ${f(a.deployedLinear.RMSE)} | ${range(b.map(v=>v.deployedLinear.RMSE))} |`);}
md.push('', '已驗證：25場較敏感，三遮罩相關均降低（最大約0.071）；41／55大多只有約0.004～0.023的相關變動，斜率也變動。推測：隨機缺少97場不是中後段跨季排序落差的充分解釋。**不能因此排除2024非隨機稽核失敗的偏差，也不能把離線差直接換成模擬RMSE差**。三遮罩的範圍不是95%區間；資料較少也可能碰巧改善某些點估計。','',
'逐遮罩joint／投影卡兩套六十隊側聚合、CV lambda、訓練ID與差異：[25](coverage/diagnosis-25.json)、[41](coverage/diagnosis-41.json)、[55](coverage/diagnosis-55.json)；固定遮罩規則見 [coverage規則](coverage/rules.json)。','',
'## A5：2024–25 v1補跑與防守訊號歸因','',
'v1保留原凍結事件機制，能力卡用截止日前舊卡、分鐘用訓練MPG；全聯盟常數用第七批同一更新方法、3個校準seed、最多5輪，初始pace1。v1不支援新的犯規／分類失誤／獨立違例倍率，這些校準欄位不會讓舊機制偷偷升級；部分moment目標不能靠此程序對齊。預測20seed與v3完全配對，兩場比分及主要box計數已與原v1遊戲函式逐項核對相同。','',
'v3→v1不只差防守訊號，還差事件記帳／時鐘／犯規等。故額外補跑v3-signals-off：相同v3卡、記帳、耗時與其他機制，只關DREB、禁區、活球失誤、出手分區、犯規五組學習訊號，重新做同一訓練聯盟校正。這是防守訊號總增量較乾淨的對照；個別五組沒有再逐一消融。','',
'| K | 版本 | net RMSE | r | SD比 | 校準斜率 | wins MAE | wins RMSE |','|---:|---|---:|---:|---:|---:|---:|---:|');
for(const k of ks)for(const v of ['v1','v3-signals-off','v3']){const m=r.seasons['2024-25'][k].models[v].metrics;md.push(`| ${k} | ${v} | ${['netRMSE','netCorrelation','netSDRatio','calibrationSlope','winMAE','winRMSE'].map(key=>f(m[key])).join(' | ')} |`);}
md.push('', '| K | v3−v1 RMSE [聯合95%] | v3−v1 MAE [聯合95%] | v3−關訊號 RMSE [聯合95%] | v3−關訊號 MAE [聯合95%] |','|---:|---:|---:|---:|---:|');
for(const k of ks){const x=r.seasons['2024-25'][k],p=pair(x,'v3','v1'),q=pair(x,'v3','v3-signals-off');md.push(`| ${k} | ${interval(p.netRMSE)} | ${interval(p.winMAE)} | ${interval(q.netRMSE)} | ${interval(q.winMAE)} |`);}
md.push('',...ks.map(k=>{const p=pair(r.seasons['2024-25'][k],'v3','v3-signals-off');return `${k}場：純防守訊號組的net RMSE為${status(p.netRMSE)}、wins MAE為${status(p.winMAE)}。`;}),'',
'防守訊號的跨季準確度增益未成立：v3對v1與純訊號控制組的淨勝分／胜場均沒有聯合區間顯著改善。防守效率SD比在25／41切分顯著提高，相關改善則三個切分都不顯著，41場相關點估計反而下降。分散放大與排序準確是不同驗收項目，不把前者算成準確度成功。','',
'| K | v1 防守r / SD比 | 關訊號 防守r / SD比 | v3 防守r / SD比 | v3−關訊號防守r [聯合95%] | v3−關訊號防守SD比 [聯合95%] |','|---:|---:|---:|---:|---:|---:|',
...ks.map(k=>{const x=r.seasons['2024-25'][k],p=pair(x,'v3','v3-signals-off');return `| ${k} | ${['v1','v3-signals-off','v3'].map(v=>`${f(x.models[v].metrics.defenseCorrelation)} / ${f(x.models[v].metrics.defenseSDRatio)}`).join(' | ')} | ${interval(p.defenseCorrelation)} | ${interval(p.defenseSDRatio)} |`;}),'',
'## 推測、失敗項目、與估算不符之處','',
'- 推測：跨季落差混有排序資訊移轉與過度分散；A1只給線性答案校準上限，沒有證明訓練內倍率能取得相同收益。','- 推測：隨機覆蓋率下降對中後段影響較小，但非隨機漏失尚無答案。','- 失敗／未證實：v4沒有在2024取得含球隊抽樣的顯著改善，也沒有在2025顯著贏較強簡單對照；訓練內简单收縮規則未穩定改善。','- 限制：A4遵守不重跑模擬，只量估計／線性投影層；未交付抽薄版遊戲結果，不能聲稱已量到整個引擎輸出覆蓋效應。','- 估算核對：A1與你的數值只有四捨五入近似差；真正改變的是顯著性判讀，不是原誤差點估計。','- 凍結版本、OVR卡與引擎未修改；沒有球隊ID機率欄位、真實勝場修補、截止日後校正或新資料抓取。球隊ID只用於資料連結、評分、成對重抽。','',
'## 重跑與停止點','', '```powershell','node scripts/prepare_defense_eighth_a_coverage.js','node scripts/campaign_defense_eighth_a_coverage.js','node scripts/diagnose_defense_eighth_a_coverage_cards.js','python scripts/diagnose_defense_eighth_a_coverage.py 25','python scripts/diagnose_defense_eighth_a_coverage.py 41','python scripts/diagnose_defense_eighth_a_coverage.py 55','node scripts/campaign_defense_eighth_a_controls.js','node scripts/assess_defense_eighth_a.js','node scripts/report_defense_eighth_a.js','node test/defense_eighth_a.js --artifacts','node test/defense_seventh.js','```','',
'估計及控制模擬腳本會重用完整已存在的快取；bootstrap表也只在來源雜湊相同時重用。若要重新算抽樣區間可先另存analysis.json再重跑評分。B的規則／v5凍結與C的2023–24資料尚未建立，階段A完成後停下。','');
const appendix=['# 階段 A：所有成對區間','', '差值一律左版本減右版本；RMSE、MAE較低好，r較高好，校準斜率需對1判讀。既有seed為第七批2000次；其餘5000次。主要判準為聯合區間。',''];
for(const s of [...seasons,'combined'])for(const k of ks){const x=s==='combined'?r.combined[k]:r.seasons[s][k];appendix.push(`## ${s}，${k}場`,'','| 比較 | 指標 | 差值 | 舊seed95% | 新seed95% | 球隊95% | 聯合95% |','|---|---|---:|---|---|---|---|');for(const[p,ms]of Object.entries(x.pairs))for(const[key,z]of Object.entries(ms))appendix.push(`| ${p} | ${key} | ${f(z.estimate)} | ${z.historicalSeed?z.historicalSeed.ci95.map(v=>f(v)).join(', '):'—'} | ${z.seed.ci95.map(v=>f(v)).join(', ')} | ${z.team.ci95.map(v=>f(v)).join(', ')} | ${z.joint.ci95.map(v=>f(v)).join(', ')} |`);appendix.push('');}
fs.writeFileSync(root+'/paired-intervals.md',appendix.join('\n')+'\n');fs.writeFileSync(root+'/closeout.md',md.join('\n')+'\n');
const sources=['src/defense_eighth_analysis.js','scripts/assess_defense_eighth_a.js','scripts/report_defense_eighth_a.js','scripts/campaign_defense_eighth_a_controls.js','scripts/campaign_defense_eighth_a_coverage.js','scripts/estimate_defense_eighth_a_coverage_factors.py','scripts/diagnose_defense_eighth_a_coverage.py','scripts/diagnose_defense_eighth_a_coverage_cards.js','test/defense_eighth_a.js',root+'/analysis.json',root+'/coverage/rules.json',...ks.map(k=>root+`/coverage/diagnosis-${k}.json`),'reports/defense-seventh/v4-freeze.json'];
fs.writeFileSync(root+'/closeout.json',JSON.stringify({stage:'A',baseline:'nba-defense-v3',BStarted:false,CStarted:false,headline,analysis:root+'/analysis.json',coverage:diagnosis,sources:Object.fromEntries(sources.map(p=>[p,hash(p)]))},null,2)+'\n');console.log(headline);

import fs from 'node:fs';
import {read,hash} from './defense_io.js';
import {mean,sd,variance} from '../src/statistical_summary.js';
import {makeRng} from '../src/rng.js';
const root='reports/defense-third',labels=['v1','accounting','independent','empirical','fouls','combined','combined-grid','season-minutes'];
const boards=Object.fromEntries(labels.map(k=>[k,read(root+'/scoreboard-'+k+'-20.json')]));
const paired=read(root+'/paired-comparison.json'),candidate=boards['combined-grid'],base=boards.v1,c=candidate.global.simulated,a=candidate.global.observed;
const u=candidate.uncertainty.metrics,comparison=paired.find(p=>p.candidate==='combined-grid').differences;
const audits=read(root+'/combined-grid-possession-audits-20.json'),real=read('reports/defense-b1/variance-sources.json'),r=real.real;
const sumCounts={};for(const s of audits.results)for(const [k,n] of Object.entries(s.counts))sumCounts[k]=(sumCounts[k]??0)+n;
const total=Object.values(sumCounts).reduce((a,b)=>a+b,0),shares=Object.fromEntries(Object.entries(sumCounts).map(([k,n])=>[k,n/total]));
const pointVariance=mean(audits.results.map(s=>s.pointsVariance));
const check=(name,value,target,pass,definition)=>({name,value,target,pass,definition});
const gates=[check('efficiencyBias',c.offensiveRatingProxy-a.offensiveRatingProxy,'±0.5',Math.abs(c.offensiveRatingProxy-a.offensiveRatingProxy)<=.5),check('boxPossBias',c.possessionsProxy-a.possessionsProxy,'±0.5',Math.abs(c.possessionsProxy-a.possessionsProxy)<=.5),check('TOV/G',c.turnovers,a.turnovers+' ±0.2',Math.abs(c.turnovers-a.turnovers)<=.2),check('STL/G',c.steals,a.steals+' ±0.3',Math.abs(c.steals-a.steals)<=.3),
  check('clockViolation/G',c.clockTurnovers,'real0.673594; within0.02',Math.abs(c.clockTurnovers-.673594132)<.02,'User supplied no numerical tolerance; explicit practical tolerance0.02/G, not a proof of equivalence.'),
  check('netRMSE',comparison['net.centeredRMSE'],'paired95CI not significantly worse',comparison['net.centeredRMSE'].ci95[0]<=0,'Absence of significant worsening is not formal noninferiority proof.'),check('netCorrelation',comparison['net.correlation'],'paired95CI not significantly worse',comparison['net.correlation'].ci95[1]>=0),
  check('netSDRatio',candidate.metrics.net.sdRatio,'>=v1 '+base.metrics.net.sdRatio,candidate.metrics.net.sdRatio>=base.metrics.net.sdRatio),
  ...[0,1,2,3,4].map(k=>check('possessionPoints'+k,shares[k],r.offensivePoints.distribution[k].share+' ±0.005',Math.abs(shares[k]-r.offensivePoints.distribution[k].share)<=.005)),
  check('possessionVariance',pointVariance,'1.41 ±0.03',Math.abs(pointVariance-1.41)<=.03),
  check('FG%',c.fg,'absolute bias <=v1',Math.abs(c.fg-a.fg)<=Math.abs(base.global.simulated.fg-a.fg)),check('3P%',c.three,'absolute bias <=v1',Math.abs(c.three-a.three)<=Math.abs(base.global.simulated.three-a.three)),
  check('FTR',c.opponentFTR,'absolute bias <=v1',Math.abs(c.opponentFTR-a.opponentFTR)<=Math.abs(base.global.simulated.opponentFTR-a.opponentFTR))];
const seasons=read(root+'/combined-grid-seeds.json').files.map(f=>read(f.file)),stats={};for(const s of seasons)for(const t of s.teams)for(const [k,v] of Object.entries(t.stats))stats[k]=(stats[k]??0)+v;
const categoryCounts=Object.fromEntries(['liveTov','clockTov','offensiveFoulTov','otherViolationTov','passOutTov','handlingOutTov','unmappedDeadTov','passSteals','touchSteals'].map(k=>[k,stats[k]/49200]));categoryCounts.deadNoClock=(stats.deadTov-stats.clockTov)/49200;
categoryCounts.passingLiveShare=categoryCounts.passSteals/(categoryCounts.passSteals+categoryCounts.passOutTov);
categoryCounts.handlingLiveShare=categoryCounts.touchSteals/(categoryCounts.touchSteals+categoryCounts.handlingOutTov);
const perSeed=audits.results.map(s=>{
  const m=s.analysis,components={singlePossessionVariance:m.meanCombinedPossessions*(m.teamCenteredPointVariance-r.teamCenteredPointVariance),meanPossessionCount:(m.meanCombinedPossessions-r.meanCombinedPossessions)*r.teamCenteredPointVariance,
    sharedPaceNet:m.decomposition.individualPaceVariance+m.decomposition.paceCovarianceReduction-r.decomposition.individualPaceVariance-r.decomposition.paceCovarianceReduction,
    remainingSameGameCovariance:m.decomposition.remainingCovarianceReduction-r.decomposition.remainingCovarianceReduction,
    withinTeamSerialAndHeterogeneity:m.decomposition.withinTeamSerialAndHeterogeneityVariance-r.decomposition.withinTeamSerialAndHeterogeneityVariance};
  if(Math.abs(Object.values(components).reduce((a,b)=>a+b,0)-(m.decomposition.total-r.decomposition.total))>1e-7)throw Error('Variance identity');
  return {seed:s.seed,...components,residualSD:m.marginResidualSD,independentSD:m.teamCenteredIndependentSD,withinTeamScoreVariance:m.withinTeamScoreVariance,scoreCovariance:m.scoreCovariance,remainingCovariance:m.remainingCovariance};
});
const uncertainty=values=>{const rng=makeRng(20261104),samples=Array.from({length:2000},()=>mean(Array.from({length:values.length},()=>values[Math.floor(rng()*values.length)]))),sorted=samples.slice().sort((a,b)=>a-b);return {estimate:mean(values),standardError:sd(samples),ci95:[sorted[49],sorted[1949]]};};
const decomposition=Object.fromEntries(Object.keys(perSeed[0]).filter(k=>k!=='seed').map(k=>[k,uncertainty(perSeed.map(s=>s[k]))]));
const remaining=Object.fromEntries(['singlePossessionVariance','remainingSameGameCovariance','withinTeamSerialAndHeterogeneity'].map(k=>[k,{...decomposition[k],previous:real.gap.components[k],remainingShare:decomposition[k].estimate/real.gap.components[k]}]));
function scoreVariances(run){const values=new Map(run.teams.map(t=>[t.id,[]]));for(const g of run.matches){values.get(g.homeId).push(g.scoreA);values.get(g.awayId).push(g.scoreB);}return Object.fromEntries([...values].map(([id,v])=>[id,variance(v)]));}
const minuteRuns=read(root+'/season-minutes-seeds.json').files.map(f=>read(f.file)),v1Runs=read('reports/defense-a/v1-seeds.json').files.map(f=>read(f.file));
const accuracyPairedAbsoluteBias={};
for(const [key,num,den,target,multiplier] of [['fg','fgm','fga',a.fg,100],['three','fg3m','fg3a',a.three,100],['FTR','fta','fga',a.opponentFTR,1]]){
  const counts=runs=>runs.map(r=>[r.teams.reduce((s,t)=>s+t.stats[num],0),r.teams.reduce((s,t)=>s+t.stats[den],0)]),x=counts(v1Runs),y=counts(seasons);
  const pooled=(m,draws)=>multiplier*draws.reduce((s,i)=>s+m[i][0],0)/draws.reduce((s,i)=>s+m[i][1],0),rng=makeRng(20261106),boot=[];
  for(let b=0;b<2000;b++){const draws=Array.from({length:20},()=>Math.floor(rng()*20));boot.push(Math.abs(pooled(y,draws)-target)-Math.abs(pooled(x,draws)-target));}
  const sorted=boot.slice().sort((a,b)=>a-b),all=Array.from({length:20},(_,i)=>i);
  accuracyPairedAbsoluteBias[key]={estimate:Math.abs(pooled(y,all)-target)-Math.abs(pooled(x,all)-target),standardError:sd(boot),ci95:[sorted[49],sorted[1949]]};
}
const minuteVars=minuteRuns.map(scoreVariances),v1Vars=v1Runs.map(scoreVariances),perTeam=Object.keys(v1Vars[0]).map(id=>({id:+id,v1:uncertainty(v1Vars.map(r=>r[id])),seasonMinutes:uncertainty(minuteVars.map(r=>r[id])),pairedDifference:uncertainty(minuteVars.map((r,i)=>r[id]-v1Vars[i][id]))}));
const minuteComparison={definition:'Frozen v1 other mechanisms. Same observed active players, starter order and bench order. In-team season MPG targets rescaled to240 with48 cap; only minute targets replaced. Whole-season MPG remains future information, so this isolates outcome-dependent per-game minutes, not all possible leakage. Score variances use final scores including OT; residualSD in scoreboard uses final scores and same retrospective team-strength fit.',
  paired:paired.find(p=>p.candidate==='season-minutes').differences,perTeam,
  leagueWithinTeamVariance:{v1:uncertainty(v1Vars.map(r=>mean(Object.values(r)))),seasonMinutes:uncertainty(minuteVars.map(r=>mean(Object.values(r)))),difference:uncertainty(minuteVars.map((r,i)=>mean(Object.values(r))-mean(Object.values(v1Vars[i]))))}};
const adjacent=[];for(const [from,to] of [['v1','accounting'],['accounting','independent'],['independent','empirical'],['empirical','fouls'],['fouls','combined-grid']]){
  const uf=boards[from].uncertainty.metrics,ut=boards[to].uncertainty.metrics;
  const getRuns=k=>read(k==='v1'?'reports/defense-a/v1-seeds.json':root+'/'+k+'-seeds.json').files.map(f=>read(f.file));
  const first=getRuns(from),second=getRuns(to),ids=first[0].teams.map(t=>t.id);
  const nets=runs=>runs.map(r=>ids.map(id=>{const t=r.teams.find(t=>t.id===id);return (t.stats.pts-t.opponent.pts)/82;}));
  const x=nets(first),y=nets(second),rng=makeRng(20261105),boots=[];
  for(let i=0;i<2000;i++){const draws=Array.from({length:20},()=>Math.floor(rng()*20)),ensemble=m=>ids.map((_,j)=>mean(draws.map(d=>m[d][j])));boots.push((sd(ensemble(y))-sd(ensemble(x)))/base.metrics.net.observedSD);}
  const ordered=boots.slice().sort((a,b)=>a-b);
  adjacent.push({from,to,sdRatioChange:ut['net.sdRatio'].estimate-uf['net.sdRatio'].estimate,standardError:sd(boots),ci95:[ordered[49],ordered[1949]],definition:'Sequential switch path; paired2000seed bootstrap. Includes stated pace recalibration and event interactions. Not a unique causal allocation.'});
}
const result={baseline:'nba-defense-v1',adopted:gates.every(g=>g.pass),candidate:'combined-grid',seeds:candidate.seeds,gates,categories:categoryCounts,pointShares:shares,pointVariance,paired:comparison,accuracyPairedAbsoluteBias,ablation:adjacent,
  decomposition:{scope:'Experimental candidate only, since no new baseline adopted. Candidate20seed means versus same1227 real fixtures; remaining-share denominators are the previous single-v1-seed28/32/43% components. Conditional seed uncertainty only; descriptive statistical decomposition, not causal mechanism estimates.',metrics:decomposition,remaining,perSeed},minutes:minuteComparison,
  offline:read(root+'/offline-model.json'),timeAudit:read(root+'/time-audit.json'),
  uncertain:['聯盟分區犯規率再以球員總FTA/FGA縮放，可能重複計入分區與造犯規能力的相關；FTR仍偏高，未用命中率或OVR補丁遮掩。','三分得分回合仍偏多。既有分區出手選擇與重複籃板機會可能有貢獻，但本批尚未證實各自原因。','分鐘輸入只作敏感度診斷，沒有排除替補排序或全季卡片資訊，也不能證明實測逐場分鐘是外生輸入。','離線測試場bootstrap固定已估係數；尚未重訓以估計模型不確定性，也尚未跨賽季驗證。','訓練要求兩隊均在前41，比單隊前41更嚴格。現行追蹤訊號使用各隊前41的官方資料，仍含被嚴格區段篩選排除的前半季場次。'],
  sources:Object.fromEntries([...labels.map(k=>root+'/scoreboard-'+k+'-20.json'),root+'/paired-comparison.json',root+'/combined-grid-possession-audits-20.json',root+'/foul-audit.json',root+'/offline-model.json',root+'/time-audit.json','scripts/report_defense_third.js'].map(f=>[f,hash(f)]))};
fs.writeFileSync(root+'/closeout.json',JSON.stringify(result,null,2)+'\n');
const f=n=>Number.isFinite(n)?n.toFixed(4):'—',pp=n=>f(n*100),ci=x=>x.ci95.map(f).join('～');
const md=['# 防守第三批：事件分布校準與 B1 離線估計','','**結果：未通過全項驗收，保留 nba-defense-v1；不接防守新屬性、不改 OVR。**',
  '','二十 seed 20261012–20261031，完整30隊×82場。合併計數聯盟均值，逐隊先平均seed，母體SD；相關／RMSE的區間為成對seed整季bootstrap。勝場MAE僅列示。',
  '','## 1. 犯規條件分布與驗收','',
  '| 出手區 | 命中且犯規／機會 | 投失且犯規／機會 | 命中時犯規機率 | 投失時未計FGA的犯規機率 |','|---|---:|---:|---:|---:|',
  ...['short','mid','long'].map(z=>{const q=read(root+'/foul-audit.json').counts[z];return `| ${z} | ${pp(q.madeAndFouledRate)}% | ${pp(q.missedAndFouledRate)}% | ${pp(q.foulGivenMake)}% | ${pp(q.foulGivenMiss)}% |`;}),
  '','v1原本獨立抽犯規與命中，另加andOne。新機制先抽命中，再用qMake或qMiss抽犯規，移除額外andOne；p.zone是記帳FGA分區，先依記帳率反推機會分區，避免漏算犯規投失。',
  '','`m = r / [r + (1-r)(1-qMiss)]`，因此 `r = m(1-qMiss)/(1-m*qMiss)`；qMake不影響FGA分母。',
  '','1227場；38筆射球犯規的罰球分類不完整而排除，118筆禁區犯規投失已記FGA，另列且不當成未記FGA機會。球員抽樣仍以個人FTA/FGA調整聯盟區域條件率；這項混合仍有偏差，不能稱為完全校準。',
  '','| 單回合得分 | 真實 | 候選20seed | 差異（百分點） |','|---|---:|---:|---:|',...[0,1,2,3,4].map(k=>`| ${k} | ${pp(r.offensivePoints.distribution[k].share)}% | ${pp(shares[k])}% | ${pp(shares[k]-r.offensivePoints.distribution[k].share)} |`),
  ``,`單回合變異數 ${f(pointVariance)}，目標1.41±0.03。`,
  '','## 2. 失誤分類','',
  '5.42是「非24秒違例的死球失誤」，包括進攻犯規及其他違例。dead touch按實測類別拆帳；出界原因不明保留unmapped，未硬分到傳球或持球。進攻犯規加在進攻球員PF，不加防守隊bonus。',
  '','| 類別／隊／場 | 真實 | 候選20seed |','|---|---:|---:|',
  ...[['liveTov',8.4164629177],['deadNoClock',5.4189079055],['clockTov',.673594132],['offensiveFoulTov',1.474327628],['otherViolationTov',.909535452],['passOutTov',4332/2454],['handlingOutTov',2311/2454],['unmappedDeadTov',805/2454],['passSteals',5.136511817],['touchSteals',3.2799511]].map(([k,n])=>`| ${k} | ${f(n)} | ${f(categoryCounts[k])} |`),
  '',`傳球／持球活球比例：真實 ${pp(12605/16937)}%／${pp(8049/10360)}%，候選 ${pp(categoryCounts.passingLiveShare)}%／${pp(categoryCounts.handlingLiveShare)}%。活球數量比由v1約3.1:4.3改善至候選 ${f(categoryCounts.passSteals)}:${f(categoryCounts.touchSteals)}，目標5.14:3.28。`,
  '','dead touch類別是校準的事件結果；傳球出界並未模擬球飛出界的物理路徑，其他違例也不是獨立場上時空判定。每類可追蹤，但不宣稱已有完整規則引擎。',
  '','## 3. 候選與逐項開關','',
  '| preset | 去均值淨勝分RMSE | 相關 | SD比 | 每分勝場 | 效率偏差 | 球權偏差 | TOV | STL |','|---|---:|---:|---:|---:|---:|---:|---:|---:|',
  ...labels.map(k=>{const b=boards[k],s=b.global.simulated;return `| ${k} | ${f(b.metrics.net.centeredRMSE)} | ${f(b.metrics.net.correlation)} | ${f(b.metrics.net.sdRatio)} | ${f(b.wins.winPerNet)} | ${f(s.offensiveRatingProxy-a.offensiveRatingProxy)} | ${f(s.possessionsProxy-a.possessionsProxy)} | ${f(s.turnovers)} | ${f(s.steals)} |`;}),
  '','accounting=團隊籃板＋原時鐘重校準；independent再加獨立違例；empirical再換經驗耗時（pace0.836）；fouls再改條件犯規；combined初始校準點0.8797377；combined-grid是完整賽季網格選到pace0.90。season-minutes僅v1分鐘輸入對照。以上每個機制都能以boolean獨立關閉。',
  '','| 相對v1（候選−v1） | 差異 | 成對95%區間 |','|---|---:|---:|',...['net.centeredRMSE','net.correlation','net.sdRatio','winPerNet'].map(k=>`| ${k} | ${f(comparison[k].estimate)} | ${ci(comparison[k])} |`),
  '','| 驗收 | 結果 | 通過 |','|---|---|---|',...gates.map(g=>`| ${g.name} | ${typeof g.value==='object'?JSON.stringify(g.value):f(g.value)}；目標 ${g.target} | ${g.pass?'是':'否'} |`),
  '','不存在顯著變差不等於證明非劣；本表依使用者指定「不得顯著劣於」判準列示。違例率沒有指定數值容忍度，明列採±0.02／隊／場，未將其包裝為等價性檢定。',
  '','FG%／3P%的「不退步」按點估計判定；其絕對偏差僅增加約0.020／0.025個百分點，不能當成已證實的顯著退步。另列相同seed的絕對偏差差異區間：',
  '','| 絕對偏差 候選−v1 | 差異 | 成對95%區間 |','|---|---:|---:|',...Object.entries(accuracyPairedAbsoluteBias).map(([k,v])=>`| ${k}${k==='FTR'?'（比例）':'（百分點）'} | ${f(v.estimate)} | ${ci(v)} |`),
  '','| 逐項切換 | SD比變化 | 成對95%區間 |','|---|---:|---:|',...adjacent.map(x=>`| ${x.from} → ${x.to} | ${f(x.sdRatioChange)} | ${ci(x)} |`),
  '','這是同seed順序開關的效果，含各步已列出的時鐘重校準及交互作用；不是唯一因果分攤。先前0.722→0.666的路徑中，由記帳到獨立違例的點估計下降最大，經驗耗時再下降一部分。舊耗時撞限失誤帶有球員傳球／持球能力差異，是可檢查的機制解釋；但開關效應本身不證明被移除的差異都是合理防守訊號，也需看上述區間。',
  '','## 4. 耗時與上一批兩表差異','',
  '上一批開關表c-empirical用pace1，二十seed用校準後pace0.836。已用同seed20261012完整賽季重跑，詳見diagnostics.json：並非同設定下的抽樣誤差。',
  '','time-audit.json量出每種起始狀態的原始均值、截斷後抽樣均值及縮放截止時間；diagnostics.json逐项對帳setup／pass／release／flight／inbound／violation／other，合計等於全場活時計秒數。',
  '','pace0.836是經驗時鐘的補償係數：原始CDF含超過24秒與跨犯規重置的長段，截斷會縮短均值；傳球抄截與非投籃犯規會提早終止抽到的截止時間；發球和籃板飛行另加時間。這些方向相反，係數不是NBA實測節奏，也不能歸因於一塊「額外時間」。',
  '','整秒CDF在21/23.9≈0.87866附近有支持集跳點。原比例校準0.87717→0.87974會新納入21秒耗時，球權數反向跳降。改用完整1230場網格0.89／0.90／0.91／0.915，以球權代理選0.90，未用勝場／球隊ID選參數。這個離散抽樣的非單調性仍存在，未偷偷更改CDF。',
  '','## 5. 變異拆解（候選診斷，沒有新基準）','',
  `候選20seed平均殘差SD ${f(decomposition.residualSD.estimate)}，真實 ${f(r.marginResidualSD)}；獨立理論SD ${f(decomposition.independentSD.estimate)}。`,
  '','| 先前28%／32%／43%來源 | 先前差（分數平方） | 候選剩餘差 ± seed SE | 剩餘／先前 |','|---|---:|---:|---:|',...Object.entries(remaining).map(([k,x])=>`| ${k} | ${f(x.previous)} | ${f(x.estimate)} ± ${f(x.standardError)} | ${pp(x.remainingShare)}% |`),
  '','候選二十seed與真實同1227場；「剩餘比例」分母沿用上一批單seed v1拆解。分數平方可加，SD不可加；序列與異質性餘項不硬歸為比分耦合。詳細分項、區間與各seed列於closeout.json。',
  '','## 6. 分鐘輸入診斷','',minuteComparison.definition,
  '','| 指標 | v1逐場分鐘 | 賽季MPG目標 | 差異95%區間 |','|---|---:|---:|---:|',
  ...['net.correlation','net.sdRatio','residualSD'].map(k=>`| ${k} | ${f(base.uncertainty.metrics[k].estimate)} | ${f(boards['season-minutes'].uncertainty.metrics[k].estimate)} | ${ci(minuteComparison.paired[k])} |`),
  `| 單隊單場得分隊內變異 | ${f(minuteComparison.leagueWithinTeamVariance.v1.estimate)} | ${f(minuteComparison.leagueWithinTeamVariance.seasonMinutes.estimate)} | ${ci(minuteComparison.leagueWithinTeamVariance.difference)} |`,
  '','每隊30列隊內變異、SE與差異區間完整列於closeout.json。這是曝光輸入敏感度診斷；保留實測出賽、先發、替補排序及全季卡片，不能據此宣稱已排除所有洩漏。',
  '','## 7. B1離線模型','',result.offline.method,'',result.offline.split,'',result.offline.currentSignalLimitation,
  '','嚴格1188場；兩隊均前41的訓練574場，測試614場。模型同時放進攻五人／防守五人，個人STL／BLK／DREB／PF與位置作先驗。每一CV折重算box先驗，不把驗證場box混進先驗；場次grouped三折決定收縮強度。後半季只用真實陣容與觀測機會加權，並不更新係數。',
  '','FTA模型保留所有標籤。罰球之間換人的零秒區段會有FTA卻無回合終點，另用零回合區段截距估計每區段計數；其餘按回合終點作曝光。這是條件區段計數模型，尚未把每顆罰球歸回犯規發生時的五人，不能直接宣稱取得可接引擎的防守犯規因果屬性。',
  '','| 指標 | 現行訊號 r / SD比 / RMSE | 先驗 | 新模型 | 新−現行RMSE 95%區間 |','|---|---:|---:|---:|---:|',
  ...['opp2','opp3','liveTOVRate','DREBRate','FTR'].map(k=>`| ${k} | ${['current','prior','new'].map(m=>['correlation','sdRatio','centeredRMSE'].map(v=>f(result.offline.metrics[m][k][v])).join(' / ')).join(' | ')} | ${ci(result.offline.paired[k])} |`),
  '','RMSE單位為比例，例如0.01是一個百分點。禁區／中距離／三分出手比例與命中率也各列於offline-model.md。後半季比較不能宣稱全項合格：三分相關、SD比與只用先驗的比較仍須看完整表；顯著RMSE改善也可能只是把不穩定訊號收縮回均值。離線係數保留，這批不接引擎。',
  '','## 8. 已驗證與仍不確定','',
  '- 已驗證：v1犯規／命中獨立、四分回合過量來源；相同seed的pace差異；整秒CDF支持集跳點；單機／worker比分一致；分類帳、分鐘240與48上限；離線各模型收斂。',
  ...result.uncertain.map(s=>'- '+s),
  '- 本批未修改比分相依輪替、同場共變異或球隊節奏，也未用球隊ID／勝場補丁。',
  '','offline-model.json/md是正式前41追蹤＋完整CV＋全FTA對照；fullsignal、coarse-cv與positive-fta檔為保留的中間診斷，不作本批結論。',
  '','重跑用直接node命令，Windows npm轉送旗標容易被剝除：`node scripts/run_defense_third_seeds.js combined-grid`、`node scripts/audit_defense_third_seeds.js combined-grid`、`python scripts/estimate_defense_third.py`。',''];
fs.writeFileSync(root+'/closeout.md',md.join('\n'));console.log(JSON.stringify({adopted:result.adopted,failed:gates.filter(g=>!g.pass).map(g=>g.name),net:candidate.metrics.net,categories:categoryCounts,variance:pointVariance,remaining},null,2));

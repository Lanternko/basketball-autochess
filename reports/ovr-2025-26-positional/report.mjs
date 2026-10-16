import fs from 'node:fs';
import crypto from 'node:crypto';
import {ROOT} from './protocol.mjs';
import {summarizeStrata,winToOvr,ATTRIBUTES} from '../../src/strength_benchmark.js';
const suffix=process.argv[2]??'representative-80';
const read=f=>JSON.parse(fs.readFileSync(f));
const protocol=read(ROOT+'/protocol-'+suffix+'.json'),checkpoint=read(ROOT+'/checkpoint-'+suffix+'.json');
if(protocol.fingerprint!==checkpoint.fingerprint)throw Error('Fingerprint mismatch');
for(const [f,h]of Object.entries(protocol.hashes))if(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')!==h)throw Error('Source mismatch: '+f);
const rows=new Map(checkpoint.rows.map(r=>[r.job.key,r]));
if(rows.size!==15+protocol.ids.length*2+8)throw Error('Incomplete results');
const split=a=>Array.from({length:30},(_,i)=>a.slice(i*protocol.samples,(i+1)*protocol.samples));
// summarizeStrata deliberately accepts only [0,1]; transform paired [-1,1]
// differences to [0,1], calculate stratum-aware SE, then transform back.
const paired=(a,b)=>{
  const values=a.map((v,i)=>(v-b[i]+1)/2),r=summarizeStrata(split(values)),delta=2*r.winRate-1,half=2*r.halfWidth95;
  return {delta,ci95:[Math.max(-1,delta-half),Math.min(1,delta+half)]};
};
const anchors=[40,70,99].map(level=>{
  const rs=Array.from({length:5},(_,slot)=>rows.get(`anchor-${slot}-${level}`).result);
  const r=summarizeStrata(rs.flatMap(r=>split(r.outcomes)));
  return {level,...r};
});
const mapping=Object.fromEntries(['low','mid','high'].map((k,i)=>[k,anchors[i].winRate]));
const old=read('reports/ovr-2025-26-latest/ranking.json');
const players=protocol.ids.map(id=>{
  const flat=rows.get(id+'-flat').result,position=rows.get(id+'-positional').result,previous=old.players.find(p=>p.playerId===id);
  const baseline=rows.get(`anchor-${protocol.roles.find(p=>p.playerId===id).slot}-70`).result;
  return {playerId:id,name:position.name,position:position.position,role:protocol.roles.find(r=>r.playerId===id),
    oldFiveSlotWinRate:previous.winRate,oldFiveSlotOvr:previous.ovr,
    naturalSlotFlatWinRate:flat.winRate,naturalSlotPositionalWinRate:position.winRate,ci95:position.ci95,
    profileChange:paired(position.outcomes,flat.outcomes),
    improvementOverPositionBaseline:paired(position.outcomes,baseline.outcomes),
    diagnosticOvr:winToOvr(position.winRate,mapping),
    diagnosticConditionalOvrCI95:position.ci95.map(v=>winToOvr(v,mapping)),
    statsPerGame:position.statsPerGame};
});
const sensitivities=[1629674,201939].flatMap(id=>['physique70','rebound-neutral','help70','short70'].map(intervention=>{
  const original=rows.get(id+'-positional').result,r=rows.get(id+'-'+intervention).result;
  return {playerId:id,name:r.name,intervention,originalWinRate:original.winRate,winRate:r.winRate,
    change:paired(r.outcomes,original.outcomes),marginChange:r.meanMargin-original.meanMargin};
}));
const validation=read(ROOT+'/validation.json'),adoptionAudit=read(ROOT+'/adoption-audit.json');
if(!validation.passed||!adoptionAudit.passed)throw Error('Implementation validation failed');
const results={generatedAt:new Date().toISOString(),status:'diagnostic-only-unvalidated-player-ability',protocol:suffix,
  model:protocol.model,totalGames:checkpoint.rows.reduce((s,r)=>s+r.result.games,0),anchors,mapping,players,sensitivities,
  validation,adoptionAudit,unknownFields:protocol.unknown,sourceHashesVerified:true};
fs.writeFileSync(ROOT+'/results-'+suffix+'.json',JSON.stringify(results,null,2)+'\n');
const pct=v=>(100*v).toFixed(2)+'%',pp=v=>(100*v).toFixed(2),ci=a=>'['+a.map(pp).join(', ')+']';
const labels={'physique70':'僅候選體格→70','rebound-neutral':'候選籃板→70＋OREB→同位置平均','help70':'僅候選協防→70','short70':'僅候選近框→70'};
const md=[
  '# 2025–26 OVR：主位置與各位置平均隊友診斷','',
  '**狀態：診斷，未通過個人能力／換隊效度驗證。這不是修好後的新Top50。**','',
  `沿用採用引擎 \`${protocol.model}\`。本次固定${players.length}位代表球員，每條件${protocol.gamesPerPlayer.toLocaleString('en-US')}場；含基準及敏感度共${results.totalGames.toLocaleString('en-US')}場。原本582人榜與引擎未改。`,'',
  '## 為什麼四項是70','',
  '70是引擎中性錨點，不是四項能力已量測為聯盟平均。早期真實球季建卡就把 offBall/screen/handle/breakDbl 全設70；純卡最新版與舊v3球隊模擬都繼承。第十批第二步已記錄直接追蹤資料缺漏，當時沒有建卡。舊設計曾使用手填三欄對齊球權，但沒有獨立來源，不能拿來當全聯盟量測。','',
  '這次仍不把未知分數改成憑印象設定的高低分；因此本診斷只有可測屬性的角色分化，尚不具備使用者要求的完整「PG控球較高／C掩護較高」。未測量欄位在protocol與結果明列。','',
  '## 球隊表現與個人OVR為何會分離','',
  '| 項目 | 舊凍結v3球隊版 | 最新採用球隊版 | 舊OVR／本次診斷 |',
  '|---|---|---|---|',
  '| 四項未量測屬性 | 全70 | 全70 | 全70 |',
  '| 五組區段結果訊號 | 開啟 | 全關，刪defenseSignals | 全關，刪defenseSignals |',
  '| 個人觀測投籃／出手量 | 保留 | 保留 | 保留 |',
  '| 曝光／隊友 | 真實逐場名單與先發、分鐘軟目標 | 同左 | 人工隊友、固定曝光、無疲勞換人 |',
  '| 聯盟校準 | 有 | 有：包括shotDelta、OREB logit與pace | 沿用最新，未針對球員排名調參 |','',
  `已獨立重播採用球隊worker的卡投影，逐一對照${adoptionAudit.playerTeamStintCardsCompared}張在隊卡、582位球員的16屬性、防守量測及OREB卡；全部一致。事件機制選項亦一致，曝光／隊友／交易出手量合併差異另列在adoption-audit.json。`,'',
  '所以不是四項在球隊版有載入、OVR版漏掉。舊v3另有用區段結果估計的防守訊號，確實能補足部分球隊表現；最新純卡已關閉，不能把它說成仍靠同一組訊號補分。最新仍以真實個人效率、出手量、失誤、抄截、OREB與聯盟常數建模。這些效率本身含原隊友和角色影響，同季團隊重現不識別每個人的可攜能力。','',
  '最新四季同季合併報告：net RMSE約2.555、勝場MAE約4.94；這是條件式同季結果，不是個人能力或新陣容通過證明。全系統不能用單一球隊勝率指標總括驗收。','',
  '## 新測量規格','',
  '球員只打真實先發曝光中最常用的位置。官方已給五分位置者直接使用；僅G/F/C者才用助攻率／身高拆分。沒有先發者保留原身高帶回退、明列低信心；不把它假稱擅長位置。','',
  `位置來源：${protocol.roleAudit.exactFivePositionTeamGames}個隊伍場次有官方五分位置，${protocol.roleAudit.broadThreePositionTeamGames}個以G/F/C拆分。全582人中${protocol.roleAudit.fallbackPlayers}人無先發位置，${protocol.roleAudit.lowConfidencePlayers}人少於5次可用先發；完整roles表已輸出。`,'',
  '五種隊友取至少5次可用先發者的當季分鐘加權平均。對12項可測屬性做共同平移、保留位置差異，四項未知固定70，使每個角色的16項算術平均恰為70（總和1120）；這不表示每項70，也不表示模擬OVR天然70。身高與輔助觀測率保留各位置形狀。','',
  '| 位置 | 三分 | 近框 | 傳球 | 籃板 | 體格 | 協防 | 控球／無球／掩護／破包夾 | 平均 |',
  '|---|---:|---:|---:|---:|---:|---:|---|---:|',
  ...protocol.profiles.map(p=>`| ${p.pos} | ${p.long.toFixed(1)} | ${p.short.toFixed(1)} | ${p.pass.toFixed(1)} | ${p.rebound.toFixed(1)} | ${p.physique.toFixed(1)} | ${p.help.toFixed(1)} | 70（未量測） | ${(ATTRIBUTES.reduce((s,k)=>s+p[k],0)/16).toFixed(1)} |`),'',
  '對手池、球員卡、引擎和14.4分鐘曝光沿用原測量，沒有同時換對手或修引擎。flat與positional使用共同seed，可對角色隊友改動作配對比較。對手仍是既有分鐘前五、按身高排序，未宣稱已修正所有對位。','',
  '## 同一引擎的對照結果','',
  '固定主位置後，Queta與Curry在全70隊友下的勝率差為19.71pp；換成角色隊友後為8.84pp。測量環境解釋部分差距，但未消除Queta/Kornet高於Jokić等不合理警訊；未據此升為可信OVR或重排全聯盟。這些結論只針對本次代表集。','',
  '| 球員 | 主位置 | 舊五位置平均勝率 | 只打主位置＋全70隊友 | 只打主位置＋角色隊友 | 角色隊友差 pp [95%] |',
  '|---|---|---:|---:|---:|---|',
  ...players.map(p=>`| ${p.name} | ${p.position}${p.role.lowConfidence?' *':''} | ${pct(p.oldFiveSlotWinRate)} | ${pct(p.naturalSlotFlatWinRate)} | ${pct(p.naturalSlotPositionalWinRate)} | ${pp(p.profileChange.delta)} ${ci(p.profileChange.ci95)} |`),'',
  '* 主位置少於5次可用先發；並非全582人重排。抽樣區間僅表示固定輸入的模擬誤差，不含位置、建卡或模型不確定性。','',
  '診斷OVR分數另存JSON，用本規格五位置40/70/99錨點等權匯總的共同映射；不要與舊OVR當成同一刻度。正文以原始勝率比較，避免換刻度看似修好了排序。','',
  '## 敏感度：哪些已建模能力在推動結果','',
  '| 球員 | 介入（其餘固定） | 原勝率 | 介入後勝率 | 差 pp [配對95%] |',
  '|---|---|---:|---:|---|',
  ...sensitivities.map(s=>`| ${s.name} | ${labels[s.intervention]} | ${pct(s.originalWinRate)} | ${pct(s.winRate)} | ${pp(s.change.delta)} ${ci(s.change.ci95)} |`),'',
  '這些是候選卡的一次一組介入，不是正確新卡；效應非線性、不得相加，也不能以一位球員推論全聯盟係數應改多少。「體格→70」同時影響其所有體格路徑，尚未識別每條路徑的合理係數。','',
  '## 已有警訊與後續驗收','',
  '第十批第二步已做過五中鋒極端陣容診斷：取消該測試隊進攻籃板，ORtg約下降26.60；一般位置配置約下降8.22；壓低控球相關欄位的人工壓力測試約下降30.89。它不是本次最新版的單一球員消融，也不證明這些效果可相加，但說明問題早有紀錄，不能只怪本次換位置。','',
  '下一版要分別驗收：團隊同季重現、留出期間或跨季預測、換人／換隊的邊際影響、五中鋒／無控球／無空間等極端陣容。四項缺資料需獨立追蹤或具明確定義的代理；screen與breakDbl尤其不能把身材、球隊殘差或名氣直接當答案。修係數後需重跑原團隊驗證，不能只按一張看起來合理的球員榜調參。','',
  `實作驗證：${validation.cacheNativeFullOutputParityGames}場加速／原引擎完整輸出一致；五角色平均、錨點平均、代表主位置與來源雜湊通過。這不是籃球能力效度驗證。`,'',
  '## 來源與重現','',
  '- `scripts/build_season_league.js`：四項固定70。',
  '- `reports/defense-tenth/step2/report.md`：資料缺漏與五中鋒診斷。',
  '- `reports/defense-tenth/step4-rebounds-turnover-time/worker.mjs`：最新球隊版關閉五訊號與卡投影。',
  '- `reports/defense-tenth/step4-rebounds-turnover-time/report.md`：最新條件式團隊成績與限制。',
  '- `reports/ovr-2025-26-latest/runtime.mjs`：舊OVR沿用採用機制及曝光差異。','',
  '`node reports/ovr-2025-26-positional/validate.mjs`',
  '`node reports/ovr-2025-26-positional/adoption-audit.mjs`',
  '`node reports/ovr-2025-26-positional/run.mjs`',
  '`node reports/ovr-2025-26-positional/report.mjs`','',
  '只有明確要全582人診斷重跑時才加 `--all`；主位置回退與四項缺漏限制仍存在。'];
fs.writeFileSync(ROOT+'/report-'+suffix+'.md',md.join('\n')+'\n');
console.log(JSON.stringify({totalGames:results.totalGames,mapping,players:players.map(p=>({name:p.name,pos:p.position,flat:p.naturalSlotFlatWinRate,positional:p.naturalSlotPositionalWinRate,diagnosticOvr:p.diagnosticOvr})),sensitivities},null,2));

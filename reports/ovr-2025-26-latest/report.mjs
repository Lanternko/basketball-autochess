import fs from 'node:fs';
import crypto from 'node:crypto';
import {ROOT,inputs} from './runtime.mjs';
import {winToOvr} from '../../src/strength_benchmark.js';
const x=inputs(),protocol=JSON.parse(fs.readFileSync(ROOT+'/protocol-16.json'));
const checkpoint=JSON.parse(fs.readFileSync(ROOT+'/checkpoint-16.json'));
if(checkpoint.fingerprint!==protocol.fingerprint)throw Error('Protocol/checkpoint mismatch');
for(const [f,expected] of Object.entries(protocol.hashes))if(crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')!==expected)throw Error('Source mismatch: '+f);
if(checkpoint.rows.length!==585)throw Error('Incomplete measurement: '+checkpoint.rows.length+'/585');
const anchorRows=[40,70,99].map(v=>checkpoint.rows.find(r=>r.job.kind==='anchor'&&r.job.id===-v).result);
const mapping=Object.fromEntries(['low','mid','high'].map((k,i)=>[k,anchorRows[i].winRate]));
winToOvr(.5,mapping);
const anchorSeparated=anchorRows[0].conservative95[1]<anchorRows[1].conservative95[0]&&anchorRows[1].conservative95[1]<anchorRows[2].conservative95[0];
const sources=new Map(x.players.map(p=>[p.playerId,p]));
const rows=checkpoint.rows.filter(r=>r.job.kind==='player').map(({result:r})=>{
  const p=sources.get(r.playerId);
  return {...r,team:x.membership[p.playerId].join(' / '),nativePosition:p.pos,
    seasonMinutes:p.observed.MIN,seasonGames:p.observed.GP,lowSample:p.observed.MIN<500,
    ovr:winToOvr(r.winRate,mapping),ovrConditionalCI95:r.ci95.map(v=>winToOvr(v,mapping))};
}).sort((a,b)=>b.winRate-a.winRate||a.playerId-b.playerId).map((p,i)=>({...p,rank:i+1}));
if(new Set(rows.map(p=>p.playerId)).size!==582)throw Error('Player count/duplicate mismatch');
const halfWidths=rows.map(p=>p.halfWidth95);
const audit={all582Players:true,anchorSeparated,monotonic:rows.every((r,i)=>!i||r.ovr<=rows[i-1].ovr),
  allHalfWidthsUnder2pp:halfWidths.every(h=>h<=.02),maxHalfWidth95:Math.max(...halfWidths),
  gamesPerMeasurement:protocol.gamesPerPlayer,totalGames:585*protocol.gamesPerPlayer,
  allSourcesUnchanged:true,memoizationParity:JSON.parse(fs.readFileSync(ROOT+'/validation.json')),
  playersWithCIOverlapping50th:rows.filter(p=>p.ci95[1]>=rows[49].ci95[0]&&p.ci95[0]<=rows[49].ci95[1]).length};
if(!audit.anchorSeparated||!audit.monotonic||!audit.memoizationParity.passed)throw Error('Acceptance failed');
const result={generatedAt:new Date().toISOString(),model:protocol.model,season:protocol.season,
  protocolFingerprint:protocol.fingerprint,protocol:'protocol-16.json',mapping,anchors:anchorRows,audit,players:rows};
fs.writeFileSync(ROOT+'/ranking.json',JSON.stringify(result,null,2)+'\n');
const csv=s=>'"'+String(s).replaceAll('"','""')+'"';
fs.writeFileSync(ROOT+'/ranking.csv','\uFEFF'+[
  ['Rank','Player','OVR','OVR_CI95_Low','OVR_CI95_High','WinRate','WinRate_CI95_Low','WinRate_CI95_High','Minutes','Teams','PlayerID'].map(csv).join(','),
  ...rows.map(p=>[p.rank,p.name,p.ovr,...p.ovrConditionalCI95,p.winRate,...p.ci95,p.seasonMinutes,p.team,p.playerId].map(csv).join(','))].join('\n')+'\n');
const pct=v=>(100*v).toFixed(2)+'%';
const md=[
  '# 2025–26 最新採用模型 OVR Top 50','',
  `模型：\`${protocol.model}\`。全 ${rows.length} 名球員，每人 ${protocol.gamesPerPlayer.toLocaleString('en-US')} 場；含 3 個錨點，共 ${audit.totalGames.toLocaleString('en-US')} 場模擬。`,'',
  '這是本次建立的固定曝光模擬 OVR，使用當季完整資料作同季回溯衡量；尚未驗證為真實 NBA 個人能力排名。','',
  '| 排名 | 球員 | OVR | OVR 95%區間† | 模擬勝率 | 當季分鐘 |','|---:|---|---:|---:|---:|---:|',
  ...rows.slice(0,50).map(p=>`| ${p.rank} | ${p.name}${p.lowSample?' *':''} | ${p.ovr} | ${p.ovrConditionalCI95.join('–')} | ${pct(p.winRate)} | ${Math.round(p.seasonMinutes).toLocaleString('en-US')} |`),'',
  '† 區間只涵蓋模擬抽樣誤差，條件於已估計的錨點；不包含建卡／模型誤差或錨點不確定性。相近名次未必分得出高下。整數 OVR 同分時依未取整數的勝率排列。',
  '* 當季少於 500 分鐘，建卡樣本較少；仍保留在全體排名中，不事後排除。','',
  '建卡限制：現有 offBall、screen、handle、breakDbl 四欄皆為中性70，缺少個別量測。五個位置等權與四名中性隊友也會影響不同角色的價值；球員換到其他隊友或賽制，排序可能不同。','',
  '交易口徑：候選球員的各隊 observed 計數先相加，再由全季 FGA、FG3A、FTA、TOV、MIN 重建出手分布與出手量。既有全季16屬性、防守量測與OREB卡沿用。固定對手陣容則保留各自在該隊的出手分布與出手量。初次取首隊版本的試算已標為 diagnostic-first-team，未用於本榜。','',
  '固定條件：30 隊固定對手池；每隊按真實在隊累積分鐘選 5 人，再按身高安排位置。候選搭配四名中性70隊友，輪流替換五個位置；每個對手／位置16個共同seed，交換兩種座位，和局算半勝。每場四節、每節216秒，共14.4分鐘，停用疲勞、換人及犯滿，不打延長。候選的投籃分布、出手量、抄截與個人進攻籃板卡均保留；最新事件機率、補籃與失誤時鐘路徑保留。這個口徑不評估出勤、輪替或體能續航價值。','',
  'OVR沿用既有勝率分段映射函式：全40／70／99的16屬性錨點分別對應OVR40／70／99；三種錨點的新增輔助欄位（出手量、抄截率、OREB份額）一律固定為聯盟中性值。中性隊友亦使用同一組聯盟輔助值。這是新的時鐘制測量，與舊固定回合榜不可直接比較。','',
  '| 錨點 | 勝率 | 95%抽樣區間 |','|---|---:|---:|',
  ...anchorRows.map((p,i)=>`| 全${[40,70,99][i]} → OVR${[40,70,99][i]} | ${pct(p.winRate)} | ${p.ci95.map(pct).join('–')} |`),'',
  `驗證：582個唯一球員ID與全季分隊計數合併；交易前後屬性一致；${audit.memoizationParity.games}場加速／原引擎完整輸出逐場相等；所有來源SHA-256不變；錨點保守區間分離=${anchorSeparated}；勝率至OVR單調=${audit.monotonic}；全體勝率95%區間半寬≤2pp=${audit.allHalfWidthsUnder2pp}（最大 ${(100*audit.maxHalfWidth95).toFixed(3)}pp）。`,
  `第50名的95%勝率區間與 ${audit.playersWithCIOverlapping50th} 名球員重疊，前50成員邊界仍有抽樣不確定性。`,'',
  '完整582人：[ranking.csv](ranking.csv)、[ranking.json](ranking.json)；輸入／規格／雜湊：[protocol-16.json](protocol-16.json)；原始分層測量：[checkpoint-16.json](checkpoint-16.json)。','',
  '重現：於專案根目錄執行 `node reports/ovr-2025-26-latest/run.mjs`，再執行 `node reports/ovr-2025-26-latest/report.mjs`。相同雜湊與規格會續用checkpoint；不同來源會拒絕混用。既有模型、凍結產物與歷次報告均未改寫。',''];
fs.writeFileSync(ROOT+'/top50.md',md.join('\n'));
console.log(JSON.stringify({audit,top10:rows.slice(0,10).map(p=>({rank:p.rank,name:p.name,ovr:p.ovr}))},null,2));

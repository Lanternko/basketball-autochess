// Offline comparison: no rerun, fitting, or selection of a "winning" opponent.
import fs from 'node:fs/promises';
const root = new URL('../reports/', import.meta.url);
const inputs = ['baselines/per36-v1.json','per36.json','per36-pr90.json'];
const datasets = await Promise.all(inputs.map(f=>fs.readFile(new URL(f,root),'utf8').then(JSON.parse)));
const labels = ['舊版全 70','新版全 70','新版全 94 壓力測試'];
const key = (r,p)=>`${r.team}|${r.season}|${p.name}`;
const maps = datasets.map(rows=>new Map(rows.flatMap(r=>r.players.map(p=>[key(r,p),{r,p}]))));
const entries = [...maps[0].keys()];
for(const map of maps) {
  if(map.size!==entries.length || entries.some(k=>!map.has(k))) throw new Error('Comparison player sets differ');
}
for(const k of entries) {
  const runs=maps.map(m=>m.get(k).r);
  if(runs.some(r=>r.n!==runs[0].n || r.seed!==runs[0].seed || r.exposure.pace!==runs[0].exposure.pace)) {
    throw new Error('Comparison requires same sample count, seeds and pace');
  }
}
const pct2 = s => s.fga>s.fg3a ? (s.fgm-s.fg3m)/(s.fga-s.fg3a) : null;
const get = (s,k)=>k==='twoPct' ? (s.twoPct ?? pct2(s)) : s[k];
const metrics = [
  ['pts','得分',1],['reb','籃板',1],['oreb','進攻籃板',1],['tov','失誤',1],
  ['blk','火鍋 beta',1],['twoPct','二分命中率（pp）',100],
  ['threePct','三分命中率（pp）',100],['ftPct','罰球命中率（pp）',100],
];
const f=(x,n=2)=>Number.isFinite(x)?x.toFixed(n):'—';
const pct=x=>Number.isFinite(x)?`${(x*100).toFixed(1)}%`:'—';
const summary=metrics.map(([k,label,scale])=>({metric:k,label,
  runs:datasets.map(rows=>{
    const errors=rows.flatMap(r=>r.players).map(p=>[get(p.simulated,k),get(p.real,k)])
      .filter(([sim,real])=>Number.isFinite(sim)&&Number.isFinite(real)).map(([s,a])=>(s-a)*scale);
    return { count:errors.length,mae:errors.length?errors.reduce((s,e)=>s+Math.abs(e),0)/errors.length:null,
      bias:errors.length?errors.reduce((s,e)=>s+e,0)/errors.length:null };
  })}));
const usage=datasets.map(rows=>{
  const errors=rows.flatMap(r=>r.players).map(p=>p.error.usageProxyPercentagePoints);
  return errors.reduce((s,e)=>s+Math.abs(e),0)/errors.length;
});
const lines=['# 籃板／火鍋與全屬性壓力測試比較','',
  `${datasets[1].length} 隊，共 ${entries.length} 人；各情境每隊 ${datasets[1][0].n.toLocaleString('en-US')} 場、相同 seed 與 pace、疲勞關閉。所有真實計數換算成同季 per-36。`, '',
  '舊版保存於 `baselines/per36-v1.json`。新版只改籃板分配及火鍋記帳，投籃／罰球曲線、球權及包夾公式未調參。', '',
  '舊稱 PR50／PR90 實際是全屬性 70／94；它們不是球隊實力百分位。全 94 僅保留為極端壓力測試，不能據此判斷聯盟前三名對戰、季後賽表現或調整命中率。表內 50／90 皆為歷史單項屬性標記。', '',
  '## 25 人平均絕對誤差（越小越接近來源）','',
  `| 指標 | ${labels.join(' | ')} |`, '|---|---:|---:|---:|',
  ...summary.map(s=>`| ${s.label} | ${s.runs.map(r=>f(r.mae)).join(' | ')} |`),
  `| usage 正規化代理（pp，非正式驗收） | ${usage.map(x=>f(x)).join(' | ')} |`, '',
  '火鍋是既有 miss 的條件分類，沒有再扣命中率；封阻後仍有籃板。其區域機率與位置分配為原型假設，未用這 25 人調到答案。抄截仍只有傳球攔截。', ''];
for(const r of datasets[1]) {
  lines.push(`## ${r.team}`,'',
    '| 球員 | 籃板 舊50→新50 / 真實 | OREB 舊50→新50 / 真實 | 得分 新50 / 新90 / 真實 | 火鍋 新50 / 新90 / 真實 |',
    '|---|---:|---:|---:|---:|');
  for(const p of r.players) {
    const old=maps[0].get(key(r,p)).p.simulated,s=p.simulated,
      high=maps[2].get(key(r,p)).p.simulated,a=p.real;
    lines.push(`| ${p.name} | ${f(old.reb,1)}→${f(s.reb,1)} / ${f(a.reb,1)} | ${f(old.oreb,1)}→${f(s.oreb,1)} / ${f(a.oreb,1)} | ${f(s.pts,1)} / ${f(high.pts,1)} / ${f(a.pts,1)} | ${f(s.blk,1)} / ${f(high.blk,1)} / ${f(a.blk,1)} |`);
  }
  lines.push('','| 球員 | 二分 新50 / 新90 / 真實 | 三分 新50 / 新90 / 真實 | USG 新50 / 新90 / 整季真實* |',
    '|---|---:|---:|---:|');
  for(const p of r.players) {
    const high=maps[2].get(key(r,p)).p.simulated,s=p.simulated,a=p.real;
    lines.push(`| ${p.name} | ${pct(s.twoPct)} / ${pct(high.twoPct)} / ${pct(a.twoPct)} | ${pct(s.threePct)} / ${pct(high.threePct)} / ${pct(a.threePct)} | ${f(s.usagePct,1)} / ${f(high.usagePct,1)} / ${f(a.usagePct,1)} |`);
  }
  lines.push('');
}
lines.push('*官方整季 USG 與固定五人同時上場的模擬份額情境不同。相關來源及抓取日期見完整 per36 報表。','',
  '- [新版 PR50 完整報表](per36.md)', '- [新版 PR90 完整報表](per36-pr90.md)', '');
await fs.writeFile(new URL('rebound-pr-comparison.md',root),lines.join('\n'));
await fs.writeFile(new URL('rebound-pr-comparison.json',root),JSON.stringify({inputs,labels,summary,usageProxyMae:usage},null,2)+'\n');
console.log('Saved reports/rebound-pr-comparison.md');

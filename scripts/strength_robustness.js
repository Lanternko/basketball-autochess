import fs from 'node:fs';
import {measureStrength,probe} from '../src/strength_benchmark.js';
import {TEAMS} from '../src/teams.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url)));
const primary=read('../reports/strength-validation.json'),league=read('../data/benchmark-league.json');
const costs=read('../data/card-costs.json').costs;
const teamSource=read('../data/benchmark-source/teams.json').data.resultSets[0];
const observed=new Map(teamSource.rowSet.map(row=>{const r=Object.fromEntries(teamSource.headers.map((k,i)=>[k,row[i]]));return[r.TEAM_ID,r];}));
const ranks=xs=>xs.map(x=>1+xs.filter(y=>y>x).length+(xs.filter(y=>y===x).length-1)/2);
const correlation=(xs,ys)=>{
 const mean=x=>x.reduce((a,b)=>a+b,0)/x.length, mx=mean(xs),my=mean(ys);
 return xs.reduce((s,x,i)=>s+(x-mx)*(ys[i]-my),0)/Math.sqrt(xs.reduce((s,x)=>s+(x-mx)**2,0)*ys.reduce((s,y)=>s+(y-my)**2,0));
};
const teamBackground=primary.teams.map(t=>({name:t.name,modelRank:t.rank,modelWinRate:t.winRate,observedWinRate:observed.get(t.id).W_PCT}));
if(teamBackground.some(t=>!Number.isFinite(t.observedWinRate)))throw new Error('Missing observed team wins');
const teamRankCorrelation=correlation(ranks(teamBackground.map(t=>t.modelWinRate)),ranks(teamBackground.map(t=>t.observedWinRate)));
const seed=20261119,rows=[];
for(const p of primary.players){
 const card=TEAMS[p.team].roster.find(r=>r.name===p.name);
 const fresh=measureStrength(Array.from({length:5},(_,i)=>probe(card,i)),league.teams,{...primary.rules,seed,samples:16});
 rows.push({name:p.name,primaryWinRate:p.winRate,primaryCI95:p.ci95,cost:costs[p.name],...fresh});
 console.log('Independent seed',p.name,fresh.winRate.toFixed(3));
}
const reversals=[];
for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++)if(rows[i].winRate<rows[j].winRate)reversals.push({higher:rows[i].name,lower:rows[j].name,separated:rows[i].ci95[1]<rows[j].ci95[0]});
const costGroups=[1,2,3,4,5].map(cost=>{const r=rows.filter(p=>p.cost===cost);return{cost,count:r.length,winRate:r.reduce((n,p)=>n+p.primaryWinRate,0)/r.length};});
let pairs=0,inversions=0;
for(const a of rows)for(const b of rows)if(a.cost>b.cost){pairs++;if(a.primaryWinRate<b.primaryWinRate)inversions++;}
const report={primaryFingerprint:primary.fingerprint,seed,samplesPerOpponentSlot:16,rows,reversals,costGroups,teamBackground,teamRankCorrelation,costDiagnostic:{pairs,inversions,inversionRate:inversions/pairs,groupMeansMonotonic:costGroups.every((p,i)=>i===0||p.winRate>=costGroups[i-1].winRate)},
 caveat:'Independent-seed results are not used to re-fit OVR. CI overlap is inconclusive, not proof of equality. Costs are existing design labels, diagnostic only. Multiple pair comparisons are exploratory.'};
fs.writeFileSync(new URL('../reports/strength-robustness.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(new URL('../reports/strength-robustness.md',import.meta.url),['# 獨立 seed 穩健性與費用診斷','',`固定新 seed ${seed}，每位球員 ${rows[0].games} 場；不重新擬合 OVR。`, '',`25 人共300對：${reversals.length} 對估計排序反轉，其中 ${reversals.filter(r=>r.separated).length} 對新seed的邊際95%區間分離。這是探索性多重比較，未作家族錯誤率校正。`, '',`費用均值單調：${report.costDiagnostic.groupMeansMonotonic}；跨費用反轉 ${inversions}/${pairs}。費用不輸入 OVR，也不根據結果重新分配。`, '', '| 費用 | 人數 | 基準平均勝率 |','|---|---:|---:|',...costGroups.map(g=>`| ${g.cost} | ${g.count} | ${(g.winRate*100).toFixed(2)}% |`),'', `球隊模型排名與官方整季勝率的 Spearman 相關：${teamRankCorrelation.toFixed(3)}。真實球季有完整輪換、傷病與不同賽程；此為外部背景診斷，不是匹配條件的驗收，也未用來擬合模型。`, '', '| 球員 | 主基準勝率 | 新seed勝率 | 新seed95% CI |','|---|---:|---:|---:|',...rows.map(r=>`| ${r.name} | ${(100*r.primaryWinRate).toFixed(2)}% | ${(100*r.winRate).toFixed(2)}% | ${r.ci95.map(p=>(p*100).toFixed(2)).join('–')}% |`),''].join('\n'));

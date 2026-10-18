import fs from 'node:fs';
import crypto from 'node:crypto';
import {clockSeconds} from '../../../src/defense_pbp_analysis.js';
const root='reports/defense-tenth/step4-t1';
const read=p=>JSON.parse(fs.readFileSync(p));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save=(p,j)=>fs.writeFileSync(root+'/'+p,JSON.stringify(j,null,2)+'\n');
const protocol=read(root+'/protocol.json');
if(hash(root+'/protocol.json')!==fs.readFileSync(root+'/protocol.sha256','utf8').split(' ')[0])throw Error('Protocol changed');
for(const [p,h] of Object.entries(protocol.inputHashes))if(hash(p)!==h)throw Error('Input changed: '+p);
const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
const sd=a=>Math.sqrt(mean(a.map(x=>(x-mean(a))**2)));
const corr=(a,b)=>{const ma=mean(a),mb=mean(b);return mean(a.map((x,i)=>(x-ma)*(b[i]-mb)))/(sd(a)*sd(b));};
// Equality tolerance only removes floating point noise; no ranking jitter.
const ranks=a=>a.map(v=>1+a.filter(x=>x>v+1e-10).length+(a.filter(x=>Math.abs(x-v)<=1e-10).length-1)/2);
const rmse=a=>Math.sqrt(mean(a.map(v=>v*v)));
const fail=(ar,pr)=>ar<=5&&pr>10?'前五掉到10名後':ar>=26&&pr<=20?'倒五進前20':null;
const direction=v=>Math.abs(v)<=0.25?'接近零':v>0?'高估':'低估';
const table=p=>{const t=read(p).data.resultSets[0];return t.rowSet.map(r=>Object.fromEntries(t.headers.map((h,i)=>[h,r[i]])));};
const stats={},real={},sourceAudit=[];
for(const season of protocol.seasons){
  const base=season==='2025-26'?'data/season-source':`data/defense-seventh/${season}`;
  const league=read(season==='2025-26'?'data/season-league.json':base+'/league.json');
  const rows=table(base+'/team-games.json');
  const byGame=new Map();for(const r of rows){const a=byGame.get(r.GAME_ID)??[];a.push(r);byGame.set(r.GAME_ID,a);}
  const teams=Object.fromEntries(league.teams.map(t=>[t.id,{id:t.id,name:t.name,games:0,wins:0,pf:0,pa:0,minutes:0,closeGames:0,closeWins:0,validGames:0,validMinutes:0,validNet:0,clutchMinutes:0,clutchNet:0,clutchPF:0,clutchPA:0}]));
  for(const rows of byGame.values()){
    if(rows.length!==2)throw Error('Nonpaired box');
    for(let i=0;i<2;i++){const r=rows[i],opp=rows[1-i],t=teams[r.TEAM_ID];t.games++;t.wins+=+(r.WL==='W');t.pf+=r.PTS;t.pa+=opp.PTS;t.minutes+=r.MIN/5;
      if(Math.abs(r.PTS-opp.PTS)<=5){t.closeGames++;t.closeWins+=+(r.WL==='W');}}
  }
  const mp=season==='2025-26'?'data/defense-a-source/manifest.json':base+'/manifest.json';
  const manifest=read(mp),failures=[],sources=[];
  for(const s of manifest.sources){
    const box=byGame.get(s.id);if(!box){failures.push({id:s.id,reason:'not in regular-season paired logs'});continue;}
    const actualHash=hash(s.file);if(s.sha256&&actualHash!==s.sha256)throw Error('Raw input hash changed: '+s.file);
    sources.push({file:s.file,sha256:actualHash});
    const actions=read(s.file).data.game.actions;
    const home=box.find(r=>r.MATCHUP.includes('vs.')),away=box.find(r=>r!==home);
    if(!home||!away){failures.push({id:s.id,reason:'no official home assignment'});continue;}
    let previousScore=[0,0],period=0,previousTime=0,minutes=0,cMinutes=0,cNet=0,cPF=0,cPA=0,bad=false;
    const span=(end)=>{const dt=previousTime-end;if(dt<-0.01){bad=true;return;}minutes+=Math.max(0,dt)/60;
      if(period>=4&&Math.abs(previousScore[0]-previousScore[1])<=5)cMinutes+=Math.max(0,Math.min(previousTime,300)-end)/60;};
    for(const e of actions){
      if(!e.period)continue;
      if(e.period!==period){if(period)span(0);period=e.period;previousTime=period<=4?720:300;}
      const time=clockSeconds(e);span(time);previousTime=time;
      const score=[Number(e.scoreHome),Number(e.scoreAway)];
      if(score.some(x=>!Number.isFinite(x))){bad=true;continue;}
      const ds=score.map((v,i)=>v-previousScore[i]);if(ds.some(x=>x<0))bad=true;
      if(e.period>=4&&time<=300&&Math.abs(previousScore[0]-previousScore[1])<=5){cNet+=ds[0]-ds[1];cPF+=ds[0];cPA+=ds[1];}
      previousScore=score;
    }
    if(period)span(0);
    if(bad||previousScore[0]!==home.PTS||previousScore[1]!==away.PTS||Math.abs(minutes-home.MIN/5)>0.1){failures.push({id:s.id,reason:'score/clock reconciliation',bad,final:previousScore,box:[home.PTS,away.PTS],minutes,boxMinutes:home.MIN/5});continue;}
    [home,away].forEach((r,i)=>{const t=teams[r.TEAM_ID];t.validGames++;t.validMinutes+=minutes;t.validNet+=(i===0?1:-1)*(home.PTS-away.PTS);t.clutchMinutes+=cMinutes;t.clutchNet+=(i===0?1:-1)*cNet;t.clutchPF+=i===0?cPF:cPA;t.clutchPA+=i===0?cPA:cPF;});
  }
  const sourceIds=new Set(manifest.sources.map(s=>s.id));for(const id of byGame.keys())if(!sourceIds.has(id))failures.push({id,reason:'missing PBP'});
  for(const t of Object.values(teams)){
    t.off=t.pf/t.games;t.allowed=t.pa/t.games;t.net=(t.pf-t.pa)/t.games;
    t.clutchNetPer48=t.clutchMinutes>0?t.clutchNet/t.clutchMinutes*48:null;
    const nonminutes=t.validMinutes-t.clutchMinutes;
    t.nonclutchNetPer48=nonminutes>0?(t.validNet-t.clutchNet)/nonminutes*48:null;
    t.clutchImpact=t.clutchNetPer48===null?null:(t.clutchNet-t.nonclutchNetPer48*t.clutchMinutes/48)/t.validGames;
    t.clutchCoverage=t.validGames/t.games;
    t.clutchFlag=t.clutchCoverage>=protocol.attribution.clutch.minimumCoverage&&t.clutchMinutes>=40&&Math.abs(t.clutchNetPer48-t.nonclutchNetPer48)>=10&&Math.abs(t.clutchImpact)>=0.75;
    t.closeWinRate=t.closeGames?t.closeWins/t.closeGames:null;
    t.expectedWins=t.games*t.pf**14/(t.pf**14+t.pa**14);
    t.winExcess=t.wins-t.expectedWins;
    t.luckFlag=t.closeGames>=15&&Math.abs(t.closeWinRate-0.5)>=0.15&&Math.abs(t.winExcess)>=3&&Math.sign(t.closeWinRate-0.5)===Math.sign(t.winExcess);
  }
  stats[season]=teams;real[season]={teams:Object.values(teams),games:byGame.size,validGames:(Object.values(teams).reduce((s,t)=>s+t.validGames,0))/2,failures};
  sourceAudit.push({season,manifest:mp,manifestHash:hash(mp),leagueHash:hash(season==='2025-26'?'data/season-league.json':base+'/league.json'),boxHash:hash(base+'/team-games.json'),sources});
  console.log('Real diagnostics',season,real[season].validGames+'/'+byGame.size,'failures',failures.length);
}
const old=read('reports/defense-seventh/full-comparison.json');
const a2=read('reports/defense-tenth/step3-a2/analysis.json');
const cells=[];
const prepare=(task,season,version,rows,source,exposures=null)=>{
  const truths=stats[season];
  const teams=rows.map(r=>({id:r.id,name:r.name,net:r.net,wins:r.wins,off:r.off??r.ppg,allowed:r.allowed??r.opponentPPG,actual:truths[r.id],sourceActual:r.actual??r.observed}));
  if(teams.length!==30)throw Error('Expected 30 teams');
  for(const t of teams)if(Math.abs(t.actual.net-t.sourceActual.net)>1e-8||t.actual.wins!==t.sourceActual.wins)throw Error('Truth differs '+season+' '+t.name);
  const mo=mean(teams.map(t=>t.off-t.actual.off)),md=mean(teams.map(t=>t.actual.allowed-t.allowed));
  const predNet=teams.map(t=>t.net),truthNet=teams.map(t=>t.actual.net),pn=ranks(predNet),an=ranks(truthNet),pw=ranks(teams.map(t=>t.wins)),aw=ranks(teams.map(t=>t.actual.wins));
  const centeredNet=teams.map(t=>t.net-t.actual.net-mean(predNet)+mean(truthNet));
  const clutchRanks=ranks(teams.map(t=>t.actual.net-(t.actual.clutchImpact??0)));
  const expectedRanks=ranks(teams.map(t=>t.actual.expectedWins));
  const pair=task==='task2'&&version==='L1'?a2.cells.find(c=>c.target===season).versions.L2.teams:null;
  const pairNet=pair?ranks(teams.map(t=>pair.find(p=>p.id===t.id).net)):null,pairWins=pair?ranks(teams.map(t=>pair.find(p=>p.id===t.id).wins)):null;
  const failures=[];
  for(let i=0;i<teams.length;i++){
    const t=teams[i];t.netRank=pn[i];t.actualNetRank=an[i];t.winsRank=pw[i];t.actualWinsRank=aw[i];
    t.netError=centeredNet[i];t.rawNetError=t.net-t.actual.net;t.winsError=t.wins-t.actual.wins;
    t.rawO=t.off-t.actual.off;t.rawD=t.actual.allowed-t.allowed;t.O=t.rawO-mo;t.D=t.rawD-md;
    if(Math.abs(t.O+t.D-t.netError)>1e-8)throw Error('O+D identity');
    t.priorOnlyMinuteShare=exposures?.teams?.[t.id]?.priorOnlyMinuteShare??null;
    for(const axis of ['net','wins']){
      const actualRank=axis==='net'?an[i]:aw[i],predictedRank=axis==='net'?pn[i]:pw[i],type=fail(actualRank,predictedRank);if(!type)continue;
      const e=axis==='net'?t.rawNetError:t.winsError,explanations=[],flags=[];
      if(t.actual.clutchFlag){
        const contribution=t.actual.clutchImpact,remaining=e+contribution;
        const eligible=axis==='net'&&Math.sign(-e)===Math.sign(contribution)&&Math.abs(remaining)<=0.5*Math.abs(e)&&!fail(clutchRanks[i],predictedRank);
        flags.push({category:'關鍵時刻異常',contribution,explainedFraction:axis==='net'?1-Math.abs(remaining)/Math.abs(e):null,eligible,axis:'net only',clutchMinutes:t.actual.clutchMinutes,rateDifferencePer48:t.actual.clutchNetPer48-t.actual.nonclutchNetPer48,counterfactualActualRank:clutchRanks[i]});
        if(eligible)explanations.push('關鍵時刻異常（答案側反事實支持，非因果證明）');
      }
      if(t.actual.luckFlag){
        const contribution=t.actual.winExcess,remaining=e+contribution;
        const eligible=axis==='wins'&&Math.sign(-e)===Math.sign(contribution)&&Math.abs(remaining)<=0.5*Math.abs(e)&&!fail(expectedRanks[i],predictedRank);
        flags.push({category:'接戰／勝場轉換異常',contribution,eligible,axis:'wins only',closeGames:t.actual.closeGames,closeWinRate:t.actual.closeWinRate,counterfactualActualRank:expectedRanks[i]});
        if(eligible)explanations.push('接戰／勝場轉換異常（未證明全是隨機運氣）');
      }
      if(pair&&t.priorOnlyMinuteShare>=0.1){
        const p=pair.find(p=>p.id===t.id),pe=axis==='net'?p.net-t.actual.net:p.wins-t.actual.wins,pr=axis==='net'?pairNet[i]:pairWins[i];
        const eligible=Math.abs(pe)<=0.5*Math.abs(e)&&!fail(actualRank,pr);
        flags.push({category:'缺前季個人樣本',share:t.priorOnlyMinuteShare,pairedChange:pe-e,L2Error:pe,L2Rank:pr,eligible});
        if(eligible)explanations.push('缺前季個人樣本（L2介入支持）');
      }
      failures.push({id:t.id,name:t.name,axis,type,actualRank,predictedRank,netError:t.netError,O:t.O,D:t.D,offenseDirection:direction(t.O),defenseDirection:direction(t.D),winsError:t.winsError,explanations,flags,status:explanations.length?'客觀條件支持解釋':'無法解釋'});
    }
  }
  const metrics={netRMSE:rmse(centeredNet),netRawRMSE:rmse(teams.map(t=>t.rawNetError)),Spearman:corr(pn,an),Pearson:corr(predNet,truthNet),winsMAE:mean(teams.map(t=>Math.abs(t.winsError))),winsRMSE:rmse(teams.map(t=>t.winsError)),calibrationSlope:corr(predNet,truthNet)*sd(truthNet)/sd(predNet),SDRatio:sd(predNet)/sd(truthNet),offenseRMSE:rmse(teams.map(t=>t.O)),defenseRMSE:rmse(teams.map(t=>t.D)),offenseBias:mo,defenseStrengthBias:md};
  cells.push({task,season,version,source,metrics,netPass:!failures.some(f=>f.axis==='net'),winsPass:!failures.some(f=>f.axis==='wins'),pass:!failures.length,failures,teams,okc:teams.find(t=>t.id===1610612760),limitations:task==='task1'?'同季含答案；v3含區段訊號，不是純卡。真實分鐘軟目標，非逐秒換人重播。':'既有球員用前季卡，L2新人用目標季卡；同季其他能力變化仍未處理，且不是換隊子群獨立檢定。未來名單/分鐘已知，預先排定賽程與真實賽程不完全相同。'});
};
prepare('task1','2025-26','v1',old.v1.teams,'reports/defense-fourth/v1-seeds.json');
prepare('task1','2025-26','v3',old.v3.teams,'reports/defense-fourth/final-normalized-seeds.json');
for(const c of a2.cells)for(const version of ['L1','L2'])prepare('task2',c.target,version,c.versions[version].teams,'reports/defense-tenth/step3-a2/analysis.json',c.oracleExposure);
const coverage=protocol.seasons.flatMap(season=>['pure','v3','v1','simple'].map(version=>({task:'task1',season,version,available:cells.some(c=>c.task==='task1'&&c.season===season&&c.version===version),reason:cells.some(c=>c.task==='task1'&&c.season===season&&c.version===version)?'既有20seed全季結果':version==='pure'?'只有截止後K25/41/55純卡；缺全季同季建卡＋五訊號全關/no-map的20seed輸出':version==='simple'?'既有simple為截止後或沿用前季對照；没有符合全季同季的既有預測。複製全季真實net不算驗證。':'只有日曆截止後資料外結果；缺全季同季20seed模擬'})));
save('coverage.json',coverage);save('real-diagnostics.json',real);save('source-audit.json',sourceAudit);
save('analysis.json',{version:protocol.version,protocolHash:hash(root+'/protocol.json'),label:'已看過答案；既有輸出的新門檻重評，不是新預測',cells,coverage,existingJointIntervals:a2.intervals});
console.log('Scoring',cells.map(c=>({task:c.task,season:c.season,version:c.version,netFailures:c.failures.filter(f=>f.axis==='net').length,winsFailures:c.failures.filter(f=>f.axis==='wins').length,explained:c.failures.filter(f=>f.explanations.length).length,metrics:c.metrics})));

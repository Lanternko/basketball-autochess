import fs from 'node:fs';import crypto from 'node:crypto';
const root='reports/defense-tenth/step4-t2',read=p=>JSON.parse(fs.readFileSync(p)),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const p=read(root+'/protocol.json'),s=read(root+'/measurement-supplement.json'),issues=[],protectedHashes=read(root+'/protected-before.json');
for(const [file,h]of Object.entries(protectedHashes))if(!fs.existsSync(file)||hash(file)!==h)issues.push({reason:'protected file changed',file});
for(const [file,h]of Object.entries({...p.inputHashes,...s.strictAudit}))if(hash(file)!==h)issues.push({reason:'measurement source changed',file});
for(const file of ['protocol','measurement-supplement'])if(hash(root+'/'+file+'.json')!==fs.readFileSync(root+'/'+file+'.sha256','utf8').split(' ')[0])issues.push({reason:'registration changed',file});
const fetch=read(root+'/fetch-manifest.json'),trades=read(root+'/trade-sources.json');
for(const src of [...fetch.sources,...trades.sources])if(hash(src.file)!==src.sha256)issues.push({reason:'download hash mismatch',file:src.file});
const strict=read(root+'/strict-failures.json'),players=read(root+'/players.json'),correlations=read(root+'/correlations.json'),team=read(root+'/team-correlations.json');
for(const q of strict){if(q.usable+q.failures.length!==1230||q.usable!==players[q.season].strictGames)issues.push({reason:'strict coverage identity',season:q.season});}
let checks=0;
for(const [season,data]of Object.entries(players))for(const pl of Object.values(data.players))for(const tm of Object.values(pl.teams)){
  for(const key of Object.keys(tm.on))if(Math.abs(tm.on[key]+tm.off[key]-tm.matchedTeam[key])>1e-6)issues.push({reason:'on+off != matched team',season,id:pl.id,team:tm.id,key});
  if(tm.on.poss>0&&Math.abs(-tm.metrics.onDefRtg*tm.on.poss/100-tm.on.points)>1e-6)issues.push({reason:'ON point/possession identity',season,id:pl.id});checks++;
}
// Independent moment-form verification of all reported pooled/season points.
const adj=read(root+'/adjacent-samples.json').rows,moves=read(root+'/move-samples.json').rows;
const point=rows=>{const periods=[...new Set(rows.map(r=>r.period))];let vx=0,vy=0,cv=0;
  for(const period of periods){const rr=rows.filter(r=>r.period===period),n=rr.length,mx=rr.reduce((s,r)=>s+r.x,0)/n,my=rr.reduce((s,r)=>s+r.y,0)/n;vx+=rr.reduce((s,r)=>s+(r.x-mx)**2,0)/n;vy+=rr.reduce((s,r)=>s+(r.y-my)**2,0)/n;cv+=rr.reduce((s,r)=>s+(r.x-mx)*(r.y-my),0)/n;}return cv/Math.sqrt(vx*vy);};
for(const c of correlations){const candidates=c.comparison==='adjacent'?adj:moves,rows=candidates.filter(r=>r.metric===c.metric&&(c.period==='pooled'||r.period===c.period)&&(c.comparison==='adjacent'?r.group===c.group:c.group==='seasonMove'||r.officialTradeParticipant));
  if(rows.length!==c.n)issues.push({reason:'pair count mismatch',metric:c.metric,group:c.group,period:c.period});
  if(c.pearson!==null&&Math.abs(point(rows)-c.pearson)>1e-9)issues.push({reason:'correlation does not reproduce',metric:c.metric,group:c.group,period:c.period});
  if(c.ci95&&(c.validBootstrap>20000||c.validBootstrap<10000||c.ci95.some(v=>!Number.isFinite(v)||Math.abs(v)>1.0000001)))issues.push({reason:'invalid bootstrap',metric:c.metric,group:c.group,period:c.period});
}
const endpoint=read(root+'/endpoint-audit.json');
const audit={completedAt:new Date().toISOString(),issues,protectedFiles:Object.keys(protectedHashes).length,originalProtocolSHA:hash(root+'/protocol.json'),supplementSHA:hash(root+'/measurement-supplement.json'),verifiedDownloads:fetch.sources.length,tradingDocuments:trades.sources.length,endpointFailures:fetch.failures.length,strictGames:Object.fromEntries(strict.map(q=>[q.season,q.usable])),onOffPlayerTeamChecks:checks,verifiedCorrelationPoints:correlations.length,teamCorrelationCells:team.results.length,filteredRowsRejected:endpoint.rejectedRows.length,splitCountChecks:endpoint.splitReconciliations.length,splitCountMismatches:endpoint.splitReconciliations.filter(q=>Math.abs(q.difference)>1e-6).length,mergedGlobalTrackingRows:endpoint.duplicateRowsMerged,newSimulations:0,newCards:0,unchanged:['A','A2','T1','src'],stopAt:'T2'};
fs.writeFileSync(root+'/completion-audit.json',JSON.stringify(audit,null,2)+'\n');
const files=fs.readdirSync(root).filter(f=>f!=='deliverable-hashes.json'&&fs.statSync(root+'/'+f).isFile()).sort();fs.writeFileSync(root+'/deliverable-hashes.json',JSON.stringify(Object.fromEntries(files.map(f=>[f,hash(root+'/'+f)])),null,2)+'\n');
console.log(JSON.stringify(audit));if(issues.length)process.exitCode=1;

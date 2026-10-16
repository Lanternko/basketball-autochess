import json,hashlib,math
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda f,d:(R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(R/'protocol.json');a=read(R/'analysis.json');pl=read(R/'player-analysis.json');team=read(R/'joint-intervals.json');player=read(R/'joint-player-intervals.json');joint=team['comparisons']['four-seasons-equal'];pd=player['comparisons']['four-seasons-equal'];d=joint['paired']['allocationMinusacquisition']
improved=pd['paired']['MAE']['joint95'][1]<0
harms=[k for k in ['OREB_RMSE','DREB_RMSE','netRMSE','winsMAE'] if d[k]['joint95'][0]>0]
drift=[{'season':c['season'],'efficiencyBias':c['metrics']['efficiencyBias'],'possessionsBias':c['metrics']['possessionsBias']} for c in a['cells'] if c['version']=='allocation' and (abs(c['metrics']['efficiencyBias'])>.5 or abs(c['metrics']['possessionsBias'])>.5)]
decision={'version':p['version'],'interpretation':p['label'],'confirmedPlayerOrebMAEImprovement':improved,'significantHarms':harms,'leagueDriftFailures':drift,'eligibleCandidate':improved and not harms and not drift,'baselinePromoted':False,'primary':pd['paired'],'teamPaired':d,'rule':p['decision']}
write('decision.json',decision)
issues=[];protected=read(R/'protected-before.json');supp=read(R/'analysis-supplement.json')
if sha(R/'protocol.json')!=(R/'protocol.sha256').read_text().split()[0]:issues.append('protocol changed')
if sha(R/'protected-before.json')!=p['protectedManifestSHA']:issues.append('protected manifest changed')
for group in [protected,p['codeHashes'],supp['codeHashes']]:
 for f,h in group.items():
  q=Path(f)
  if not q.exists() or sha(q)!=h:issues.append('changed '+f)
parity=read(R/'parity.json');manifest=read(R/'run-manifest.json')
if len(parity['results'])!=4 or any(x['games']!=1230 or not x['identical'] for x in parity['results']):issues.append('OFF parity')
if len(manifest['files'])!=80:issues.append('run count')
ledger=[];traces=[]
for m in manifest['files']:
 f=Path(m['file']);r=read(f)
 if sha(f)!=m['sha256']:issues.append('run hash '+str(f))
 if len(r['matches'])!=1230 or any(t['games']!=82 for t in r['teams']):issues.append('schedule')
 opt=r['options'];cal=read(Path('reports/defense-tenth/step4-rebounds-oreb')/m['season']/'calibration-oreb.json')['selected']
 if m['calibration']!=cal:issues.append('calibration changed')
 if not opt.get('individualOrebAllocation') or not opt.get('individualOrebCard') or any(opt.get(k) for k in ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal']) or opt.get('defenseSignals'):issues.append('switches')
 s={k:sum(t['stats'][k] for t in r['teams']) for k in ['oreb','dreb','teamOreb','teamDreb','reboundChances']}
 if s['oreb']+s['dreb']+s['teamOreb']+s['teamDreb']!=s['reboundChances']:issues.append('rebound conservation')
 tr=r['allocationTrace']
 if tr['fgOreb']+tr['ftOreb']!=s['oreb'] or tr['dreb']!=s['dreb']:issues.append('trace accounting')
 ledger.append({'season':m['season'],'seed':m['seed'],**s});traces.append({'season':m['season'],'seed':m['seed'],**tr})
for c in a['cells']:
 if any(not math.isfinite(v) for v in c['metrics'].values()):issues.append('nonfinite scoreboard')
for x in pl:
 if not all(math.isfinite(x[k]) for k in ['MAE','RMSE']):issues.append('nonfinite player score')
write('completion-audit.json',{'finishedUTC':datetime.now(timezone.utc).isoformat(),'protocolSHA':sha(R/'protocol.json'),'protectedFiles':len(protected),'newEvaluationGames':98400,'parityGames':4920,'teamBootstrap':team['replicates'],'playerBootstrap':player['replicates'],'issues':issues,'ledger':ledger})
write('putback-diagnostic.json',{'interpretation':'Same-path conditional expected putback probabilities, not actual putback scoring or independently validated landing positions. Baseline first seed only; candidate all20 seeds. Non-random observer, no extra RNG draws.','baselineFixedPaths':parity['results'],'candidate':traces})
f=lambda n:f'{n:.4f}'
ci=lambda x:f"{x['point']:+.4f} [{x['joint95'][0]:+.4f}, {x['joint95'][1]:+.4f}]"
lines=['# OREB人選分配：取得率固定、只改接球人','',
 ('個人OREB36 MAE確認改善。' if improved else '個人OREB36 MAE未確認改善。')+('候選通過預登記副作用與聯盟漂移檢查，保留為獨立開關。' if decision['eligibleCandidate'] else '候選未通過全部條件；失敗項目照實列出，未調常數補過關。'),
 '**四季已看過答案，全季當季重現；不是換隊或跨季預測。凍結版本、上一批protocol／能力卡／常數／輸出均未改。**','',
 '| 四季等權指標 | 取得候選＋舊分配 | 取得候選＋新分配 | 差值；球隊＋seed聯合95% |', '|---|---:|---:|---|']
for k in ['MAE','RMSE']:
 lines.append('| 個人OREB36 真實分鐘加權'+k+' | '+' | '.join(f(pd['versions'][v][k]['point']) for v in ['acquisition','allocation'])+' | '+ci(pd['paired'][k])+' |')
labels={'OREB_MAE':'球隊OREB率去均值MAE pp','OREB_RMSE':'球隊OREB率去均值RMSE pp','OREB_Correlation':'球隊OREB率相關','DREB_RMSE':'DREB率去均值RMSE pp','netRMSE':'淨勝分去均值RMSE','Spearman':'淨勝分排名Spearman','SDRatio':'淨勝分SD比','winsMAE':'勝場MAE','winsRMSE':'勝場RMSE'}
for k,label in labels.items():lines.append('| '+label+' | '+' | '.join(f(joint['versions'][v][k]['point']) for v in ['acquisition','allocation'])+' | '+ci(d[k])+' |')
lines+=['','## 做法與歸因','',
 '- 取得機率直接重用上一批函式，能力卡與所有聯盟校正常數完全相同，未重新建卡或校準。',
 '- FG球員OREB分配：w_i=收縮後個人OREB份額_i／五人份額總和。移除舊30%均分與額外位置／體能倍率；小樣本已有先驗收縮，不再重複均分。',
 '- 防守籃板、FT球員OREB、團隊籃板／出界規則不改。一次投失仍只分配一個球員或團隊籃板。',
 '- 固定的是「相同陣容與投失條件下的取得函式」，不是整季實現的籃板總數。改選人會改變補籃機會與後續出手、比分、輪替，因此整季球隊數據可以改變。',
 '- 補籃函式未改。觀測器沒有增加亂數，量出同一投失路徑上舊、新分配下的條件期望補籃機率，避免把人選變化誤說成補籃公式改進。','',
 '## 逐季','', '| 球季 | 版本 | 個人OREB36 MAE | 個人OREB36 RMSE | 球隊OREB RMSE pp | net RMSE | wins MAE | 效率偏差 | 球權偏差 | TOV偏差 | FG偏差pp | 3P偏差pp |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for c in a['cells']:
 q=next(x for x in pl if x['season']==c['season'] and x['version']==c['version']);m=c['metrics']
 lines.append('| '+c['season']+' | '+c['version']+' | '+f(q['MAE'])+' | '+f(q['RMSE'])+' | '+' | '.join(f(m[k]) for k in ['OREB_RMSE','netRMSE','winsMAE','efficiencyBias','possessionsBias','TOVBias','FGpctBias','threePctBias'])+' |')
lines+=['','## 補籃耦合（診斷，不當驗收）','', '| 基準固定路徑；第一seed | FG球員OREB | 舊分配條件期望補籃% | 新分配條件期望補籃% | 差pp |','|---|---:|---:|---:|---:|']
for q in parity['results']:
 t=q['trace'];n=t['fgOreb'];old=t['expectedOldPutback']/n*100;new=t['expectedNewPutback']/n*100;lines.append(f"| {q['season']} | {n} | {f(old)} | {f(new)} | {f(new-old)} |")
lines+=['','此表只回答舊路徑上「換成新的人選權重」會如何改變既有補籃模型的機會；不等於真實補籃頻率、補籃得分或落點的驗證。','',
 '## 已驗證、推測、失敗','',
 '- 已驗證：關閉分配開關後，四季第一seed共4920場的逐場比分、球隊與球員統計完全一致。FT與DREB權重不變，場上五人分配和為1，取得函式相同。',
 '- 已驗證：20seed完整80球季核對籃板守恆與分配觀測記帳；20000次franchise＋seed聯合重抽。',
 '- 統計結果：個人改善='+str(improved)+'；显著副作用='+str(harms)+'；聯盟漂移失敗='+str(drift)+'。',
 '- 推測：均分下限可能過度分配給低OREB球員；本次只檢定整組分配替換，不能單獨量出均分、位置與體能各自占幾成。',
 '- 限制：個人OREB%包含當季角色與隊友影響。新分配沒有籃板落點、多人卡位、幫隊友卡位或受壓迫後重新進攻的資料。',
 '- 取得後的落點／補籃時機未重建，因此分配較準不等於搶板過程物理較準。',
 '- 沒有把獨立DREB卡疊入，沒有新增球隊或球員補丁，也未改OVR。歷史TOV偏差照報，不改失誤參數。','',
 '## 評分口徑','',
 '球員交易前後先按ID加總，再計36×20seed平均OREB／20seed平均模擬分鐘。真實分鐘加權。個人重抽以該季真實分鐘最多的franchise為群集（同分鐘取TEAM_ID較小者）；franchise與seed跨季配對，四季等權。ID只用來合併與群集，不是機率輸入。',
 '排除實際0分鐘或任一版本平均模擬0分鐘的球員；完整名單見player-arrays.json。重抽樣的模擬0分鐘以預測率0處理，未事後選樣。','',
 '## 重跑','', '```powershell',
 'node reports/defense-tenth/step4-rebounds-allocation/parity.mjs',
 'node reports/defense-tenth/step4-rebounds-allocation/run.mjs',
 'node reports/defense-tenth/step4-rebounds-allocation/analyze.mjs',
 'node reports/defense-tenth/step4-rebounds-allocation/score-players.mjs',
 'python reports/defense-tenth/step4-rebounds-allocation/bootstrap.py',
 'python reports/defense-tenth/step4-rebounds-allocation/player-bootstrap.py',
 'python reports/defense-tenth/step4-rebounds-allocation/finish.py', '```','',
 'setup.py只允許第一次預登記，不覆寫protocol；run跳過既有完整輸出。',
 f"預登記UTC {p['registeredUTC']}；SHA-256 `{sha(R/'protocol.json')}`。",f"保護{len(protected)}個檔案，稽核{len(issues)}項問題。",'']
(R/'report.md').write_text('\n'.join(lines).replace('显著','顯著'),encoding='utf-8')
write('deliverable-hashes.json',{f.name:sha(f) for f in R.iterdir() if f.is_file() and f.name!='deliverable-hashes.json'})
print(json.dumps({'decision':{k:v for k,v in decision.items() if k not in ['teamPaired','rule']},'teamPaired':{k:d[k] for k in labels},'issues':issues},ensure_ascii=True))
if issues:raise SystemExit(1)

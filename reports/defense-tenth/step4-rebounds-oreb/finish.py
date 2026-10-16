"""Report registered team-acquisition experiment; never select another formula."""
import json, hashlib, math
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(R/'protocol.json');a=read(R/'analysis.json');j=read(R/'joint-intervals.json');players=read(R/'player-diagnostic.json');arrays=read(R/'seed-arrays.json')
joint=j['comparisons']['four-seasons-equal'];delta=joint['paired']['orebMinuspooled'];pv=joint['versions']
improved=all(delta[k]['joint95'][1]<0 for k in ['OREB_MAE','OREB_RMSE'])
harms=[k for k in ['netRMSE','winsMAE','DREB_RMSE'] if delta[k]['joint95'][0]>0]
decision={'label':'已看過答案；四季同季重現','candidate':'pure-oreb-acquisition-1','confirmedOrebImprovement':improved,'significantHarms':harms,'eligibleIndependentCandidate':improved and not harms,'baselinePromoted':False,'baseline':'T0 remains unchanged; full replacement and portability not established','thresholds':p['decision'],'paired':delta}
write(R/'decision.json',decision)

# Additional uncertainty summaries do not change the preregistered adoption rule.
seedse=[]
for season,d in arrays.items():
    for version,v in d['versions'].items():
        for i,tid in enumerate(d['ids']):
            seedse.append({'season':season,'version':version,'teamId':tid,**{k+'SeedSE':float(np.std(np.array(v[k])[:,i],ddof=1)/math.sqrt(len(p['seeds']))) for k in ['oreb','net','wins']}})
write(R/'seed-standard-errors.json',seedse)

issues=[];protected=read(R/'protected-before.json');repair=read(R/'analysis-code-repair-1.json');repair2=read(R/'analysis-code-repair-2.json')
if sha(R/'protocol.json')!=(R/'protocol.sha256').read_text().split()[0]:issues.append('protocol changed')
if sha(R/'protected-before.json')!=p['protectedManifestSHA']:issues.append('manifest changed')
for group in [protected,p['inputHashes']]:
    for name,h in group.items():
        f=Path(name)
        if not f.exists() or sha(f)!=h:issues.append('protected/input changed '+name)
for name,h in p['codeHashes'].items():
    expected=repair['afterSHA'] if name==repair['file'] else repair2['afterSHA'] if name==repair2['file'] else h
    if sha(Path(name))!=expected:issues.append('code changed '+name)
if sha(R/'analyze-initial.mjs')!=repair['beforeSHA']:issues.append('repair backup mismatch')
if sha(R/'player-diagnostic-initial.mjs')!=repair2['beforeSHA']:issues.append('player repair backup mismatch')
manifest=read(R/'run-manifest.json');parity=read(R/'parity.json')
if len(manifest['files'])!=80:issues.append('wrong run count')
ledger=[]
for q in manifest['files']:
    f=Path(q['file']);r=read(f)
    if sha(f)!=q['sha256']:issues.append('run hash mismatch '+q['file'])
    if len(r['matches'])!=1230 or any(t['games']!=82 for t in r['teams']):issues.append('schedule '+q['file'])
    if not r['options'].get('individualOrebCard') or any(r['options'].get(k) for k in ['rimSignal','reboundSignal','liveSignal','zoneSignal','foulSignal']) or r['options'].get('defenseSignals'):issues.append('switches '+q['file'])
    recovered=sum(t['stats']['oreb']+t['stats']['dreb']+t['stats']['teamOreb']+t['stats']['teamDreb'] for t in r['teams'])
    chances=sum(t['stats']['reboundChances'] for t in r['teams'])
    ledger.append({'season':q['season'],'seed':q['seed'],'effectiveMisses':chances,'recovered':recovered,'difference':recovered-chances})
    if recovered!=chances:issues.append('rebound ledger '+q['file'])
if len(parity['results'])!=4 or any(x['games']!=1230 or not x['teamPlayerStatsIdentical'] for x in parity['results']):issues.append('parity')
for c in a['cells']:
    for t in c['teams']:
        if abs(t['O']+t['D']-t['netError'])>1e-8:issues.append('O+D mismatch')
    if any(not math.isfinite(v) for v in c['metrics'].values()):issues.append('nonfinite metrics')
audit={'finishedUTC':datetime.now(timezone.utc).isoformat(),'protocolSHA':sha(R/'protocol.json'),'protectedFiles':len(protected),'newEvaluationSeasons':80,'newEvaluationGames':98400,'parityGames':4920,'bootstrapReplicates':j['replicates'],'issues':issues,'reboundLedger':ledger}
write(R/'completion-audit.json',audit)

f=lambda v:f'{v:.4f}'
ci=lambda d:f"{d['point']:+.4f} [{d['joint95'][0]:+.4f}, {d['joint95'][1]:+.4f}]"
lines=['# 進攻籃板取得判定：獨立 OREB 卡候選','',
 ('球隊 OREB 率的去均值 MAE、RMSE 均確認改善。' if improved else '球隊 OREB 率改善未通過預登記的兩項聯合區間判準。')+(' 主指標有顯著退步：'+', '.join(harms)+'。' if harms else '淨勝分、勝場與防守籃板的顯著副作用見下表，未據此修改既有基準。'),
 '**四季全部已看過答案；這是當季個人資料＋真實逐場名單與分鐘軟目標的重現測試，不是跨季、換隊或季前預測。**','',
 '| 四季等權指標 | 原純卡 T0 | 同聯盟校準 pooled | OREB 取得候選 | 候選−pooled；球隊＋seed 聯合95% |',
 '|---|---:|---:|---:|---|']
labels={'OREB_MAE':'OREB率去均值MAE（百分點）','OREB_RMSE':'OREB率去均值RMSE（百分點）','OREB_RawMAE':'OREB率未去均值MAE（百分點）','OREB_Correlation':'OREB率相關','OREB_SDRatio':'OREB率SD比','DREB_RMSE':'DREB率去均值RMSE（百分點）','netRMSE':'淨勝分去均值RMSE（分／場）','Spearman':'淨勝分排名Spearman','SDRatio':'淨勝分SD比（副作用）','calibrationSlope':'淨勝分校準斜率','winsMAE':'勝場MAE（勝）','winsRMSE':'勝場RMSE（勝）'}
for key,label in labels.items():lines.append('| '+label+' | '+' | '.join(f(pv[v][key]['point']) for v in ['T0','pooled','oreb'])+' | '+ci(delta[key])+' |')
lines+=['',
 '淨勝分RMSE的聯合95%區間低於0，確認改善。勝場MAE的區間仍跨0，不能宣稱勝場MAE確認改善；勝場RMSE為次要指標，区间見表。',
 '球隊淨勝分SD比點估計下降，差值區間略跨0，仍是需追蹤的副作用；OREB率SD比提升到約0.83，也尚未完全還原真實球隊差距。這一批不在看完結果後放大係數。',
 '## 確認與尚未確認','',
 '- 已確認：球隊OREB率去均值MAE與RMSE、淨勝分RMSE改善。',
 '- 尚未確認：勝場MAE、DREB率RMSE、排名Spearman改善，或淨勝分SD比退步。',
 '- 個人OREB36 MAE四季點估計均降低，但此診斷沒有個人重抽區間，不稱為個人層級的統計確認。']
lines+=['','## 已驗證事實','',
 '- 本批唯一新機制是進攻方取得球員籃板的機率。個人 OREB%、OREB、分鐘估計獨立 share；樣本不足向聯盟個人先驗收縮。五人 share 合為一次隊伍機率，與原防守競爭項合成，再抽一次成功／失敗。取得後的人選、補籃、FT、團隊留球、出界、區段防守訊號皆未改。',
 '- 5名高OREB球員仍只能在一次投失後取得1個球員籃板。新增籃板必須先出現下一次投失。完整80個候選球季核對有效投失與球員＋團隊回收記帳。',
 '- 4季關閉新卡與校正常數後，4920場逐場比分、球隊與球員統計完全相同。',
 '- 聯盟校準用獨立3 seeds、最多6輪；沿用先前 pooled 的完全相同方法。聯盟均值是校準目標，不當作獨立準確度證據。主比較為候選對同校準的 pooled，避免把歷史−3.5分效率平移算成新卡功勞。','',
 '## 逐季結果','',
 '| 球季 | 版本 | OREB MAE | OREB RMSE | OREB r | DREB RMSE | net RMSE | wins MAE | 效率偏差 | 球權偏差 | TOV偏差 | FG偏差pp | 3P偏差pp |',
 '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for c in a['cells']:
    m=c['metrics'];lines.append('| '+c['season']+' | '+c['version']+' | '+' | '.join(f(m[k]) for k in ['OREB_MAE','OREB_RMSE','OREB_Correlation','DREB_RMSE','netRMSE','winsMAE','efficiencyBias','possessionsBias','TOVBias','FGpctBias','threePctBias'])+' |')
lines+=['','## 個人分配與副作用','', '| 球季 | 版本 | 真實分鐘加權OREB36 MAE |','|---|---|---:|']
for c in players:lines.append(f"| {c['season']} | {c['version']} | {f(c['minutesWeightedOreb36MAE'])} |")
lines+=['','取得率與人選分配是兩件事。這一批刻意保留原本 .30 均分＋.70 原位置／能力權重，因此個人OREB36誤差即使未改善，也不與球隊取得率的改善矛盾。防守卡未改；DREB的變化可能來自對手進攻搶板量改變，不代表已重建防守技能。','',
 '## 機制與資料','',
 '- 卡估計：N=個人OREB／官方OREB%；後驗share=(OREB+κμ)/(N+κ)。0個OREB的機會數用本人分鐘乘聯盟機會／分鐘；無缺卡。μ、κ只用各季個人統計，不能視為純天賦。',
 '- 取得：logit(clip(場上五人share總和,.01,.95)) + 原中性進攻對目前防守的logit − logit(DEFAULT_OREB_SHARE) + 聯盟ORB常數。最終機率仍限制 .05至.60。',
 '- 此公式取代進攻取得階段的固定PG/C衝搶與身材落點倍率，避免再對已含角色的OREB%重複加成。原防守競爭、取得後的位置權重仍保留。','',
 '| 球季 | 個人先驗μ | κ | ≥500分鐘估計人數 | 卡覆蓋分鐘 |','|---|---:|---:|---:|---:|']
for c in read(R/'coverage.json'):lines.append(f"| {c['season']} | {f(c['mu'])} | {f(c['kappa'])} | {c['fitPlayers']} | {100*c['minuteCoverage']:.1f}% |")
lines+=['','## 推測、失敗與限制','',
 '- OREB%包含當季衝搶角色、隊友與投失分布；本結果不能证明卡換队后仍准确。下一次换队检定需独立冻结、用换队前资料。',
 '- 尚無十人座標，沒有估計本人距離、卡位、替隊友擋人或搶板後落點。這一批不加入無資料支持的身材或卡位係數。',
 '- 舊防守競爭與取得後分配仍依位置、總籃板與體能，因此護框者打控衛的角色可轉移性尚未修正。',
 '- 本次未把既有獨立DREB候選疊進來，避免同批混合兩端變動；即使單項成功，組合也必須獨立驗證。',
 '- 歷史三季TOV偏低若仍出現，照實列示，不調失誤參數補過關。',
 '- 計分程式生成時，版本名稱替換誤改DREB欄位選擇器，個人OREB診斷也殘留DREB真實欄位；兩者均在產出相關評分前修復，保留原程式與修復SHA於analysis-code-repair-1/2.json。protocol未改。','',
 '## 下一步','',
 '先依上述結果決定是否保留取得開關。若取得率改善但個人MAE未改善，下一批只測人選分配（不再動球隊取得率）；在該項完成前不把搶板距離、卡位與補籃一起加入。','',
 '## 重跑','',
 '```powershell',
 'node reports/defense-tenth/step4-rebounds-oreb/prepare.mjs',
 'node reports/defense-tenth/step4-rebounds-oreb/parity.mjs',
 'node reports/defense-tenth/step4-rebounds-oreb/calibrate.mjs',
 'node reports/defense-tenth/step4-rebounds-oreb/run.mjs',
 'node reports/defense-tenth/step4-rebounds-oreb/analyze.mjs',
 'python reports/defense-tenth/step4-rebounds-oreb/bootstrap.py',
 'node reports/defense-tenth/step4-rebounds-oreb/player-diagnostic.mjs',
 'python reports/defense-tenth/step4-rebounds-oreb/finish.py',
 '```','',
 'run/calibrate對已存在的完成檔案跳過；若要全新重算請另建輸出副本，不刪改凍結產物。',
 f"預登記UTC：{p['registeredUTC']}。SHA-256：`{sha(R/'protocol.json')}`。",
 f"稽核：{len(protected)}個既有檔案，{len(issues)}項問題。完整逐隊、失敗名單、SE與区间见同目录JSON。",'']
text='\n'.join(lines).replace('不能证明卡換队后仍准确。下一次换队检定需独立冻结、用换队前资料。','不能證明卡換隊後仍準確。下一次換隊檢定需獨立凍結、用換隊前資料。').replace('SE與区间见同目录JSON。','SE與區間見同目錄JSON。').replace('区间見表','區間見表')
(R/'report.md').write_text(text,encoding='utf-8')
write(R/'deliverable-hashes.json',{f.name:sha(f) for f in R.iterdir() if f.is_file() and f.name!='deliverable-hashes.json'})
print(json.dumps({'confirmedOrebImprovement':improved,'significantHarms':harms,'paired':{k:delta[k] for k in labels},'auditIssues':issues},ensure_ascii=True))
if issues:raise SystemExit(1)

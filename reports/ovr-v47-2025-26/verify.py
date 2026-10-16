import json, math, hashlib, statistics, csv
from pathlib import Path
root=Path(__file__).parent
load=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
r=load(root/'ranking.json'); protocol=load(root/'healthy-protocol.json')
players=r['players'];byid={p['playerId']:p for p in players}
assert len(players)==len(byid)==582
assert set(byid)==set(protocol['ids'])
assert [p['rank'] for p in players]==list(range(1,583))
assert players==sorted(players,key=lambda p:(-p['healthy']['meanContribution'],p['playerId']))
assert r['availabilityPenalty']==0
availability=load(root/'availability.json');av={p['playerId']:p for p in availability['players']};assert set(av)==set(byid)
raw_count=0; games=0
for line in (root/'raw.jsonl').open(encoding='utf-8'):
 m=json.loads(line);p=byid[m['result']['playerId']]; arm=m['result']['arms'][0]
 assert m['job']['samples']==4 and m['job']['seed']==protocol['seed']
 assert len(arm['games'])==120 and m['result']['simulatedGames']==480
 strata={}; stat={}; mins=[];seen=set()
 for g in arm['games']:
  key=(g['opponent'],g['i']);assert key not in seen;seen.add(key)
  assert 0<=g['opponent']<30 and 0<=g['i']<4 and g['phase']==g['i']%2
  expected_seed=(protocol['seed']+(g['opponent']*5+m['result']['slot'])*1000003+g['i']*7919)&0xffffffff
  assert g['seed']==expected_seed
  assert len(g['pair'])==2 and {v['side'] for v in g['pair']}=={0,1}
  strata.setdefault(g['opponent'],[]).append(statistics.mean(v['margin']-v['baselineMargin'] for v in g['pair']))
  for v in g['pair']:
   assert abs(v['playerMinutes']-arm['minutes'])<.0002
   mins.append(v['playerMinutes'])
   for k,n in v['playerStats'].items(): stat.setdefault(k,[]).append(n)
 assert len(strata)==30 and all(len(a)==4 for a in strata.values())
 mean=statistics.mean(statistics.mean(a) for a in strata.values())
 se=math.sqrt(sum(statistics.variance(a)/len(a) for a in strata.values())/900)
 h=p['healthy'];assert abs(mean-h['meanContribution'])<1e-10
 assert abs(se-h['standardError'])<1e-10
 for a,b in zip([mean-1.96*se,mean+1.96*se],h['ci95']):assert abs(a-b)<1e-10
 for k,vs in stat.items():assert abs(statistics.mean(vs)-h['statsPerGame'][k])<1e-10
 raw_count+=1;games+=m['result']['simulatedGames']
assert raw_count==582
for f,h in protocol['hashes'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,f
old=load('reports/model-evolution-20261016/latest-full-ovr/ranking.json')
oldmap={p['playerId']:p for p in old['players']}
def paired_change(p,q):
 a={s['opponent']:s['values'] for s in p['healthy']['strata']}
 b={s['opponent']:s['values'] for s in q['healthy']['strata']}
 assert set(a)==set(b)
 diffs=[[x-y for x,y in zip(a[k],b[k])] for k in a]
 delta=statistics.mean(statistics.mean(v) for v in diffs)
 se=math.sqrt(sum(statistics.variance(v)/len(v) for v in diffs)/len(diffs)**2)
 return delta,se,delta-1.96*se,delta+1.96*se
with (root/'comparison.csv').open('w',encoding='utf-8-sig',newline='') as out:
 w=csv.writer(out);w.writerow(['rank','old_v41_rank','places_gained','name','position','source_games_played','source_minutes_per_played_game','healthy_minutes','margin_contribution','old_contribution','conditional_ci95_low','conditional_ci95_high','change_from_v41','change_standard_error','change_ci95_low','change_ci95_high'])
 for p in players:
  q=oldmap[p['playerId']];h=p['healthy'];w.writerow([p['rank'],q['rank'],q['rank']-p['rank'],p['name'],p['position'],av[p['playerId']]['gamesPlayed'],av[p['playerId']]['minutesPerPlayedGame'],h['minutes'],h['meanContribution'],q['healthy']['meanContribution'],*h['ci95'],*paired_change(p,q)])
stability=load(root/'stability.json')
decision={'fullLeagueComplete':True,'integrityPassed':True,'objectiveOvrAccepted':False,'experimental':True,'adopted':False,'assessmentType':'post-run diagnostic; no preregistered adoption threshold','reasons':['Split-half rank correlation only '+str(stability['spearman']),'Top20 overlap only '+str(stability['top20Intersection'])+' of 20','Source-small-sample players remain at top ranks; position baseline transfer and source estimate reliability need separate validation'],'probabilityModelAdoptionUnchanged':True,'productionDefaultChanged':False,'availabilityDeduction':False}
(root/'decision.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
lines=['# v47 2025–26 全聯盟健康貢獻排行','', '**結論：全量計算及統計完整性通過，但目前不採用此榜作為客觀 OVR。**','', '582 人全部重新模擬，共 279,360 場。採用 v46 防守與 v47 罰球；固定自然位置及健康負荷，出勤另列且不扣主要分數。此處數值是相較同位置平均隊友的每場淨勝分增量，並非 0–99 OVR。實驗排行尚未證明符合客觀強弱。','', '每人 30 個對手 × 4 組種子／輪替 × 2 個主客位，同時模擬候選及平均基準。健康分鐘上限約 35 分，固定測試輪替，未套入實際球隊 v49 輪替。原始能力值、自然位置、非更新測量維持 v41 測試設定。','', '新五區描述的合成隊友以同位置且位置可信球員的來源分鐘加權平均；16 個能力值算術平均仍為70。新實際球員測量替換投籃基準、五區防守／選擇與 FT；舊粗區防守係數歸零避免重複。合成隊友 FT 保留能力曲線。','', '95% 區間只涵蓋條件式蒙地卡羅抽樣誤差，未涵蓋資料、角色、模型與對手選擇不確定性。相鄰名次應連同區間解讀，不能以名次本身宣稱已校準。','', '| 新排名 | v41 排名 | 球員 | 位置 | 增量淨勝分 | 95% 區間 |','|---:|---:|---|---|---:|---|']
for p in players[:50]:
 h=p['healthy'];lo,hi=h['ci95'];lines.append(f"| {p['rank']} | {oldmap[p['playerId']]['rank']} | {p['name']} | {p['position']} | {h['meanContribution']:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
lines+=['','## 關注球員的新舊差異','','貢獻值差異的區間以相同對手／種子的成對差計算；仍只代表條件式抽樣誤差。','','| 球員 | v41 → v47 排名 | 貢獻值變化 | 變化的 95% 區間 |','|---|---:|---:|---|']
for p in players:
 if any(n.lower() in p['name'].lower() for n in ['Curry','Cunningham','Wembanyama','Mitchell Robinson','Queta']):
  q=oldmap[p['playerId']];delta,se,lo,hi=paired_change(p,q);lines.append(f"| {p['name']} | {q['rank']} → {p['rank']} | {delta:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
lines+=['','comparison.csv 另外列出來源出賽場數與出賽時場均分鐘；這些是描述性數據，並非傷病診斷或多年可靠度評分，不扣主要貢獻分數。','', '本次排行不是新一輪真實賽事回測，因此不會更新既有個人／球隊數據準確度結論。v47 的既有回測與這份控制情境排行是兩種不同驗證。']
from collections import Counter
position_counts={f'{label}Top{n}':dict(Counter(p['position'] for p in ps[:n])) for label,ps in [('v41',old['players']),('v47',players)] for n in [20,50]}
(root/'position-counts.json').write_text(json.dumps(position_counts,indent=2),encoding='utf-8')
lines+=['','## 位置分布（描述性統計）','','中鋒數量可用來追蹤先前疑慮，但位置數量本身不能證明排名準確。','','| 榜單 | PG | SG | SF | PF | C |','|---|---:|---:|---:|---:|---:|']
for label,counts in position_counts.items():lines.append('| '+label+' | '+' | '.join(str(counts.get(pos,0)) for pos in ['PG','SG','SF','PF','C'])+' |')
lines+=['','## 未採用原因與尚未釐清的部分','',f"將四組種子拆成兩半（兩邊都含兩種輪替時序及全部30隊），排名 Spearman 相關僅 {stability['spearman']:.3f}；前20僅重疊 {stability['top20Intersection']} 人。條件式95%區間半寬中位數約 {stability['medianConditional95HalfWidth']:.2f} 分。這些是跑完後的診斷，並非事前登錄的正式採用門檻。",'', 'Cormac Ryan 第2（來源11場）、Josh Oduro 第10（來源3場），且低分鐘球員仍能進入前段。Curry第194、Cade第181；不能以這些名次當成可靠的客觀實力評價。兩半裡仍靠前的極小樣本球員也顯示，抽樣波動並非唯一需要排查的方向。','', '待驗證：合成平均70隊友與位置基準的五區轉接、來源小樣本估計的收縮，以及增量淨勝分估計的變異。這些是候選原因，尚未證實哪一項造成各球員的偏差。主要分數不因傷病缺賽扣分；小樣本估計可靠度與缺賽扣分是不同問題。','', '本次未改動已接受的v46／v47賽事模型，也沒有用手動加減球星分數來調整榜單。']
(root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
checks={'passed':True,'integrityPassed':True,'objectiveOvrAccepted':False,'stabilitySHA256':hashlib.sha256((root/'stability.json').read_bytes()).hexdigest(),'stabilityScriptSHA256':hashlib.sha256((root/'stability.py').read_bytes()).hexdigest(),'decisionSHA256':hashlib.sha256((root/'decision.json').read_bytes()).hexdigest(),'all582RawResultsRecomputed':True,'allFrozenHashesPassed':True,'uniquePlayers':len(byid),'simulatedGames':games,'rankingSHA256':hashlib.sha256((root/'ranking.json').read_bytes()).hexdigest(),'positionCountsSHA256':hashlib.sha256((root/'position-counts.json').read_bytes()).hexdigest(),'availabilitySHA256':hashlib.sha256((root/'availability.json').read_bytes()).hexdigest(),'reportSHA256':hashlib.sha256((root/'report.md').read_bytes()).hexdigest(),'comparisonSHA256':hashlib.sha256((root/'comparison.csv').read_bytes()).hexdigest(),'protocolSHA256':hashlib.sha256((root/'healthy-protocol.json').read_bytes()).hexdigest(),'inputVerificationSHA256':hashlib.sha256((root/'input-verification.json').read_bytes()).hexdigest(),'verificationScriptSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rawSHA256':hashlib.sha256((root/'raw.jsonl').read_bytes()).hexdigest()}
(root/'independent-verification.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps({'verification':checks,'positionCounts':position_counts,'top20':[(p['rank'],p['name'],oldmap[p['playerId']]['rank'],round(p['healthy']['meanContribution'],3)) for p in players[:20]],'focus':[(p['rank'],p['name'],oldmap[p['playerId']]['rank']) for p in players if any(n.lower() in p['name'].lower() for n in ['Curry','Cunningham','Wembanyama','Robinson','Queta'])]},ensure_ascii=True))

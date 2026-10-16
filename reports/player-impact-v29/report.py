"""Descriptive all-player workload table and selected paired rotation experiment."""
import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT=Path('reports/player-impact-v29')
read=lambda f:json.loads((ROOT/f).read_text(encoding='utf-8'))
src=read('workload-source.json');state=read('checkpoint.json');manifest=read('manifest.json')
opp=read('opponent-role-exposure.json')
opps={p['playerId']:p for p in opp['seasons'][-1]['players']}
old=json.loads(Path('reports/player-impact-v24/all-2025-26/ranking.json').read_text(encoding='utf-8'))
oldmap={p['playerId']:p for p in old['players']}

def estimate(values):
    by={}
    for (opponent,i),v in values.items():by.setdefault(opponent,[]).append(v)
    means=[statistics.mean(v) for v in by.values()]
    var=sum(statistics.variance(v)/len(v) for v in by.values())/len(by)**2
    mean=statistics.mean(means);se=math.sqrt(var)
    return dict(mean=mean,standardError=se,ci95=[mean-1.96*se,mean+1.96*se],independentSeatPairs=len(values))

results=[]
for item in state['rows']:
    r=item['result'];arms=[];vals={}
    for a in r['arms']:
        def vector(f):return {(g['opponent'],g['i']):statistics.mean(f(p) for p in g['pair']) for g in a['games']}
        margin=vector(lambda p:p['margin']-p['baselineMargin'])
        wins=vector(lambda p:p['win']-p['baselineWin'])
        vals[a['arm']]=margin
        arms.append(dict(arm=a['arm'],minutes=a['minutes'],pairedMargin=estimate(margin),pairedWins=estimate(wins),
            rawWinRate=statistics.mean(p['win'] for g in a['games'] for p in g['pair']),
            baselineWinRate=statistics.mean(p['baselineWin'] for g in a['games'] for p in g['pair']),
            meanPlayerStats={k:statistics.mean(p['playerStats'][k] for g in a['games'] for p in g['pair'])
                for k in a['games'][0]['pair'][0]['playerStats']}))
    changes={}
    for label,left,right in [('workloadChange','supportedHealthy','fullCapCounterfactual'),
        ('recurrent05Change','recurrent05','supportedHealthy'),('recurrent10Change','recurrent10','supportedHealthy')]:
        changes[label]=estimate({k:vals[left][k]-vals[right][k] for k in vals[left]})
    results.append(dict(playerId=r['playerId'],name=r['name'],position=r['position'],arms=arms,**changes))
summary=dict(design='Matched own-slot mean70 baseline at identical workload, schedule, opponent, phase and seed; both seats form one independent observation. Reported CIs are conditional simulation normal intervals, not source/load/clinical/model uncertainty. Diagnostic selection only; no full new OVR or ranks.',
    capMinutes=src['capMinutes'],players=results,simulatedGames=manifest['simulatedGames'])
(ROOT/'pilot-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
if '--summary-only' in sys.argv:
    print(json.dumps(dict(pilotPlayers=len(results),games=manifest['simulatedGames'])))
    sys.exit(0)
policy=read('reliability-policy.json')
policies={p['playerId']:p for p in policy['players']}

table=[]
for key,p in src['players'].items():
    current=p['history']['2025-26'];past=p['history'];o=opps.get(p['playerId'])
    row=dict(playerId=p['playerId'],name=p['name'],position=oldmap[p['playerId']]['position'],
        playedGames=current['playedGames'],starts=current['starts'],minutesPerPlayedGame=current['minutesPerPlayedGame'],
        capMinutes=src['capMinutes'],supportedMinutes=p['supportedMinutes'],workloadShare=p['workloadShare'],
        documentedInjuryIllnessGames=current['documentedInjuryIllnessGames'],otherDocumentedAbsences=current['otherDocumentedAbsences'],
        unknownZeroMinuteGames=current['unknownZeroMinuteGames'],listedGames=current['listedGames'],
        recurrentInjuryIllnessRate=p['persistentDocumentedInjuryIllnessRate'],reliabilityScalePrototype=p['reliabilityScale'],
        injuryMinutesDiagnosticOnly=p['primaryBenchmarkMinutes'],
        opposingStarterFraction=o['opposingStarterFraction'] if o else None,
        strictOnCourtMinutes=o['seconds']/60 if o else 0,
        opponentScope='Strict-source role exposure; no opponent ability adjustment',
        ratingScope='Workload/absence source facts and provisional policy only; no new OVR')
    for season in ['2022-23','2023-24','2024-25','2025-26']:
        h=past.get(season)
        for name,key2 in [('GP','playedGames'),('injuryIllness','documentedInjuryIllnessGames'),('listed','listedGames'),('coverageAdequate','historyCoverageAdequate')]:
            row[f'{season}_{name}']=h[key2] if h else None
    table.append(row)
with (ROOT/'2025-26-all-player-workload.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)

fmt=lambda x:f'{x:.3f}'
ci=lambda x:f"{x['mean']:+.2f} [{x['ci95'][0]:+.2f}, {x['ci95'][1]:+.2f}]"
lines=['# 替補負荷與跨季傷缺：v29 評分原型','',
    '**已完成四季來源資料、582人負荷表與10人有輪替的成對實驗；不是新版全員OVR，尚未採用。**','',
    '## 使用者已確認的評分定義','',
    '主要看能上場時的貢獻；單一傷缺球季不直接扣能力，反覆多季傷缺才小幅影響可靠度。短時間替補不能將per36效率直接外推成先發能力；先發／替補標籤本身不扣分，能維持大負荷的第六人可以保留價值。超額分鐘不持續增加能力。','',
    '## 改了什麼','',
    f"共同負荷標準為 **{src['capMinutes']:.2f} 分鐘**：只用2022–25三季，每隊挑至少打過一半球隊場次球員中場均分鐘最高者，取90個球員隊季的中位數。這是比較用標準，不是測出人體疲勞頂點，也未按新排名調整。2025–26不參與選標準。",'',
    '`可交付分鐘 = 已出賽場次中，每場 min(實際分鐘, 共同標準) 的平均`。缺賽不當成零分鐘；加時或教練過度使用的超額分鐘不增加標準負荷。固定相同效率時，36分鐘24分與42分鐘28分都在標準封頂，24分鐘16分、12分鐘8分分別只支持較少的場上貢獻。這不是證明短時間球員沒有更高潛力，也不直接改動任何能力屬性。','',
    '改為48分鐘、有輪替且開啟既有疲勞的測試。球員只打可交付分鐘，其餘時間交由同位置平均70卡；其餘四位置有不同形狀、算術平均70的球員。比較基準也用完全相同分鐘／換人／對手／seed，以球員隊減同位置平均隊的分差或勝率衡量貢獻，避免休息時間不同造成假加分。雙方都有平均70替補、固定四節；平手記半勝，關閉犯滿離場以固定負荷。兩種標準輪替時序均衡抽樣。','',
    '傷缺只計原始box明確標記的injury／illness；教練決定、G League及原因未知者分開。四季中，只有至少列名半季的球季才用於可靠度；取傷病／列名比率的第二高值，一個孤立的傷缺球季因此恰為零。未登錄或尚未進聯盟的年份不補成健康季。這是現有box記錄的反覆缺賽指標，不是完整合約期間出勤或醫療預測。','',
    '最初另測試把傷缺轉成每場少打分鐘；結果部分球員的模擬貢獻反而提高。少打分鐘還會改變休息與比賽路徑，因此**該方式只保留為診斷，未選為主要可靠度扣分**。','',
    '選用原型：`主評分貢獻 = 健康負荷貢獻 − max(健康負荷貢獻, 0) × 0.10 × 反覆傷缺比率`。可靠度不改健康時的屬性或單場輪替，只折減已證明的正向貢獻；負貢獻不會因受傷而加分。**0.10是明列的試驗政策權重，尚未校準，不是假裝資料推導出的精準常數**；保留0、0.05、0.10幅度比較，最重也只折減正貢獻的10%。一般低負荷替補的折減遠大於此，但不能保證每一個替補都低於每一個傷病先發。傷病縮短了其出賽時的實際負荷而資料未標明限制時，仍無法完全分離教練選擇與健康限制。','',
    '## 實際來源負荷與對手角色','',
    '| 球員 | 本季出賽／先發 | 出賽場均分鐘 | 封頂後負荷 | 多季傷缺調整幅度（原型） | 在場對手先發占比 |',
    '|---|---:|---:|---:|---:|---:|']
for r in results:
    p=src['players'][str(r['playerId'])];h=p['history']['2025-26'];o=opps.get(r['playerId'])
    lines.append(f"| {r['name']} | {h['playedGames']}／{h['starts']} | {h['minutesPerPlayedGame']:.2f} | {p['supportedMinutes']:.2f} | {(1-p['reliabilityScale'])*100:.2f}% | {o['opposingStarterFraction']*100:.1f}% |")
lines+=['',
    '對手先發占比依真實攻守五人、同一場的先發名單與秒數計算；四季各人的在場秒數均與獨立嚴格PBP帳目一致。它只呈現角色暴露差異，**不是對手實力，也尚未修正球員來源效率中的對手選擇偏差**。不能先假定替補全都打弱者，或把此占比直接乘進能力。','',
    '## 成對輪替實驗結果','',
    f"共 **{manifest['simulatedGames']:,}場實際模擬**，10名診斷球員，各30對手×4組seed×兩席次；每個球員場景另有同分鐘基準。完全相同的分鐘場景只重用一次已算結果。區間只反映固定模型的模擬抽樣，尚未含來源、負荷、傷病與模型不確定性；120組席次配對不能當成精確名次。",'',
    '| 球員 | 假設全標準負荷：相對平均隊分差 | 來源負荷：相對平均隊分差 | 負荷變動的成對分差差值［95%］ | 只供診斷：傷缺轉分鐘額外差值［95%］ |',
    '|---|---:|---:|---:|---:|']
for r in results:
    a={v['arm']:v for v in r['arms']}
    lines.append(f"| {r['name']} | {a['fullCapCounterfactual']['pairedMargin']['mean']:+.2f} | {a['supportedHealthy']['pairedMargin']['mean']:+.2f} | {ci(r['workloadChange'])} | {ci(r['recurrent10Change'])} |")
lines+=['',
    '上述是共同測試環境中的分差貢獻；不是實際NBA淨效率、因果ON–OFF或新的0–99 OVR。負荷改變會連帶改變隊友、對手狀態與比賽路徑，有限樣本下不強制分差逐項單調，不加名單修正去湊順序。','',
    '## 選用可靠度政策的幅度比較','',
    '此表保持健康負荷試驗完全相同，再依公開公式折減正貢獻。這是政策敏感度，不是重新模擬；單位同上，沒有轉成0–99 OVR。取值基於「受傷不能使評分變高」的明確不變條件，沒有按名次選規則。','',
    '| 球員 | 不作可靠度扣減 | 0.05係數 | 0.10係數 | 0.10實際扣減 |',
    '|---|---:|---:|---:|---:|']
for r in results:
    ps=policies[r['playerId']]['reliabilitySensitivity']
    lines.append(f"| {r['name']} | {ps[0]['adjustedContribution']:+.3f} | {ps[1]['adjustedContribution']:+.3f} | {ps[2]['adjustedContribution']:+.3f} | {ps[2]['deduction']:.3f} |")
lines+=['',
    '## 已驗證與仍未解決','',
    '已驗證：全部582人保留；四季4,920場box逐場對上既有分鐘；明確傷病與其他缺賽分開；單季傷缺零可靠度扣減；高分鐘封頂；每位置恰一人、換人分鐘精確至0.1秒；零負荷與相同平均卡貢獻完全為零；所有試驗比分、球員／球隊計數、抄截與活球失誤帳目通過。','',
    '仍未解決：來源對手強弱／教練角色選擇的效率偏差、健康時真正可提高到何種負荷、長時間下籃板／傳球／防守等能力變化。既有疲勞只作用於投籃和突破，並不能靠開啟疲勞就宣稱這些問題修好了。原型的反覆傷缺幅度及共同負荷定義仍需時間外驗證；沒有再把per36直接視為先發實力，也沒有據此宣稱替補必定比較差。','',
    'v28四季球隊勝場採用界線仍有兩季未過；本輪沒有改動比賽機制去補排名，也未重跑一般四季勝場。最新完整全員榜仍為v24。整體個人數據與OVR修正任務尚未完成。','',
    '檔案：[582人跨季負荷／缺賽表](2025-26-all-player-workload.csv)、[試驗明細](pilot-summary.json)、[預先凍結協定](protocol.json)、[核對結果](verification.json)。']
(ROOT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'status.json').write_text(json.dumps(dict(stage='completed-workload-prototype',adopted=False,fullOvr=False,allPlayers=582,pilotPlayers=len(results),games=manifest['simulatedGames'],unresolved=['source-opponent quality portability','sustainable efficiency at higher workloads','multi-season reliability weight validation','overall player and team adoption gates']),indent=2),encoding='utf-8')
print(json.dumps(dict(players=len(table),pilotPlayers=len(results),games=manifest['simulatedGames'])))

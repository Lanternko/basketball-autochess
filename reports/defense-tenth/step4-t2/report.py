import json,hashlib
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[3];O=R/'reports/defense-tenth/step4-t2'
def read(p):return json.loads((O/p).read_text(encoding='utf-8'))
def save(p,v):(O/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(p,rows):(O/p).write_text('\n'.join(rows)+'\n',encoding='utf-8')
def n(x,d=3):return '—' if x is None else f'{x:.{d}f}'
def ci(x):return f"{n(x['pearson'])} [{n(x['ci95'][0])}, {n(x['ci95'][1])}]（{x['n']}）" if x and x['ci95'] else f"—（{x['n'] if x else 0}）"
p=read('protocol.json');s=read('measurement-supplement.json');inv=read('inventory.json');corr=read('correlations.json');team=read('team-correlations.json');data=read('players.json');moves=read('move-samples.json');ea=read('endpoint-audit.json')
labels={'BLK36':'阻攻/36','STL36':'抄截/36','DREB36':'防守籃板/36','PF36':'犯規/36','CHARGES_DRAWN36':'製造進攻犯規/36','CONTESTED_SHOTS_2PT36':'兩分干擾出手/36','CONTESTED_SHOTS_3PT36':'三分干擾出手/36','DEFLECTIONS36':'破壞傳球/36','DEF_BOXOUTS36':'防守卡位/36','defensiveLoad':'對位負擔（對手USG）','matchupSuppression':'對位命中壓制','usageWeightedMatchupSuppression':'使用率加權對位壓制','officialDefRtg':'官方個人DEF_RATING','onDefRtg':'原始在場防守效率','onOffDef':'同場次on/off防守差','onOffRimShare':'on/off對手禁區占比差','onOffThreeShare':'on/off對手三分占比差','rimSuppression':'六呎內命中壓制','threeSuppression':'三分命中壓制','teamCenteredOn':'去球隊均值在場防守'}
metrics=sorted(labels)
def get(m,g,period='pooled'):
    return next(x for x in corr if x['metric']==m and x['group']==g and x['period']==period)
def tc(m,period='pooled',kind='teamDefRtg'):
    return next(x for x in team['results'] if x['metric']==m and x['period']==period and x['kind']==kind)
allcorr=['# 全部防守指標穩定性','', '格式：Pearson [球員＋franchise聯合95%區間]（成對筆數）。成對筆數不是獨立球員數；JSON另列unique players與Spearman。所有球季已看過答案。']
periods=sorted({x['period'] for x in corr if x['comparison']=='adjacent' and x['period']!='pooled'})
for m in metrics:
    allcorr.extend(['',f'## {labels[m]}','', '| 相鄰季 | 同隊 | 換隊 |','|---|---|---|'])
    for period in periods+['pooled']:allcorr.append(f"| {period} | {ci(get(m,'same',period))} | {ci(get(m,'moved',period))} |")
    allcorr.extend(['','| 季中 | 全部換隊代理 | 官方交易名單交集子樣本 |','|---|---|---|'])
    for period in p['seasons']+['pooled']:allcorr.append(f"| {period} | {ci(get(m,'seasonMove',period))} | {ci(get(m,'officialTradeParticipant',period))} |")
write('correlations.md',allcorr)
teams=['# 指標與球隊防守效率的關聯','', '球隊為官方box球權代理DefRtg的負值，越高表示防守較好。每季各自去均值、等權合併；區間共同重抽franchise。個人指標按真實分鐘加權，合格指標樣本必須覆蓋至少80%隊內分鐘，否則該隊留缺。這不是資料外球隊預測成績。']
for m in metrics:
    teams.extend(['',f'## {labels[m]}','','| 球季 | 與球隊DefRtg相關 [95%]（隊數） |','|---|---|'])
    for period in p['seasons']+['pooled']:teams.append(f"| {period} | {ci(tc(m,period))} |")
    teams.extend(['',f"與同場次球員不在場防守效率之關聯：{ci(tc(m,kind='matchedOffContext'))}。on/off差本身含OFF項，不能把這個相關直接視為體系污染的因果證據。"])
write('team-correlations.md',teams)
inventory=['# 四季可取得性與覆蓋率','', '球員分母為官方逐場log中全季正分鐘者；raw存在不代表達到相關分析的出手／回合數門檻。分鐘覆蓋只表示該球員有指標，不表示PBP涵蓋所有分鐘。']
for m in metrics:
    inventory.extend(['',f'## {labels[m]}','','| 球季 | 有指標／全體 | 球員覆蓋 | 球員分鐘覆蓋 | ≥500分鐘有指標／全體 |','|---|---:|---:|---:|---:|'])
    for r in inv['metrics']:
        if r['metric']==m:inventory.append(f"| {r['season']} | {r['players']}/{r['totalPlayers']} | {r['playerCoverage']*100:.2f}% | {r['minuteCoverage']*100:.3f}% | {r['rotationPlayers']}/{r['totalRotationPlayers']} |")
write('inventory.md',inventory)
strict=[]
for season in p['seasons']:
    b='reports/defense-b1' if season=='2025-26' else f'reports/defense-seventh/{season}/stints';v=json.loads((R/b/'defensive-samples.json').read_text(encoding='utf-8'));failures={}
    for key in ['missingPbp','lineupFailed','uncertainPossessionGames','counterMismatchGames']:
        for g in v[key]:
            gid=g if isinstance(g,str) else g['id'];failures.setdefault(gid,[]).append(key)
    strict.append({'season':season,'usable':v['strictUsableGames'],'coverage':v['strictCoverage'],'failures':[{'id':gid,'reasons':reasons} for gid,reasons in sorted(failures.items())]})
save('strict-failures.json',strict)
profile=[]
targets={1610612752:'尼克',1610612738:'塞爾提克',1610612766:'黃蜂',1610612756:'太陽',1610612760:'雷霆'}
old=json.loads((R/'reports/defense-tenth/step2/season-analysis.json').read_text(encoding='utf-8'))
for season in p['seasons']:
    cell=next(c for c in old['points'] if c['season']==season and c['k']==55)
    for tid,name in targets.items():
        err=next(t for t in cell['versions']['pure']['teams'] if t['id']==tid)['centeredDefContribution']
        row={'season':season,'id':tid,'name':name,'pureK55CenteredDefenseError':err}
        for metric in ['DEFLECTIONS36','DEF_BOXOUTS36','CONTESTED_SHOTS_3PT36']:
            pool=[v for v in team['predictions'] if v['period']==season and v['metric']==metric];obs=next((v for v in pool if v['id']==tid),None)
            mu=sum(v['x'] for v in pool)/len(pool);sd=(sum((v['x']-mu)**2 for v in pool)/len(pool))**.5
            row[metric+'Z']=(obs['x']-mu)/sd if obs else None
        profile.append(row)
save('target-team-observations.json',profile)
sha=lambda f:hashlib.sha256((O/f).read_bytes()).hexdigest()
report=['# 第十批第四步 T2：防守資料盤點與可攜性檢定','',
'**T2完成並停下。直接防守事件與近框壓制最值得作新卡來源；官方個人防守效率、原始在場效率、三分命中率差，不適合直接當成可攜防守能力。on/off與對位壓制有少量跨季訊號，但季中換隊檢定仍分不出，不能靠與球隊防守高相關就採用。未跑模擬、未建卡，沒有宣稱球隊RMSE已改善。**', '',
f"protocol登記 {p['registeredAt']}，SHA `{sha('protocol.json')}`。相關分析前補充既有嚴格稽核來源與官方交易名單驗證，登記 {s['registeredAt']}，SHA `{sha('measurement-supplement.json')}`；原protocol未修改。",
'','## 已驗證：資料完整度','',
'四季共575個全季統計端點成功、0個失敗，另取得4份官方交易清單。包括全聯盟與有季中換隊球員的各隊篩選；以全季原始行、出手計數、球員GP核對，不依結果挑球員。原有leaguedashptdefend大多到calendar55，本次全季資料另存raw，不覆蓋原始來源。','',
'| 球季 | 全季正分鐘球員 | 嚴格區段可用場次 | 場次覆蓋 | 失敗／缺場 |','|---|---:|---:|---:|---:|',
*[f"| {v['season']} | {len(data[v['season']]['players'])} | {v['usable']}/1230 | {v['coverage']*100:.2f}% | {len(v['failures'])} |" for v in strict], '',
'嚴格可用以既有defensive-samples.json為準，同時排除換人／分鐘失敗、回合不確定、計數不符與缺PBP；沒有重新建陣容或手改失敗場次。on/off對手禁區／三分占比已從合格區段新算，OFF只取球員確實上過場的相同場次，避免把整段缺陣誤當成OFF對照。禁區為限制區＋其他油漆區，與追蹤的六呎內不同。','',
'| 資料 | 可取得性／用途 |','|---|---|',
'| leaguedashptdefend | 四季全季六呎內、三分被防守命中率及對手正常命中率；跨季皆可用。 |',
'| 逐球on/off防守、對手出手占比 | 四季可新算；主要限制是上述嚴格場次覆蓋與OFF樣本。 |',
'| leagueseasonmatchups | 四季逐對位FGA／FGM、PARTIAL_POSS、對手；另用個人USG加權，分開報命中壓制與負擔。 |',
'| hustle | 四季兩分／三分干擾、破壞傳球、卡位、製造進攻犯規；全季與分隊版本可用。 |',
'| 個人防守效率 | 四季Advanced DEF_RATING可用；是球員在場的球隊效率，不是單獨球員守備價值。 |','',
'各指標原始球員與分鐘覆蓋、≥500分鐘球員覆蓋完整見inventory.md。六呎／三分有值的球員約98%，其球員分鐘覆蓋均>99.97%；hustle與官方效率同樣接近完整。但這不是事件／區段100%覆蓋，也不是所有人都通過最小樣本門檻。','',
'資料核對中特別處理：官方game log把極短上場四捨五入成MIN=0，GP仍須計入；全球追蹤端點2022–23 Mikal Bridges回傳兩段同ID資料，依出手數合併，不能保留最後一筆。TeamID篩選後隊名仍可能是最後一隊，使用請求的隊別與GP／出手數核對，而非回傳隊名。處理後的拒收與分隊合計檢查見endpoint-audit.json。','',
'## 已驗證：穩定性與體系影子','',
'下表 r [聯合95%]（成對筆數）。跨季要求兩季各≥500分鐘、主要球隊分鐘≥60%；六呎至少100次、三分75次、對位100次；ON與OFF各1000回合。季中兩側各≥300分鐘，使用較低的50／40／50次與300回合門檻。詳細三組相鄰季、各季交易前後、unique球員數與Spearman均另列。20,000次球員ID＋franchise共同重抽；這裡沒有模擬seed，沒有拿seed區間代替球員資料不確定性。','',
'| 指標 | 同隊相鄰季 | 換隊相鄰季 | 官方交易名單交集：季中前後 | 與球隊防守相關 |','|---|---|---|---|---|',
*[f"| {labels[m]} | {ci(get(m,'same'))} | {ci(get(m,'moved'))} | {ci(get(m,'officialTradeParticipant'))} | {ci(tc(m))} |" for m in ['rimSuppression','threeSuppression','DEFLECTIONS36','DEF_BOXOUTS36','CONTESTED_SHOTS_2PT36','CONTESTED_SHOTS_3PT36','BLK36','STL36','DREB36','PF36','officialDefRtg','onDefRtg','onOffDef','onOffRimShare','onOffThreeShare','matchupSuppression','usageWeightedMatchupSuppression','defensiveLoad']], '',
'相同球員可以出現在多個相鄰季，n不是獨立人數；重抽時同ID跨季共用權重，franchise亦跨季配對，每次重抽內重新去季均值並維持季等權。原始在場效率與官方DEF_RATING的球隊相關接近1，包含同一批得失分的機械關聯，不能當成個人能力驗證。','',
'季中「換隊」由逐場log客觀辨認，全部代理與官方交易名單交集分開報。官方交易名單由球員ID連結或完整名稱吻合，僅保留兩個出賽franchise；但不含完整逐日簽約／裁撤歷史，不能保證每個首隊→末隊移動都完全由該交易直接造成。這個限制保留，不把未確認的換隊人硬標成交易。','',
'## 防守卡提案（推測，尚未建卡）','',
'| 新欄位 | 候選觀測 | 理由與限制 |','|---|---|---|',
'| 近框阻止 | 六呎內命中壓制、BLK/36，兩分干擾作曝光／角色條件 | 換隊、季中均有延續性；命中結果與干擾量分開，避免把中鋒角色直接當能力。 |',
'| 外圍參與 | 三分干擾/36、對位負擔；不使用三分命中率差當主要能力 | 三分干擾換隊後穩定，實際命中差不穩；主要影響出手被有效干擾的機會，不能把所有防守者直接轉成降低3P%。 |',
'| 破壞球權 | DEFLECTIONS/36與STL/36分開 | 破壞傳球換隊r約0.84、抄截約0.75；可觀測傳球壓力，不只記最後的steal。要避免把同一次deflection與steal算兩次。 |',
'| 防守卡位／收板 | DEF_BOXOUTS/36加個人DREB的機會率 | 卡位換隊r約0.87、季中約0.82；把為隊友取得籃板的行為與自己收板分開，避免只用個人REB高低。DREB/36仍受對手投失與位置影響。 |',
'| 犯規紀律 | PF/36，製造進攻犯規另列 | PF換隊r約0.81，適合獨立約束送罰球風險；PF並非全為投籃犯規，未歸因的犯規種類不可硬轉成FTA。 |',
'| 防守負擔（條件欄，非強度加分） | PARTIAL_POSS加權對手USG | 換隊r約0.65；用來比較守的是誰及曝光，不代表負擔越高能力越好。 |','',
'暫不建「禁區嚇阻」與「獨立協防」：on/off禁區占比在季中前後接近0；目前不能從隊友與對手選擇中獨立識別個人嚇阻。對位命中壓制雖與球隊防守約0.81相關，季中前後仍分不出；它缺少同出手位置、空間與進攻動作條件，不能直接取代onBall。','',
'每項應獨立開關，事件量與結果率分開按機會數收縮；公式與權重須在下一次建卡前另登記。預期先改善個人防守訊號的辨識度；T2沒有模擬，因此沒有可負責任的net RMSE／勝場改善數字。是否真正提高球隊準確度仍待純卡驗收。','',
'## 五隊個案：不能一律補防守分','',
'下面是既有純卡K55截止後的去均值防守貢獻誤差（負值低估防守，分／場），不是同季全季；沒有重跑。','',
'| 球隊 | 2022–23 | 2023–24 | 2024–25 | 2025–26 |','|---|---:|---:|---:|---:|',
*[f"| {name} | "+' | '.join(n(next(r for r in profile if r['id']==tid and r['season']==season)['pureK55CenteredDefenseError'],2) for season in p['seasons'])+' |' for tid,name in targets.items()], '',
'雷霆2023–24、2024–25，太陽與黃蜂2024–25，其防守在這個口徑反而被高估，不能接受「五隊四季都被低估」的前提。','',
'2025–26全季個人事件組成的球隊觀測z值（聯盟隊平均為0；只是答案側描述，不是K55建卡輸入）：','',
'| 球隊 | 破壞傳球 | 防守卡位 | 三分干擾 |','|---|---:|---:|---:|',
*[f"| {name} | "+' | '.join(n(next(r for r in profile if r['id']==tid and r['season']=='2025-26')[m+'Z'],2) for m in ['DEFLECTIONS36','DEF_BOXOUTS36','CONTESTED_SHOTS_3PT36'])+' |' for tid,name in targets.items()], '',
'推測：雷霆可先檢驗外圍參與＋破壞球權；太陽先檢驗破壞球權；尼克、塞爾提克與黃蜂先檢驗為隊友卡位這項現有個人籃板未完整反映的行為。尼克／塞爾提克／黃蜂的破壞傳球不是聯盟特強，資料不支持替這三隊一律加抄截壓力。這些都是球員觀測的候選路徑，不按隊補分，也不能當成已找到每隊防守誤差的原因。','',
'## 失敗與限制','',
'- 所有端點取得成功，不代表所有樣本合格；完整區段失敗名單在strict-failures.json，分隊樣本不足／時間重疊／官方交易未確認清單在move-samples.json。','- 三分命中差未證明可攜；on/off禁區嚇阻、獨立協防及季中對位壓制仍未通過穩定性證據。','- 相鄰季相關也可能反映身材、位置與固定角色；強穩定性不足以證明相同數值在任意陣容仍有相同效果。沒有控制全部十名球員的因果模型，也沒有用防守效率修補卡。','- 四季全季資料是觀測答案；若下一步建截止前卡，必須重新套DateTo／逐場截止篩選，不能把本批全季值搬回K25/41/55。','- 與球隊效率的相關屬同樣本描述，不能冒稱資料外準確度，亦未對20項相關做多重檢定的採用決策。','',
'## 重跑與封存','',
'從專案根目錄執行；fetch可復用本批raw快取，不覆寫舊版本：','',
'```powershell','node reports/defense-tenth/step4-t2/fetch.mjs','node reports/defense-tenth/step4-t2/fetch-trades.mjs','python reports/defense-tenth/step4-t2/prepare.py','python reports/defense-tenth/step4-t2/analyze.py','python reports/defense-tenth/step4-t2/report.py','node reports/defense-tenth/step4-t2/audit.mjs','```','',
'register與register-supplement已封存，重跑時不得覆寫。未開始T3／T4／B／D，完成T2後停下。','',
'端點欄位以官方原始回應為準，程式接口對照 [nba_api 對位端點原碼](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/leagueseasonmatchups.py)、[hustle端點原碼](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/leaguehustlestatsplayer.py)。防守效率概念參照 [NBA Stats glossary](https://www.nba.com/stats/help/glossary)。官方交易驗證來源：'+', '.join(f"[{x['season']} NBA trade tracker]({x['url']})" for x in read('trade-sources.json')['sources'])+'.'
]
write('report.md',report)
print('REPORTS',len(corr),len(team['results']),len(profile))

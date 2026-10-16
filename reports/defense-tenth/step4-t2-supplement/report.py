import json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];OLD=R/'reports/defense-tenth/step4-t2'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(f,s):(O/f).write_text(s,encoding='utf8')
def f(x,n=3):return '—' if x is None else f'{x:.{n}f}'
def tab(headers,rows):return '| '+' | '.join(headers)+' |\n|'+ '|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)+'\n'
def ci(x):return f(x['pearson'])+' ['+', '.join(f(v) for v in x['ci95'])+']; n='+str(x['n']) if x['ci95'] else 'n='+str(x['n'])+'；不足'
C=read(O/'cases.json');F=read(O/'cached-factors.json');L=read(O/'lineup-observations.json');pairs=read(O/'named-pairs.json');league=read(O/'league-reference.json');corr=read(O/'matchup-correlations.json')
oldcorr=read(OLD/'correlations.json');tc=read(OLD/'team-correlations.json')['results'];p=read(O/'protocol.json')
s='''# T2 防守資料與對位補充（不改卡、不跑模擬）

T2 完成。現有資料支持優先分離「護框命中壓制、破壞傳球、防守籃板／卡位、對位負擔與範圍」，不支持把所有缺口都歸給護框或放大 onBall。騎士 2022–23、尼克 2023–24 的純卡禁區命中率已壓得比真實低；v3 仍缺防守籃板，騎士還缺迫使失誤、尼克則禁區出手比例過高。尼克三季的對位負擔符合 Brunson 較輕、OG 較重且涵蓋後衛／前鋒，但不能由彙總對位證明 Hart／Towns 在特定回合替 Brunson 補位。

雷霆 2024–25 的 net 低估有進攻與防守兩部分；2025–26 主要在防守。v3 的補強路徑也不同：前者活球失誤壓力最突出，後者禁區壓制與籃板更突出。以下全是四個已看過答案球季的全季描述；v3 區段係數為全季 in-sample，不能當作個人可攜能力或資料外改善的證明。

## 登記、範圍與資料口徑

'''
s+=f"主要規格登記 {p['registeredAt']}，SHA-256 `{(O/'protocol.sha256').read_text().split()[0]}`。補充具名雙內線檢查另登記於 named-pairs-supplement.json；其 SHA 為 `{(O/'named-pairs-supplement.sha256').read_text().split()[0]}`。T0、舊 T2、引擎與既有 protocol/output 均保護；未下載新資料，未建卡、未重跑比賽，T2b 未開始。\n\n"
s+='T0 防守誤差 D 是**去聯盟均值後的場均失分差**，負數表示低估防守，不是每百回合。下表的防守代理與T0一樣，採雙方 FGA−OREB+TOV+0.44FTA 的平均；真實區段 PPP 則用重建回合。這兩種分母不同，不互相當效率目標。歷史純卡共用 v3 常數，帶有已知聯盟漂移，絕對效率不得代替去均值誤差。\n\n'
s+='## 已驗證：四季覆蓋與跟著球員走檢定\n\n'
inv=read(OLD/'inventory.json');cov=read(O/'matchup-coverage.json')['coverage']
s+=tab(['球季','嚴格場數／1230','護框個人分鐘覆蓋','對位位置權重覆蓋','對位使用率權重覆蓋'],[[a['season'],str(read(OLD/'players.json')[a['season']]['strictGames'])+'/1230',f(100*next(v['minuteCoverage'] for v in inv['metrics'] if v['season']==a['season'] and v['metric']=='rimSuppression'),3)+'%',f(100*a['positionCoverage'],3)+'%',f(100*a['usageCoverage'],3)+'%'] for a in cov])
s+='舊 T2 已完成 575 個端點請求，失敗 0；各指標的球員數、500 分鐘輪替覆蓋、缺漏與交易切分拒收清單，完整沿用 [原始盤點](../step4-t2/inventory.md)、[原始檢定](../step4-t2/correlations.md)、[端點稽核](../step4-t2/endpoint-audit.json)。個人 DEF_RATING 與在場 DRtg 是場上團隊結果；不能因覆蓋率高就當純卡能力。6 呎內 DFG 的 PLUSMINUS 是命中率差，並非場上正負值。\n\n'
metrics=['rimSuppression','threeSuppression','matchupSuppression','usageWeightedMatchupSuppression','onDefRtg','onOffDef','onOffRimShare','onOffThreeShare','officialDefRtg','DEFLECTIONS36','DEF_BOXOUTS36','CONTESTED_SHOTS_2PT36','CONTESTED_SHOTS_3PT36','BLK36','STL36','DREB36','PF36']
rows=[]
for m in metrics:
 def get(g):return next(x for x in oldcorr if x['metric']==m and x['group']==g and x['period']=='pooled')
 t=next(x for x in tc if x['metric']==m and x['period']=='pooled' and x['kind']=='teamDefRtg')
 rows.append([m,ci(get('same')),ci(get('moved')),ci(get('officialTradeParticipant')),f(t['pearson'])])
s+=tab(['個人指標','同隊相鄰季 r [95%]; n','換隊相鄰季','季中交易前後¹','球隊防守強度 r'],rows)
s+='¹ 官方交易名單確認子樣本；不是完整交易因果辨識。舊檢定門檻：相鄰兩季各 ≥500 分鐘、主要隊占比 ≥60%；交易兩端各 ≥300 分鐘；另有出手／on-off 回合門檻。球員與 franchise 聯合重抽 20,000 次、每個季別重新去均值並等權。未控制所有防守角色／隊友／受傷，所以相關只表示可攜候選訊號。球隊 r 是個人指標依分鐘加總對負 DRtg，非因果，也不等於加進引擎的增益。\n\n'
s+='## 已驗證：新增對位多樣性與負擔\n\n'
s+=tab(['指標','同隊相鄰季','換隊相鄰季','季中交易前後','球隊防守強度'],[[m]+[ci(next(x for x in corr if x['metric']==m and x['group']==g)) for g in ['same','moved','officialTradeParticipant','team']] for m in ['load','highUsageShare','diversity','effectivePositions','guardShare','forwardShare','centerShare']])
s+='新增檢定要求對位 PARTIAL_POSS ≥1000、位置與使用率權重覆蓋各 ≥95%。相鄰季有 596 同隊／184 換隊樣本，官方交易子樣本 69。多樣性為 G/F/C 三組的正規化熵；混合位置等分。這個高穩定性很可能也反映身材與常守位置，**不表示換防能力有同等高信度**；球隊相關約 0.062，不能直接加防守分。五位置只另外提供凍結卡的身高推定 proxy，不能拿它證明真實一到四號換防。完整逐人矩陣在 matchup-player-data.json。\n\n'
s+='## 已驗證：尼克對位與藏人假說\n\n'
rows=[]
for c in C:
 if c['team']!='New York Knicks':continue
 for x in c['players']:
  if x['name'] not in ['Jalen Brunson','OG Anunoby','Josh Hart','Karl-Anthony Towns']:continue
  v=x['matchups'];m=v['metrics']
  rows.append([c['season'],x['name'],f(m['load'],2),f(x['burdenPeerPercentile'],1),f(m['highUsageShare'],1),'/'.join(f(100*v['positions'][k],1) for k in ['G','F','C'])])
s+=tab(['球季','球員','對手使用率加權%','同官方位置負擔百分位','守使用率≥25%對手占比','守 G/F/C%'],rows)
s+='Brunson 三季負擔在同位置約第 8／9／11 百分位，OG 約第 80／91／89；OG 對後衛與前鋒皆有大量對位。這支持「任務分配不同」，尚不能證明差異是尼克戰術創造的淨收益，也不能從 Hart／Towns 的卡位與籃板直接辨識誰替誰補位。Towns 的 2024–25／2025–26 卡位 2.26／1.72 次每36分鐘（詳表以原值為準），Hart 的籃板卡強但不是高卡位次數球員。\n\n'
s+='## 引擎稽核（T0 實際使用的 fourth 引擎）\n\n'
s+=tab(['路徑','現況與限制','程式位置'],[
 ['誰守誰','出手者槽位 i 對防守槽位 i；換人沿原槽位替換，沒有每回合對位最適分派／換防圖','src/defense_fourth_game.js:142、159、243、266'],
 ['是否主動點名弱者','T0 使用 volume 選人：個人 FGA/FTA/TOV 每分鐘權重，不依對位弱點選初始持球／接球人；命中與 EV 會影響出手／傳球決策','src/defense_fourth_game.js:243、271–290；src/defense_probability.js:73–79'],
 ['隊友對弱者的影響','有：最強兩位 help+physique，60%/40%；團隊 STL/min 壓力。沒有：弱者被分派給低負擔對手的專屬保護','src/probability_model.js:201–204；src/constants.js:435；src/defense_probability.js:14–23、67–71'],
 ['v3 如何進來','五位防守者係數等權平均減中心；護框替代 neutral help，籃板替代舊防守籃板能力，失誤／犯規乘 hazard，分區重配機率','src/defense_fourth_effects.js:7–28；src/defense_fourth_game.js:187–191、255、282、308–311、332'],
 ['為何不能把區段係數當人能力','同季十人區段模型的條件係數；含場上體系與共線性，且平均化不能表達獨立的雙內線互補','src/defense_fourth_effects.js:7、14；T0 factors/engine-signals.json']])
s+='本表是程式路徑解釋，不是新機制測試。傳球攔截與協防會間接改善弱防守者同場的結果；不能因此說引擎已經有藏人。\n\n'
s+='## 八個個案：誤差與四要素\n\n'
s+=tab(['球季／球隊','純卡 O','純卡 D','v3 O','v3 D','真實 net／純卡／v3'],[[c['season']+' '+c['team'],f(c['T0']['pure']['O']),f(c['T0']['pure']['D']),f(c['T0']['v3']['O']),f(c['T0']['v3']['D']),'/'.join(f(v) for v in [c['actualNet'],c['T0']['pure']['net'],c['T0']['v3']['net']])] for c in C])
s+='O 正數＝高估進攻；D 正數＝高估防守。均為去聯盟均值後 PPG。雷霆 2024–25 net −8.054 中，進攻 −2.928、防守 −5.126；2025–26 net −6.449 中，進攻 +0.596、防守 −7.045。v3 防守分別補 4.613／4.920 PPG，但後者仍低估防守 2.125，由進攻高估 1.366 抵銷，才使 net 看起來幾乎補齊。\n\n'
for x in F:
 s+='### '+x['season']+' '+x['team']+'\n\n'
 s+=tab(['版本','防守代理','對手 eFG%','迫使 TOV%','DREB%','對手 FTR','對手3PA占比%','對手3P%'],[[v]+[f(z.get(k)) for k in ['defProxy','efg','forcedTOVpct','DREBpct','FTR','threeShare','threeFG']] for v,z in x['fullSeason'].items()])
 s+=tab(['口徑','禁區出手占比%','禁區 FG%'],[['真實嚴格區段',f(x['strictPbpPaintReference']['paintShare']),f(x['strictPbpPaintReference']['paintFG'])]]+[[v+' 全季',f(x['fullSeason'][v]['paintShare']),f(x['fullSeason'][v]['paintFG'])] for v in ['pure','v3']])
s+='禁區表真實只涵蓋嚴格場次，模擬為全季；T0 只存逐場比分，沒有逐場分區計數，無法無重跑取得同場交集。此處不是同場因果差值。全季 box 四要素則同口徑。\n\n'
s+='## 雙內線與護框：哪些說法被推翻\n\n'
s+=tab(['球季／雙內線','在場','防守回合','DRtg（重建）','禁區占比%','禁區FG%','對手3P%'],[[x['season']+' '+ '／'.join(x['pair']),'／'.join(x['present']) or '兩者皆無',f(x['stats']['poss'],1),f(x['stats']['defRtg']),f(x['stats']['paintShare']),f(x['stats']['paintFG']),f(x['stats']['threeFG'])] for x in pairs])
s+='''騎士 Allen／Mobley 同場 2229.9 防守回合，禁區 FG 54.48%，比兩者皆無 60.24% 低 5.76 個百分點；但 DRtg 110.54 對 109.73，總效率沒有同步變好，對手三分也由 30.87% 到 37.89%。所以資料支持禁區命中壓制，**不支持雙內線必然有額外整體防守加成**。兩人卡 help 已達 88.8／84.7；純卡模擬禁區 FG 52.96% 甚至比嚴格真實 55.83% 低，無證據再加護框係數。騎士 v3 迫使失誤率少 2.18 個百分點，DREB 少 4.94 個百分點，應先釐清這兩路。

尼克 2023–24 Hartenstein／Robinson 同場是 0 回合，不能把兩位中鋒的季級資料當雙中鋒陣容增益。Hartenstein 單獨在場禁區 FG 55.71%、Robinson 單獨 62.73%，受對手與搭檔差異影響，不能把差全部歸給個人。v3 禁區 FG 57.19% 對嚴格真實 57.34% 已近，禁區出手占比 51.71% 對 46.81% 卻偏高；DREB 71.31% 對全季真實 76.06%，比「再加護框」更值得先查。

原登記護框型＝身高≥82吋＋BLK36≥1＋近框100出手且壓制>0。Allen 在本機為81吋，因而漏分類；保留原結果於 lineup-observations.json，不把門檻事後改成81。具名雙內線為看到此分類缺陷後追加的描述檢查，另存規格與 SHA，沒有當採用驗收。NYK 2024–25 原分類無護框型也不等於沒有任何護框；DET Stewart 的高度亦會被這種硬門檻漏掉。

所有原分類的 0／1／2+ 分組完整在 lineup-observations.json；少於500回合的對照不解讀（如 NYK 2025–26 雙護框僅1回合）。OKC 2024–25 雙護框 613.1回合 DRtg111.56，並未優於單護框105.25；2025–26雙護框1412.8回合 DRtg102.14，優於單護框107.28。這些未控制對手／比分／時段，不能據此硬寫全聯盟雙內線加成。

## 雷霆：v3 補的是哪些訊號／哪些人

'''
s+=tab(['球季','禁區命中 logit','活球失誤 log multiplier','DREB logit','FTA log multiplier','禁區／三分 share raw effect'],[[c['season']]+[f(c['allPlayersMeanSignal'][k]) for k in ['shortFG','liveTOV','DREB','FTA']]+[f(c['allPlayersMeanSignal']['shortShare'])+' / '+f(c['allPlayersMeanSignal']['threeShare'])] for c in C if c['team']=='Oklahoma City Thunder'])
s+='''這是按嚴格真實陣容回合加權的「五人平均係數減中心」，不是模擬實際陣容平均，更不是每位球員帶來幾分。2024–25 活球失誤倍率 exp(0.250)=1.284，2025–26為 exp(0.116)=1.123；2025–26禁區命中 −0.328 logit、DREB +0.131 logit。midFG／threeFG 係數雖存在於 map，這五開關不會把它們當成額外命中抑制，不能計功。

2024–25 的活球失誤正貢獻主要為 Jalen Williams +0.096、Caruso +0.079、Wallace +0.076、SGA +0.063；2025–26 是 Wallace +0.157、Caruso +0.040、Ajay Mitchell +0.024。Wallace 的純卡 onBall 66.2／73.3，只由三分 DFG 構成，無法描述他的 deflections36 4.68／5.96；但純卡另有 STL/min 團隊壓力，不能說完全沒讀抄截。

2025–26 禁區壓制的主要負貢獻為 Chet −0.131、SGA −0.054、Jaylin Williams −0.047、Hartenstein −0.039；DREB 正貢獻 Chet +0.103、Hartenstein +0.066、Jaylin +0.064。Chet 純卡 help 已到99，改善並非只把他的卡變高，而是 v3 的替代映射與全體陣容訊號。Dort 的 v3 活球失誤係數2025–26反而略負，不可因名聲把所有雷霆人都描述為被低估。

完整80名「個案球隊分鐘前十」的純卡、防守高階指標、on/off、負擔、分區及 v3 個人係數與曝險貢獻，見 [逐人對照](player-comparisons.md)／[機讀資料](cases.json)。這回答的是 map 如何分配訊號，**沒有球員級反事實模擬，不能把4.6／4.9分改善因果分配給某幾人**。

## 提案（推測，未改卡／引擎）

1. **護框命中壓制**：6呎內 DFG 相對對手基準、FGA樣本、BLK／護框干擾作多個獨立訊號，依樣本收縮；不以 on/off DRtg 建卡。現有 help 強者已高，騎士不應先放大；驗證要能改善分區命中與可攜性，而非只補球隊 net。
2. **破壞傳球／逼迫活球失誤**：deflections 與 STL 分開量，再由實際事件比率決定如何影響傳球／持球失誤，避免重複計分。可優先驗證 OKC Wallace／Caruso、DET Ausar／Green，不能把全季區段殘差搬過來。
3. **卡位與收板**：DEF_BOXOUTS、DREB機會／實得、身材；分「為隊友卡位」與「自己拿板」。Towns／Hartenstein／Queta 的卡位、Hart 的收板是不同角色；有望解決 NYK、BOS 的低估，但騎士 v3 的 DREB替代路徑本身也須另批檢查，不能保證新卡即可修好。
4. **對位範圍／負擔**：G/F/C位置分布、對手USG及對位相對命中率。範圍用來約束誰能接手誰，不直接加能力分；使用率負擔是測量條件，不是越高越強的獎勵。三分DFG 跨隊無穩定性，3pt contested雖可攜但球隊r≈0.037，暫不直接當三分壓制。
5. **防守犯規**：個人 PF/防守機會；進攻犯規與防守犯規要分離後才進卡。PF36可攜只證明頻率穩定，尚不是乾淨防守犯規訊號。

**藏人規則提案**：每次攻守五人先形成5×5對位分配，讓對位範圍、身材、個人對位能力決定可承擔的任務，並受一人不能同時守兩人的容量限制。對手高使用率／自主創造者需要有人承接；若隊友如OG能接手，弱者可分配給低使用率者，其高曝光代價自然降低。若其餘四人接不住，不能免費減罰；換防造成的補位與籃板代價也須保留。與現況同槽位相比，預期先改善任務分配，不先承諾 net RMSE 的幅度。下一批若試，必須先凍結全聯盟規則，對位預測用換隊個人樣本驗證，再看純卡T0成績；不能以尼克ID或Brunson個別豁免。

**嚇阻／協防欄位暫不成立**：on/off禁區占比換隊 r0.195、交易前後約0.023；3P占比交易前後也近零。現有資料不足以把「讓對手不投禁區」獨立歸因到某球員；HELP_BLK/HELP_FGA可列觀察，但要先確認事件歸屬與可攜檢定，不能先填新卡。CHA 的 deflections36 聯盟z為−1.74、卡位+1.61；PHX 則+1.42／−0.75（沿用舊T2的2025–26個人觀測）。因此 CHA 候選是補卡位，不是硬加失誤壓力；PHX 候選相反。BOS Queta的護框／卡位、NYK Towns的卡位與Hart的收板、OKC的傳球破壞各有不同依據，不能用單一總防守分保證五隊一起改善。

以上新卡全部應是個人觀測欄位；v3只作in-sample對照。未來另版本校正聯盟合計FG／FTA／TOV／回合常數，不能把球隊net、名次、勝場或on/off殘差加回卡。

## 失敗、限制與未解決

- 「雙內線總防守一定更好」沒有成立；騎士同場的禁區壓制可見，但總效率不一致。尼克2023–24沒有指定雙中鋒同場樣本。
- 「雷霆net幾乎補齊＝防守已準」不成立；2025–26仍有攻防誤差互相抵銷。
- 還不能驗證真實一到四號換防、Hart/Towns替Brunson補位、或每位球員的因果得分貢獻。對位位置僅官方G/F/C，細五位置是身高proxy。
- 新位置門檻量測有漏分類，如實保留並另列具名探索；不是事後調門檻。
- 第一遍新腳本把opponent.dreb當成本方DREB；檢查區段結構後修正為另一隊opponent.dreb，並用相同登記規則完整重算。這是記帳修正，未改分組或選擇指標。
- 對位多樣性高相關可能主要是身材／職責穩定；不能據此宣稱有可泛化的防守能力分。所有新增區段比較未控制隊友、對手、比分與樣本選擇。
- 嚴格覆蓋87.72%／86.42%／88.70%／96.59%，缺場未補；個人端點覆蓋高不代表區段樣本無偏。個人進攻卡、年齡傷病替代解釋屬T2b，本次未做。

## 重跑與稽核

```powershell
python -X utf8 reports/defense-tenth/step4-t2-supplement/analyze.py
python -X utf8 reports/defense-tenth/step4-t2-supplement/named_pairs.py
python -X utf8 reports/defense-tenth/step4-t2-supplement/cached_factors.py
python -X utf8 reports/defense-tenth/step4-t2-supplement/report.py
python -X utf8 reports/defense-tenth/step4-t2-supplement/audit.py
```

只重算新目錄量測，不會重跑T0或改凍結檔。完整輸入雜湊／程式雜湊與保護檔比對見 completion-audit.json。

端點欄位參照 [nba_api原始介面](https://github.com/swar/nba_api/blob/master/src/nba_api/stats/endpoints/leagueseasonmatchups.py)；NBA指標命名參照 [NBA glossary](https://www.nba.com/stats/help/glossary)。實測數字來自本機已封存官方資料，並非網頁文章估算。
'''
write('report.md',s)

details='# T2 個案：純卡與個人高階防守指標\n\n全季已看過答案；v3係數為in-sample。負擔採該隊對位，計數率採該隊每36分鐘；被交易者可能缺單隊端點，空值不補。純卡同一球員全季卡不按隊修改。\n\n'
for c in C:
 details+='## '+c['season']+' '+c['team']+'\n\n'
 details+=tab(['球員','分鐘','onBall/help/REB','6ft壓制pp','3pt壓制pp','STL/BLK/DREB/PF36','干擾2/3PT36','deflections36','卡位36','對位壓制pp','對手USG%','on-off防守好幾分'],[[x['name'],f(x['minutes'],0),'/'.join(f(x['card'][k],1) for k in ['onBall','help','rebound']),f(x['metrics'].get('rimSuppression'),2),f(x['metrics'].get('threeSuppression'),2),'/'.join(f(x['metrics'].get(k),2) for k in ['STL36','BLK36','DREB36','PF36']),'/'.join(f(x['metrics'].get(k),2) for k in ['CONTESTED_SHOTS_2PT36','CONTESTED_SHOTS_3PT36']),f(x['metrics'].get('DEFLECTIONS36'),2),f(x['metrics'].get('DEF_BOXOUTS36'),2),f(x['metrics'].get('matchupSuppression'),2),f(x['matchups']['metrics']['load'],2) if x['matchups'] else '—',f(x['metrics'].get('onOffDef'),2)] for x in c['players']])
 details+='v3個人去中心係數（非每回合得分／因果能力）：\n\n'
 details+=tab(['球員','禁區FG logit','活球失誤 log multiplier','DREB logit','FTA log multiplier','禁區／三分share raw effect'],[[x['name']]+[f(x['centeredSignal'][k]) for k in ['shortFG','liveTOV','DREB','FTA']]+[f(x['centeredSignal']['shortShare'])+' / '+f(x['centeredSignal']['threeShare'])] for x in c['players']])
details+='## 具名雙內線額外球員\n\n'
for pair in pairs:
 if len(pair['present'])!=0:continue
 details+=tab(['球季','球員','分鐘','身高in','onBall/help/REB','6ft壓制pp','BLK36'],[[pair['season'],x['name'],f(x['minutes'],0),str(x['card']['heightInches']),'/'.join(f(x['card'][k],1) for k in ['onBall','help','rebound']),f(x['metrics']['rimSuppression'],2),f(x['metrics']['BLK36'],2)] for x in pair['playerCards']])
write('player-comparisons.md',details)
print('REPORT',len(s),len(details))

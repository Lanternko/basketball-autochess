"""Report the context diagnostic; no new estimates or result-driven tuning."""
from register import HERE,SEASONS,read

NAMES={'boxPersistence':'直接沿用上半季 box OREB／36','chancePersistence':'直接沿用上半季追蹤率',
       'history':'只有個人歷史的機會模型','role':'歷史＋組織角色變化','competition':'歷史＋隊友競爭變化','both':'歷史＋兩者'}
def ci(x,field='joint95'):
 a,b=x[field];return f"{x['point']:+.5f} [{a:+.5f}, {b:+.5f}]"
def main():
 p=read(HERE/'protocol.json');d=read(HERE/'decision.json');a=read(HERE/'data-audit.json');r=read(HERE/'results.json')['results'];desc=read(HERE/'descriptive.json');geo=read(HERE/'geometry-inventory.json')
 out=[]
 def line(x=''):out.append(x)
 line('# 同一球員換角色與隊友：OREB 機會診斷')
 line()
 line('**結論：兩個角色／隊友替代量皆未增加可確認的 OREB 預測價值，合併版本也未通過。暫不據此修改角色倍率、卡位係數或引擎。** '
      '兩個檢查季等權合併，OREB／36 MAE：上半季原率沿用 0.35151，個人歷史 0.35512，加角色 0.35468，加隊友競爭 0.35488，兩者 0.35391。'
      '三候選對沿用原率與個人歷史的主要聯合區間均跨 0。')
 line()
 line('本批四季均**已看過答案**；以 2022–23、2023–24 估計，以 2024–25、2025–26 檢查。'
      '同季上半資料是截止前特徵，後半真實陣容與分鐘分配是**答案側的條件式診斷**，不是完全事前預測。'
      '沒有使用球隊淨勝分、效率、勝場、排名、正負值或區段攻守殘差來建模；區段僅提供場上五人與時間。沒有跑新模擬或改卡。')
 line()
 line('## 規則、理由與資料門檻')
 line()
 line('前一批的季彙總只能測「球員歷史是否穩定」。此次改成同人前後半變化，檢查隊友／角色變化能否提供原率沒有的資訊。'
      '若這條機會路徑有用，預期會降低機會預測誤差，再透過固定的上半季取得率降低 OREB 誤差；不預先指定改善量或強迫係數方向。')
 line()
 line(f"登記版本 `{p['version']}`，UTC `{p['at']}`；SHA-256 `{(HERE/'protocol.sha256').read_text().split()[0]}`。")
 line()
 line('- 聯盟共同日曆截止日：例行賽中位場次的日期；該日全部比賽歸上半，其次日開始下半。NBA Cup 決賽不在官方 `002` 例行賽樣本內。')
 line('- 新取得八份官方 `leaguedashptstats / Rebounding / Totals`，四季各前後半；回傳日期、GP 與原全季計數均核對。每名球員前＋後半的 OREB、機會數都精確等於已快取全季值。')
 line('- 只用既有嚴格場次的場上五人，沒有另調換人或分鐘。入樣兩半各至少 200 box 分鐘、100 追蹤分鐘，上半至少 10 次機會，兩半嚴格區段覆蓋各達本人 box 分鐘 70%。所有排除逐人保留。')
 line('- 組織角色：上半季 AST／36 在該五人中最高者的在場時間占比；同值均分。這只是組織任務代理，**不是實際持球時間或控衛位置**。')
 line('- 隊友競爭：另外四人的上半季機會／36 加總，依共同在場時間加權。固定使用上半季能力；缺資料／下半新出現者用上半季聯盟中位數，不偷取下半能力。')
 line('- 各模型基礎同為本人上半機會／36、log(上半 box 分鐘＋1)、AST／36；分別加入角色占比變化、隊友競爭變化、或兩者。只估機會變化，不改取得率。預測 OREB／36＝預測機會／36×上半季原始取得率。')
 line('- 五折以球員 ID 雜湊分組，ridge 只用前兩季選；ID 與球隊僅作配對／分組，不當特徵。沒有校正後半聯盟常數或看結果改倍率。')
 line('- 20,000 次球隊＋球員聯合重抽；同人同球隊跨季配對，季內分鐘加權、兩個檢查季等權。沒有模擬 seed 或重新訓練模型的不確定性。')
 line('- 主要六筆為三候選各對原率沿用／個人歷史的合併 OREB MAE；95% 與 Bonferroni 99.1667% 同報。其餘為探索，不用於採用。')
 line()
 line('## 已驗證：樣本與輸入')
 line()
 line('| 球季 | 截止日 | 嚴格場次／全季 | 覆蓋 | 入樣球員 | 前後半主要球隊不同 | 用途 |')
 line('|---|---|---:|---:|---:|---:|---|')
 for x in a['seasons']:
  line(f"| {x['season']} | {x['cutoff']} | {x['strictGames']}/{x['games']} | {x['strictCoverage']:.2%} | {x['cohort']} | {x['movers']} | {'估計' if x['season'] in p['estimator']['train'] else '檢查，已看過答案'} |")
 line()
 line('估計樣本 624 人季，檢查樣本 651 人季。檢查季「前後半主要球隊不同」合計 80 人季（42、38）；不是所有曾交易者，也不是 80 個獨立球員。'
      '排除低機會與低分鐘球員會限制泛化，新秀／新角色與追蹤缺漏不在本批結論範圍。')
 line()
 line('## 主表：後半個人 OREB 誤差')
 line()
 line('單位 OREB／36 分鐘；實際答案用個人 box OREB／box 分鐘。追蹤率使用追蹤分母，兩者分開，不能把來源差異算作角色效應。')
 line()
 line('| 模型 | 2024–25 MAE | 2025–26 MAE | 合併 MAE | 合併 RMSE | 合併相關 |')
 line('|---|---:|---:|---:|---:|---:|')
 for m in ['boxPersistence','chancePersistence','history','role','competition','both']:
  z=r['rate']['pooled-test']['all']['versions'][m]
  line(f"| {NAMES[m]} | {r['rate']['2024-25']['all']['versions'][m]['MAE']:.5f} | {r['rate']['2025-26']['all']['versions'][m]['MAE']:.5f} | {z['MAE']:.5f} | {z['RMSE']:.5f} | {z['Pearson']:.4f} |")
 line()
 line('| 候選 | 對照 | OREB MAE 差與聯合 95% | 聯合 99.1667% |')
 line('|---|---|---|---|')
 for m in ['role','competition','both']:
  for ref in ['BoxPersistence','History']:
   z=r['rate']['pooled-test']['all']['paired'][m+'Minus'+ref]['MAE']
   line(f"| {NAMES[m]} | {'原率沿用' if ref=='BoxPersistence' else '個人歷史'} | {ci(z)} | {ci(z,'jointBonferroni6')} |")
 line()
 line('負值為改善。候選相對個人歷史的改善點估計僅 0.00024–0.00120 OREB／36，連未校正 95% 都無法確認；'
      '相對直接沿用 box 原率反而稍差，亦不顯著。這批的人員、截止與評分期間和前批跨季 399 人測試不同，不能拿前批 0.3338 和這裡 0.3515 作版本改善比較。')
 line()
 line('## 機會路徑與合併的副作用')
 line()
 line('| 模型 | 合併機會／36 MAE | RMSE | 對個人歷史 MAE 差與聯合 95% |')
 line('|---|---:|---:|---|')
 for m in ['chancePersistence','history','role','competition','both']:
  z=r['chance']['pooled-test']['all'];v=z['versions'][m]
  delta='—' if m=='history' else ci(z['paired'][m+'MinusHistory']['MAE'])
  line(f"| {NAMES[m]} | {v['MAE']:.5f} | {v['RMSE']:.5f} | {delta} |")
 line()
 line('只有個人歷史的模型已把原機會沿用 MAE 從 0.52608 降到 0.50314。再加入角色／隊友，沒有進一步改善；'
      '兩者合併反而是 +0.01027，未校正 95% [＋0.00045, ＋0.01971]，99.1667% 跨零。'
      '這是離線機會預測的副作用，不是引擎籃板、快攻或戰績副作用。兩者模型的 ridge 由訓練折選到 1000，其他為100，不能把差異完全歸因於單一角色路徑。')
 line()
 line('2025–26 的候選機會數都贏原機會沿用，但個人歷史已做到，候選與個人歷史仍分不出；不能誤認為角色造成增益。完整各季與換隊區間在 `results.json`。')
 line()
 line('## 換隊診斷')
 line()
 line('| 檢查季／分組 | 人季 | 原 box 率沿用 MAE | 個人歷史 MAE | ＋角色 MAE | ＋隊友 MAE | ＋兩者 MAE | 兩者對原率：聯合 95% |')
 line('|---|---:|---:|---:|---:|---:|---:|---|')
 for s in ['2024-25','2025-26','pooled-test']:
  z=r['rate'][s]['movers'];v=z['versions']
  line(f"| {s} movers | {v['boxPersistence']['n']} | {v['boxPersistence']['MAE']:.5f} | {v['history']['MAE']:.5f} | {v['role']['MAE']:.5f} | {v['competition']['MAE']:.5f} | {v['both']['MAE']:.5f} | {ci(z['paired']['bothMinusBoxPersistence']['MAE'])} |")
 line()
 line('合併換隊組有 −0.00720 的點估計，但區間 [−0.05483, ＋0.04633]，不能宣稱卡換隊後更準。')
 line()
 line('## 描述性角色關聯與空間缺口')
 line()
 line('以下為**探索、非採用依據**；相關沒有聯合區間，不由它宣稱效果成立。依原登記做同人前後半差，角色變化至少15個百分點、隊友競爭變化至少1次機會／36才列為明顯變動。')
 line()
 line('| 球季 | 組織角色變化 vs 機會變化 r | 隊友競爭變化 vs 機會變化 r | 角色明顯上升／下降人數 |')
 line('|---|---:|---:|---:|')
 for s in SEASONS:
  z={x['feature']:x for x in desc if x['season']==s};u=z['deltaRole'];v=z['deltaCompetition']
  line(f"| {s} | {u['Pearson']:.4f} | {v['Pearson']:.4f} | {u['groups']['up']['n']}/{u['groups']['down']['n']} |")
 line()
 line('檢查季 651 人季僅 70 筆角色代理明顯變化。組織者代理的關聯方向與幅度不穩，不能支持引擎把同一卡由 C 移 PG 就大幅降低機會；'
      '隊友競爭在部分年份有弱負關聯，但未形成可確認的資料外 OREB 增益。')
 line()
 line(f"四季各抽3場逐球文件，共 {len(geo)} 場、{sum(x['actions'] for x in geo):,} 事件，{sum(x['actionsWithNumericXY'] for x in geo):,} 事件有 x/y；沒有發現十人位置陣列。"
      '這是抽樣格式盤點，不能當作全資料完整掃描。事件的投籃位置不等於十人的投籃當下站位。'
      '[官方籃板機會定義](https://www.nba.com/stats/help/glossary)也不提供起始站位。')
 line()
 line('## 事後資料警訊：機會計數跨季變動')
 line()
 line('這是輸入稽核後的探索，不用來改模型。')
 line()
 line('| 球季 | 官方追蹤 OREB 合計 | 官方追蹤機會合計 | 合併取得率 |')
 line('|---|---:|---:|---:|')
 for x in a['seasons']:
  o=x['reconcile']['OREB']['fullTotal'];c=x['reconcile']['OREB_CHANCES']['fullTotal']
  line(f"| {x['season']} | {o:,} | {c:,} | {o/c:.2%} |")
 line()
 line('OREB 增加而機會計數減少，合併取得率約 42.93%→59.63%。前後半重加總均精確，排除了這批日期切錯造成的漂移；'
      '但尚未分辨是實際機會形態變化、追蹤口徑／覆蓋變化或其他原因。不能未經核對便把全部變化歸為球員技巧，這也是跨季分解能力需謹慎的理由。')
 line()
 line('## 已驗證、推測、失敗與停止')
 line()
 line('- **已驗證：**日期篩選通過，分段計數守恆；可重建的陣容時間與個人前半數據能形成兩個獨立代理；兩代理沒有確認超過原率沿用與個人歷史。')
 line('- **推測：**AST 排序沒有捕捉出手當下站位／退防任務；季半平均的隊友機會數也沒有捕捉共享落點與卡位配對。取得率變化可能限制固定取得率路徑，但本批依可歸因規則不另修它。')
 line('- **失敗：**未辨識可泛化的角色機會係數、未確認換隊收益、未驗證卡位因果貢獻。兩代理一起加入的機會誤差有未校正退步。')
 line('- **限制：**已知後段陣容的答案側診斷，不是季前預測；機會數並非按陣容區段觀測，所以仍有聚合誤差。人員選擇、投失頻率、投籃分區、戰術與傷勢未因果控制；沒有偽造座標或把結果誰拿到板當成起始機會。')
 line('- **決定：**本批到此停止，維持引擎。不能宣稱 DREB、球隊 OREB 或 net／勝場 MAE 改善。下一個資料優先序應為核對官方機會口徑及可取得的逐次空間／卡位標籤，尚未下載或啟動下一批。')
 line()
 line('## 格式修復與重跑')
 line()
 line('初版將 API 回傳 `MM/DD/YYYY` 與登記的 `YYYY-MM-DD` 字串直接比較，誤判八筆日期。'
      '原程式、原稽核與原停止決定已保留；`analysis-code-repair-1.json` 在修正結果產出前登記，只做日期同義正規化與修復鏈鎖。'
      '沒有變動 protocol、截止日、樣本門檻、模型、資料或判準。')
 line()
 line('保留登記，不重跑 `register.py`；`fetch.mjs` 重用快取：')
 line()
 line('```powershell')
 for cmd in ['node reports/defense-tenth/step4-rebounds-context/fetch.mjs','python reports/defense-tenth/step4-rebounds-context/analyze.py','python reports/defense-tenth/step4-rebounds-context/report.py','python reports/defense-tenth/step4-rebounds-context/audit.py']:line(cmd)
 line('```')
 line()
 line('`data-audit.json` 完整資料門檻；`cohort-exclusions.json` 所有排除；`samples.json` 逐人前半與後半條件；'
      '`prefix-profiles.json` 來源期個人數據；`lineup-contexts.json` 角色代理；`fits.json` 訓練選擇與係數；'
      '`predictions.json` 逐人預測；`results.json` 所有配對區間；`completion-audit.json` 保護與重算稽核。')
 (HERE/'report.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
 print('Report rendered')
if __name__=='__main__':main()

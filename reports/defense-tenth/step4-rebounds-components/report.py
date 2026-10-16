"""Render the preregistered component diagnostic without refitting or selection."""
from analyze import read
from register import HERE, SEASONS

NAMES = {'persistence':'直接沿用前季 OREB/36','pctOnly':'只用前季 OREB%＋分鐘',
         'history':'原歷史模型','chance':'歷史＋機會數','conversion':'歷史＋取得率',
         'both':'歷史＋機會數＋取得率','adjustedBoth':'歷史＋機會數＋調整取得率（探索）',
         'missingOnly':'歷史＋缺值旗標（負對照）'}

def ci(x, field='joint95'):
    a,b=x[field]
    return f"{x['point']:+.4f} [{a:+.4f}, {b:+.4f}]"

def main():
    p=read(HERE/'protocol.json');r=read(HERE/'results.json')['results']
    d=read(HERE/'decision.json');q=read(HERE/'data-quality.json');s=read(HERE/'stability.json')
    out=[]
    def line(x=''):out.append(x)
    line('# OREB 機會與取得率：分開測試')
    line()
    line('**結論：三個主要候選皆未通過登記門檻，沒有可確認的額外預測增益，這一批不接入引擎。** '
         '2025–26 的個人 OREB/36 MAE，直接沿用前季為 0.3338，加機會為 0.3200，加取得率為 0.3178，兩者合加為 0.3187；'
         '點估計減少約 4–5%，但對前季沿用與原歷史模型的主要配對區間都跨 0。這不證明訊號不存在，也不證明效果相等。')
    line()
    line('四季均為**已看過答案**。以下是回溯的時間資料外診斷，不是新盲測，也不是引擎的球隊 OREB MAE。'
         '沒有跑新賽季模擬、沒有改球員卡、引擎或凍結版本。')
    line()
    line('## 設計與登記')
    line()
    line(f"- 規則版本：`{p['version']}`；UTC 登記時間：`{p['registeredAt']}`。")
    line(f"- SHA-256：`{read(HERE/'results.json')['protocolSHA256']}`。")
    line('- 主測試：用 2022–23→2023–24、2023–24→2024–25 訓練，預測 2024–25→2025–26；399 人。')
    line('- 重現測試：只用 2022–23→2023–24 訓練，預測 2023–24→2024–25；392 人。2023–24 缺更早訓練對，只列相鄰季穩定性。')
    line('- 兩季均至少 100 分鐘；缺追蹤欄位不刪人。前季資料才可作特徵，目標季真實分鐘只用於評分權重及已知曝光的籃板總數診斷。')
    line('- 所有模型在各項結果中使用完全相同的人員；各模型獨立由歷史訓練資料的球員分組五折選 ridge，沒有依測試結果調參。')
    line('- 區間：20,000 次球隊＋球員交叉聯合重抽；跨季使用共同球隊及球員權重。此處沒有模擬 seed，不冒稱球隊＋模擬 seed 區間。未包含重新訓練模型的不確定性。')
    line('- 主要六筆比較為三個候選各對「直接沿用」與「歷史模型」的 2025–26 OREB/36 MAE；同列 95% 與 Bonferroni 99.1667% 區間。其餘結果為探索。')
    line()
    line('## 已驗證：主測試')
    line()
    line('單位為進攻籃板／36 分鐘；MAE、RMSE 以目標季分鐘加權，相關為球員間 Pearson。原歷史模型包含前季 OREB/36、官方 OREB% 與 log(分鐘＋1)。')
    line()
    line('| 模型 | MAE | RMSE | 相關 | 已知分鐘的個人季總 OREB MAE |')
    line('|---|---:|---:|---:|---:|')
    for m,v in r['2025-26-rate']['all']['versions'].items():
        line(f"| {NAMES[m]} | {v['MAE']:.4f} | {v['RMSE']:.4f} | {v['Pearson']:.4f} | {v['conditionalCountMAE']:.2f} |")
    line()
    line('最後一欄給定每人真實季總分鐘，將預測率乘分鐘／36，再對球員平均絕對誤差；不是每場誤差，也不是事前分鐘預測。')
    line()
    line('| 候選 | 對照 | MAE 差與聯合 95% 區間 | MAE 差與聯合 99.1667% 區間 |')
    line('|---|---|---|---|')
    for m in ['chance','conversion','both']:
        for ref in ['Persistence','History']:
            x=r['2025-26-rate']['all']['paired'][m+'Minus'+ref]['MAE']
            line(f"| {NAMES[m]} | {'直接沿用' if ref=='Persistence' else '歷史模型'} | {ci(x)} | {ci(x,'jointBonferroni6')} |")
    line()
    line('負值代表候選誤差較低。六筆主要比較連未校正的 95% 區間都跨 0，不能以點估計挑贏家。')
    line()
    line('## 重現、合併與 OREB%')
    line()
    line('合併採兩個目標季等權，各季內先以分鐘加權。791 筆是球員季觀測，並非 791 個獨立球員；共同球員權重處理跨季重複。')
    line()
    line('| 目標 | 模型 | MAE | RMSE | 對直接沿用的 MAE 差與聯合 95% 區間 |')
    line('|---|---|---:|---:|---|')
    for label in ['2024-25-rate','pooled-rate','2025-26-pct','pooled-pct']:
        for m in ['persistence','history','chance','conversion','both']:
            v=r[label]['all']['versions'][m]
            delta='—' if m=='persistence' else ci(r[label]['all']['paired'][m+'MinusPersistence']['MAE'])
            name='直接沿用前季 OREB%' if label.endswith('-pct') and m=='persistence' else NAMES[m]
            line(f"| {label} | {name} | {v['MAE']:.4f} | {v['RMSE']:.4f} | {delta} |")
    line()
    line('`pct` 的 MAE/RMSE 單位為官方個人 OREB% 的百分點；不能與 OREB/36 混用。'
         '2024–25 只加機會相對歷史模型有未校正 95% 的單點改善（−0.0061，區間 [−0.0115, −0.0007]），'
         '但對直接沿用不顯著、主測試與合併亦不確認，不據此採用。')
    line()
    line('## 換隊與低分鐘：有沒有更能泛化？')
    line()
    line('換隊定義為來源季與目標季的主要球隊不同（最多分鐘球隊）；這不是控制角色、對手與交易選擇後的因果檢定。')
    line()
    line('| 目標／組別 | 人次 | 直接沿用 MAE | ＋機會 MAE | ＋取得率 MAE | ＋兩者 MAE | ＋兩者相對沿用：95% 區間 |')
    line('|---|---:|---:|---:|---:|---:|---|')
    for label in ['2024-25-rate','2025-26-rate','pooled-rate']:
        for g in ['movers','stayers','lowSourceMinutes','both500']:
            z=r[label][g];v=z['versions']
            line(f"| {label}／{g} | {v['persistence']['n']} | {v['persistence']['MAE']:.4f} | {v['chance']['MAE']:.4f} | {v['conversion']['MAE']:.4f} | {v['both']['MAE']:.4f} | {ci(z['paired']['bothMinusPersistence']['MAE'])} |")
    line()
    line('2025–26 換隊 120 人，三種候選 MAE 均略高於沿用前季；差異區間跨 0。'
         '低分鐘組（前季 100–499 分鐘）有較大的點估計改善，但相對直接沿用的區間仍跨 0，不能把事後較好看的分組升格為主要結論。')
    line()
    line('## 機會與取得率各自有多穩定？')
    line()
    line('| 相鄰季 | 組別 | 機會／36 相關（n） | 取得率相關（n） | OREB／36 相關（n） | 官方 OREB% 相關（n） |')
    line('|---|---|---:|---:|---:|---:|')
    for source,target in zip(SEASONS,SEASONS[1:]):
        for g in ['all','movers']:
            z={x['feature']:x for x in s if x['source']==source and x['target']==target and x['group']==g}
            cells=[f"{z[f]['Pearson']:.3f} ({z[f]['n']})" for f in ['chance36','conversion','rate','pct']]
            line(f"| {source}→{target} | {g} | "+' | '.join(cells)+' |')
    line()
    line('這裡的相關是描述性球員間相關，未剔除角色、身材及其跨季延續；不能直接當成個人技能信度。'
         '機會數很穩，但官方 OREB% 本身同樣穩。取得率較不穩定，讓板調整後也沒有變得更穩。')
    line()
    line('## 記帳恆等式與資料品質')
    line()
    line('同一追蹤樣本中，`機會／36 × OREB／機會 = 追蹤 OREB／36`。'
         '全資料最大浮點誤差低於 2×10⁻¹⁵；把同期兩者相乘不能稱作新增資訊。'
         '此次是以前季欄位預測下一季，才有評估額外資訊的意義。機會數是實際追蹤結果，不是出手當下的起始距離；讓板次數也不等於替隊友卡位。')
    line()
    line('| 球季 | 有機會欄位／總球員 | 有機會欄位球員所占 box 分鐘 | 追蹤 MIN／box MIN | 追蹤 OREB／box OREB | 異常數 |')
    line('|---|---:|---:|---:|---:|---:|')
    for x in q:
        line(f"| {x['season']} | {x['coverage']['chance36']['n']}/{x['players']} | {x['coverage']['chance36']['minuteFraction']:.3%} | {x['trackedMinutes']/x['boxMinutes']:.3%} | {x['trackedOreb']}/{x['boxOreb']} | {len(x['issues'])} |")
    line()
    line('有某球員的追蹤彙總列，不等於他的每場、每分鐘均有逐次追蹤。追蹤 MIN 與 box MIN 合計差異仍存在，'
         '本批未辨識其全部原因，不把這個比例當作已證實的逐球覆蓋率，也不混用兩個分母。缺值由歷史訓練資料中位數補入並附缺值旗標。')
    line()
    line('四季沒有重複 ID 或原始取得率的計數／回報比例超容忍值不一致；2025–26 有兩筆調整取得率超過 100%：')
    line()
    line('| 球員 | OREB | 機會 | 讓板 | 原回報調整取得率 | 本批處理 |')
    line('|---|---:|---:|---:|---:|---|')
    for x in q:
        for issue in x['issues']:
            line(f"| {issue['name']} | {issue['OREB']} | {issue['chances']} | {issue['deferred']} | {issue['reportedAdjusted']:.3f} | 調整取得率設缺值，保留原始資料；不影響原始取得率 |")
    line()
    line('這兩筆是目標季欄位，只影響描述性穩定性及資料稽核，不會流入 2025–26 的前季預測特徵。負對照與歷史模型的主表結果完全一致，改善並非由缺值旗標帶來。完整問題清單在 `data-quality.json`。')
    line()
    line('## 推測、失敗與決定')
    line()
    line('- **推測：**機會數可能主要延續了原本 OREB 率已包含的角色與參與程度；取得率的樣本雜訊、球落點與隊友讓板可能限制其增量。此次沒有識別這些因果占比。')
    line('- **失敗：**三個主要候選都未確認能超過兩個歷史對照；沒有確認換隊泛化收益，未能用現有彙總量標定控衛／中鋒的參與倍率。')
    line('- **決定：**維持現有引擎與能力卡。沒有新的引擎 OREB／DREB、net 或勝場改善可報，也沒有測過接入後的副作用。個人率診斷較小的點估計不是採用依據。')
    line('- 若下一批要繼續，最有辨識力的問題是同一球員在不同場上角色與組合下的搶板機會是否改變；需投失事件對齊十人位置／追蹤資料或可驗證替代量。現有季彙總與固定槽位無法回答，不宜憑敘事增加固定參數。本批到此停止。')
    line()
    line('## 重跑與產物')
    line()
    line('保留現有登記，不重跑 `register.py`。以下只寫本批目錄：')
    line()
    line('```powershell')
    line('python reports/defense-tenth/step4-rebounds-components/analyze.py')
    line('python reports/defense-tenth/step4-rebounds-components/report.py')
    line('python reports/defense-tenth/step4-rebounds-components/audit.py')
    line('```')
    line()
    line('資料來源為前一批已下載的 NBA 官方 Rebounding 四季彙總與既有個人 box／advanced 數據，沒有新增下載。'
         '`predictions.json` 保存逐球員預測、`fits.json` 保存欄位與 ridge 選擇、`results.json` 保存所有分組與區間、'
         '`stability.json` 保存三個相鄰季的完整穩定性、`decision.json` 保存登記判準、`completion-audit.json` 保存完整性稽核。')
    (HERE/'report.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    print('Report rendered:',HERE/'report.md')

if __name__=='__main__':main()

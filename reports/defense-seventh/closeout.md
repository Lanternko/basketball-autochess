# 第七批：校準收尾、凍結與跨季盲測

2024–25 跨季盲測未支持 v4 穩定優於 v3 流程：25／41 場切分的淨勝分 RMSE 無顯著改善，55 場切分顯著退步；勝場 MAE 只有25場切分顯著改善。三個切分的淨勝分 RMSE 都顯著輸給簡單對照，勝場 MAE 在25／55場優於簡單對照、41場差異不顯著。v4流程保留凍結，校準收尾未通過，不升為正式基準；正式基準維持 nba-defense-v3。

## 評分口徑與凍結

v4於 2026-10-12T11:17:10.610Z 凍結，當時2024–25資料尚未下載。能力估計、CV、投影、聯盟常數重估與校正規則及程式雜湊見 [凍結規格](v4-freeze.json)。第1項驗收失敗仍保存為「凍結測試流程」，沒有假稱驗收通過或替換v3。盲測後沒有改動凍結的估計、投影、校正或引擎。

重建包裝腳本有一個缺少引號的語法修復；修復發生於2024建模之前，原始／執行雜湊與完整差異見 [執行修復紀錄](v4-execution-fixes.json)。沒有改選擇規則或數值。測試逐一核對凍結雜湊，只允許這筆明列的修復。

日曆v3對照重建舊能力卡與B1，並與v4共用相同的訓練期聯盟常數估計方法；它不是原2025年固定數值的v3 preset。2024–25 bundle沒有載入任何2025–26已估數值檔案；原先凍結的引擎曲線與規則仍共用。因此這是凍結方法的跨季移轉，並非只用2024資料研發出的新引擎。

20個seed均為20261012–20261031。成對95%區間用2000次seed bootstrap，抽到的seed先平均各隊再計算指標；**區間只衡量模擬抽樣誤差，不能視為跨球季一般化信心區間**。30隊等權，SD採母體標準差；全聯盟效率、命中率、球權以合併計數計算。淨勝分RMSE去均值，校準斜率是真實對預測的回歸。勝場按該截止日後各隊實際場數評分，不外推到82場。

各隊前K場的舊口徑與共同日曆口徑分開列。日曆截止為聯盟平均GP首次達K的完整比賽日；日期選擇只用賽程。25／41／55的條件式測試供給未來實際出賽名單／先發，能力、B1、聯盟常數及分鐘／替補優先順序只用訓練資料。球員身份、身體／位置目錄保留全季條件式母體；沒有使用未來個人表現，但這仍不是事前可部署的傷停與名單預測。季前零場另建完整事前假設。

## 1. 四個收尾與全季參考

### 1a. 聯盟平均來源：有修正、未達驗收

已核對：進攻殘差在訓練分鐘座標確實去均值，並非遺漏去均值。邊界截斷帶來正偏差，方向與負效率偏差相反，不能用它解釋低估。原投影與部署的中性化設定不一致已改成一致；使用同一中性化參考重算攻守中心，再只用訓練期全聯盟合併計數校正共同shot-logit與pace。沒有用後半均值校正。

| 各隊前K場 | 殘差去均值前均數 | 截斷投影偏差 | 舊卡訓練→後半曝光均值變化 | 候選卡同項 | 收尾效率偏差 | 球權偏差 |
|---|---:|---:|---:|---:|---:|---:|
| 25 | -0.000035 | 0.151 | -0.467 | -1.954 | -1.943 | 1.665 |
| 41 | 0.000469 | 0.052 | -0.618 | -1.873 | -2.739 | 1.529 |
| 55 | 0.000417 | 0.058 | -0.469 | -1.674 | -3.549 | 1.502 |

41場切分候選卡曝光加權進攻均值下降1.873，舊卡只下降0.618；支持「卡的曝光／角色組成移轉」是來源之一。這個反查使用真實後半分鐘只作診斷，未進入訓練或校正。單一卡EV、實際出手選擇與非線性場上反應口徑不同，上表不是每百回合效率的精確因果拆分；尚無證據能把全部剩餘偏差分配給某一機制。

訓練校正常數移到後半仍失準，三個切分都沒有達到 |效率偏差|<0.5。改善隊間淨勝分不能掩蓋這項失敗。原來源診斷與近似FG權重的限制見 [診斷JSON](projection-source-diagnosis.json)。

### 1b. 時間順向CV與原隨機分組並列

| 切分 | plain λ 隨機／順向 | role λ 隨機／順向 | role係數最大差 | 收尾校準斜率 | 第六批斜率 |
|---|---:|---:|---:|---:|---:|
| 25 | 100 / 300 | 300 / 300 | 0.000000 | 0.661 | 0.683 |
| 41 | 300 / 300 | 300 / 300 | 0.000000 | 0.856 | 0.864 |
| 55 | 300 / 300 | 300 / 300 | 0.000000 | 0.880 | 0.881 |

順向三折：前50%日期訓練預測其後1/6，前2/3預測其後1/6，前5/6預測最後1/6；每折重建box／角色先驗。以訓練期的Poisson負對數似然選ridge，無截止日後選擇，無事後乘分散係數。role模型三個切分都選300，與原版的攻守四組係數完全一致。25場plain模型從100改300，role-minus-plain的防守投影因此也可能改變；其餘plain亦一致。**這次CV改法沒有產生普遍較強的收縮，也沒有讓校準斜率全面更接近1。** [完整係數核對](ridge-comparison.json)。

| 舊各隊前K場收尾 | RMSE | 相關 | SD比 | 校準斜率 | 勝場MAE | 勝場RMSE | ΔRMSE對第六批 [95%] | ΔMAE對第六批 [95%] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 4.662 | 0.790 | 1.196 | 0.661 | 4.152 | 5.284 | 0.204 [-0.055, 0.464] | 0.005 [-0.307, 0.287] |
| 41 | 3.720 | 0.876 | 1.024 | 0.856 | 3.023 | 3.728 | 0.161 [-0.054, 0.351] | -0.005 [-0.262, 0.280] |
| 55 | 4.076 | 0.881 | 1.001 | 0.880 | 2.380 | 2.784 | -0.019 [-0.385, 0.317] | 0.172 [-0.045, 0.337] |

三個切分主指標未顯著退步，但均值與斜率條件未過，故第1項整體驗收失敗。舊收尾批次未收集單場殘差SD，原計分助手缺值會產生0；這份報告不把它當成真實0。後面的日曆批次已直接從正規四節比分收集殘差SD。

### 1c. 防守proxy斜率與防守殘差

舊加總proxy斜率 **1.764** 重現。補入觀測訓練期籃板／失誤／罰球的Shapley反查後為 **1.264**：OREB降低斜率差距0.081，TOV 0.363，FTA 0.055，合計解釋對1的差距約65.4%。這是「已知訓練結果可補回多少」的資訊上限診斷，沒有把它當作球員輸入。其餘34.6%混有卡壓縮、賽程、模型與代理口徑誤差，不能全稱為卡真的被壓縮。

防守殘差接入測試比照進攻，將完整joint allowed效果反投影至現有禁區FG壓制，可獨立關閉。41場RMSE 4.267，對第六批差 0.708 [0.458, 0.923]；勝場MAE 3.315，差 0.287 [0.050, 0.562]，兩者顯著退步，**關閉**。

可能原因是完整失分殘差含籃板／失誤／送罰球，B1已各自建模，再全部轉成投籃壓制可能重複算入；這是有支持的推測，未完成因果定位。保留既有B1訊號與角色防守差異，不部署full defense residual。[proxy拆解](proxy-decomposition.json)。

### 1d. 球員誤差、邊界與多屬性方案

以下先列原第六批v4-candidate與凍結v3、相同各隊前K場條件。每項是「MAE / RMSE / bias」，以後半實際分鐘加權；得分／出手／助攻／籃板為每個實際出賽場平均，FG與3P是百分點。交易前後依playerID加總；零出手比例另排除，不當作0%。

| 切分／卡 | 得分 | 出手 | FG | 3P | 助攻 | 籃板 |
|---|---:|---:|---:|---:|---:|---:|
| 25 / v3 | 2.611 / 3.415 / -0.209 | 1.983 / 2.571 / -0.252 | 3.659 / 5.015 / -0.560 | 5.751 / 9.873 / 1.105 | 1.003 / 1.456 / -0.572 | 0.897 / 1.194 / -0.095 |
| 25 / candidate | 3.420 / 4.430 / 0.059 | 2.325 / 3.025 / -0.087 | 5.355 / 7.159 / -2.063 | 7.119 / 10.994 / -0.488 | 1.049 / 1.526 / -0.586 | 0.910 / 1.228 / -0.085 |
| 41 / v3 | 2.716 / 3.467 / -0.296 | 1.973 / 2.597 / -0.209 | 3.901 / 5.198 / -0.952 | 5.994 / 10.275 / 0.834 | 0.989 / 1.417 / -0.562 | 0.928 / 1.222 / -0.084 |
| 41 / candidate | 3.185 / 4.008 / -0.103 | 2.222 / 2.846 / -0.055 | 5.204 / 7.055 / -2.460 | 6.986 / 10.673 / -0.298 | 1.021 / 1.479 / -0.587 | 0.945 / 1.249 / -0.043 |
| 55 / v3 | 2.882 / 3.613 / -0.469 | 2.130 / 2.751 / -0.301 | 4.225 / 5.627 / -1.073 | 6.692 / 11.038 / 1.337 | 1.039 / 1.482 / -0.596 | 0.993 / 1.321 / -0.113 |
| 55 / candidate | 3.248 / 3.995 / -0.299 | 2.342 / 2.917 / -0.154 | 5.146 / 6.965 / -2.354 | 7.179 / 11.238 / 0.216 | 1.047 / 1.509 / -0.605 | 0.998 / 1.333 / -0.057 |

各指標個人資料明顯變差，尤其FG：41場MAE由3.901增至5.204。原候選至少一項攻擊屬性撞0／120的球員數25／41／55為107／69／60；訓練分鐘占15.29%／8.45%／6.75%。原完整名單見 [原候選球員診斷](initial-diagnosis.json)。

另以單一日曆與實際部署校正後卡重算（新舊雙方都用訓練MPG）：

| 日曆切分／卡 | 得分 | 出手 | FG | 3P | 助攻 | 籃板 | 0／120邊界人數 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 25 / v3 | 2.659 / 3.462 / -0.177 | 2.002 / 2.580 / -0.135 | 3.674 / 5.015 / -0.893 | 5.871 / 10.055 / -0.506 | 0.972 / 1.420 / -0.500 | 0.904 / 1.208 / -0.017 | 0 |
| 25 / v4 | 3.343 / 4.305 / -0.055 | 2.346 / 3.020 / 0.016 | 5.145 / 7.090 / -2.769 | 6.932 / 10.663 / -1.968 | 1.001 / 1.458 / -0.503 | 0.927 / 1.254 / 0.047 | 142 |
| 41 / v3 | 2.757 / 3.511 / -0.318 | 1.983 / 2.603 / -0.090 | 3.994 / 5.314 / -1.381 | 6.190 / 9.769 / -0.857 | 0.978 / 1.392 / -0.493 | 0.951 / 1.244 / -0.008 | 0 |
| 41 / v4 | 3.187 / 4.003 / -0.212 | 2.219 / 2.873 / 0.047 | 5.190 / 6.998 / -3.059 | 6.929 / 10.465 / -1.774 | 0.993 / 1.432 / -0.508 | 0.964 / 1.278 / 0.064 | 72 |
| 55 / v3 | 2.916 / 3.673 / -0.520 | 2.105 / 2.728 / -0.199 | 4.302 / 5.728 / -1.441 | 6.512 / 10.482 / -0.603 | 1.025 / 1.460 / -0.534 | 0.980 / 1.311 / -0.042 | 0 |
| 55 / v4 | 3.187 / 3.925 / -0.437 | 2.324 / 2.903 / -0.075 | 5.326 / 7.270 / -3.177 | 7.102 / 10.727 / -1.681 | 1.033 / 1.486 / -0.548 | 1.003 / 1.341 / 0.051 | 65 |

測試多屬性投影：把同一個進攻logit位移沿現有局部EV梯度分到 pass／tovSkill／offBall／screen／drive，加上三項投籃；這是最小變化的替代映射，不是假稱單一得分殘差能辨識六種技能。41場FG MAE 5.261，仍高於原候選 5.204；RMSE 3.616，對第六批 0.057 [-0.164, 0.252]，勝場MAE 3.083，差 0.055 [-0.220, 0.342]。沒有可靠修好個人命中率，**不採用**。

### 1e. 全季參考（僅回測）

候選參考使用整季建卡、中性化一致投影、順向CV；此參考沒有新日曆流程的訓練聯盟校正。能力與逐場條件來自整季，不能拿來證明預測準確度。

| 全季參考 | RMSE | 相關 | SD比 | 校準斜率 | 殘差SD | 勝場MAE | 勝場RMSE | 每分換勝 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 | 3.547 | 0.821 | 0.722 | 1.137 | 17.377 | 6.813 | 8.149 | 1.793 |
| v3 | 2.555 | 0.911 | 0.838 | 1.087 | 16.935 | 5.070 | 6.197 | 1.821 |
| candidate | 1.846 | 0.961 | 1.080 | 0.890 | — | 4.093 | 5.179 | 1.693 |

候選−v3：淨勝分RMSE -0.709 [-0.883, -0.509]；勝場MAE -0.977 [-1.343, -0.517]。候選的單場殘差SD未收集，明列缺值。完整同第五批格式的隊表、全聯盟計數與成對區間見 [全季參考JSON](full-comparison.json)。

## 2–3. 凍結後的兩季共同日曆測試

### 2024-25：未參與選擇的跨季盲測

| K／截止日 | 版本 | RMSE | 相關 | 校準斜率 | SD比 | 勝場MAE | 勝場RMSE |
|---|---|---:|---:|---:|---:|---:|---:|
| 25 / 2024-12-14 | v3 | 5.335 | 0.587 | 0.637 | 0.922 | 6.053 | 7.834 |
| 25 / 2024-12-14 | v4 | 5.301 | 0.710 | 0.581 | 1.221 | 5.657 | 7.066 |
| 25 / 2024-12-14 | simple | 4.716 | 0.733 | 0.665 | 1.102 | 6.130 | 7.640 |
| 41 / 2025-01-18 | v3 | 5.503 | 0.633 | 0.679 | 0.932 | 4.473 | 5.634 |
| 41 / 2025-01-18 | v4 | 5.554 | 0.684 | 0.624 | 1.096 | 4.297 | 5.394 |
| 41 / 2025-01-18 | simple | 4.873 | 0.709 | 0.774 | 0.917 | 4.341 | 5.258 |
| 55 / 2025-02-21 | v3 | 5.875 | 0.620 | 0.853 | 0.727 | 2.960 | 3.759 |
| 55 / 2025-02-21 | v4 | 6.310 | 0.652 | 0.629 | 1.037 | 2.997 | 3.757 |
| 55 / 2025-02-21 | simple | 5.499 | 0.681 | 0.860 | 0.792 | 3.281 | 3.758 |

| K | 訓練GP範圍 | v4−v3 ΔRMSE [95%] | Δ勝場MAE [95%] | v4−簡單 ΔRMSE [95%] | Δ勝場MAE [95%] |
|---|---:|---:|---:|---:|---:|
| 25 | 23–27 | -0.034 [-0.320, 0.251] | -0.397 [-0.620, -0.190] | 0.585 [0.395, 0.814] | -0.474 [-0.690, -0.237] |
| 41 | 38–43 | 0.051 [-0.191, 0.292] | -0.177 [-0.447, 0.113] | 0.681 [0.553, 0.865] | -0.044 [-0.227, 0.199] |
| 55 | 54–58 | 0.435 [0.077, 0.775] | 0.037 [-0.187, 0.277] | 0.811 [0.571, 1.138] | -0.284 [-0.458, -0.051] |

| K | v3／v4 效率偏差 | v3／v4 球權偏差 | v4 FG偏差(百分點) | v3／v4 單場殘差SD |
|---|---:|---:|---:|---:|
| 25 | -2.097 / -3.524 | 0.965 / 1.202 | -2.012 | 16.871 / 17.549 |
| 41 | -2.721 / -3.774 | 1.029 / 1.293 | -1.936 | 16.860 / 17.448 |
| 55 | -2.584 / -3.895 | 1.151 / 1.369 | -1.968 | 16.563 / 17.175 |

### 2025-26：曾參與研發的資料外補跑

| K／截止日 | 版本 | RMSE | 相關 | 校準斜率 | SD比 | 勝場MAE | 勝場RMSE |
|---|---|---:|---:|---:|---:|---:|---:|
| 25 / 2025-12-14 | v3 | 5.555 | 0.538 | 0.701 | 0.768 | 6.527 | 7.722 |
| 25 / 2025-12-14 | v4 | 4.386 | 0.805 | 0.696 | 1.156 | 4.363 | 5.304 |
| 25 / 2025-12-14 | simple | 4.725 | 0.744 | 0.696 | 1.070 | 5.649 | 6.987 |
| 41 / 2026-01-16 | v3 | 5.669 | 0.650 | 0.983 | 0.661 | 5.273 | 6.153 |
| 41 / 2026-01-16 | v4 | 3.765 | 0.873 | 0.869 | 1.005 | 3.330 | 4.053 |
| 41 / 2026-01-16 | simple | 4.777 | 0.769 | 1.047 | 0.734 | 4.062 | 5.048 |
| 55 / 2026-02-19 | v3 | 5.943 | 0.694 | 0.990 | 0.701 | 3.503 | 4.064 |
| 55 / 2026-02-19 | v4 | 4.540 | 0.847 | 0.859 | 0.985 | 2.497 | 2.889 |
| 55 / 2026-02-19 | simple | 5.101 | 0.797 | 1.192 | 0.669 | 2.993 | 3.602 |

| K | 訓練GP範圍 | v4−v3 ΔRMSE [95%] | Δ勝場MAE [95%] | v4−簡單 ΔRMSE [95%] | Δ勝場MAE [95%] |
|---|---:|---:|---:|---:|---:|
| 25 | 22–27 | -1.169 [-1.441, -0.896] | -2.163 [-2.623, -1.710] | -0.339 [-0.465, -0.165] | -1.285 [-1.515, -1.022] |
| 41 | 39–44 | -1.903 [-2.113, -1.671] | -1.943 [-2.273, -1.633] | -1.012 [-1.145, -0.780] | -0.732 [-0.909, -0.466] |
| 55 | 53–57 | -1.403 [-1.702, -1.086] | -1.007 [-1.183, -0.833] | -0.561 [-0.680, -0.317] | -0.497 [-0.600, -0.377] |

| K | v3／v4 效率偏差 | v3／v4 球權偏差 | v4 FG偏差(百分點) | v3／v4 單場殘差SD |
|---|---:|---:|---:|---:|
| 25 | -0.488 / -2.041 | 1.979 / 2.032 | -0.903 | 17.213 / 18.339 |
| 41 | -1.345 / -2.812 | 1.743 / 1.964 | -1.357 | 16.799 / 17.417 |
| 55 | -2.075 / -3.746 | 1.363 / 1.758 | -1.795 | 16.667 / 17.010 |

2025–26 三個日曆切分的v4兩項主誤差均顯著低於共同常數v3對照與簡單對照，表示第六批同季效果不是各隊前K場口徑才有。然而2024–25完全沒有重現相同模式：不能以2025–26補跑取代第一個盲測的失敗。全聯盟均值偏差也仍未通過；日曆v4過度分散在2024–25更突出，校準斜率只有0.581／0.624／0.629。

簡單對照：截止日前真實場均淨勝分直接預測後段；勝場用截止日前得失分比與訓練隊戰績估出的單一Pythagorean指數乘後段場數。沒有按後段表現選收縮或指數。它是評分對照，不是模擬器球隊ID補丁。合成計數只承載淨勝分與勝場，沒有真實的防守／殘差SD或box預測，因此那些欄位已標示缺值。

### 2024–25 重建稽核

官方基本數據：2460隊場、26306球員場、1230份box；1229場PBP，缺／不符場次0022400072。能通過五人與分鐘驗證 1104 場，嚴格可用 1091 / 1230 場。125場陣容重建失敗，11場計數不符，逐項名單與差異保留，不用手改分鐘強行補過。分鐘檢查38950筆，平均絕對差約0.06185秒，最大1.080秒，門檻1.1秒。

完整 [資料manifest](../../data/defense-seventh/2024-25/manifest.json)、[嚴格樣本與失敗清單](2024-25/stints/defensive-samples.json)、[逐球員分鐘核對](2024-25/stints/minute-checks.jsonl)。2024–25嚴格覆蓋較2025–26的1188場低；可能有選樣偏差，未量化其對結果的因果影響。

隔離測試把2025數值preset清空，只供給2024bundle／卡／校正，兩場比分和每隊／球員計數與正常路徑完全一致。[隔離稽核](season-isolation-test.json)。

## 4. 前一季先驗（盲測完成後的獨立實驗）

2024–25完整嚴格資料重新估球員joint能力，再以playerID帶到2025–26。只在joint能力先驗加上一季效果；B1九項防守模型維持本季方法。200估計回合偽樣本預先固定，本季權重n/(n+200)，n=MIN/48×100；每折重建本季box／位置／MPG角色先驗，舊值在本折訓練曝光去均值；未知球員沿本季角色先驗。仍用順向三折選當季殘差ridge，校正只用本季訓練資料。沒有依後段效果選先驗強度或回頭改凍結v4。

| 日曆切分 | v4 RMSE | 上季先驗 RMSE | 先驗相關 | 校準斜率 | v4勝場MAE | 先驗勝場MAE | 先驗勝場RMSE | ΔRMSE [95%] | ΔMAE [95%] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 4.386 | 4.499 | 0.772 | 0.713 | 4.363 | 4.757 | 5.659 | 0.113 [-0.121, 0.364] | 0.393 [0.030, 0.740] |
| 41 | 3.765 | 4.015 | 0.851 | 0.881 | 3.330 | 3.367 | 4.240 | 0.250 [-0.030, 0.529] | 0.037 [-0.280, 0.360] |
| 55 | 4.540 | 4.570 | 0.838 | 0.899 | 2.497 | 2.567 | 3.067 | 0.030 [-0.284, 0.315] | 0.070 [-0.117, 0.283] |

25場勝場MAE顯著退步；41／55兩項沒有顯著改善，**先驗不採用、不併入v4**。55場role λ由當季驗證選1000，其餘role300；不是依後半選出。這次是200偽回合與joint能力的單一明列方案，不能推論所有前季資料方法都無用。

### 真正季前零場：另建名單與輪替

遵照使用者選擇，**沒有給逐場未來出賽名單、先發、實際分鐘、交易或實際Cup配對**。開季名單用2025-10-20 NBA發布PDF，30隊522人，436人有2024–25 NBA卡、86人用同位置MPG<10替補卡與B1效果均值；後者包括新秀及無上一季NBA樣本的回歸球員。能力、打法、個人事件率與聯盟常數全部來自2024–25，未用本季校正。身體／位置身份欄位另有白名單，沒有複製本季observed數據。

新秀假設12分鐘，two-way權重最多5分鐘。出賽由前一季GP、同MPG角色GP平均與20場收縮的Bernoulli抽樣；開季PDF列為非two-way inactive者先缺14場，之後回到該先驗。每場最多12人，至少8人，排序用前一季MPG，先發按位置距離與MPG決定，現有軟分鐘目標按240正規化。滿足最少8人而補入的抽樣未出賽者明列各seed fallbackSelections。這是輪替／傷停模型假設，未拿本季結果調整。

Haliburton與Sorber整季缺席是季前已確認資訊；Tatum、Lillard、VanVleet整季缺席是**保守情境**，當時並非全部已有確切整季回歸结論。沒有把後來的回歸日期填回去。各球員參數與來源見 [季前規則](prior/preseason-0/rules.json)、[522人能力與輪替覆蓋](prior/preseason-0/coverage.json)。

賽程直接由2025-08-14的官方PDF讀1200個已知配對；各隊剩兩場NBA Cup未定賽程由名字排序的固定循環配對補30場，日期12/11與12/15，各隊合計82場。不使用後來的Cup晉級、臨時配對或延期日。這是未定賽程的明列近似，未模擬Cup晉級機制。

[NBA開季名單公告](https://www.nba.com/news/nba-rosters-set-for-2025-26-regular-season)／[原發布PDF鏡像](https://bloximages.chicago2.vip.townnews.com/tucson.com/content/tncms/assets/v3/editorial/4/ff/4ff8d6d8-1df5-4f17-aadb-dacba08d7860/68f6d1c879bf0.pdf.pdf)；[NBA事前賽程公告](https://pr.nba.com/2025-26-nba-regular-season-schedule/)與[2025-08-14賽程PDF](https://pr.nba.com/wp-content/uploads/sites/46/2025/08/2025-26-NBA-Regular-Season-Schedule-By-Date-8-14-25.pdf)。公布日與原始檔雜湊保存在data/defense-seventh/preseason-2025-26。

| 真正季前全季預測 | RMSE | 相關 | 校準斜率 | SD比 | 勝場MAE | 勝場RMSE |
|---|---:|---:|---:|---:|---:|---:|
| 上季球員卡＋名單／輪替假設 | 7.026 | 0.525 | 0.405 | 1.297 | 11.213 | 12.854 |
| 上季球隊淨勝分＋Pythagorean簡單對照 | 5.864 | 0.524 | 0.543 | 0.964 | 10.347 | 13.141 |

季前RMSE95%區間 [6.897, 7.173]，勝場MAE [10.923, 11.533]。相對上季球隊簡單對照，ΔRMSE 1.162 [1.027, 1.308]，ΔMAE 0.866 [0.573, 1.203]。是較弱的預測；不能拿它跟已知逐場名單的日曆條件式測試當作純能力卡A/B。區間包含seed下的缺陣與比賽抽樣，沒有涵蓋輪替、傷停情境、交易或新秀能力假設的模型不確定性。

## 重跑與凍結稽核

已存在的freeze不能重新產生或覆寫來假裝盲測之前凍結；第一份凍結JSON與修復紀錄請保留。campaign會重用已有輸出；需要真正重跑評分seed用rerun腳本。

```powershell
node scripts/campaign_defense_seventh_calendar.js 2025-26
node scripts/fetch_defense_seventh_season.js
node scripts/prepare_defense_seventh_season.js
node scripts/campaign_defense_seventh_calendar.js 2024-25
node scripts/assess_defense_seventh_calendar.js 2025-26
node scripts/assess_defense_seventh_calendar.js 2024-25
node scripts/rerun_defense_seventh.js 2024-25-calendar-41-v4

# 完成盲測後才允許建立前季先驗
node scripts/prepare_defense_seventh_calendar.js 2024-25 82
node scripts/fetch_defense_seventh_tracking.js reports/defense-seventh/2024-25/calendar-82/config.json
python scripts/estimate_defense_seventh_prior_full_factors.py reports/defense-seventh/2024-25/calendar-82/config.json random
node scripts/build_defense_seventh_base.js reports/defense-seventh/2024-25/calendar-82/config.json
node scripts/build_defense_seventh_bundle.js reports/defense-seventh/2024-25/calendar-82/config.json
$env:DEFENSE_SEVENTH_CONFIG='reports/defense-seventh/2024-25/calendar-82/config.json'
python scripts/estimate_defense_seventh.py 82 forward
Remove-Item Env:DEFENSE_SEVENTH_CONFIG
node scripts/build_defense_seventh_cards.js 82 '{"label":"v4","configFile":"reports/defense-seventh/2024-25/calendar-82/config.json"}'
node scripts/calibrate_defense_seventh_bundle.js reports/defense-seventh/2024-25/calendar-82/config.json v4
node scripts/campaign_defense_seventh_prior.js

# PDF讀取使用附pdfplumber的bundled Python；原PDF與hash在data目錄
python scripts/prepare_defense_seventh_opening_rosters.py
python scripts/prepare_defense_seventh_opening_schedule.py
node scripts/prepare_defense_seventh_preseason.js
node scripts/run_defense_seventh_preseason.js
node scripts/assess_defense_seventh_prior.js
node scripts/assess_defense_seventh_preseason_uncertainty.js
node scripts/diagnose_defense_seventh_calendar_players.js
node scripts/assess_defense_seventh_full.js
node scripts/report_defense_seventh.js
node test/defense_seventh.js
node test/defense_seventh_season_isolation.js
node test/defense_seventh_artifacts.js
```

全部單一日曆與先驗20seed已完成；逐場比分、球員／隊計數、輸入卡與校正常數、來源雜湊、所有指標的成對區間均在對應*-seeds.json與*-assessment.json。freeze規格列出所有超參數、上下界、CV/停止/選擇規則。使用同一已快取輸入可離線重跑seed；原資料重抓可能遇到API修訂或不可用，應保留原始來源與雜湊。

## 限制與仍未證實事項

- 校準收尾沒有過關；跨季能力效果未穩定重現。沒有以聯盟後段常數或球隊ID／真實勝場修補。
- forward CV改善了時間資訊隔離，卻沒替role模型選出更強收縮；係數先驗ridge3仍固定。
- 防守proxy未涵蓋因素解釋65.4%是觀測反查，非卡真實壓縮的因果比例；轉FG的防守殘差重複算入也尚是推測。
- 一個得分殘差轉成投籃值有識別限制與邊界問題；多屬性替代測試沒有修好個人數據，不能從整隊RMSE推論球員OVR已準。
- 2024嚴格區段覆蓋較低，排除場次的選樣影響未量化。
- 日曆v3對照共用新的訓練聯盟常數估計器，是能力流程對照，不是跨季搬用原2025數值preset。
- 25／41／55仍是已知未來實際名單與先發的條件式測試；零場才是完整事前名單／輪替預測，但其傷停與Cup賽程假設很粗。
- 所有顯著性為seed誤差；沒有跨季多樣本、訓練重抽或傷停模型信心區間。2024是第一個未參與選擇的球季，也只有一季。
- 前季先驗只測了200偽回合與joint能力offset方案，沒有搜尋其他先驗強度或把前季資料接進B1，不外推到所有前季方法。
- 原版／v1／v2／v3能力卡與引擎保留；v4與prior輸出全部在獨立版本目錄，沒有部署升級。

## 附錄：所有成對指標區間

### 2024-25

| K | 指標 | v4−v3 [95%] | v4−簡單 [95%] |
|---|---|---:|---:|
| 25 | netRMSE | -0.034 [-0.320, 0.251] | 0.585 [0.395, 0.814] |
| 25 | netCorrelation | 0.123 [0.093, 0.155] | -0.023 [-0.045, -0.003] |
| 25 | netSDRatio | 0.300 [0.256, 0.343] | 0.119 [0.099, 0.146] |
| 25 | calibrationSlope | -0.056 [-0.100, -0.012] | -0.084 [-0.108, -0.064] |
| 25 | calibrationError | 0.056 [0.012, 0.100] | 0.084 [0.064, 0.108] |
| 25 | winMAE | -0.397 [-0.620, -0.190] | -0.474 [-0.690, -0.237] |
| 25 | winRMSE | -0.768 [-1.042, -0.458] | -0.573 [-0.759, -0.307] |
| 25 | winSlope | -0.119 [-0.165, -0.070] | -0.325 [-0.350, -0.297] |
| 25 | residualSD | 0.678 [0.411, 0.934] | — |
| 25 | defenseCorrelation | 0.005 [-0.066, 0.074] | — |
| 25 | defenseSDRatio | -0.022 [-0.070, 0.032] | — |
| 41 | netRMSE | 0.051 [-0.191, 0.292] | 0.681 [0.553, 0.865] |
| 41 | netCorrelation | 0.051 [0.028, 0.078] | -0.025 [-0.042, -0.011] |
| 41 | netSDRatio | 0.164 [0.118, 0.206] | 0.179 [0.155, 0.210] |
| 41 | calibrationSlope | -0.055 [-0.093, -0.013] | -0.149 [-0.172, -0.132] |
| 41 | calibrationError | 0.055 [0.013, 0.094] | 0.149 [0.132, 0.172] |
| 41 | winMAE | -0.177 [-0.447, 0.113] | -0.044 [-0.227, 0.199] |
| 41 | winRMSE | -0.240 [-0.516, 0.037] | 0.136 [-0.022, 0.388] |
| 41 | winSlope | -0.043 [-0.080, -0.009] | -0.241 [-0.261, -0.220] |
| 41 | residualSD | 0.588 [0.313, 0.859] | — |
| 41 | defenseCorrelation | 0.026 [-0.044, 0.094] | — |
| 41 | defenseSDRatio | -0.052 [-0.098, 0.000] | — |
| 55 | netRMSE | 0.435 [0.077, 0.775] | 0.811 [0.571, 1.138] |
| 55 | netCorrelation | 0.032 [-0.007, 0.077] | -0.028 [-0.052, -0.010] |
| 55 | netSDRatio | 0.310 [0.263, 0.352] | 0.246 [0.205, 0.298] |
| 55 | calibrationSlope | -0.224 [-0.273, -0.156] | -0.231 [-0.273, -0.197] |
| 55 | calibrationError | 0.224 [0.157, 0.274] | 0.231 [0.197, 0.273] |
| 55 | winMAE | 0.037 [-0.187, 0.277] | -0.284 [-0.458, -0.051] |
| 55 | winRMSE | -0.002 [-0.238, 0.237] | -0.001 [-0.146, 0.197] |
| 55 | winSlope | -0.057 [-0.079, -0.036] | -0.172 [-0.185, -0.157] |
| 55 | residualSD | 0.611 [0.265, 0.962] | — |
| 55 | defenseCorrelation | 0.040 [-0.037, 0.111] | — |
| 55 | defenseSDRatio | 0.052 [0.003, 0.097] | — |

### 2025-26

| K | 指標 | v4−v3 [95%] | v4−簡單 [95%] |
|---|---|---:|---:|
| 25 | netRMSE | -1.169 [-1.441, -0.896] | -0.339 [-0.465, -0.165] |
| 25 | netCorrelation | 0.266 [0.233, 0.303] | 0.060 [0.045, 0.072] |
| 25 | netSDRatio | 0.388 [0.346, 0.426] | 0.086 [0.065, 0.111] |
| 25 | calibrationSlope | -0.005 [-0.061, 0.055] | 0.001 [-0.019, 0.014] |
| 25 | calibrationError | 0.005 [-0.055, 0.061] | -0.001 [-0.014, 0.019] |
| 25 | winMAE | -2.163 [-2.623, -1.710] | -1.285 [-1.515, -1.022] |
| 25 | winRMSE | -2.418 [-2.892, -1.925] | -1.683 [-1.880, -1.399] |
| 25 | winSlope | -0.122 [-0.175, -0.064] | -0.469 [-0.496, -0.443] |
| 25 | residualSD | 1.126 [0.908, 1.356] | — |
| 25 | defenseCorrelation | 0.012 [-0.035, 0.061] | — |
| 25 | defenseSDRatio | 0.004 [-0.044, 0.053] | — |
| 41 | netRMSE | -1.903 [-2.113, -1.671] | -1.012 [-1.145, -0.780] |
| 41 | netCorrelation | 0.223 [0.198, 0.256] | 0.104 [0.090, 0.113] |
| 41 | netSDRatio | 0.344 [0.301, 0.384] | 0.271 [0.244, 0.307] |
| 41 | calibrationSlope | -0.114 [-0.156, -0.051] | -0.178 [-0.213, -0.153] |
| 41 | calibrationError | 0.114 [0.051, 0.146] | 0.084 [0.058, 0.118] |
| 41 | winMAE | -1.943 [-2.273, -1.633] | -0.732 [-0.909, -0.466] |
| 41 | winRMSE | -2.100 [-2.412, -1.785] | -0.995 [-1.148, -0.751] |
| 41 | winSlope | -0.075 [-0.111, -0.036] | -0.291 [-0.309, -0.273] |
| 41 | residualSD | 0.618 [0.297, 0.903] | — |
| 41 | defenseCorrelation | 0.066 [0.007, 0.121] | — |
| 41 | defenseSDRatio | -0.012 [-0.051, 0.026] | — |
| 55 | netRMSE | -1.403 [-1.702, -1.086] | -0.561 [-0.680, -0.317] |
| 55 | netCorrelation | 0.153 [0.118, 0.191] | 0.050 [0.034, 0.059] |
| 55 | netSDRatio | 0.284 [0.248, 0.319] | 0.317 [0.297, 0.346] |
| 55 | calibrationSlope | -0.130 [-0.195, -0.059] | -0.332 [-0.360, -0.315] |
| 55 | calibrationError | 0.130 [0.059, 0.153] | -0.051 [-0.068, -0.023] |
| 55 | winMAE | -1.007 [-1.183, -0.833] | -0.497 [-0.600, -0.377] |
| 55 | winRMSE | -1.175 [-1.397, -0.920] | -0.713 [-0.807, -0.524] |
| 55 | winSlope | -0.064 [-0.093, -0.038] | -0.174 [-0.193, -0.157] |
| 55 | residualSD | 0.343 [-0.103, 0.809] | — |
| 55 | defenseCorrelation | 0.048 [-0.033, 0.140] | — |
| 55 | defenseSDRatio | 0.002 [-0.054, 0.063] | — |

## 附錄：日曆v4的0／120邊界完整名單

以下每人只列碰邊界的屬性。原第六批候選名單另見initial-diagnosis.json，不混用投影前與校正後計數。

### 25場切分：142人

| 球員 | ID | 邊界屬性 |
|---|---:|---|
| Christian Koloko | 1631132 | long=0, mid=0, short=0 |
| RayJ Dennis | 1642484 | short=0 |
| Keshon Gilbert | 1642933 | short=0 |
| Jacob Toppin | 1631210 | long=0, short=0 |
| N'Faly Dante | 1642368 | short=0 |
| Amari Williams | 1642873 | long=0, mid=0, short=0 |
| John Tonje | 1642910 | short=0 |
| Max Shulga | 1642917 | short=0 |
| Darius Garland | 1629636 | short=0 |
| Thomas Bryant | 1628418 | long=0, short=0 |
| Lonzo Ball | 1628366 | long=0, mid=0, short=0 |
| Larry Nance Jr. | 1626204 | short=0 |
| Max Strus | 1629622 | short=0 |
| Luke Travers | 1631247 | long=0, mid=0, short=0 |
| Olivier Sarr | 1630846 | long=0, short=0 |
| Herbert Jones | 1630529 | short=0 |
| Josh Oduro | 1642490 | long=0, short=0 |
| Patrick Williams | 1630172 | short=0 |
| Rob Dillingham | 1642265 | long=0, short=0 |
| Guerschon Yabusele | 1627824 | long=0 |
| Leonard Miller | 1631159 | long=0, mid=0, short=0 |
| Nick Richards | 1630208 | long=0, mid=0, short=0 |
| Lachlan Olbrich | 1642950 | long=0, mid=0, short=0 |
| Mouhamadou Gueye | 1631338 | long=0, short=0 |
| Emanuel Miller | 1641801 | long=0, short=0 |
| Caleb Martin | 1628997 | long=0, mid=0, short=0 |
| John Poulakidas | 1642967 | short=0 |
| AJ Johnson | 1642358 | long=0, mid=0, short=0 |
| Tyler Smith | 1641890 | long=0, short=0 |
| Miles Kelly | 1642939 | long=0, short=0 |
| Tyus Jones | 1626145 | long=0, short=0 |
| Bruce Brown | 1628971 | long=0, short=0 |
| Julian Strawther | 1631124 | long=0, mid=0, short=0 |
| Jalen Pickett | 1629618 | long=0, short=0 |
| Zeke Nnaji | 1630192 | long=0, mid=0, short=0 |
| Hunter Tyson | 1641816 | long=0, short=0 |
| David Roddy | 1631223 | long=0, short=0 |
| KJ Simpson | 1642354 | long=0, short=0 |
| Draymond Green | 203110 | long=0, mid=0, short=0 |
| Gui Santos | 1630611 | long=0, mid=0, short=0 |
| Al Horford | 201143 | short=0 |
| Malevy Leons | 1642502 | long=0, short=0 |
| Nate Williams | 1631466 | short=0 |
| Jae'Sean Tate | 1630256 | short=0 |
| JD Davison | 1631120 | long=0, short=0 |
| Isaiah Crawford | 1642384 | long=0, short=0 |
| Tristen Newton | 1641803 | short=0 |
| Chris Paul | 101108 | short=0 |
| Jahmyl Telfort | 1643141 | long=0, mid=0, short=0 |
| Bronny James | 1642355 | long=0, mid=0, short=0 |
| Kobe Bufkin | 1641723 | short=0 |
| Chris Mañon | 1643024 | long=0, mid=0, short=0 |
| Nikola Jović | 1631107 | long=0, mid=0, short=0 |
| Gary Harris | 203914 | long=0, short=0 |
| Andre Jackson Jr. | 1641748 | long=0, mid=0, short=0 |
| Cormac Ryan | 1642504 | short=0 |
| Amir Coffey | 1629599 | long=0, mid=0, short=0 |
| Terrence Shannon Jr | 1630545 | short=0 |
| Joe Ingles | 204060 | long=0, mid=0, short=0 |
| Zyon Pullin | 1642389 | short=0 |
| Enrique Freeman | 1642402 | long=0, short=0 |
| Ziaire Williams | 1630533 | long=0 |
| Nolan Traore | 1642849 | long=0, mid=0, short=0 |
| Ben Saraf | 1642879 | long=0, mid=0, short=0 |
| Malachi Smith | 1641869 | short=0 |
| Ochai Agbaji | 1630534 | long=0, short=0 |
| Tyler Kolek | 1642278 | long=0, mid=0, short=0 |
| Mohamed Diawara | 1642885 | long=0, mid=0, short=0 |
| Ariel Hukporti | 1630574 | long=0, mid=0, short=0 |
| Pacôme Dadiet | 1642359 | long=0, mid=0, short=0 |
| Trey Jemison III | 1641998 | long=0, mid=0, short=0 |
| Dillon Jones | 1641794 | short=0 |
| Tosan Evbuomwan | 1641787 | long=0, short=0 |
| Jonathan Isaac | 1628371 | long=0 |
| Jamal Cain | 1631288 | long=0 |
| Alex Morales | 1631457 | short=0 |
| Colin Castleton | 1630658 | long=0, short=0 |
| Jarace Walker | 1641716 | long=0, mid=0, short=0 |
| Ben Sheppard | 1641767 | long=0, short=0 |
| Micah Potter | 1630695 | long=0, short=0 |
| Kam Jones | 1642880 | short=0 |
| Taelon Peter | 1643007 | long=0, mid=0, short=0 |
| Cody Martin | 1628998 | long=0, mid=0, short=0 |
| Kyle Lowry | 200768 | long=0, mid=0, short=0 |
| Johni Broome | 1641780 | long=0, mid=0, short=0 |
| Hunter Sallis | 1642282 | long=0, mid=0, short=0 |
| Rasheer Fleming | 1642853 | long=0, mid=0, short=0 |
| Khaman Maluach | 1642863 | long=0, mid=0, short=0 |
| Nigel Hayes-Davis | 1628502 | long=0, mid=0, short=0 |
| Haywood Highsmith | 1629312 | short=0 |
| Koby Brea | 1642886 | long=0, mid=0, short=0 |
| Rayan Rupert | 1641712 | long=0, mid=0, short=0 |
| Yang Hansen | 1642905 | long=0, mid=0, short=0 |
| Javonte Cooke | 1631451 | long=0, mid=0, short=0 |
| Chris Youngblood | 1642959 | long=0, mid=0, short=0 |
| Nique Clifford | 1642363 | long=0, short=0 |
| Devin Carter | 1642269 | long=0, short=0 |
| Killian Hayes | 1630165 | short=0 |
| DaQuan Jeffries | 1629610 | short=0 |
| Dario Saric | 203967 | long=0, mid=0, short=0 |
| Carter Bryant | 1642868 | long=0, mid=0, short=0 |
| Lindy Waters III | 1630322 | long=0, short=0 |
| Bismack Biyombo | 202687 | long=0, mid=0, short=0 |
| David Jones Garcia | 1642357 | short=0 |
| Mason Plumlee | 203486 | long=0, mid=0, short=0 |
| Stanley Umude | 1630649 | short=0 |
| Jaylin Williams | 1631119 | long=0 |
| Brooks Barnhizer | 1642964 | long=0, mid=0, short=0 |
| Nikola Topić | 1642260 | short=0 |
| Buddy Boeheim | 1631205 | short=0 |
| Jonathan Mogbo | 1642367 | long=0, mid=0, short=0 |
| Garrett Temple | 202066 | long=0, mid=0, short=0 |
| Markelle Fultz | 1628365 | short=0 |
| Chucky Hepburn | 1642935 | long=0, short=0 |
| Cody Williams | 1642262 | long=0, short=0 |
| Isaiah Collier | 1642268 | long=0, mid=0, short=0 |
| Jusuf Nurkić | 203994 | long=0, mid=0, short=0 |
| Elijah Harkless | 1641989 | long=0, mid=0, short=0 |
| Vince Williams Jr. | 1631246 | long=0, mid=0, short=0 |
| Hayden Gray | 1643060 | short=0 |
| GG Jackson | 1641713 | long=0, mid=0, short=0 |
| Kentavious Caldwell-Pope | 203484 | long=0, short=0 |
| Olivier-Maxence Prosper | 1641765 | long=0, mid=0, short=0 |
| Ty Jerome | 1629660 | short=0 |
| DeJon Jarreau | 1630610 | short=0 |
| Lucas Williamson | 1631351 | short=0 |
| Dariq Whitehead | 1641727 | short=0 |
| Taj Gibson | 201959 | long=0, short=0 |
| Bub Carrington | 1642267 | long=0, mid=0, short=0 |
| Bilal Coulibaly | 1641731 | long=0, short=0 |
| Anthony Gill | 1630264 | long=0, short=0 |
| Sharife Cooper | 1630536 | long=0, mid=0, short=0 |
| Leaky Black | 1641778 | short=0 |
| Julian Reese | 1642882 | long=0, short=0 |
| Malaki Branham | 1631103 | long=0, mid=0, short=0 |
| Alondes Williams | 1631214 | short=0 |
| Kadary Richmond | 1642955 | short=0 |
| Skal Labissiere | 1627746 | long=0, short=0 |
| Bobi Klintman | 1641752 | long=0, mid=0, short=0 |
| Colby Jones | 1641732 | long=0, short=0 |
| Sion James | 1642883 | short=0 |
| Tre Mann | 1630544 | long=0, short=0 |

### 41場切分：72人

| 球員 | ID | 邊界屬性 |
|---|---:|---|
| RayJ Dennis | 1642484 | short=0 |
| Amari Williams | 1642873 | long=0, short=0 |
| Lonzo Ball | 1628366 | long=0, short=0 |
| Larry Nance Jr. | 1626204 | short=0 |
| Luke Travers | 1631247 | long=0, mid=0, short=0 |
| Herbert Jones | 1630529 | short=0 |
| Jordan Hawkins | 1641722 | short=0 |
| Patrick Williams | 1630172 | long=0, short=0 |
| Rob Dillingham | 1642265 | long=0, mid=0, short=0 |
| Nick Richards | 1630208 | long=0, mid=0, short=0 |
| Dalen Terry | 1631207 | long=0, mid=0, short=0 |
| Lachlan Olbrich | 1642950 | long=0, mid=0, short=0 |
| Caleb Martin | 1628997 | long=0, short=0 |
| AJ Johnson | 1642358 | long=0, mid=0, short=0 |
| Tyus Jones | 1626145 | short=0 |
| Bruce Brown | 1628971 | short=0 |
| Julian Strawther | 1631124 | long=0, mid=0, short=0 |
| Hunter Tyson | 1641816 | short=0 |
| KJ Simpson | 1642354 | long=0, short=0 |
| Draymond Green | 203110 | long=0 |
| JD Davison | 1631120 | long=0, short=0 |
| Cam Christie | 1642353 | long=0, short=0 |
| Kobe Brown | 1641738 | long=0, short=0 |
| Chris Paul | 101108 | short=0 |
| Jahmyl Telfort | 1643141 | long=0, mid=0, short=0 |
| Maxi Kleber | 1628467 | long=0, short=0 |
| Bronny James | 1642355 | long=0, mid=0, short=0 |
| Adou Thiero | 1642876 | short=0 |
| Nikola Jović | 1631107 | long=0, short=0 |
| Keshad Johnson | 1642352 | short=0 |
| Vladislav Goldin | 1642884 | long=0, mid=0, short=0 |
| Jericho Sims | 1630579 | long=0 |
| Gary Harris | 203914 | short=0 |
| Andre Jackson Jr. | 1641748 | long=0, mid=0, short=0 |
| Amir Coffey | 1629599 | long=0, mid=0, short=0 |
| Mike Conley | 201144 | short=0 |
| Terrence Shannon Jr | 1630545 | short=0 |
| Joe Ingles | 204060 | long=0, mid=0, short=0 |
| Nolan Traore | 1642849 | long=0, mid=0, short=0 |
| Ben Saraf | 1642879 | long=0, short=0 |
| Mohamed Diawara | 1642885 | long=0, short=0 |
| Ariel Hukporti | 1630574 | long=0, mid=0, short=0 |
| Kevin McCullar Jr. | 1641755 | long=0, short=0 |
| Pacôme Dadiet | 1642359 | long=0, mid=0, short=0 |
| Trey Jemison III | 1641998 | long=0, short=0 |
| Jarace Walker | 1641716 | short=0 |
| Ben Sheppard | 1641767 | short=0 |
| Cody Martin | 1628998 | long=0, mid=0, short=0 |
| Kyle Lowry | 200768 | long=0, short=0 |
| Johni Broome | 1641780 | long=0, mid=0, short=0 |
| Hunter Sallis | 1642282 | long=0, mid=0, short=0 |
| Rasheer Fleming | 1642853 | long=0 |
| Khaman Maluach | 1642863 | long=0, mid=0, short=0 |
| Nigel Hayes-Davis | 1628502 | long=0, mid=0, short=0 |
| Koby Brea | 1642886 | long=0, mid=0, short=0 |
| Yang Hansen | 1642905 | long=0, mid=0, short=0 |
| Javonte Cooke | 1631451 | long=0, mid=0, short=0 |
| Dario Saric | 203967 | long=0, mid=0, short=0 |
| Carter Bryant | 1642868 | long=0, mid=0, short=0 |
| Kelly Olynyk | 203482 | long=0 |
| Bismack Biyombo | 202687 | long=0, mid=0, short=0 |
| Mason Plumlee | 203486 | long=0, short=0 |
| Brooks Barnhizer | 1642964 | long=0, mid=0, short=0 |
| Jonathan Mogbo | 1642367 | long=0, short=0 |
| Garrett Temple | 202066 | long=0, mid=0, short=0 |
| Isaiah Collier | 1642268 | long=0, mid=0, short=0 |
| Vince Williams Jr. | 1631246 | short=0 |
| Jahmai Mashack | 1642942 | long=0, short=0 |
| Bub Carrington | 1642267 | short=0 |
| Malaki Branham | 1631103 | long=0, short=0 |
| Bobi Klintman | 1641752 | long=0, short=0 |
| Sion James | 1642883 | short=0 |

### 55場切分：65人

| 球員 | ID | 邊界屬性 |
|---|---:|---|
| Christian Koloko | 1631132 | short=0 |
| RayJ Dennis | 1642484 | long=0, short=0 |
| Keshon Gilbert | 1642933 | long=0, mid=0, short=0 |
| Amari Williams | 1642873 | long=0, mid=0, short=0 |
| Lonzo Ball | 1628366 | long=0, mid=0, short=0 |
| Luke Travers | 1631247 | long=0, mid=0, short=0 |
| Jordan Hawkins | 1641722 | short=0 |
| Patrick Williams | 1630172 | short=0 |
| Rob Dillingham | 1642265 | long=0, mid=0, short=0 |
| Leonard Miller | 1631159 | long=0 |
| Dalen Terry | 1631207 | short=0 |
| Lachlan Olbrich | 1642950 | long=0, short=0 |
| Caleb Martin | 1628997 | short=0 |
| AJ Johnson | 1642358 | long=0, mid=0, short=0 |
| Tyus Jones | 1626145 | short=0 |
| Hunter Tyson | 1641816 | long=0, mid=0, short=0 |
| KJ Simpson | 1642354 | long=0, short=0 |
| Draymond Green | 203110 | long=0 |
| Chris Paul | 101108 | long=0, short=0 |
| Jahmyl Telfort | 1643141 | long=0, mid=0, short=0 |
| Bronny James | 1642355 | long=0, mid=0, short=0 |
| Chris Mañon | 1643024 | long=0, mid=0, short=0 |
| Nikola Jović | 1631107 | long=0, short=0 |
| Gary Harris | 203914 | short=0 |
| Cole Anthony | 1630175 | long=0, short=0 |
| Andre Jackson Jr. | 1641748 | long=0, mid=0, short=0 |
| Mike Conley | 201144 | short=0 |
| Terrence Shannon Jr | 1630545 | short=0 |
| Joe Ingles | 204060 | long=0, mid=0, short=0 |
| Enrique Freeman | 1642402 | long=0, short=0 |
| Drake Powell | 1642962 | long=0 |
| Nolan Traore | 1642849 | short=0 |
| Ben Saraf | 1642879 | long=0, mid=0, short=0 |
| Jalen Wilson | 1630592 | short=0 |
| Mohamed Diawara | 1642885 | short=0 |
| Ariel Hukporti | 1630574 | long=0, mid=0, short=0 |
| Kevin McCullar Jr. | 1641755 | long=0, mid=0, short=0 |
| Pacôme Dadiet | 1642359 | long=0, mid=0, short=0 |
| Trey Jemison III | 1641998 | long=0, mid=0, short=0 |
| Dillon Jones | 1641794 | short=0 |
| Jonathan Isaac | 1628371 | long=0 |
| Jarace Walker | 1641716 | short=0 |
| Cody Martin | 1628998 | long=0, mid=0, short=0 |
| Kyle Lowry | 200768 | long=0, mid=0, short=0 |
| Johni Broome | 1641780 | long=0, mid=0, short=0 |
| Hunter Sallis | 1642282 | long=0, mid=0, short=0 |
| Khaman Maluach | 1642863 | long=0, mid=0, short=0 |
| Nigel Hayes-Davis | 1628502 | long=0, mid=0, short=0 |
| Rayan Rupert | 1641712 | long=0, short=0 |
| Yang Hansen | 1642905 | long=0, mid=0, short=0 |
| Javonte Cooke | 1631451 | long=0, mid=0, short=0 |
| Dario Saric | 203967 | long=0, mid=0, short=0 |
| Carter Bryant | 1642868 | long=0, short=0 |
| Kelly Olynyk | 203482 | long=0, mid=0, short=0 |
| Jordan McLaughlin | 1629162 | short=0 |
| Bismack Biyombo | 202687 | long=0, mid=0, short=0 |
| Mason Plumlee | 203486 | long=0, short=0 |
| Brooks Barnhizer | 1642964 | long=0, mid=0, short=0 |
| Jonathan Mogbo | 1642367 | long=0, mid=0, short=0 |
| Garrett Temple | 202066 | long=0, mid=0, short=0 |
| Isaiah Collier | 1642268 | long=0 |
| Bub Carrington | 1642267 | short=0 |
| Bobi Klintman | 1641752 | long=0, mid=0, short=0 |
| Sion James | 1642883 | short=0 |
| Tre Mann | 1630544 | short=0 |


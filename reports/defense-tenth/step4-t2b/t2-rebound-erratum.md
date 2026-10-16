# T2補充：區段防守籃板隊側勘誤

前次T2補充誤把區段opponent.dreb換成另一隊的值，錯在我的欄位語義判讀。原產物不覆寫。本次改正只影響該補充的嚴格樣本及陣容分桶DREB%，不影響cached-factors.json的全季box、純卡／v3模擬籃板率，也未觸及T0。

根據[prepare_defense_b1.js](D:/Projects/CODING/basketball-autochess/scripts/prepare_defense_b1.js:32)，一般進攻事件放對方防守側；防守籃板例外，放抓到籃板的同側。故防守側的opponent.dreb其實是自身DREB，opponent.oreb才是對手OREB。正確比率=DREB/(DREB+對手OREB)。本次逐隊加總嚴格場次DREB，與官方相同場次box完全一致，四季均通過。

舊雜湊檢查只能證明檔案未變，無法檢查這個語義錯誤；本次加入事件側別與官方DREB對帳。

| 球季 | 隊伍 | 舊嚴格DREB% | 正確DREB% | DREB／對手OREB |
|---|---|---|---|---|
| 2022-23 | Cleveland Cavaliers | 75.891 | 75.625 | 2057／663 |
| 2023-24 | New York Knicks | 74.818 | 75.910 | 2398／761 |
| 2024-25 | New York Knicks | 73.764 | 74.328 | 2212／764 |
| 2024-25 | Oklahoma City Thunder | 73.957 | 74.515 | 2573／880 |
| 2025-26 | New York Knicks | 75.492 | 76.816 | 2601／785 |
| 2025-26 | Boston Celtics | 73.843 | 76.087 | 2625／825 |
| 2025-26 | Oklahoma City Thunder | 73.577 | 74.280 | 2735／947 |
| 2025-26 | Detroit Pistons | 72.089 | 74.010 | 2580／906 |

所有0／1／2+分桶逐項如下。桶內樣本小不作因果解讀；尤其騎士合資格護框者2+桶為空，不能稱為雙護框證據。

| 球季 | 隊伍 | 分類 | 數量桶 | 舊DREB% | 正確DREB% | DREB／對手OREB |
|---|---|---|---|---|---|---|
| 2022-23 | Cleveland Cavaliers | rimProtector | 0 | 75.862 | 74.942 | 649／217 |
| 2022-23 | Cleveland Cavaliers | rimProtector | 1 | 75.905 | 75.944 | 1408／446 |
| 2022-23 | Cleveland Cavaliers | rimProtector | 2+ | — | — | 0／0 |
| 2022-23 | Cleveland Cavaliers | sizeOnly | 0 | 76.093 | 75.668 | 510／164 |
| 2022-23 | Cleveland Cavaliers | sizeOnly | 1 | 75.710 | 75.530 | 1531／496 |
| 2022-23 | Cleveland Cavaliers | sizeOnly | 2+ | 86.364 | 84.211 | 16／3 |
| 2023-24 | New York Knicks | rimProtector | 0 | 76.014 | 76.161 | 869／272 |
| 2023-24 | New York Knicks | rimProtector | 1 | 74.100 | 75.768 | 1529／489 |
| 2023-24 | New York Knicks | rimProtector | 2+ | — | — | 0／0 |
| 2023-24 | New York Knicks | sizeOnly | 0 | 76.259 | 76.386 | 427／132 |
| 2023-24 | New York Knicks | sizeOnly | 1 | 74.483 | 75.798 | 1970／629 |
| 2023-24 | New York Knicks | sizeOnly | 2+ | 100.000 | 100.000 | 1／0 |
| 2024-25 | New York Knicks | rimProtector | 0 | 73.764 | 74.328 | 2212／764 |
| 2024-25 | New York Knicks | rimProtector | 1 | — | — | 0／0 |
| 2024-25 | New York Knicks | rimProtector | 2+ | — | — | 0／0 |
| 2024-25 | New York Knicks | sizeOnly | 0 | 74.312 | 73.435 | 387／140 |
| 2024-25 | New York Knicks | sizeOnly | 1 | 73.714 | 74.529 | 1779／608 |
| 2024-25 | New York Knicks | sizeOnly | 2+ | 70.370 | 74.194 | 46／16 |
| 2024-25 | Oklahoma City Thunder | rimProtector | 0 | 75.260 | 74.239 | 1098／381 |
| 2024-25 | Oklahoma City Thunder | rimProtector | 1 | 72.514 | 73.684 | 1246／445 |
| 2024-25 | Oklahoma City Thunder | rimProtector | 2+ | 75.455 | 80.919 | 229／54 |
| 2024-25 | Oklahoma City Thunder | sizeOnly | 0 | 75.588 | 74.343 | 933／322 |
| 2024-25 | Oklahoma City Thunder | sizeOnly | 1 | 72.653 | 73.715 | 1405／501 |
| 2024-25 | Oklahoma City Thunder | sizeOnly | 2+ | 75.000 | 80.479 | 235／57 |
| 2025-26 | New York Knicks | rimProtector | 0 | 76.058 | 77.042 | 1500／447 |
| 2025-26 | New York Knicks | rimProtector | 1 | 74.701 | 76.511 | 1101／338 |
| 2025-26 | New York Knicks | rimProtector | 2+ | — | — | 0／0 |
| 2025-26 | New York Knicks | sizeOnly | 0 | 78.378 | 78.495 | 146／40 |
| 2025-26 | New York Knicks | sizeOnly | 1 | 75.118 | 76.428 | 2221／685 |
| 2025-26 | New York Knicks | sizeOnly | 2+ | 77.358 | 79.592 | 234／60 |
| 2025-26 | Boston Celtics | rimProtector | 0 | 74.005 | 75.029 | 1295／431 |
| 2025-26 | Boston Celtics | rimProtector | 1 | 73.663 | 77.146 | 1330／394 |
| 2025-26 | Boston Celtics | rimProtector | 2+ | — | — | 0／0 |
| 2025-26 | Boston Celtics | sizeOnly | 0 | 71.821 | 72.419 | 512／195 |
| 2025-26 | Boston Celtics | sizeOnly | 1 | 74.327 | 76.943 | 2069／620 |
| 2025-26 | Boston Celtics | sizeOnly | 2+ | 78.723 | 81.481 | 44／10 |
| 2025-26 | Oklahoma City Thunder | rimProtector | 0 | 72.736 | 70.846 | 695／286 |
| 2025-26 | Oklahoma City Thunder | rimProtector | 1 | 74.052 | 74.865 | 1528／513 |
| 2025-26 | Oklahoma City Thunder | rimProtector | 2+ | 73.477 | 77.576 | 512／148 |
| 2025-26 | Oklahoma City Thunder | sizeOnly | 0 | 72.736 | 70.846 | 695／286 |
| 2025-26 | Oklahoma City Thunder | sizeOnly | 1 | 74.052 | 74.865 | 1528／513 |
| 2025-26 | Oklahoma City Thunder | sizeOnly | 2+ | 73.477 | 77.576 | 512／148 |
| 2025-26 | Detroit Pistons | rimProtector | 0 | 71.937 | 73.214 | 1271／465 |
| 2025-26 | Detroit Pistons | rimProtector | 1 | 72.247 | 74.800 | 1309／441 |
| 2025-26 | Detroit Pistons | rimProtector | 2+ | — | — | 0／0 |
| 2025-26 | Detroit Pistons | sizeOnly | 0 | 71.530 | 72.805 | 1186／443 |
| 2025-26 | Detroit Pistons | sizeOnly | 1 | 72.604 | 75.067 | 1394／463 |
| 2025-26 | Detroit Pistons | sizeOnly | 2+ | — | — | 0／0 |

勘誤改變部分分桶差距與方向，因此舊的分桶DREB敘述應以本表取代；全季防守籃板被低估的觀察保留，但在做任何籃板機制修正前仍須使用改正後資料評估，不能說所有舊推論都不受影響。

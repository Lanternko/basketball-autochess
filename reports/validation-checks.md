# 2026-09-19 驗證紀錄

- `npm test`：57 passed、0 failed；另有60場完整時鐘比賽通過分鐘、輪替、比分、罰球、助攻、延長賽、重播及舊模式一致性。
- `npm run test:measurement`：7項通過，含20個舊版指紋、双邊記帳守恆、抽樣誤差、36分鐘換算。
- `npm run test:rebound-blocks`：6項通過；`test:rebound-ratio`、`test:season-style` 通過。
- `npm run test:strength`：同季30隊／150卡、37份來源雜湊、在隊分鐘前五選擇、單調勝率映射、先後手配對方差、自身對戰50%、固定隊友、PR同分與seed重現通過。
- `npm run test:possession-calibration`：EV／實際事件失誤機率一致、處理能力的壓力失誤效果、罰球曲線不變、順下接球路徑、高EV接球權重、雙方記帳與seed重現通過。
- `npm run benchmark:build`：從官方快照重建與已存檔逐byte相同。
- `per36 --team OKC --preset stable-v1 --n 2000 --seed 20261219`：球員統計逐欄精確重現正式四隊驗證中的OKC結果。
- `--team-pr 90` 曾對舊引擎雜湊報告拒絕執行；正式報告重跑後可選取2025–26固定五人的Cleveland Cavaliers。此隊估計第三名，保守名次範圍2–4，不能宣稱真實NBA第三強。

統計驗收、區間及完整樣本數分別保存在 `strength-validation`、`strength-robustness`、`possession-calibration`、`possession-uncertainty` 的 Markdown／JSON。所有測試與結論皆有範圍限制，固定五人不等同完整輪換，usage代理不等同實際lineup usage。

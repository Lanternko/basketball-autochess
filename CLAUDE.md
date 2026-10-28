# basketball-autochess

NBA 球員數值模型＋自走棋原型。對使用者用繁體中文。

## 開工先讀（依序）
1. `memory/handoff.md`：目前狀態、誰在做、下一步。
2. `memory/lessons.md`：踩過的坑，每條都是硬規則。
3. `memory/rulings.md`：使用者對球員評價、驗收方式、流程的裁定。
4. 其他（`findings.md`、`experiments.md`、`references.md`）用 grep 查 ID 或關鍵字，不要整份讀。

寫入規則見 `memory/README.md`：ID 只追加不刪；改狀態只改狀態欄並註明日期；樣本內結果不算證據（R-007）；被抓到的錯一律寫成 lesson；收工整份覆寫 `handoff.md`。

## 角色
| 角色 | skill | 做什麼 |
|---|---|---|
| lead | `.claude/skills/role-lead/` | 規劃、寫 spec、派工、看五道關卡決定採用 |
| model | `.claude/skills/role-model/` | 模擬引擎（`src/`）與防守／球權版本 |
| card | `.claude/skills/role-card/` | 卡片 OVR、賽中 OVR、預註冊回測 |
| audit | `.claude/skills/role-audit/` | 獨立核對數字、樣本內外、預註冊有沒有被違反 |

## 五道關卡（摘要，完整見 `memory/README.md`）
G1 `npm test` 過 → G2 卡／板記錄版本、RAPM 窗、資料 sha256 → G3 同版本同人群同 seed 才比，用 team+seed 重抽 → G4 樣本外（RAPM 分半、沒看過的季、凍結預註冊）→ G5 使用者抽查（2K27 或 RAPM 其一、前十長人）。

## 指令
```bash
npm test
python reports/status/status_snapshot.py
```
重度運算（多 seed 模擬、回測掃描）跑 5090，本機只跑輕量。

## 絕不
- 使用者沒說不 commit、不 push。
- 不在本檔或 memory/ 存金鑰、token、`.env` 值。
- 不在看過答案後挑參數再當盲測（L-026）。

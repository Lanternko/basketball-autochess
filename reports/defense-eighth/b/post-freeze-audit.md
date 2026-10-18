# 凍結後驗證補充

原產物測試在c=0時因JSON負零記帳失敗：記憶體中的負係數乘0得到−0，JSON存檔後讀回為+0，嚴格比較誤判。預測、能力值、校準、c與比分均未修改。

已保留原凍結規格及全部來源雜湊；另用相同JSON往返正規化預期的殘差陣列，再執行完整產物測試，全部通過。沒有放寬數值容差或略過檢查。

凍結規格SHA-256：c21ca1e02c267f8143ed2561729d36f27fa11406c6d44a3682cbd699ce590d98。完整驗證來源、單一修正與時間見 [post-freeze-audit.json](post-freeze-audit.json)。

請以以下指令取代原報告的產物測試指令：

```powershell
node scripts/validate_defense_eighth_b_serialization.js
node test/defense_seventh.js
```

`npm run test:ability-eighth-b`也已指向此補充驗證。完成B後停下，沒有下載兩個盲測季。

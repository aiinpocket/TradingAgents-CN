# 開發工作流規則 - Development Workflow Rules

## ⚠️ 關键安全規則

### 🔒 Main 分支保護
- **絕對禁止** 直接向 `main` 分支推送未經測試的代碼
- **絕對禁止** 未經用戶測試確認就合並 PR 到 `main` 分支
- 所有對 `main` 分支的修改必须經過嚴格的測試流程

### 🚫 禁止操作
1. 直接在 `main` 分支開發功能
2. 未經測試就推送到 `main` 分支
3. 跳過測試流程强制合並 PR
4. 在生產環境部署未經驗證的代碼

## 📋 强制工作流程

### 1. 功能開發流程
```bash
# 1. 從 main 分支創建功能分支
git checkout main
git pull origin main
git checkout -b feature/功能名稱

# 2. 在功能分支中開發
# 開發代碼...

# 3. 提交到功能分支
git add .
git commit -m "描述性提交信息"
git push origin feature/功能名稱
```

### 2. 測試確認流程
```bash
# 1. 切換到功能分支進行測試
git checkout feature/功能名稱

# 2. 運行完整測試套件
python -m pytest tests/
python scripts/syntax_checker.py
# 其他相關測試...

# 3. 用戶手動測試確認
# - 功能測試
# - 集成測試
# - 回歸測試
```

### 3. 合並到 Main 流程
```bash
# 只有在用戶明確確認測試通過後才能執行：

# 1. 切換到 main 分支
git checkout main
git pull origin main

# 2. 合並功能分支（需要用戶明確批準）
git merge feature/功能名稱

# 3. 推送到远程（需要用戶明確批準）
git push origin main

# 4. 清理功能分支
git branch -d feature/功能名稱
git push origin --delete feature/功能名稱
```

## 🛡️ 技術保護措施

### 1. Git Pre-push 钩子
- 自動阻止直接推送到 `main` 分支
- 位置：`.git/hooks/pre-push`
- 绕過方式：`git push --no-verify`（仅緊急情况使用）

### 2. 建议的 GitHub 分支保護規則
```yaml
分支：main
保護規則：
  - 需要拉取請求審核才能合並
  - 要求狀態檢查通過才能合並
  - 要求分支在合並前保持最新
  - 包括管理員在內的所有人都需要遵守
  - 允許强制推送：否
  - 允許刪除：否
```

## 🚨 緊急情况處理

### 生產事故回滚流程
```bash
# 1. 立即回滚到已知穩定版本
git checkout main
git reset --hard <穩定版本SHA>

# 2. 强制推送（需要明確確認）
git push origin main --force-with-lease

# 3. 創建事故分析分支
git checkout -b hotfix/incident-YYYY-MM-DD

# 4. 分析問題並制定修複方案
# 5. 在修複分支中測試解決方案
# 6. 經過完整測試後合並修複
```

## 📝 操作檢查清單

### 合並前檢查清單
- [ ] 功能在獨立分支中開發完成
- [ ] 通過所有自動化測試
- [ ] 經過用戶手動測試確認
- [ ] 代碼審查通過
- [ ] 文档已更新
- [ ] 备份計劃已制定

### 推送前檢查清單
- [ ] 確認目標分支正確
- [ ] 確認推送內容已經過測試
- [ ] 確認有回滚計劃
- [ ] 用戶已明確批準推送操作

## 🎯 最佳實踐

1. **小步快跑**：功能拆分成小的、可測試的單元
2. **持续測試**：每個提交都要經過測試
3. **明確沟通**：所有重要操作都要獲得明確確認
4. **文档先行**：重要變更要先更新文档
5. **备份意识**：重要操作前要有回滚計劃

## 🔄 版本管理策略

### 分支命名規範
- `main`: 生產穩定版本
- `develop`: 開發集成分支
- `feature/功能名`: 功能開發分支
- `hotfix/問題描述`: 緊急修複分支
- `release/版本號`: 發布準备分支

### 提交信息規範
```
類型(範围): 簡短描述

詳細描述（可選）

相關問題：#issue號碼
```

類型包括：
- `feat`: 新功能
- `fix`: 修複bug
- `docs`: 文档更新
- `style`: 代碼格式調整
- `refactor`: 代碼重構
- `test`: 測試相關
- `chore`: 構建過程或辅助工具的變動

---

**記住：安全和穩定性永远是第一優先級！**
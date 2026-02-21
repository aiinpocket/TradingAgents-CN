# 分支管理指南

本文檔說明了TradingAgents-CN項目的分支管理策略和工作流程。

## 🌳 分支結構

### 主要分支
- **main**: 主分支，包含穩定的生產代碼
- **develop**: 開發分支，包含最新的開發功能
- **feature/***: 功能分支，用於開發新功能
- **hotfix/***: 熱修複分支，用於緊急修複

### 分支命名規範
```
feature/功能名稱          # 新功能開發
hotfix/修複描述          # 緊急修複
release/版本號           # 版本發布
docs/文檔更新            # 文檔更新
```

## 🔄 工作流程

### 1. 功能開發流程
```bash
# 1. 從develop創建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 開發功能
# ... 編寫代碼 ...

# 3. 提交更改
git add .
git commit -m "feat: 添加新功能"

# 4. 推送分支
git push origin feature/new-feature

# 5. 創建Pull Request到develop
```

### 2. 熱修複流程
```bash
# 1. 從main創建熱修複分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. 修複問題
# ... 修複代碼 ...

# 3. 提交更改
git add .
git commit -m "fix: 修複關鍵問題"

# 4. 推送分支
git push origin hotfix/critical-fix

# 5. 創建PR到main和develop
```

### 3. 版本發布流程
```bash
# 1. 從develop創建發布分支
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. 準備發布
# ... 更新版本號、文檔等 ...

# 3. 測試驗證
# ... 運行測試 ...

# 4. 合並到main
git checkout main
git merge release/v1.0.0
git tag v1.0.0

# 5. 合並回develop
git checkout develop
git merge release/v1.0.0
```

## 📋 分支保護規則

### main分支
- 禁止直接推送
- 需要Pull Request
- 需要代碼審查
- 需要通過所有測試

### develop分支
- 禁止直接推送
- 需要Pull Request
- 建議代碼審查

## 🔍 代碼審查

### 審查要點
- [ ] 代碼品質和規範
- [ ] 功能完整性
- [ ] 測試覆蓋率
- [ ] 文檔更新
- [ ] 性能影響

### 審查流程
1. 創建Pull Request
2. 自動化測試運行
3. 代碼審查
4. 修改反饋
5. 批準合並

## 🚀 最佳實踐

### 提交規範
```
feat: 新功能
fix: 修複
docs: 文檔
style: 格式
refactor: 重構
test: 測試
chore: 構建
```

### 分支管理
- 保持分支簡潔
- 及時刪除已合並分支
- 定期同步上游更改
- 避免長期存在的功能分支

### 衝突解決
```bash
# 1. 更新目標分支
git checkout develop
git pull origin develop

# 2. 切換到功能分支
git checkout feature/my-feature

# 3. 變基到最新develop
git rebase develop

# 4. 解決衝突
# ... 手動解決衝突 ...

# 5. 繼續變基
git rebase --continue

# 6. 強制推送
git push --force-with-lease origin feature/my-feature
```

## 📊 分支狀態監控

### 檢查命令
```bash
# 查看所有分支
git branch -a

# 查看分支狀態
git status

# 查看分支歷史
git log --oneline --graph

# 查看遠端分支
git remote show origin
```

### 清理命令
```bash
# 刪除已合並的本地分支
git branch --merged | grep -v main | xargs git branch -d

# 刪除遠端跟蹤分支
git remote prune origin

# 清理無用的引用
git gc --prune=now
```

## 🔧 工具配置

### Git配置
```bash
# 設置用戶信息
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 設置默認分支
git config init.defaultBranch main

# 設置推送策略
git config push.default simple
```

### IDE集成
- 使用Git圖形化工具
- 配置代碼格式化
- 設置提交模板
- 啟用分支保護

---

遵循這些指南可以確保項目的代碼品質和開發效率。

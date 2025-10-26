# 🌳 TradingAgents-CN 分支管理策略

## 📋 當前分支狀况分析

基於項目的發展歷程，當前可能存在以下分支：

### 🎯 主要分支
- **main** - 穩定的生產版本
- **develop** - 開發主分支
- **feature/tushare-integration** - Tushare集成和v0.1.6功能
- **feature/deepseek-v3-integration** - DeepSeek V3集成（可能已合並）

### 🔧 功能分支（可能存在）
- **feature/dashscope-openai-fix** - 阿里百炼修複
- **feature/data-source-upgrade** - 數據源升級
- **hotfix/*** - 緊急修複分支

## 🎯 推薦的分支管理策略

### 1. 簡化分支結構

#### 目標結構
```
main (生產版本)
├── develop (開發主分支)
├── feature/v0.1.7 (下一版本開發)
└── hotfix/* (緊急修複)
```

#### 清理策略
```bash
# 1. 確保所有重要功能都在main分支
# 2. 刪除已合並的功能分支
# 3. 保持簡潔的分支結構
```

### 2. 版本發布流程

#### 當前v0.1.6發布流程
```bash
# Step 1: 確保feature/tushare-integration包含所有v0.1.6功能
git checkout feature/tushare-integration
git status

# Step 2: 合並到develop分支
git checkout develop
git merge feature/tushare-integration

# Step 3: 合並到main分支並打標簽
git checkout main
git merge develop
git tag v0.1.6
git push origin main --tags

# Step 4: 清理功能分支
git branch -d feature/tushare-integration
git push origin --delete feature/tushare-integration
```

### 3. 未來版本開發流程

#### v0.1.7開發流程
```bash
# Step 1: 從main創建新的功能分支
git checkout main
git pull origin main
git checkout -b feature/v0.1.7

# Step 2: 開發新功能
# ... 開發工作 ...

# Step 3: 定期同步main分支
git checkout main
git pull origin main
git checkout feature/v0.1.7
git merge main

# Step 4: 完成後合並回main
git checkout main
git merge feature/v0.1.7
git tag v0.1.7
```

## 🔧 分支清理腳本

### 檢查分支狀態
```bash
#!/bin/bash
echo "🔍 檢查分支狀態"
echo "=================="

echo "📋 本地分支:"
git branch

echo -e "\n🌐 远程分支:"
git branch -r

echo -e "\n📊 分支關系:"
git log --oneline --graph --all -10

echo -e "\n🎯 當前分支:"
git branch --show-current

echo -e "\n📝 未提交的更改:"
git status --porcelain
```

### 分支清理腳本
```bash
#!/bin/bash
echo "🧹 分支清理腳本"
echo "=================="

# 1. 切換到main分支
git checkout main
git pull origin main

# 2. 查看已合並的分支
echo "📋 已合並到main的分支:"
git branch --merged main

# 3. 查看未合並的分支
echo "⚠️ 未合並到main的分支:"
git branch --no-merged main

# 4. 刪除已合並的功能分支（交互式）
echo "🗑️ 刪除已合並的功能分支..."
git branch --merged main | grep -E "feature/|hotfix/" | while read branch; do
    echo "刪除分支: $branch"
    read -p "確認刪除? (y/N): " confirm
    if [[ $confirm == [yY] ]]; then
        git branch -d "$branch"
        git push origin --delete "$branch" 2>/dev/null || true
    fi
done
```

## 📋 具體操作建议

### 立即執行的操作

#### 1. 確認當前狀態
```bash
# 檢查當前分支
git branch --show-current

# 檢查未提交的更改
git status

# 查看最近的提交
git log --oneline -5
```

#### 2. 整理v0.1.6版本
```bash
# 如果當前在feature/tushare-integration分支
# 確保所有v0.1.6功能都已提交
git add .
git commit -m "完成v0.1.6所有功能"

# 推送到远程
git push origin feature/tushare-integration
```

#### 3. 發布v0.1.6正式版
```bash
# 合並到main分支
git checkout main
git merge feature/tushare-integration

# 創建版本標簽
git tag -a v0.1.6 -m "TradingAgents-CN v0.1.6正式版"

# 推送到远程
git push origin main --tags
```

### 長期維護策略

#### 1. 分支命名規範
- **功能分支**: `feature/功能名稱` 或 `feature/v版本號`
- **修複分支**: `hotfix/問題描述`
- **發布分支**: `release/v版本號` (可選)

#### 2. 提交信息規範
```
類型(範围): 簡短描述

詳細描述（可選）

- 具體更改1
- 具體更改2

Closes #issue號
```

#### 3. 版本發布檢查清單
- [ ] 所有功能開發完成
- [ ] 測試通過
- [ ] 文档更新
- [ ] 版本號更新
- [ ] CHANGELOG更新
- [ ] 創建發布標簽

## 🎯 推薦的下一步行動

### 立即行動（今天）
1. **確認當前分支狀態**
2. **提交所有未保存的更改**
3. **發布v0.1.6正式版**

### 短期行動（本周）
1. **清理已合並的功能分支**
2. **建立標準的分支管理流程**
3. **創建v0.1.7開發分支**

### 長期行動（持续）
1. **遵循分支命名規範**
2. **定期清理過時分支**
3. **維護清晰的版本歷史**

## 🛠️ 分支管理工具

### Git別名配置
```bash
# 添加有用的Git別名
git config --global alias.br branch
git config --global alias.co checkout
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.cleanup "!git branch --merged main | grep -v main | xargs -n 1 git branch -d"
```

### VSCode擴展推薦
- **GitLens** - Git歷史可視化
- **Git Graph** - 分支圖形化顯示
- **Git History** - 文件歷史查看

## 📞 需要幫助時

如果在分支管理過程中遇到問題：

1. **备份當前工作**
   ```bash
   git stash push -m "备份當前工作"
   ```

2. **寻求幫助**
   - 查看Git文档
   - 使用 `git help <command>`
   - 咨詢团隊成員

3. **恢複工作**
   ```bash
   git stash pop
   ```

---

**記住**: 分支管理的目標是让開發更有序，而不是增加複雜性。保持簡單、清晰的分支結構是關键。

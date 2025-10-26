# 分支管理策略

## 🌿 分支架構設計

### 主要分支

```
main (生產分支)
├── develop (開發主分支)
├── feature/* (功能開發分支)
├── enhancement/* (中文增强分支)
├── hotfix/* (緊急修複分支)
├── release/* (發布準备分支)
└── upstream-sync/* (上游同步分支)
```

### 分支說明

#### 🏠 **main** - 生產主分支
- **用途**: 穩定的生產版本
- **保護**: 受保護，只能通過PR合並
- **來源**: develop、hotfix、upstream-sync
- **特點**: 始终保持可發布狀態

#### 🚀 **develop** - 開發主分支
- **用途**: 集成所有功能開發
- **保護**: 受保護，通過PR合並
- **來源**: feature、enhancement分支
- **特點**: 最新的開發進度

#### ✨ **feature/** - 功能開發分支
- **命名**: `feature/功能名稱`
- **用途**: 開發新功能
- **生命周期**: 短期（1-2周）
- **示例**: `feature/portfolio-optimization`

#### 🇨🇳 **enhancement/** - 中文增强分支
- **命名**: `enhancement/增强名稱`
- **用途**: 中文本地化和增强功能
- **生命周期**: 中期（2-4周）
- **示例**: `enhancement/chinese-llm-integration`

#### 🚨 **hotfix/** - 緊急修複分支
- **命名**: `hotfix/修複描述`
- **用途**: 緊急Bug修複
- **生命周期**: 短期（1-3天）
- **示例**: `hotfix/api-timeout-fix`

#### 📦 **release/** - 發布準备分支
- **命名**: `release/版本號`
- **用途**: 發布前的最後準备
- **生命周期**: 短期（3-7天）
- **示例**: `release/v1.1.0-cn`

#### 🔄 **upstream-sync/** - 上游同步分支
- **命名**: `upstream-sync/日期`
- **用途**: 同步上游更新
- **生命周期**: 臨時（1天）
- **示例**: `upstream-sync/20240115`

## 🔄 工作流程

### 功能開發流程

```mermaid
graph LR
    A[main] --> B[develop]
    B --> C[feature/new-feature]
    C --> D[開發和測試]
    D --> E[PR to develop]
    E --> F[代碼審查]
    F --> G[合並到develop]
    G --> H[測試集成]
    H --> I[PR to main]
    I --> J[發布]
```

### 中文增强流程

```mermaid
graph LR
    A[develop] --> B[enhancement/chinese-feature]
    B --> C[本地化開發]
    C --> D[中文測試]
    D --> E[文档更新]
    E --> F[PR to develop]
    F --> G[審查和合並]
```

### 緊急修複流程

```mermaid
graph LR
    A[main] --> B[hotfix/urgent-fix]
    B --> C[快速修複]
    C --> D[測試驗證]
    D --> E[PR to main]
    E --> F[立即發布]
    F --> G[合並到develop]
```

## 📋 分支操作指南

### 創建功能分支

```bash
# 從develop創建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/portfolio-analysis

# 開發完成後推送
git push -u origin feature/portfolio-analysis
```

### 創建中文增强分支

```bash
# 從develop創建增强分支
git checkout develop
git pull origin develop
git checkout -b enhancement/tushare-integration

# 推送分支
git push -u origin enhancement/tushare-integration
```

### 創建緊急修複分支

```bash
# 從main創建修複分支
git checkout main
git pull origin main
git checkout -b hotfix/api-error-fix

# 推送分支
git push -u origin hotfix/api-error-fix
```

## 🔒 分支保護規則

### main分支保護
- ✅ 要求PR審查
- ✅ 要求狀態檢查通過
- ✅ 要求分支為最新
- ✅ 限制推送權限
- ✅ 限制强制推送

### develop分支保護
- ✅ 要求PR審查
- ✅ 要求CI通過
- ✅ 允許管理員绕過

### 功能分支
- ❌ 無特殊保護
- ✅ 自動刪除已合並分支

## 🏷️ 命名規範

### 分支命名

```bash
# 功能開發
feature/功能名稱-簡短描述
feature/chinese-data-source
feature/risk-management-enhancement

# 中文增强
enhancement/增强類型-具體內容
enhancement/llm-baidu-integration
enhancement/chinese-financial-terms

# Bug修複
hotfix/問題描述
hotfix/memory-leak-fix
hotfix/config-loading-error

# 發布準备
release/版本號
release/v1.1.0-cn
release/v1.2.0-cn-beta
```

### 提交信息規範

```bash
# 功能開發
feat(agents): 添加量化分析師智能體
feat(data): 集成Tushare數據源

# 中文增强
enhance(llm): 集成文心一言API
enhance(docs): 完善中文文档體系

# Bug修複
fix(api): 修複API超時問題
fix(config): 解決配置文件加載錯誤

# 文档更新
docs(readme): 更新安裝指南
docs(api): 添加API使用示例
```

## 🧪 測試策略

### 分支測試要求

#### feature分支
- ✅ 單元測試覆蓋率 > 80%
- ✅ 功能測試通過
- ✅ 代碼風格檢查

#### enhancement分支
- ✅ 中文功能測試
- ✅ 兼容性測試
- ✅ 文档完整性檢查

#### develop分支
- ✅ 完整測試套件
- ✅ 集成測試
- ✅ 性能測試

#### main分支
- ✅ 生產環境測試
- ✅ 端到端測試
- ✅ 安全扫描

## 📊 分支監控

### 分支健康度指標

```bash
# 檢查分支狀態
git branch -a --merged    # 已合並分支
git branch -a --no-merged # 未合並分支

# 檢查分支差異
git log develop..main --oneline
git log feature/branch..develop --oneline

# 檢查分支大小
git rev-list --count develop..feature/branch
```

### 定期清理

```bash
# 刪除已合並的本地分支
git branch --merged develop | grep -v "develop\|main" | xargs -n 1 git branch -d

# 刪除远程跟蹤分支
git remote prune origin

# 清理過期分支
git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads | awk '$2 <= "'$(date -d '30 days ago' '+%Y-%m-%d')'"' | cut -d' ' -f1
```

## 🚀 發布流程

### 版本發布步骤

1. **創建發布分支**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.1.0-cn
   ```

2. **版本準备**
   ```bash
   # 更新版本號
   # 更新CHANGELOG.md
   # 最後測試
   ```

3. **合並到main**
   ```bash
   git checkout main
   git merge release/v1.1.0-cn
   git tag v1.1.0-cn
   git push origin main --tags
   ```

4. **回合並到develop**
   ```bash
   git checkout develop
   git merge main
   git push origin develop
   ```

## 🔧 自動化工具

### Git Hooks

```bash
# pre-commit hook
#!/bin/sh
# 運行代碼風格檢查
black --check .
flake8 .

# pre-push hook
#!/bin/sh
# 運行測試
python -m pytest tests/
```

### GitHub Actions

```yaml
# 分支保護檢查
on:
  pull_request:
    branches: [main, develop]
    
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: python -m pytest
```

## 🚀 推薦的開發工作流

### 1. 日常功能開發流程

#### 標準功能開發
```bash
# 步骤1: 創建功能分支
python scripts/branch_manager.py create feature portfolio-optimization -d "投資組合優化功能"

# 步骤2: 開發功能
# 編寫代碼...
git add .
git commit -m "feat: 添加投資組合優化算法"

# 步骤3: 定期同步develop分支
git fetch origin
git merge origin/develop  # 或使用 git rebase origin/develop

# 步骤4: 推送到远程
git push origin feature/portfolio-optimization

# 步骤5: 創建Pull Request
# 在GitHub上創建PR: feature/portfolio-optimization -> develop
# 填寫PR模板，包含功能描述、測試說明等

# 步骤6: 代碼審查
# 等待团隊成員審查，根據反馈修改代碼

# 步骤7: 合並和清理
# PR合並後，刪除本地和远程分支
python scripts/branch_manager.py delete feature/portfolio-optimization
```

#### 功能開發檢查清單
- [ ] 功能需求明確，有詳細的設計文档
- [ ] 創建了合適的分支名稱和描述
- [ ] 編寫了完整的單元測試
- [ ] 代碼符合項目編碼規範
- [ ] 更新了相關文档
- [ ] 通過了所有自動化測試
- [ ] 進行了代碼審查
- [ ] 測試了与現有功能的兼容性

### 2. 中文增强開發流程

#### 本地化功能開發
```bash
# 步骤1: 創建增强分支
python scripts/branch_manager.py create enhancement tushare-integration -d "集成Tushare A股數據源"

# 步骤2: 開發中文功能
# 集成中文數據源
git add tradingagents/data/tushare_source.py
git commit -m "enhance(data): 添加Tushare數據源適配器"

# 添加中文配置
git add config/chinese_config.yaml
git commit -m "enhance(config): 添加中文市場配置"

# 步骤3: 更新中文文档
git add docs/data/tushare-integration.md
git commit -m "docs: 添加Tushare集成文档"

# 步骤4: 中文功能測試
python -m pytest tests/test_tushare_integration.py
git add tests/test_tushare_integration.py
git commit -m "test: 添加Tushare集成測試"

# 步骤5: 推送和合並
git push origin enhancement/tushare-integration
# 創建PR到develop分支
```

#### 中文增强檢查清單
- [ ] 功能適配中國金融市場特點
- [ ] 添加了完整的中文文档
- [ ] 支持中文金融術語
- [ ] 兼容現有的國际化功能
- [ ] 測試了中文數據處理
- [ ] 更新了配置文件和示例

### 3. 緊急修複流程

#### 生產環境Bug修複
```bash
# 步骤1: 從main創建修複分支
python scripts/branch_manager.py create hotfix api-timeout-fix -d "修複API請求超時問題"

# 步骤2: 快速定位和修複
# 分析問題根因
# 實施最小化修複
git add tradingagents/api/client.py
git commit -m "fix: 增加API請求超時重試機制"

# 步骤3: 緊急測試
python -m pytest tests/test_api_client.py -v
# 手動測試關键路徑

# 步骤4: 立即部署到main
git push origin hotfix/api-timeout-fix
# 創建PR到main，標記為緊急修複

# 步骤5: 同步到develop
git checkout develop
git merge main
git push origin develop
```

#### 緊急修複檢查清單
- [ ] 問題影響評估和優先級確認
- [ ] 實施最小化修複方案
- [ ] 通過了關键路徑測試
- [ ] 有回滚計劃
- [ ] 同步到所有相關分支
- [ ] 通知相關团隊成員

### 4. 版本發布流程

#### 正式版本發布
```bash
# 步骤1: 創建發布分支
python scripts/branch_manager.py create release v1.1.0-cn -d "v1.1.0中文增强版發布"

# 步骤2: 版本準备
# 更新版本號
echo "1.1.0-cn" > VERSION
git add VERSION
git commit -m "bump: 版本號更新到v1.1.0-cn"

# 更新變更日誌
git add CHANGELOG.md
git commit -m "docs: 更新v1.1.0-cn變更日誌"

# 最终測試
python -m pytest tests/ --cov=tradingagents
python examples/full_test.py

# 步骤3: 合並到main
git checkout main
git merge release/v1.1.0-cn
git tag v1.1.0-cn
git push origin main --tags

# 步骤4: 回合並到develop
git checkout develop
git merge main
git push origin develop

# 步骤5: 清理發布分支
python scripts/branch_manager.py delete release/v1.1.0-cn
```

#### 版本發布檢查清單
- [ ] 所有計劃功能已完成並合並
- [ ] 通過了完整的測試套件
- [ ] 更新了版本號和變更日誌
- [ ] 創建了版本標簽
- [ ] 準备了發布說明
- [ ] 通知了用戶和社区

### 5. 上游同步集成流程

#### 与原項目保持同步
```bash
# 步骤1: 檢查上游更新
python scripts/sync_upstream.py

# 步骤2: 如果有更新，會自動創建同步分支
# upstream-sync/20240115

# 步骤3: 解決可能的冲突
# 保護我們的中文文档和增强功能
# 採用上游的核心代碼更新

# 步骤4: 測試同步結果
python -m pytest tests/
python examples/basic_example.py

# 步骤5: 合並到主分支
git checkout main
git merge upstream-sync/20240115
git push origin main

# 步骤6: 同步到develop
git checkout develop
git merge main
git push origin develop
```

## 📈 最佳實踐

### 開發建议

1. **小而頻繁的提交** - 每個提交解決一個具體問題
2. **描述性分支名** - 清楚表達分支用途
3. **及時同步** - 定期從develop拉取最新更改
4. **完整測試** - 合並前確保所有測試通過
5. **文档同步** - 功能開發同時更新文档

### 協作規範

1. **PR模板** - 使用標準的PR描述模板
2. **代碼審查** - 至少一人審查後合並
3. **冲突解決** - 及時解決合並冲突
4. **分支清理** - 及時刪除已合並分支
5. **版本標記** - 重要節點創建版本標簽

### 质量保證

1. **自動化測試** - 每個PR都要通過CI測試
2. **代碼覆蓋率** - 保持80%以上的測試覆蓋率
3. **性能測試** - 重要功能要進行性能測試
4. **安全扫描** - 定期進行安全漏洞扫描
5. **文档更新** - 功能變更同步更新文档

通過這套完整的分支管理策略和開發工作流，我們可以確保項目開發的有序進行，同時保持代碼质量和發布穩定性。

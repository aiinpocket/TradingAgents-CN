# 上游同步策略

## 概述

本文檔詳細說明如何保持 TradingAgents-CN 與原項目 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 的同步。

## 🎯 同步目標

### 主要目標
- **保持技術先進性**: 及時獲得原項目的新功能和改進
- **修複安全問題**: 快速同步安全補丁和Bug修複
- **維護兼容性**: 確保中文增強功能與原項目兼容
- **減少維護成本**: 避免重複開發已有功能

### 平衡原則
- **核心功能同步**: 同步所有核心功能更新
- **文檔保持獨立**: 保持我們的中文文檔體系
- **增強功能保護**: 保護我們的中文增強功能
- **衝突優雅處理**: 妥善處理合並衝突

## 🔄 同步策略

### 1. 監控策略

#### 自動監控
```bash
# 設置GitHub通知
# 1. 訪問 https://github.com/TauricResearch/TradingAgents
# 2. 點擊 "Watch" -> "Custom" -> 選擇 "Releases" 和 "Issues"
# 3. 啟用邮件通知
```

#### 定期檢查
- **每周檢查**: 檢查是否有新的提交和發布
- **每月深度同步**: 進行完整的同步和測試
- **重要更新立即同步**: 安全補丁和重大Bug修複

### 2. 分支策略

```
main (我們的主分支)
├── upstream-sync-YYYYMMDD (同步分支)
├── feature/chinese-enhancement (中文增強功能)
└── hotfix/urgent-fixes (緊急修複)

upstream/main (原項目主分支)
```

#### 分支說明
- **main**: 我們的穩定主分支，包含所有中文增強
- **upstream-sync-YYYYMMDD**: 臨時同步分支，用於合並上游更新
- **feature/chinese-enhancement**: 我們的功能增強分支
- **hotfix/urgent-fixes**: 緊急修複分支

### 3. 同步流程

#### 標準同步流程

```bash
# 1. 檢查當前狀態
git status
git log --oneline -5

# 2. 獲取上游更新
git fetch upstream

# 3. 檢查新提交
git log --oneline HEAD..upstream/main

# 4. 使用自動化腳本同步
python scripts/sync_upstream.py

# 5. 解決衝突（如果有）
# 手動編辑衝突文件
git add <resolved_files>
git commit

# 6. 測試同步結果
python -m pytest tests/
python examples/basic_example.py

# 7. 推送更新
git push origin main
```

#### 使用自動化腳本

```bash
# 基本同步
python scripts/sync_upstream.py

# 使用rebase策略
python scripts/sync_upstream.py --strategy rebase

# 自動模式（不詢問確認）
python scripts/sync_upstream.py --auto
```

## ⚠️ 衝突處理策略

### 常見衝突類型

#### 1. 文檔衝突
**原因**: 我們有完整的中文文檔，原項目可能更新英文文檔

**處理策略**:
```bash
# 保持我們的中文文檔，參考原項目更新內容
# 衝突文件: README.md, docs/
# 解決方案: 保留我們的版本，手動同步有價值的內容
```

#### 2. 配置文件衝突
**原因**: 配置文件格式或默認值變更

**處理策略**:
```bash
# 仔細比較差異，合並有價值的配置
git diff HEAD upstream/main -- config/
# 手動合並配置更改
```

#### 3. 代碼功能衝突
**原因**: 核心代碼邏輯變更

**處理策略**:
```bash
# 優先採用上游版本，然後重新應用我們的增強
# 1. 接受上游版本
git checkout --theirs <conflicted_file>
# 2. 重新應用我們的增強功能
# 3. 測試確保功能正常
```

### 衝突解決優先級

1. **安全修複**: 最高優先級，立即採用上游版本
2. **Bug修複**: 高優先級，通常採用上游版本
3. **新功能**: 中等優先級，評估後決定是否採用
4. **文檔更新**: 低優先級，保持我們的中文版本
5. **配置變更**: 低優先級，谨慎合並

## 📋 同步檢查清單

### 同步前檢查
- [ ] 當前分支是否干淨（無未提交更改）
- [ ] 是否有正在進行的功能開發
- [ ] 是否有未解決的Issue需要考慮
- [ ] 備份當前狀態（創建標簽）

### 同步過程檢查
- [ ] 上游更新是否獲取成功
- [ ] 新提交是否包含重大變更
- [ ] 是否存在合並衝突
- [ ] 衝突是否正確解決

### 同步後檢查
- [ ] 代碼是否能正常運行
- [ ] 測試是否全部通過
- [ ] 文檔是否需要更新
- [ ] 中文增強功能是否正常
- [ ] 配置文件是否正確

## 🧪 測試策略

### 自動化測試
```bash
# 運行完整測試套件
python -m pytest tests/ -v

# 運行基本功能測試
python examples/basic_example.py

# 運行性能測試
python tests/performance_test.py
```

### 手動測試
```bash
# 測試核心功能
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
state, decision = ta.propagate('AAPL', '2024-01-15')
print(f'Decision: {decision}')
"

# 測試中文文檔
# 檢查 docs/ 目錄下的文檔是否正常顯示
```

## 📊 同步記錄

### 同步日誌格式
```json
{
  "sync_time": "2024-01-15T10:30:00Z",
  "upstream_commits": 5,
  "conflicts_resolved": 2,
  "files_changed": ["tradingagents/core.py", "config/default.yaml"],
  "tests_passed": true,
  "notes": "同步了新的風險管理功能"
}
```

### 版本標記策略
```bash
# 同步前創建標簽
git tag -a v1.0.0-cn-pre-sync -m "同步前狀態"

# 同步後創建標簽
git tag -a v1.0.1-cn -m "同步上游更新 v1.2.3"

# 推送標簽
git push origin --tags
```

## 🚨 應急處理

### 同步失敗回滾
```bash
# 回滾到同步前狀態
git reset --hard v1.0.0-cn-pre-sync

# 或者回滾到上一個提交
git reset --hard HEAD~1

# 強制推送（谨慎使用）
git push origin main --force-with-lease
```

### 緊急熱修複
```bash
# 創建熱修複分支
git checkout -b hotfix/urgent-fix

# 應用修複
# ... 修複代碼 ...

# 快速合並
git checkout main
git merge hotfix/urgent-fix
git push origin main

# 刪除熱修複分支
git branch -d hotfix/urgent-fix
```

## 📅 同步計劃

### 定期同步計劃
- **每周一**: 檢查上游更新，評估同步需求
- **每月第一周**: 進行完整同步和測試
- **重大版本發布後**: 立即評估和同步

### 特殊情況處理
- **安全漏洞**: 24小時內同步
- **重大Bug**: 48小時內同步
- **新功能**: 1周內評估，2周內同步

## 🤝 社群協作

### 與原項目互動
- **Issue報告**: 向原項目報告發現的Bug
- **功能建議**: 提出有價值的功能建議
- **代碼貢獻**: 將通用改進貢獻回原項目

### 維護透明度
- **同步日誌**: 公開同步記錄和決策過程
- **變更說明**: 詳細說明每次同步的內容
- **用戶通知**: 及時通知用戶重要更新

通過這套完整的同步策略，我們可以確保 TradingAgents-CN 始終保持與原項目的技術同步，同時維護我們獨特的中文增強價值。

# 緊急回滚和事故處理程序

## 🚨 緊急情况分類

### 1級：嚴重生產事故
- 系統完全無法使用
- 數據丢失或損坏
- 安全漏洞暴露

### 2級：功能性問題
- 核心功能異常
- 性能嚴重下降
- 部分用戶受影響

### 3級：一般性問題
- 非核心功能異常
- 轻微性能問題
- 少數用戶受影響

## 🔄 立即回滚程序

### 步骤1：確認問題嚴重性
```bash
# 檢查當前版本
git log --oneline -5

# 確認最後已知穩定版本
git log --oneline --grep="stable" -10
```

### 步骤2：執行緊急回滚
```bash
# 切換到 main 分支
git checkout main

# 回滚到最後已知穩定版本
git reset --hard <穩定版本SHA>

# 强制推送（需要明確確認風險）
git push origin main --force-with-lease
```

### 步骤3：驗證回滚成功
```bash
# 確認當前版本
git rev-parse HEAD

# 檢查系統狀態
python -c "import tradingagents; print('導入成功')"
```

## 📋 事故處理檢查清單

### 立即響應（0-15分鐘）
- [ ] 確認事故嚴重性級別
- [ ] 通知相關人員
- [ ] 記錄事故開始時間
- [ ] 評估是否需要立即回滚
- [ ] 執行回滚操作（如需要）
- [ ] 驗證回滚成功

### 短期處理（15分鐘-2小時）
- [ ] 創建事故分析分支
- [ ] 收集錯誤日誌和信息
- [ ] 分析根本原因
- [ ] 制定修複計劃
- [ ] 評估影響範围
- [ ] 更新利益相關者

### 中期修複（2-24小時）
- [ ] 在修複分支中開發解決方案
- [ ] 進行充分測試
- [ ] 準备修複部署計劃
- [ ] 代碼審查修複方案
- [ ] 準备回滚計劃（以防修複失败）

### 長期改進（1-7天）
- [ ] 完成事故後分析報告
- [ ] 识別流程改進點
- [ ] 更新文档和程序
- [ ] 實施預防措施
- [ ] 团隊回顧和學习

## 🔧 常用回滚命令

### 查找穩定版本
```bash
# 查看最近的標簽版本
git tag --sort=-version:refname | head -10

# 查看包含"stable"的提交
git log --oneline --grep="stable" -20

# 查看發布相關的提交
git log --oneline --grep="release\\|版本" -20
```

### 不同類型的回滚
```bash
# 1. 回滚到特定提交（推薦）
git reset --hard <commit-sha>

# 2. 回滚最近的几個提交
git reset --hard HEAD~<數量>

# 3. 創建反向提交（保留歷史）
git revert <commit-sha>

# 4. 回滚到特定標簽
git reset --hard <tag-name>
```

### 强制推送選項
```bash
# 推薦：安全的强制推送
git push origin main --force-with-lease

# 谨慎：完全强制推送（可能覆蓋他人工作）
git push origin main --force

# 最安全：先备份分支
git push origin main:backup-before-rollback
git push origin main --force-with-lease
```

## 🛡️ 預防措施

### 1. 定期备份
```bash
# 每日备份重要分支
git push origin main:backup-$(date +%Y%m%d)
git push origin develop:backup-develop-$(date +%Y%m%d)
```

### 2. 標記穩定版本
```bash
# 在確認穩定後打標簽
git tag -a v0.1.13-stable -m "穩定版本 v0.1.13"
git push origin v0.1.13-stable
```

### 3. 監控和警報
- 設置自動化測試在每次推送後運行
- 配置錯誤日誌監控
- 建立性能監控基線

## 📞 緊急聯系流程

### 聯系顺序
1. **項目负责人**：立即通知
2. **技術负责人**：協助技術決策
3. **測試负责人**：驗證修複方案
4. **運維负责人**：監控系統狀態

### 沟通模板
```
【緊急事故通知】
事故級別：[1級/2級/3級]
發生時間：[YYYY-MM-DD HH:mm]
影響範围：[描述]
當前狀態：[已回滚/修複中/調查中]
預計恢複：[時間估計]
负责人：[姓名]
```

## 📊 事故報告模板

### 事故概述
- 事故開始時間：
- 事故結束時間：
- 影響持续時間：
- 嚴重性級別：
- 影響用戶數量：

### 時間線
- [時間] 事故發生
- [時間] 事故發現
- [時間] 開始響應
- [時間] 執行回滚
- [時間] 服務恢複
- [時間] 根本原因確認

### 根本原因分析
- 直接原因：
- 根本原因：
- 贡献因素：

### 修複措施
- 立即修複：
- 短期改進：
- 長期預防：

### 經驗教训
- 做得好的地方：
- 需要改進的地方：
- 行動計劃：

## 🔄 測試環境快速恢複

### 創建測試環境
```bash
# 克隆仓庫到測試目錄
git clone . ../TradingAgentsCN-test
cd ../TradingAgentsCN-test

# 切換到問題版本進行調試
git checkout <問題版本SHA>

# 安裝依賴進行測試
pip install -r requirements.txt
```

### 問題複現和驗證
```bash
# 運行相關測試
python -m pytest tests/ -v

# 檢查特定功能
python -c "
import sys
sys.path.append('.')
# 測試有問題的功能
"
```

---

**記住：在緊急情况下，穩定性優於完美性。先恢複服務，再慢慢修複問題！**
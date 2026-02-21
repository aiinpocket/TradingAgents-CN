# Scripts Directory

這個目錄包含TradingAgentsCN項目的各種腳本工具，按功能分類組織。

## 目錄結構

###  setup/ - 安裝和配置腳本
- 環境設置
- 依賴安裝
- API配置
- 資料庫設置

###  validation/ - 驗證腳本
- Git配置驗證
- 依賴檢查
- 配置驗證
- API連接測試

###  maintenance/ - 維護腳本
- 緩存清理
- 資料備份
- 依賴更新
- 上游同步
- 分支管理

###  development/ - 開發輔助腳本
- 代碼分析
- 性能基準測試
- 文檔生成
- 貢獻準備
- 資料下載

###  deployment/ - 部署腳本
- GitHub發布
- 版本發布
- 打包部署

###  docker/ - Docker腳本
- Docker服務管理
- 容器啟動停止
- 資料庫初始化

###  git/ - Git工具腳本
- 上游同步
- Fork環境設置
- 貢獻工作流

## 使用原則

### 腳本分類
- **tests/** - 單元測試和集成測試（pytest運行）
- **scripts/** - 工具腳本和驗證腳本（獨立運行）
- **utils/** - 實用工具腳本

### 運行方式
```bash
# 從項目根目錄運行
cd C:\code\TradingAgentsCN

# Python腳本
python scripts/validation/verify_gitignore.py

# PowerShell腳本  
powershell -ExecutionPolicy Bypass -File scripts/maintenance/cleanup.ps1

# Bash腳本
bash scripts/git/upstream_git_workflow.sh
```

## 目錄說明

| 目錄 | 用途 | 示例腳本 |
|------|------|----------|
| `setup/` | 環境配置和初始化 | setup_databases.py |
| `validation/` | 驗證和檢查 | verify_gitignore.py |
| `maintenance/` | 維護和管理 | sync_upstream.py |
| `development/` | 開發輔助 | prepare_upstream_contribution.py |
| `deployment/` | 部署發布 | create_github_release.py |
| `docker/` | 容器管理 | start_docker_services.bat |
| `git/` | Git工具 | upstream_git_workflow.sh |

## 註意事項

- 所有腳本應該從項目根目錄運行
- 檢查腳本的依賴要求
- 某些腳本可能需要特殊權限
- 保持腳本的獨立性和可重用性

## 開發指南

### 添加新腳本
1. 確定腳本類型和目標目錄
2. 建立腳本檔案
3. 添加適當的文檔註釋
4. 更新相應目錄的README
5. 測試腳本功能

### 腳本模板
每個腳本應包含：
- 檔案頭註釋說明用途
- 使用方法說明
- 依賴要求
- 錯誤處理
- 日誌輸出

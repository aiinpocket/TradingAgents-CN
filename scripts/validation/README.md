# Validation Scripts

## 目錄說明

這個目錄包含各種驗證腳本，用於檢查項目配置、依賴、Git設置等。

## 腳本列表

- `verify_gitignore.py` - 驗證Git忽略配置，確保docs/contribution目錄不被版本控制
- `check_dependencies.py` - 檢查項目依賴是否正確安裝
- `smart_config.py` - 智能配置檢測和管理

## 使用方法

```bash
# 進入項目根目錄
cd C:\code\TradingAgentsCN

# 運行驗證腳本
python scripts/validation/verify_gitignore.py
python scripts/validation/check_dependencies.py
python scripts/validation/smart_config.py
```

## 驗證腳本 vs 測試腳本的区別

### 驗證腳本 (scripts/validation/)
- **目的**: 檢查項目配置、環境設置、依賴狀態
- **運行時機**: 開發環境設置、部署前檢查、問題排查
- **特點**: 獨立運行，提供詳細的檢查報告和修複建议

### 測試腳本 (tests/)
- **目的**: 驗證代碼功能正確性
- **運行時機**: 開發過程中、CI/CD流程
- **特點**: 使用pytest框架，專註於代碼逻辑測試

## 註意事項

- 確保在項目根目錄下運行腳本
- 驗證腳本會檢查系統狀態並提供修複建议
- 某些驗證可能需要網絡連接或特定權限
- 驗證失败時會提供詳細的錯誤信息和解決方案

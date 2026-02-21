# 數據目錄配置指南 | Data Directory Configuration Guide

本指南詳細說明如何在TradingAgents中配置數據目錄路徑，解決路徑相關問題，並提供多種配置方式。

This guide explains how to configure data directory paths in TradingAgents, resolve path-related issues, and provides multiple configuration methods.

## 概述 | Overview

TradingAgents支持靈活的數據目錄配置，允許用戶：
- 自定義數據存儲位置
- 通過環境變量配置
- 使用CLI命令管理
- 自動創建必要的目錄結構

TradingAgents supports flexible data directory configuration, allowing users to:
- Customize data storage locations
- Configure via environment variables
- Manage through CLI commands
- Automatically create necessary directory structures

## 配置方法 | Configuration Methods

### 1. CLI命令配置 | CLI Command Configuration

#### 查看當前配置 | View Current Configuration
```bash
# 顯示當前數據目錄配置
python -m cli.main data-config
python -m cli.main data-config --show
```

#### 設置自定義數據目錄 | Set Custom Data Directory
```bash
# Windows
python -m cli.main data-config --set "C:\MyTradingData"

# Linux/macOS
python -m cli.main data-config --set "/home/user/trading-data"
```

#### 重置為默認配置 | Reset to Default Configuration
```bash
python -m cli.main data-config --reset
```

### 2. 環境變量配置 | Environment Variable Configuration

#### Windows
```cmd
# 設置數據目錄
set TRADINGAGENTS_DATA_DIR=C:\MyTradingData

# 設置緩存目錄
set TRADINGAGENTS_CACHE_DIR=C:\MyTradingData\cache

# 設置結果目錄
set TRADINGAGENTS_RESULTS_DIR=C:\MyTradingData\results
```

#### Linux/macOS
```bash
# 設置數據目錄
export TRADINGAGENTS_DATA_DIR="/home/user/trading-data"

# 設置緩存目錄
export TRADINGAGENTS_CACHE_DIR="/home/user/trading-data/cache"

# 設置結果目錄
export TRADINGAGENTS_RESULTS_DIR="/home/user/trading-data/results"
```

#### .env文件配置 | .env File Configuration
```env
# 在項目根目錄創建.env文件
TRADINGAGENTS_DATA_DIR=/path/to/your/data
TRADINGAGENTS_CACHE_DIR=/path/to/your/cache
TRADINGAGENTS_RESULTS_DIR=/path/to/your/results
```

### 3. 程序化配置 | Programmatic Configuration

```python
from tradingagents.dataflows.config import set_data_dir, get_data_dir
from tradingagents.config.config_manager import config_manager

# 設置數據目錄
set_data_dir("/path/to/custom/data")

# 獲取當前數據目錄
current_dir = get_data_dir()
print(f"當前數據目錄: {current_dir}")

# 確保目錄存在
config_manager.ensure_directories_exist()
```

## 目錄結構 | Directory Structure

配置數據目錄後，系統會自動創建以下目錄結構：

After configuring the data directory, the system automatically creates the following directory structure:

```
data/
├── cache/                          # 緩存目錄 | Cache directory
├── finnhub_data/                   # Finnhub數據目錄 | Finnhub data directory
│   ├── news_data/                  # 新聞數據 | News data
│   ├── insider_sentiment/          # 內部人情緒數據 | Insider sentiment data
│   └── insider_transactions/       # 內部人交易數據 | Insider transaction data
└── results/                        # 分析結果 | Analysis results
```

## 配置優先級 | Configuration Priority

配置的優先級從高到低：

Configuration priority from high to low:

1. **環境變量** | Environment Variables
2. **CLI設置** | CLI Settings
3. **默認配置** | Default Configuration

## 默認配置 | Default Configuration

如果沒有自定義配置，系統使用以下默認路徑：

If no custom configuration is provided, the system uses the following default paths:

- **Windows**: `C:\Users\{username}\Documents\TradingAgents\data`
- **Linux/macOS**: `~/Documents/TradingAgents/data`

## 常見問題解決 | Troubleshooting

### 問題1：路徑不存在錯誤 | Issue 1: Path Not Found Error

**錯誤信息** | Error Message:
```
No such file or directory: '/data/finnhub_data/news_data'
```

**解決方案** | Solution:
```bash
# 使用CLI重新配置數據目錄
python -m cli.main data-config --set "C:\YourDataPath"

# 或重置為默認配置
python -m cli.main data-config --reset
```

### 問題2：權限不足 | Issue 2: Permission Denied

**解決方案** | Solution:
1. 確保對目標目錄有寫權限
2. 選擇用戶目錄下的路徑
3. 在Windows上以管理員身份運行

### 問題3：跨平台路徑問題 | Issue 3: Cross-Platform Path Issues

**解決方案** | Solution:
- 使用正斜杠 `/` 或雙反斜杠 `\\` 在Windows上
- 避免硬編碼路徑分隔符
- 使用環境變量進行跨平台配置

## 驗證配置 | Verify Configuration

### 1. 使用CLI驗證 | Verify Using CLI
```bash
python -m cli.main data-config --show
```

### 2. 使用測試腳本驗證 | Verify Using Test Script
```bash
python test_data_config_cli.py
```

### 3. 使用演示腳本驗證 | Verify Using Demo Script
```bash
python examples/data_dir_config_demo.py
```

## 最佳實踐 | Best Practices

1. **使用絕對路徑** | Use Absolute Paths
   - 避免相對路徑可能導致的問題
   - Avoid issues that relative paths might cause

2. **定期備份數據** | Regular Data Backup
   - 重要的分析結果應定期備份
   - Important analysis results should be backed up regularly

3. **環境隔離** | Environment Isolation
   - 不同項目使用不同的數據目錄
   - Use different data directories for different projects

4. **權限管理** | Permission Management
   - 確保應用程序對數據目錄有適當權限
   - Ensure the application has appropriate permissions to the data directory

## 高級配置 | Advanced Configuration

### 自定義子目錄結構 | Custom Subdirectory Structure

```python
from tradingagents.config.config_manager import config_manager

# 自定義目錄結構
custom_dirs = {
    'custom_data': 'my_custom_data',
    'reports': 'analysis_reports',
    'logs': 'application_logs'
}

# 創建自定義目錄
for dir_name, dir_path in custom_dirs.items():
    full_path = os.path.join(config_manager.get_data_dir(), dir_path)
    os.makedirs(full_path, exist_ok=True)
```

### 動態配置更新 | Dynamic Configuration Updates

```python
# 運行時更新配置
config_manager.set_data_dir('/new/data/path')
config_manager.ensure_directories_exist()

# 驗證更新
print(f"新數據目錄: {config_manager.get_data_dir()}")
```

## 相關文件 | Related Files

- `tradingagents/config/config_manager.py` - 配置管理器
- `tradingagents/dataflows/config.py` - 數據流配置
- `cli/main.py` - CLI命令實現
- `examples/data_dir_config_demo.py` - 配置演示腳本
- `test_data_config_cli.py` - 配置測試腳本

## 技術支持 | Technical Support

如果遇到配置問題，請：
1. 查看錯誤日誌
2. 運行診斷腳本
3. 檢查權限設置
4. 參考故障排除指南

If you encounter configuration issues, please:
1. Check error logs
2. Run diagnostic scripts
3. Check permission settings
4. Refer to the troubleshooting guide
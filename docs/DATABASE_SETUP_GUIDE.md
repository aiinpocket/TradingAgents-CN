# 數據庫依賴包安裝指南

## 🎯 概述

本指南幫助您正確安裝TradingAgents的數據庫依賴包，解決Python 3.10+環境下的兼容性問題。

## ⚠️ 重要提醒

- **Python版本要求**: Python 3.10 或更高版本
- **已知問題**: `pickle5` 包在Python 3.10+中會導致兼容性問題
- **推薦方式**: 使用更新後的 `requirements_db.txt`

## 🔧 快速檢查

在安裝前，運行兼容性檢查工具：

```bash
python check_db_requirements.py
```

這個工具會：
- ✅ 檢查Python版本是否符合要求
- ✅ 檢查已安裝的包版本
- ✅ 识別兼容性問題
- ✅ 提供具體的解決方案

## 📦 安裝步骤

### 1. 檢查Python版本

```bash
python --version
```

確保版本 ≥ 3.10.0

### 2. 創建虛擬環境（推薦）

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 升級pip

```bash
python -m pip install --upgrade pip
```

### 4. 安裝數據庫依賴

```bash
pip install -r requirements_db.txt
```

## 🐛 常见問題解決

### 問題1: pickle5 兼容性錯誤

**錯誤信息**:
```
ImportError: cannot import name 'pickle5' from 'pickle'
```

**解決方案**:
```bash
# 卸載pickle5包
pip uninstall pickle5

# Python 3.10+已內置pickle協议5支持，無需額外安裝
```

### 問題2: 版本冲突

**錯誤信息**:
```
ERROR: pip's dependency resolver does not currently have a backtracking
```

**解決方案**:
```bash
# 清理現有安裝
pip uninstall pymongo motor redis hiredis pandas numpy

# 重新安裝
pip install -r requirements_db.txt
```

### 問題3: MongoDB連接問題

**錯誤信息**:
```
pymongo.errors.ServerSelectionTimeoutError
```

**解決方案**:
1. 確保MongoDB服務正在運行
2. 檢查連接字符串配置
3. 驗證網絡連接

### 問題4: Redis連接問題

**錯誤信息**:
```
redis.exceptions.ConnectionError
```

**解決方案**:
1. 確保Redis服務正在運行
2. 檢查Redis配置
3. 驗證端口和密碼設置

## 📋 依賴包詳情

| 包名 | 版本要求 | 用途 | 必需性 |
|------|----------|------|--------|
| pymongo | 4.3.0 - 4.x | MongoDB驱動 | 必需 |
| motor | 3.1.0 - 3.x | 異步MongoDB | 可選 |
| redis | 4.5.0 - 5.x | Redis驱動 | 必需 |
| hiredis | 2.0.0 - 2.x | Redis性能優化 | 可選 |
| pandas | 1.5.0 - 2.x | 數據處理 | 必需 |
| numpy | 1.21.0 - 1.x | 數值計算 | 必需 |

## 🔍 驗證安裝

運行以下命令驗證安裝：

```python
# 測試MongoDB連接
python -c "import pymongo; print('MongoDB驱動安裝成功')"

# 測試Redis連接
python -c "import redis; print('Redis驱動安裝成功')"

# 測試數據處理包
python -c "import pandas, numpy; print('數據處理包安裝成功')"

# 測試pickle兼容性
python -c "import pickle; print(f'Pickle協议版本: {pickle.HIGHEST_PROTOCOL}')"
```

## 🚀 Docker方式（推薦）

如果遇到依賴問題，推薦使用Docker：

```bash
# 構建Docker鏡像
docker-compose build

# 啟動服務
docker-compose up -d
```

Docker方式會自動處理所有依賴關系。

## 📞 獲取幫助

如果仍然遇到問題：

1. **運行診斷工具**: `python check_db_requirements.py`
2. **查看詳細日誌**: 啟用詳細模式安裝 `pip install -v -r requirements_db.txt`
3. **提交Issue**: 在GitHub仓庫提交問題，包含：
   - Python版本
   - 操作系統信息
   - 完整錯誤信息
   - 診斷工具輸出

## 📝 更新日誌

### v0.1.7
- ✅ 移除pickle5依賴，解決Python 3.10+兼容性問題
- ✅ 更新包版本要求，提高穩定性
- ✅ 添加兼容性檢查工具
- ✅ 完善安裝指南和故障排除

### 歷史版本
- v0.1.6: 初始數據庫支持
- v0.1.5: 基础依賴包配置

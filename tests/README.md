# TradingAgents-CN 測試目錄

這個目錄包含了 TradingAgents-CN 專案的所有測試檔案，用於驗證功能正確性、API 整合和模型測試。

## 目錄結構

```
tests/
├── README.md                           # 本文件
├── __init__.py                         # Python 套件初始化
├── test_*.py                          # 各種功能測試
└── debug_*.py                         # 除錯和診斷工具
```

## 測試分類

### API 和整合測試
- `test_all_apis.py` - 所有 API 金鑰測試
- `test_correct_apis.py` - Google 和 Reddit API 測試
- `test_toolkit_tools.py` - 工具套件測試

### 效能測試
- `test_redis_performance.py` - Redis 效能基準測試
- `quick_redis_test.py` - Redis 快速連線測試

### AI 模型測試
- `test_gemini*.py` - Google Gemini 模型系列測試
- `test_google_memory_fix.py` - Google AI 記憶體功能測試

### Web 介面測試
- `test_web_fix.py` - Web 介面功能測試

### 除錯和診斷工具
- `debug_imports.py` - 匯入問題診斷
- `diagnose_gemini_25.py` - Gemini 2.5 模型診斷
- `check_gemini_models.py` - Gemini 模型可用性檢查

### 功能測試
- `test_analysis.py` - 基礎分析功能測試
- `test_format_fix.py` - 格式化修復測試
- `test_progress.py` - 進度追蹤測試

## 執行測試

### 執行所有測試
```bash
# 從專案根目錄執行
python -m pytest tests/

# 或者直接執行特定測試
cd tests
python test_gemini_correct.py
```

### 執行特定類別的測試
```bash
# API 測試
python tests/test_all_apis.py

# Gemini 模型測試
python tests/test_gemini_correct.py

# Web 介面測試
python tests/test_web_fix.py

# Redis 效能測試
python tests/quick_redis_test.py
python tests/test_redis_performance.py
```

### 診斷工具
```bash
# 診斷 Gemini 模型問題
python tests/diagnose_gemini_25.py

# 檢查匯入問題
python tests/debug_imports.py

# 檢查所有可用的 Gemini 模型
python tests/check_gemini_models.py
```

## 測試環境要求

### 必需的環境變數
在執行測試前，請確保在 `.env` 檔案中配置了以下 API 金鑰：

```env
# OpenAI API（推薦）
OPENAI_API_KEY=your_openai_key

# Google AI API（可選，用於 Gemini 測試）
GOOGLE_API_KEY=your_google_key

# 金融資料 API（可選）
FINNHUB_API_KEY=your_finnhub_key

# Reddit API（可選）
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=your_user_agent
```

### Python 相依套件
```bash
pip install -r requirements.txt
```

### 測試結果解讀
- **所有測試通過**：功能完全正常，可以使用完整功能
- **部分測試通過**：基本功能正常，可能需要檢查配置
- **大部分測試失敗**：存在問題，需要排查 API 金鑰和環境配置

## 貢獻指南

新增測試時，請遵循以下規範：

1. **測試檔案命名**: `test_功能名稱.py`
2. **除錯工具命名**: `debug_問題描述.py` 或 `diagnose_問題描述.py`
3. **測試函式命名**: `test_具體功能()`
4. **文件**: 在函式開頭添加清晰的文件字串
5. **分類**: 根據功能將測試放在適當的類別中

### 測試範本

```python
#!/usr/bin/env python3
"""
新功能測試
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 載入環境變數
load_dotenv(project_root / ".env", override=True)

def test_new_feature():
    """測試新功能"""
    try:
        print("測試新功能")
        print("=" * 50)

        # 測試程式碼

        print("測試成功")
        return True
    except Exception as e:
        print(f"測試失敗: {e}")
        return False

def main():
    """主測試函式"""
    print("新功能測試")
    print("=" * 60)

    success = test_new_feature()

    if success:
        print("所有測試通過!")
    else:
        print("測試失敗")

if __name__ == "__main__":
    main()
```

## 最近更新

- 新增 Google Gemini 模型系列測試
- 新增 Web 介面 Google 模型選擇測試
- 新增 API 整合測試（Google、Reddit）
- 新增記憶體系統測試
- 整理所有測試檔案到 tests 目錄
- 新增除錯和診斷工具

## 測試最佳實踐

1. **測試隔離**：每個測試應該獨立執行
2. **清晰命名**：測試函式名應該清楚描述測試內容
3. **錯誤處理**：測試應該能夠處理各種錯誤情況
4. **文件化**：為複雜的測試添加詳細註釋
5. **快速回饋**：測試應該盡快給出結果

## 故障排除

### 常見問題
1. **API 金鑰問題** - 檢查 .env 檔案配置
2. **網路連線問題** - 確認網路和防火牆設定
3. **相依套件問題** - 確保所有相依套件已安裝
4. **模型相容性** - 檢查模型名稱和版本

### 除錯技巧
1. 啟用詳細輸出查看錯誤訊息
2. 單獨執行測試函式定位問題
3. 使用診斷工具檢查配置
4. 查看 Web 應用日誌了解執行狀態

## 授權條款

本專案遵循 Apache 2.0 授權條款。


## 新增的測試檔案

### 整合測試
- `quick_test.py` - 快速整合測試，驗證基本功能
- `test_smart_system.py` - 智慧系統完整測試

### 執行方法
```bash
# 快速測試
python tests/quick_test.py

# 智慧系統測試
python tests/test_smart_system.py
```

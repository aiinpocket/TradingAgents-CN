# TradingAgents-CN 測試目錄

這個目錄包含了TradingAgents-CN項目的所有測試文件，用於驗證功能正確性、API集成和模型測試。

## 目錄結構

```
tests/
├── README.md                           # 本文件
├── __init__.py                         # Python包初始化
├── integration/                        # 集成測試
│   ├── __init__.py
│   └── test_dashscope_integration.py   # 阿里百炼集成測試
├── test_*.py                          # 各種功能測試
└── debug_*.py                         # 調試和診斷工具
```

## 測試分類

### 🔧 API和集成測試
- `test_all_apis.py` - 所有API密鑰測試
- `test_correct_apis.py` - Google和Reddit API測試
- `test_analysis_with_apis.py` - API集成分析測試
- `test_toolkit_tools.py` - 工具包測試
- `integration/test_dashscope_integration.py` - 阿里百炼集成測試

### 📊 數據源測試
- `fast_tdx_test.py` - Tushare數據接口快速連接測試
- `test_tdx_integration.py` - Tushare數據接口完整集成測試

### ⚡ 性能測試
- `test_redis_performance.py` - Redis性能基準測試
- `quick_redis_test.py` - Redis快速連接測試

### 🤖 AI模型測試
- `test_chinese_output.py` - 中文輸出測試
- `test_gemini*.py` - Google Gemini模型系列測試
- `test_embedding_models.py` - 嵌入模型測試
- `test_google_memory_fix.py` - Google AI內存功能測試

### 🌐 Web界面測試
- `test_web_interface.py` - Web界面功能測試

### 🔍 調試和診斷工具
- `debug_imports.py` - 導入問題診斷
- `diagnose_gemini_25.py` - Gemini 2.5模型診斷
- `check_gemini_models.py` - Gemini模型可用性檢查

### 🧪 功能測試
- `test_analysis.py` - 基础分析功能測試
- `test_format_fix.py` - 格式化修複測試
- `test_progress.py` - 進度跟蹤測試

## 運行測試

### 運行所有測試
```bash
# 從項目根目錄運行
python -m pytest tests/

# 或者直接運行特定測試
cd tests
python test_chinese_output.py
```

### 運行特定類別的測試
```bash
# API測試
python tests/test_all_apis.py

# Gemini模型測試
python tests/test_gemini_correct.py

# Web界面測試
python tests/test_web_interface.py

# 阿里百炼集成測試
python tests/integration/test_dashscope_integration.py

# Tushare數據接口測試
python tests/fast_tdx_test.py
python tests/test_tdx_integration.py

# Redis性能測試
python tests/quick_redis_test.py
python tests/test_redis_performance.py
```

### 診斷工具
```bash
# 診斷Gemini模型問題
python tests/diagnose_gemini_25.py

# 檢查導入問題
python tests/debug_imports.py

# 檢查所有可用的Gemini模型
python tests/check_gemini_models.py
```

## 測試環境要求

### 必需的環境變量
在運行測試前，請確保在`.env`文件中配置了以下API密鑰：

```env
# 阿里百炼API（必需）
DASHSCOPE_API_KEY=your_dashscope_key

# Google AI API（可選，用於Gemini測試）
GOOGLE_API_KEY=your_google_key

# 金融數據API（可選）
FINNHUB_API_KEY=your_finnhub_key

# Reddit API（可選）
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=your_user_agent
```

### Python依賴
```bash
pip install -r requirements.txt
```

### 測試結果解讀
- **所有測試通過**：功能完全正常，可以使用完整功能
- **部分測試通過**：基本功能正常，可能需要檢查配置
- **大部分測試失败**：存在問題，需要排查API密鑰和環境配置

## 贡献指南

添加新測試時，請遵循以下規範：

1. **測試文件命名**: `test_功能名稱.py`
2. **調試工具命名**: `debug_問題描述.py` 或 `diagnose_問題描述.py`
3. **測試函數命名**: `test_具體功能()`
4. **文档**: 在函數開头添加清晰的文档字符串
5. **分類**: 根據功能将測試放在適當的類別中

### 測試模板

```python
#!/usr/bin/env python3
"""
新功能測試
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_new_feature():
    """測試新功能"""
    try:
        print("🧪 測試新功能")
        print("=" * 50)

        # 測試代碼

        print("✅ 測試成功")
        return True
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 新功能測試")
    print("=" * 60)

    success = test_new_feature()

    if success:
        print("🎉 所有測試通過！")
    else:
        print("❌ 測試失败")

if __name__ == "__main__":
    main()
```

## 最近更新

- ✅ 添加了Google Gemini模型系列測試
- ✅ 添加了Web界面Google模型選擇測試
- ✅ 添加了API集成測試（Google、Reddit）
- ✅ 添加了中文輸出功能測試
- ✅ 添加了內存系統和嵌入模型測試
- ✅ 整理了所有測試文件到tests目錄
- ✅ 添加了調試和診斷工具

## 測試最佳實踐

1. **測試隔離**：每個測試應该獨立運行
2. **清晰命名**：測試函數名應该清楚描述測試內容
3. **錯誤處理**：測試應该能夠處理各種錯誤情况
4. **文档化**：為複雜的測試添加詳細註釋
5. **快速反馈**：測試應该尽快給出結果

## 故障排除

### 常见問題
1. **API密鑰問題** - 檢查.env文件配置
2. **網絡連接問題** - 確認網絡和防火墙設置
3. **依賴包問題** - 確保所有依賴已安裝
4. **模型兼容性** - 檢查模型名稱和版本

### 調試技巧
1. 啟用詳細輸出查看錯誤信息
2. 單獨運行測試函數定位問題
3. 使用診斷工具檢查配置
4. 查看Web應用日誌了解運行狀態

## 許可證

本項目遵循Apache 2.0許可證。


## 新增的測試文件

### 集成測試
- `quick_test.py` - 快速集成測試，驗證基本功能
- `test_smart_system.py` - 智能系統完整測試
- `demo_fallback_system.py` - 降級系統演示和測試

### 運行方法
```bash
# 快速測試
python tests/quick_test.py

# 智能系統測試
python tests/test_smart_system.py

# 降級系統演示
python tests/demo_fallback_system.py
```

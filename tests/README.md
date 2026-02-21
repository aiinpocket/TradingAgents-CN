# TradingAgents-CN 測試目錄

這個目錄包含了 TradingAgents-CN 專案的所有測試檔案，用於驗證功能正確性、API 整合和模型測試。

## 目錄結構

```
tests/
├── README.md                           # 本文件
├── __init__.py                         # Python 套件初始化
└── test_*.py                          # 各種功能測試
```

## 測試分類

### 效能測試
- `test_redis_performance.py` - Redis 效能基準測試
- `quick_redis_test.py` - Redis 快速連線測試

### Web 介面測試
- `test_web_fix.py` - Web 介面功能測試

### 功能測試
- `test_analysis.py` - 基礎分析功能測試
- `test_format_fix.py` - 格式化修復測試
- `test_progress.py` - 進度追蹤測試
- `test_traditional_chinese.py` - 繁體中文檢測測試

### 整合測試
- `quick_test.py` - 快速整合測試，驗證基本功能
- `test_smart_system.py` - 智慧系統完整測試

## 執行測試

### 執行所有測試
```bash
python -m pytest tests/
```

### 執行特定測試
```bash
# Web 介面測試
python tests/test_web_fix.py

# Redis 效能測試
python tests/quick_redis_test.py
python tests/test_redis_performance.py

# 快速整合測試
python tests/quick_test.py
```

## 測試環境要求

### 必需的環境變數
在執行測試前，請確保在 `.env` 檔案中配置了以下 API 金鑰：

```env
# OpenAI API（必需）
OPENAI_API_KEY=your_openai_key

# Anthropic API（可選）
ANTHROPIC_API_KEY=your_anthropic_key

# 金融資料 API（可選）
FINNHUB_API_KEY=your_finnhub_key
```

### Python 相依套件
```bash
pip install -r requirements-lock.txt
```

## 貢獻指南

新增測試時，請遵循以下規範：

1. **測試檔案命名**: `test_功能名稱.py`
2. **測試函式命名**: `test_具體功能()`
3. **文件**: 在函式開頭添加清晰的文件字串
4. **分類**: 根據功能將測試放在適當的類別中

## 故障排除

### 常見問題
1. **API 金鑰問題** - 檢查 .env 檔案配置
2. **網路連線問題** - 確認網路和防火牆設定
3. **相依套件問題** - 確保所有相依套件已安裝

## 授權條款

本專案遵循 Apache 2.0 授權條款。

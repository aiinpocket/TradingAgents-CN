# 自定義OpenAI端點使用指南

## 概述

TradingAgents 支援自訂 OpenAI 相容端點，允許您使用任何支援 OpenAI API 格式的服務，包括：

- 官方 OpenAI API
- 第三方 OpenAI 代理服務
- 本地部署的模型（如 vLLM 等）
- 其他相容 OpenAI 格式的 API 服務

## 功能特性

- **完整整合**: 支援 Web UI 和 CLI 兩種使用方式
- **靈活配置**: 可自訂 API 端點 URL 和 API 金鑰
- **豐富模型**: 預置常用模型選項，支援自訂模型
- **快速配置**: 提供常用服務的快速配置按鈕
- **統一介面**: 與其他 LLM 提供商使用相同的介面  

## Web UI使用方法

### 1. 選擇提供商
在側邊欄的「LLM配置」部分，從下拉選單中選擇「自訂 OpenAI 端點」。

### 2. 配置端點
- **API 端點 URL**: 輸入您的 OpenAI 相容 API 端點
  - 官方 OpenAI: `https://api.openai.com/v1`
  - 本地服務: `http://localhost:8000/v1`
- **API 金鑰**: 輸入對應的 API 金鑰

### 3. 選擇模型
從預置模型中選擇，或選擇「自訂模型」手動輸入模型名稱。

### 4. 快速配置
使用快速配置按鈕一鍵設定常用服務：
- **官方 OpenAI**: 自動設定官方 API 端點
- **中轉服務**: 設定常用的 API 代理服務
- **本地部署**: 設定本地模型服務端點

## CLI 使用方法

### 1. 啟動 CLI
```bash
python cli/main.py
```

### 2. 選擇提供商
在 LLM 提供商選擇介面，選擇「自訂 OpenAI 端點」。

### 3. 配置端點
輸入您的自訂 OpenAI 端點 URL，例如：
- `https://api.openai.com/v1`
- `http://localhost:8000/v1`

### 4. 選擇模型
從可用模型列表中選擇適合的模型。

## 環境變數配置

### 設定 API 金鑰
在 `.env` 檔案中新增：
```bash
CUSTOM_OPENAI_API_KEY=your_api_key_here
```

### 設定預設端點（可選）
```bash
CUSTOM_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 支援的模型

### OpenAI 官方模型
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`
- `gpt-4o-mini`

### Anthropic 模型（透過代理）
- `claude-3-haiku`
- `claude-3-sonnet`
- `claude-3-opus`
- `claude-3.5-sonnet`

### 開源模型
- `llama-3.1-8b`
- `llama-3.1-70b`
- `llama-3.1-405b`

## 使用場景

### 1. 使用官方 OpenAI API
```
端點: https://api.openai.com/v1
金鑰: 您的 OpenAI API 金鑰
模型: gpt-4o-mini
```

### 2. 使用第三方代理服務
```
端點: https://your-proxy-service.com/v1
金鑰: 您的代理服務金鑰
模型: gpt-4o
```

### 3. 使用本地部署模型
```
端點: http://localhost:8000/v1
金鑰: 任意值（本地服務通常不需要）
模型: llama-3.1-8b
```

## 故障排除

### 常見問題

**Q: 連線失敗怎麼辦？**
A: 檢查端點 URL 是否正確，確保網路連線正常，驗證 API 金鑰是否有效。

**Q: 模型不可用怎麼辦？**
A: 確認您選擇的模型在目標 API 服務中可用，或選擇「自訂模型」手動輸入。

**Q: 如何驗證配置是否正確？**
A: 可以先進行一次簡單的股票分析測試，查看是否能正常回傳結果。

### 除錯技巧

1. **檢查日誌**: 查看控制台輸出的錯誤資訊
2. **驗證端點**: 使用 curl 或 Postman 測試 API 端點
3. **確認模型**: 查詢 API 服務支援的模型列表
4. **網路檢查**: 確保能存取目標 API 服務

## 技術實現

### 核心元件
- `ChatCustomOpenAI`: 自訂 OpenAI 適配器類別
- `create_openai_compatible_llm`: 統一 LLM 建立工廠函式
- `OPENAI_COMPATIBLE_PROVIDERS`: 提供商配置字典

### 整合點
- **Web UI**: `web/components/sidebar.py`
- **CLI**: `cli/utils.py` 和 `cli/main.py`
- **核心邏輯**: `tradingagents/graph/trading_graph.py`
- **分析執行器**: `web/utils/analysis_runner.py`

---

如有問題或建議，請提交 Issue。
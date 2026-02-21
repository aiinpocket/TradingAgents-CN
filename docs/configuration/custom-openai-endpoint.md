# 自定義OpenAI端點使用指南

## 概述

TradingAgents現在支持自定義OpenAI兼容端點，允許您使用任何支持OpenAI API格式的服務，包括：

- 官方OpenAI API
- 第三方OpenAI代理服務
- 本地部署的模型（如Ollama、vLLM等）
- 其他兼容OpenAI格式的API服務

## 功能特性

✅ **完整集成**: 支持Web UI和CLI两種使用方式  
✅ **靈活配置**: 可自定義API端點URL和API密鑰  
✅ **丰富模型**: 預置常用模型選項，支持自定義模型  
✅ **快速配置**: 提供常用服務的快速配置按鈕  
✅ **統一接口**: 與其他LLM提供商使用相同的接口  

## Web UI使用方法

### 1. 選擇提供商
在側邊栏的"LLM配置"部分，從下拉菜單中選擇"🔧 自定義OpenAI端點"。

### 2. 配置端點
- **API端點URL**: 輸入您的OpenAI兼容API端點
  - 官方OpenAI: `https://api.openai.com/v1`
  - 
  - 本地服務: `http://localhost:8000/v1`
- **API密鑰**: 輸入對應的API密鑰

### 3. 選擇模型
從預置模型中選擇，或選擇"自定義模型"手動輸入模型名稱。

### 4. 快速配置
使用快速配置按鈕一鍵設置常用服務：
- **官方OpenAI**: 自動設置官方API端點
- **中轉服務**: 設置常用的API代理服務
- **本地部署**: 設置本地模型服務端點

## CLI使用方法

### 1. 啟動CLI
```bash
python cli/main.py
```

### 2. 選擇提供商
在LLM提供商選擇界面，選擇"🔧 自定義OpenAI端點"。

### 3. 配置端點
輸入您的自定義OpenAI端點URL，例如：
- `https://api.openai.com/v1`
- `https://api.
- `http://localhost:8000/v1`

### 4. 選擇模型
從可用模型列表中選擇適合的模型。

## 環境變量配置

### 設置API密鑰
在`.env`文件中添加：
```bash
CUSTOM_OPENAI_API_KEY=your_api_key_here
```

### 設置默認端點（可選）
```bash
CUSTOM_OPENAI_BASE_URL=https://api.openai.com/v1
```

## 支持的模型

### OpenAI官方模型
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`
- `gpt-4o-mini`

### Anthropic模型（通過代理）
- `claude-3-haiku`
- `claude-3-sonnet`
- `claude-3-opus`
- `claude-3.5-sonnet`

### 開源模型
- `llama-3.1-8b`
- `llama-3.1-70b`
- `llama-3.1-405b`

### Google模型（通過代理）
- `gemini-pro`
- `gemini-1.5-pro`

## 使用場景

### 1. 使用官方OpenAI API
```
端點: https://api.openai.com/v1
密鑰: 您的OpenAI API密鑰
模型: gpt-4o-mini
```

### 2. 使用第三方代理服務
```
端點: https://your-proxy-service.com/v1
密鑰: 您的代理服務密鑰
模型: gpt-4o
```

### 3. 使用本地部署模型
```
端點: http://localhost:8000/v1
密鑰: 任意值（本地服務通常不需要）
模型: llama-3.1-8b
```

### 4. 使用
```
端點: https://api.
密鑰: 您的
模型: 
```

### 5. 使用硅基流動（SiliconFlow）
```
端點: https://api.siliconflow.cn/v1
密鑰: 您的SiliconFlow API密鑰
模型: Qwen/Qwen2.5-7B-Instruct（免費）
```

硅基流動是一家專註於AI基礎設施的服務商，提供：
- 🆓 **免費模型**: Qwen2.5-7B等多個模型免費使用
- 💰 **按量計費**: 靈活的定價方案
- 🔌 **OpenAI兼容**: 完全兼容OpenAI API格式
- 🚀 **高性能**: 優化的推理性能和低延迟

## 故障排除

### 常見問題

**Q: 連接失敗怎么办？**
A: 檢查端點URL是否正確，確保網絡連接正常，驗證API密鑰是否有效。

**Q: 模型不可用怎么办？**
A: 確認您選擇的模型在目標API服務中可用，或選擇"自定義模型"手動輸入。

**Q: 如何驗證配置是否正確？**
A: 可以先進行一次簡單的股票分析測試，查看是否能正常返回結果。

### 調試技巧

1. **檢查日誌**: 查看控制台輸出的錯誤信息
2. **驗證端點**: 使用curl或Postman測試API端點
3. **確認模型**: 查詢API服務支持的模型列表
4. **網絡檢查**: 確保能訪問目標API服務

## 技術實現

### 核心組件
- `ChatCustomOpenAI`: 自定義OpenAI適配器類
- `create_openai_compatible_llm`: 統一LLM創建工廠函數
- `OPENAI_COMPATIBLE_PROVIDERS`: 提供商配置字典

### 集成點
- **Web UI**: `web/components/sidebar.py`
- **CLI**: `cli/utils.py` 和 `cli/main.py`
- **核心邏輯**: `tradingagents/graph/trading_graph.py`
- **分析運行器**: `web/utils/analysis_runner.py`

## 更新日誌

### v1.0.0 (2025-01-01)
- ✅ 添加自定義OpenAI端點支持
- ✅ 集成Web UI配置界面
- ✅ 集成CLI選擇流程
- ✅ 支持多種預置模型
- ✅ 添加快速配置功能
- ✅ 完善錯誤處理和日誌記錄

---

如有問題或建議，請提交Issue或聯系開發团隊。
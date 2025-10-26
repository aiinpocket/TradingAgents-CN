# Google AI 配置指南

本指南将幫助您配置Google AI (Gemini)模型，以便在TradingAgents-CN中使用Google的强大AI能力進行股票分析。

## 🎯 概述

TradingAgents-CN v0.1.2新增了對Google AI的完整支持，包括：

- **Gemini 2.5 Pro** - 🚀 最新旗舰模型，推薦使用
- **Gemini 2.0 Flash** - 最新模型，推薦使用
- **Gemini 1.5 Pro** - 强大性能，適合深度分析  
- **Gemini 1.5 Flash** - 快速響應，適合簡單分析
- **智能混合嵌入** - Google AI推理 + 阿里百炼嵌入

## 🔑 獲取Google AI API密鑰

### 1. 訪問Google AI Studio

1. 打開 [Google AI Studio](https://aistudio.google.com/)
2. 使用您的Google账號登錄
3. 如果是首次使用，需要同意服務條款

### 2. 創建API密鑰

1. 在左侧導航栏中點擊 **"API keys"**
2. 點擊 **"Create API key"** 按钮
3. 選擇一個Google Cloud項目（或創建新項目）
4. 複制生成的API密鑰

### 3. 配置API密鑰

在項目根目錄的 `.env` 文件中添加：

```env
# Google AI API密鑰
GOOGLE_API_KEY=your_google_api_key_here
```

## 🤖 支持的模型

### Gemini 2.5 系列 (🚀 最新推薦)

#### Gemini 2.5 Pro
- **模型名稱**: `gemini-2.5-pro`
- **特點**: Google最新旗舰模型，性能卓越
- **適用場景**: 複雜股票分析，重要投資決策
- **優势**: 
  - 🧠 最强的推理能力
  - 🌍 優秀的中文理解
  - 🔧 完美的LangChain集成
  - 💾 支持超長上下文
  - 🎯 精準的金融分析

#### Gemini 2.5 Flash
- **模型名稱**: `gemini-2.5-flash`
- **特點**: 最新快速模型，平衡了速度和性能
- **適用場景**: 實時市場分析、快速交易決策、日常投資咨詢
- **優势**: 響應迅速，成本效益高

#### Gemini 2.5 Flash Lite
- **模型名稱**: `gemini-2.5-flash-lite`
- **特點**: 轻量級快速模型，專註於效率
- **適用場景**: 簡單查詢、基础分析、高頻次調用
- **優势**: 極低延迟，成本最優

#### Gemini 2.5 Pro-002
- **模型名稱**: `gemini-2.5-pro-002`
- **特點**: Gemini 2.5 Pro的優化版本
- **適用場景**: 需要最高精度的專業分析
- **優势**: 經過優化的性能表現

#### Gemini 2.5 Flash-002
- **模型名稱**: `gemini-2.5-flash-002`
- **特點**: Gemini 2.5 Flash的優化版本
- **適用場景**: 快速且準確的分析任務
- **優势**: 優化的速度和準確性平衡

### Gemini 2.0 系列

#### Gemini 2.0 Flash (推薦)
- **模型名稱**: `gemini-2.0-flash`
- **特點**: 最新版本，性能優秀，LangChain集成穩定
- **適用場景**: 日常股票分析，推薦首選
- **優势**: 
  - 🧠 優秀的推理能力
  - 🌍 完美的中文支持
  - 🔧 穩定的LangChain集成
  - 💾 完整的內存學习功能

### Gemini 1.5 系列

#### Gemini 1.5 Pro
- **模型名稱**: `gemini-1.5-pro`
- **特點**: 强大性能，適合複雜分析
- **適用場景**: 深度分析，重要投資決策
- **優势**: 功能强大，分析深度高

#### Gemini 1.5 Flash  
- **模型名稱**: `gemini-1.5-flash`
- **特點**: 快速響應，成本較低
- **適用場景**: 快速查詢，批量分析
- **優势**: 響應速度快，適合高頻使用

## 🔧 配置方法

### 1. Web界面配置

1. **啟動Web界面**:
   ```bash
   python -m streamlit run web/app.py
   ```

2. **在左侧邊栏中**:
   - 選擇 **"Google AI - Gemini模型"** 作為LLM提供商
   - 選擇具體的Gemini模型
   - 啟用記忆功能獲得更好效果

3. **開始分析**:
   - 輸入股票代碼
   - 選擇分析師
   - 點擊"開始分析"

### 2. CLI配置

```bash
# 使用Gemini 2.0 Flash模型
python -m cli.main --llm-provider google --model gemini-2.0-flash --stock AAPL

# 使用Gemini 1.5 Pro進行深度分析
python -m cli.main --llm-provider google --model gemini-1.5-pro --stock TSLA --analysts market fundamentals news
```

### 3. Python API配置

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置Google AI
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash"
config["memory_enabled"] = True

# 創建分析圖
graph = TradingAgentsGraph(["market", "fundamentals"], config=config)

# 執行分析
state, decision = graph.propagate("AAPL", "2025-06-27")
```

## 🔄 智能混合嵌入

TradingAgents-CN的一個獨特功能是智能混合嵌入服務：

### 工作原理
```
🧠 Google Gemini (主要推理)
    ↓
🔍 阿里百炼嵌入 (向量化和記忆)
    ↓  
💾 ChromaDB (向量數據庫)
    ↓
🎯 中文股票分析結果
```

### 優势
- **最佳性能**: Google AI的强大推理能力
- **中文優化**: 阿里百炼的中文嵌入優势
- **成本控制**: 合理的API調用成本
- **穩定可靠**: 經過充分測試的集成方案

## 🧪 測試配置

### 1. 運行測試腳本

```bash
# 測試Google AI連接
python tests/test_gemini_correct.py

# 測試Web界面Google模型功能
python tests/test_web_interface.py

# 完整的Gemini功能測試
python tests/final_gemini_test.py
```

### 2. 驗證配置

```bash
# 檢查API密鑰配置
python tests/test_all_apis.py

# 測試中文輸出功能
python tests/test_chinese_output.py
```

## 💡 使用建议

### 模型選擇建议

1. **重要決策**: 推薦 `gemini-2.5-pro` 🚀 或 `gemini-2.5-pro-002` 🔧
   - Google最新旗舰模型
   - 最强推理和分析能力
   - 適合重要投資決策

2. **日常使用**: 推薦 `gemini-2.5-flash` ⚡ 或 `gemini-2.0-flash`
   - 性能優秀，成本合理
   - LangChain集成穩定
   - 中文支持完美

3. **深度分析**: 使用 `gemini-1.5-pro`
   - 適合複雜分析任務
   - 分析深度更高
   - 推理能力强

4. **快速查詢**: 使用 `gemini-2.5-flash-lite` 💡 或 `gemini-1.5-flash`
   - 響應速度快
   - 適合批量分析
   - 成本較低

5. **最新功能**: 推薦 `gemini-2.5-pro` 🚀 或 `gemini-2.5-flash` ⚡
   - 最新模型版本
   - 優化的性能表現
   - 最佳用戶體驗

### 最佳實踐

1. **啟用內存功能**: 让AI學习您的分析偏好
2. **合理選擇分析師**: 根據需要選擇相關的分析師
3. **設置適當的研究深度**: 平衡分析质量和時間成本
4. **定期檢查API額度**: 確保有足夠的API調用額度

## ⚠️ 註意事項

### API限制
- Google AI有API調用頻率限制
- 建议合理控制分析頻率
- 監控API使用量和成本

### 網絡要求
- 需要穩定的網絡連接
- 某些地区可能需要特殊網絡配置
- 建议使用穩定的網絡環境

### 數據安全
- API密鑰仅在本地使用
- 不會上傳到任何服務器
- 建议定期更換API密鑰

## 🔧 故障排除

### 常见問題

#### 1. API密鑰無效
```bash
# 檢查API密鑰格式
echo $GOOGLE_API_KEY

# 驗證API密鑰有效性
python tests/test_correct_apis.py
```

#### 2. 模型調用失败
- 檢查網絡連接
- 驗證API額度是否充足
- 確認模型名稱正確

#### 3. 中文輸出異常
- 檢查字符編碼設置
- 驗證模型配置
- 運行中文輸出測試

### 獲取幫助

如果遇到問題：

1. 📖 查看 [完整文档](../README.md)
2. 🧪 運行 [測試程序](../../tests/)
3. 💬 提交 [GitHub Issue](https://github.com/hsliuping/TradingAgents-CN/issues)

## 🎉 開始使用

現在您已經完成了Google AI的配置，可以開始享受Gemini模型的强大分析能力了！

```bash
# 啟動Web界面
python -m streamlit run web/app.py

# 或使用CLI
python -m cli.main --llm-provider google --model gemini-2.0-flash --stock AAPL
```

祝您投資分析愉快！🚀

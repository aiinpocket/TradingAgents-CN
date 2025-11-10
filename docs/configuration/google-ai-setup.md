# Google AI 配置指南

本指南將幫助您配置Google AI (Gemini)模型，以便在TradingAgents-CN中使用Google的強大AI能力進行股票分析。

## 🎯 概述

TradingAgents-CN v0.1.2新增了對Google AI的完整支援，包括：

- **Gemini 2.5 Pro** - 🚀 最新旗艦模型，推薦使用
- **Gemini 2.0 Flash** - 最新模型，推薦使用
- **Gemini 1.5 Pro** - 強大效能，適合深度分析
- **Gemini 1.5 Flash** - 快速響應，適合簡單分析

## 🔑 獲取Google AI API金鑰

### 1. 訪問Google AI Studio

1. 開啟 [Google AI Studio](https://aistudio.google.com/)
2. 使用您的Google帳號登入
3. 如果是首次使用，需要同意服務條款

### 2. 建立API金鑰

1. 在左側導覽列中點擊 **"API keys"**
2. 點擊 **"Create API key"** 按鈕
3. 選擇一個Google Cloud專案（或建立新專案）
4. 複製產生的API金鑰

### 3. 配置API金鑰

在專案根目錄的 `.env` 檔案中新增：

```env
# Google AI API金鑰
GOOGLE_API_KEY=your_google_api_key_here
```

## 🤖 支援的模型

### Gemini 2.5 系列 (🚀 最新推薦)

#### Gemini 2.5 Pro
- **模型名稱**: `gemini-2.5-pro`
- **特點**: Google最新旗艦模型，效能卓越
- **適用場景**: 複雜股票分析，重要投資決策
- **優勢**:
  - 🧠 最強的推理能力
  - 🌍 優秀的中文理解
  - 🔧 完美的LangChain整合
  - 💾 支援超長上下文
  - 🎯 精準的金融分析

#### Gemini 2.5 Flash
- **模型名稱**: `gemini-2.5-flash`
- **特點**: 最新快速模型，平衡了速度和效能
- **適用場景**: 即時市場分析、快速交易決策、日常投資諮詢
- **優勢**: 響應迅速，成本效益高

#### Gemini 2.5 Flash Lite
- **模型名稱**: `gemini-2.5-flash-lite`
- **特點**: 輕量級快速模型，專注於效率
- **適用場景**: 簡單查詢、基礎分析、高頻次呼叫
- **優勢**: 極低延遲，成本最優

#### Gemini 2.5 Pro-002
- **模型名稱**: `gemini-2.5-pro-002`
- **特點**: Gemini 2.5 Pro的優化版本
- **適用場景**: 需要最高精度的專業分析
- **優勢**: 經過優化的效能表現

#### Gemini 2.5 Flash-002
- **模型名稱**: `gemini-2.5-flash-002`
- **特點**: Gemini 2.5 Flash的優化版本
- **適用場景**: 快速且準確的分析任務
- **優勢**: 優化的速度和準確性平衡

### Gemini 2.0 系列

#### Gemini 2.0 Flash (推薦)
- **模型名稱**: `gemini-2.0-flash`
- **特點**: 最新版本，效能優秀，LangChain整合穩定
- **適用場景**: 日常股票分析，推薦首選
- **優勢**:
  - 🧠 優秀的推理能力
  - 🌍 完美的中文支援
  - 🔧 穩定的LangChain整合
  - 💾 完整的記憶學習功能

### Gemini 1.5 系列

#### Gemini 1.5 Pro
- **模型名稱**: `gemini-1.5-pro`
- **特點**: 強大效能，適合複雜分析
- **適用場景**: 深度分析，重要投資決策
- **優勢**: 功能強大，分析深度高

#### Gemini 1.5 Flash
- **模型名稱**: `gemini-1.5-flash`
- **特點**: 快速響應，成本較低
- **適用場景**: 快速查詢，批次分析
- **優勢**: 響應速度快，適合高頻使用

## 🔧 配置方法

### 1. Web介面配置

1. **啟動Web介面**:
   ```bash
   python -m streamlit run web/app.py
   ```

2. **在左側邊欄中**:
   - 選擇 **"Google AI - Gemini模型"** 作為LLM提供商
   - 選擇具體的Gemini模型
   - 啟用記憶功能獲得更好效果

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

# 建立分析圖
graph = TradingAgentsGraph(["market", "fundamentals"], config=config)

# 執行分析
state, decision = graph.propagate("AAPL", "2025-06-27")
```

## 🧪 測試配置

### 1. 執行測試腳本

```bash
# 測試Google AI連接
python tests/test_gemini_correct.py

# 測試Web介面Google模型功能
python tests/test_web_interface.py

# 完整的Gemini功能測試
python tests/final_gemini_test.py
```

### 2. 驗證配置

```bash
# 檢查API金鑰配置
python tests/test_all_apis.py

# 測試中文輸出功能
python tests/test_chinese_output.py
```

## 💡 使用建議

### 模型選擇建議

1. **重要決策**: 推薦 `gemini-2.5-pro` 🚀 或 `gemini-2.5-pro-002` 🔧
   - Google最新旗艦模型
   - 最強推理和分析能力
   - 適合重要投資決策

2. **日常使用**: 推薦 `gemini-2.5-flash` ⚡ 或 `gemini-2.0-flash`
   - 效能優秀，成本合理
   - LangChain整合穩定
   - 中文支援完美

3. **深度分析**: 使用 `gemini-1.5-pro`
   - 適合複雜分析任務
   - 分析深度更高
   - 推理能力強

4. **快速查詢**: 使用 `gemini-2.5-flash-lite` 💡 或 `gemini-1.5-flash`
   - 響應速度快
   - 適合批次分析
   - 成本較低

5. **最新功能**: 推薦 `gemini-2.5-pro` 🚀 或 `gemini-2.5-flash` ⚡
   - 最新模型版本
   - 優化的效能表現
   - 最佳使用者體驗

### 最佳實踐

1. **啟用記憶功能**: 讓AI學習您的分析偏好
2. **合理選擇分析師**: 根據需要選擇相關的分析師
3. **設定適當的研究深度**: 平衡分析品質和時間成本
4. **定期檢查API額度**: 確保有足夠的API呼叫額度

## ⚠️ 注意事項

### API限制
- Google AI有API呼叫頻率限制
- 建議合理控制分析頻率
- 監控API使用量和成本

### 網路要求
- 需要穩定的網路連線
- 某些地區可能需要特殊網路配置
- 建議使用穩定的網路環境

### 資料安全
- API金鑰僅在本地使用
- 不會上傳到任何伺服器
- 建議定期更換API金鑰

## 🔧 故障排除

### 常見問題

#### 1. API金鑰無效
```bash
# 檢查API金鑰格式
echo $GOOGLE_API_KEY

# 驗證API金鑰有效性
python tests/test_correct_apis.py
```

#### 2. 模型呼叫失敗
- 檢查網路連線
- 驗證API額度是否充足
- 確認模型名稱正確

#### 3. 中文輸出異常
- 檢查字元編碼設定
- 驗證模型配置
- 執行中文輸出測試

### 獲取幫助

如果遇到問題：

1. 📖 查看 [完整文件](../README.md)
2. 🧪 執行 [測試程式](../../tests/)
3. 💬 提交 [GitHub Issue](https://github.com/hsliuping/TradingAgents-CN/issues)

## 🎉 開始使用

現在您已經完成了Google AI的配置，可以開始享受Gemini模型的強大分析能力了！

```bash
# 啟動Web介面
python -m streamlit run web/app.py

# 或使用CLI
python -m cli.main --llm-provider google --model gemini-2.0-flash --stock AAPL
```

祝您投資分析愉快！🚀

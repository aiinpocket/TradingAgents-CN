# 📋 TradingAgents 節點工具快速參考

## 🔄 分析流程概覽

```
🚀 開始 → 🔍 驗證 → 🔧 準备 → 💰 預估 → ⚙️ 配置 → 🏗️ 初始化
    ↓
👥 分析師团隊 (並行執行)
├── 📈 市場分析師      ← get_stock_market_data_unified
├── 📊 基本面分析師    ← get_stock_fundamentals_unified  
├── 📰 新聞分析師      ← get_realtime_stock_news
└── 💬 社交媒體分析師  ← get_stock_news_openai
    ↓
🎯 研究員辩論
├── 🐂 看涨研究員 ←→ 🐻 看跌研究員
└── 👔 研究經理 (形成共识)
    ↓
💼 交易員 (制定交易策略)
    ↓
⚠️ 風險評估团隊
├── 🔥 激進評估 ← 🛡️ 保守評估 → ⚖️ 中性評估
└── 🎯 風險經理 (最终風險決策)
    ↓
📡 信號處理 → ✅ 最终決策
```

## 👥 核心節點速查

| 節點類型 | 節點名稱 | 主要職责 | 核心工具 |
|---------|---------|---------|---------|
| **分析師** | 📈 市場分析師 | 技術分析、趋势识別 | `get_stock_market_data_unified` |
| **分析師** | 📊 基本面分析師 | 財務分析、估值模型 | `get_stock_fundamentals_unified` |
| **分析師** | 📰 新聞分析師 | 新聞事件、宏觀分析 | `get_realtime_stock_news` |
| **分析師** | 💬 社交媒體分析師 | 情绪分析、舆論監控 | `get_stock_news_openai` |
| **研究員** | 🐂 看涨研究員 | 乐觀角度、增長潜力 | LLM推理 + 記忆 |
| **研究員** | 🐻 看跌研究員 | 悲觀角度、風險识別 | LLM推理 + 記忆 |
| **管理層** | 👔 研究經理 | 辩論主持、共识形成 | LLM推理 + 記忆 |
| **交易** | 💼 交易員 | 交易決策、仓位管理 | LLM推理 + 記忆 |
| **風險** | 🔥 激進評估 | 高風險高收益策略 | LLM推理 |
| **風險** | 🛡️ 保守評估 | 低風險穩健策略 | LLM推理 |
| **風險** | ⚖️ 中性評估 | 平衡風險收益 | LLM推理 |
| **管理層** | 🎯 風險經理 | 風險控制、政策制定 | LLM推理 + 記忆 |
| **處理** | 📡 信號處理 | 信號整合、最终輸出 | 信號處理算法 |

## 🔧 核心工具速查

### 📈 市場數據工具
```python
# 統一市場數據工具 (推薦)
get_stock_market_data_unified(ticker, start_date, end_date)
# 自動识別股票類型，調用最佳數據源
# A股: Tushare + AKShare | 港股: AKShare + Yahoo | 美股: Yahoo + FinnHub

# 备用工具
get_YFin_data_online(symbol, start_date, end_date)           # Yahoo Finance
get_stockstats_indicators_report_online(symbol, period)     # 技術指標
```

### 📊 基本面工具
```python
# 統一基本面工具 (推薦)
get_stock_fundamentals_unified(ticker, start_date, end_date, curr_date)
# 自動识別股票類型，調用最佳數據源
# A股: Tushare + AKShare | 港股: AKShare | 美股: FinnHub + SimFin

# 補充工具
get_finnhub_company_insider_sentiment(symbol)               # 內部人士情绪
get_simfin_balance_sheet(ticker, year, period)             # 資產负债表
get_simfin_income_stmt(ticker, year, period)               # 利润表
```

### 📰 新聞工具
```python
# 實時新聞
get_realtime_stock_news(symbol, days_back)                 # 實時股票新聞
get_global_news_openai(query, max_results)                 # 全球新聞 (OpenAI)
get_google_news(query, lang, country)                      # Google 新聞

# 歷史新聞
get_finnhub_news(symbol, start_date, end_date)             # FinnHub 新聞
get_reddit_news(subreddit, limit)                          # Reddit 新聞
```

### 💬 社交媒體工具
```python
# 情绪分析
get_stock_news_openai(symbol, sentiment_focus)             # 股票新聞情绪
get_reddit_stock_info(symbol, limit)                       # Reddit 討論
get_chinese_social_sentiment(symbol, platform)             # 中國社交媒體
```

## 🎯 數據源映射

| 股票類型 | 识別規則 | 市場數據源 | 基本面數據源 | 新聞數據源 |
|---------|---------|-----------|-------------|-----------|
| **A股** | 6位數字 (000001) | Tushare + AKShare | Tushare + AKShare | 財聯社 + 新浪財經 |
| **港股** | .HK後缀 (0700.HK) | AKShare + Yahoo | AKShare | Google News |
| **美股** | 字母代碼 (AAPL) | Yahoo + FinnHub | FinnHub + SimFin | FinnHub + Google |

## ⚙️ 配置速查

### 分析師選擇
```python
# 快速分析 (1-2分鐘)
selected_analysts = ["market"]

# 基础分析 (3-5分鐘)  
selected_analysts = ["market", "fundamentals"]

# 完整分析 (5-10分鐘)
selected_analysts = ["market", "fundamentals", "news", "social"]
```

### 研究深度
```python
research_depth = 1    # 快速: 减少工具調用，快速模型
research_depth = 2    # 標準: 平衡速度和质量 (推薦)
research_depth = 3    # 深度: 增加辩論轮次，深度模型
```

### LLM提供商
```python
llm_provider = "dashscope"    # 阿里百炼 (推薦，中文優化)
llm_provider = "deepseek"     # DeepSeek (性價比高)
llm_provider = "google"       # Google Gemini (质量高)
```

## 🔄 工具調用循環

每個分析師都遵循LangGraph的標準循環：

```
1️⃣ 分析師節點
    ↓ (決定需要什么數據)
2️⃣ 條件判斷 
    ↓ (檢查是否有工具調用)
3️⃣ 工具節點
    ↓ (執行數據獲取)
4️⃣ 回到分析師節點
    ↓ (處理數據，生成報告)
5️⃣ 條件判斷
    ↓ (檢查是否完成)
6️⃣ 消息清理 → 下一個分析師
```

**日誌示例**:
```
📊 [模塊開始] market_analyst - 股票: 000858
📊 [市場分析師] 工具調用: ['get_stock_market_data_unified']  
📊 [模塊完成] market_analyst - ✅ 成功 - 耗時: 41.73s
```

## 🚀 快速使用

### 基本用法
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 創建分析圖
graph = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals"],
    config={"llm_provider": "dashscope", "research_depth": 2}
)

# 執行分析
state, decision = graph.propagate("000858", "2025-01-17")
print(f"建议: {decision['action']}, 置信度: {decision['confidence']}")
```

### Web界面使用
```bash
# 啟動Web界面
python web/run_web.py

# 訪問 http://localhost:8501
# 1. 輸入股票代碼
# 2. 選擇分析師和研究深度  
# 3. 點擊"開始分析"
# 4. 查看實時進度和結果
```

## ❓ 常见問題速查

| 問題 | 原因 | 解決方案 |
|-----|------|---------|
| 分析時間過長 | 研究深度過高/網絡慢 | 降低research_depth，檢查網絡 |
| 重複分析師調用 | LangGraph正常機制 | 正常現象，等待完成 |
| 基本面分析師多轮調用 | 强制工具調用機制 | 正常現象，確保數據质量 |
| API調用失败 | 密鑰錯誤/限額超出 | 檢查.env配置，確認API額度 |
| 進度卡住 | 網絡超時/API異常 | 刷新页面，檢查日誌 |
| 中文乱碼 | 編碼問題 | 使用UTF-8編碼，檢查字體 |

## 🔄 工具調用機制詳解

### 📈 市場分析師（簡單模式）
```
1️⃣ 分析師決策 → 2️⃣ 調用統一工具 → 3️⃣ 生成報告
```

### 📊 基本面分析師（複雜模式）
```
1️⃣ 嘗試LLM自主調用 → 2️⃣ 工具執行 → 3️⃣ 數據處理
                ↓ (如果LLM未調用工具)
4️⃣ 强制工具調用 → 5️⃣ 重新生成報告
```

### 🧠 LLM工具選擇逻辑
1. **系統提示詞引導** (權重最高)
2. **工具描述匹配度**
3. **工具名稱語義理解**
4. **參數簡潔性偏好**
5. **模型特性差異**

## 📊 輸出格式

### 最终決策格式
```json
{
    "action": "买入/持有/卖出",
    "confidence": 8.5,
    "target_price": "45.80",
    "stop_loss": "38.20", 
    "position_size": "中等仓位",
    "time_horizon": "3-6個月",
    "reasoning": "詳細分析理由..."
}
```

### 分析報告結構
```
📈 市場分析報告
├── 股票基本信息
├── 技術指標分析  
├── 價格趋势分析
├── 成交量分析
└── 投資建议

📊 基本面分析報告  
├── 財務狀况分析
├── 估值分析
├── 行業對比
├── 風險評估
└── 投資建议
```

---

*快速參考 | TradingAgents v0.1.7 | 更多詳情請查看完整文档*

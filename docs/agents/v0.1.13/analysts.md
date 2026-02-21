# 分析師團隊

## 概述

分析師團隊是 TradingAgents 框架的核心分析組件，負責從不同維度對股票進行專業分析。團隊由四類專業分析師組成，每個分析師都專注於特定的分析領域，透過協作為投資決策提供全面的數據支援。

## 分析師架構

### 基礎分析師設計

所有分析師都基於統一的架構設計，使用相同的工具介面和日誌系統：

```python
# 統一的分析師模組日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_analyst_module("analyst_type")
def analyst_node(state):
    # 分析師邏輯實作
    pass
```

### 智能體狀態管理

分析師透過 `AgentState` 進行狀態管理：

```python
class AgentState:
    company_of_interest: str      # 股票代碼
    trade_date: str              # 交易日期
    fundamentals_report: str     # 基本面報告
    market_report: str           # 市場分析報告
    news_report: str             # 新聞分析報告
    sentiment_report: str        # 情緒分析報告
    messages: List              # 訊息歷史
```

## 分析師團隊成員

### 1. 基本面分析師 (Fundamentals Analyst)

**檔案位置**: `tradingagents/agents/analysts/fundamentals_analyst.py`

**核心職責**:
- 分析公司財務數據和基本面指標
- 評估公司估值和財務健康度
- 提供基於財務數據的投資建議

**技術特性**:
- 使用統一工具架構自動識別股票類型
- 支持美股的基本面分析
- 智能選擇合適的數據源（線上/離線模式）

**核心實作**:
```python
def create_fundamentals_analyst(llm, toolkit):
    @log_analyst_module("fundamentals")
    def fundamentals_analyst_node(state):
        ticker = state["company_of_interest"]

        # 獲取股票市場資訊
        from tradingagents.utils.stock_utils import get_stock_market_info
        market_info = get_stock_market_info(ticker)

        # 獲取公司名稱
        company_name = _get_company_name_for_fundamentals(ticker, market_info)

        # 選擇合適的工具
        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_fundamentals_unified]
        else:
            # 離線模式工具選擇
            tools = [...]
```

**支持的數據源**:
- **美股**: FinnHub、SimFin等數據源

### 2. 市場分析師 (Market Analyst)

**檔案位置**: `tradingagents/agents/analysts/market_analyst.py`

**核心職責**:
- 技術指標分析（RSI、MACD、布林帶等）
- 價格趨勢和圖表模式識別
- 支撐阻力位分析
- 交易訊號生成

**分析維度**:
- 短期技術指標
- 中長期趨勢分析
- 成交量分析
- 價格動量評估

### 3. 新聞分析師 (News Analyst)

**檔案位置**: `tradingagents/agents/analysts/news_analyst.py`

**核心職責**:
- 新聞事件影響分析
- 宏觀經濟數據解讀
- 政策影響評估
- 產業動態分析

**數據來源**:
- Google News API
- FinnHub新聞數據
- 即時新聞流
- 經濟數據發布

**特殊功能**:
- 新聞過濾和品質評估
- 情感分析和影響評級
- 時效性評估

### 4. 社交媒體分析師 (Social Media Analyst)

**檔案位置**: `tradingagents/agents/analysts/social_media_analyst.py`

**核心職責**:
- 社交媒體情緒分析
- 投資者情緒監測
- 輿論趨勢識別
- 熱點話題追蹤

**數據來源**:
- Reddit討論數據
- Twitter情感數據
- 金融論壇討論
- 社交媒體熱度指標

## 工具整合

### 統一工具架構

分析師使用統一的工具介面，支援自動股票類型識別：

```python
# 統一基本面分析工具
tools = [toolkit.get_stock_fundamentals_unified]

# 工具內部自動識別股票類型並呼叫對應數據源
# - 美股: 使用Yahoo Finance、FinnHub等國際數據源
```

### 線上/離線模式

**線上模式** (`online_tools=True`):
- 使用即時API數據
- 數據最新但成本較高
- 適合生產環境

**離線模式** (`online_tools=False`):
- 使用快取數據
- 成本低但數據可能延遲
- 適合開發和測試

## 股票類型支援

### 市場識別機制

```python
from tradingagents.utils.stock_utils import get_stock_market_info
market_info = get_stock_market_info(ticker)

# 回傳資訊包括：
# - is_us: 是否為美股
# - market_name: 市場名稱
# - currency_name: 貨幣名稱
# - currency_symbol: 貨幣符號
```

### 支援的市場

**美國股市**
- 股票代碼格式：AAPL, TSLA等
- 貨幣單位：美元(USD)
- 數據源：FinnHub, Yahoo Finance等

## 分析流程

### 1. 數據獲取階段
```mermaid
graph LR
    A[股票代碼] --> B[市場類型識別]
    B --> C[選擇數據源]
    C --> D[獲取原始數據]
    D --> E[數據預處理]
```

### 2. 分析執行階段
```mermaid
graph TB
    A[原始數據] --> B[基本面分析師]
    A --> C[市場分析師]
    A --> D[新聞分析師]
    A --> E[社交媒體分析師]

    B --> F[基本面報告]
    C --> G[市場分析報告]
    D --> H[新聞分析報告]
    E --> I[情緒分析報告]
```

### 3. 報告生成階段
```mermaid
graph LR
    A[各分析師報告] --> B[狀態更新]
    B --> C[傳遞給研究員團隊]
    C --> D[進入辯論階段]
```

## 設定選項

### 分析師選擇
```python
# 可選擇的分析師類型
selected_analysts = [
    "market",        # 市場分析師
    "social",        # 社交媒體分析師
    "news",          # 新聞分析師
    "fundamentals"   # 基本面分析師
]
```

### 工具設定
```python
toolkit_config = {
    "online_tools": True,     # 是否使用線上工具
    "cache_enabled": True,    # 是否啟用快取
    "timeout": 30,           # API超時時間
    "retry_count": 3         # 重試次數
}
```

## 日誌和監控

### 統一日誌系統
```python
# 每個分析師都使用統一的日誌系統
logger = get_logger("default")

# 詳細的除錯日誌
logger.debug(f"📊 [DEBUG] 基本面分析師節點開始")
logger.info(f"📊 [基本面分析師] 正在分析股票: {ticker}")
logger.warning(f"⚠️ [DEBUG] memory為None，跳過歷史記憶檢索")
```

### 效能監控
- 分析耗時統計
- API呼叫次數追蹤
- 錯誤率監控
- 快取命中率統計

## 擴展指南

### 新增新的分析師

1. **建立分析師檔案**
```python
# tradingagents/agents/analysts/custom_analyst.py
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.utils.logging_init import get_logger

def create_custom_analyst(llm, toolkit):
    @log_analyst_module("custom")
    def custom_analyst_node(state):
        # 自訂分析邏輯
        pass
    return custom_analyst_node
```

2. **註冊到系統**
```python
# 在trading_graph.py中新增
selected_analysts.append("custom")
```

### 新增新的數據源

1. **實作數據介面**
2. **加入到工具集**
3. **更新設定選項**

## 最佳實踐

### 1. 錯誤處理
- 使用try-catch包裝API呼叫
- 提供降級方案
- 記錄詳細錯誤資訊

### 2. 效能最佳化
- 啟用數據快取
- 合理設定超時時間
- 避免重複API呼叫

### 3. 數據品質
- 驗證數據完整性
- 處理異常值
- 提供數據品質評分

### 4. 可維護性
- 使用統一的程式碼結構
- 加入詳細的註釋
- 遵循命名規範

## 故障排除

### 常見問題

1. **API呼叫失敗**
   - 檢查網路連線
   - 驗證API金鑰
   - 查看速率限制

2. **數據格式錯誤**
   - 檢查股票代碼格式
   - 驗證市場類型識別
   - 查看數據源相容性

3. **效能問題**
   - 啟用快取機制
   - 最佳化並行設定
   - 減少不必要的API呼叫

### 除錯技巧

1. **啟用詳細日誌**
```python
logger.setLevel(logging.DEBUG)
```

2. **檢查狀態傳遞**
```python
logger.debug(f"當前狀態: {state}")
```

3. **驗證工具設定**
```python
logger.debug(f"工具設定: {toolkit.config}")
```

分析師團隊是整個TradingAgents框架的基礎，透過專業化分工和協作，為後續的研究辯論和交易決策提供高品質的數據支援。

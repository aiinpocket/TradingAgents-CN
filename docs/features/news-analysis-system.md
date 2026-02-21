# 新聞分析工具鏈和提示詞系統

本文檔詳細介紹了TradingAgentsCN系統中的新聞分析工具鏈架構、提示詞設計和實現機制。

## 1. 新聞分析工具鏈架構

### 1.1 整體架構圖

```
新聞分析師 (NewsAnalyst)
    ↓
工具選擇器 (根據股票類型和模式)
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   工具鏈     │   非工具鏈   │   離線工具鏈    │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                   ↓                   ↓
實時新聞聚合器 (RealtimeNewsAggregator)
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  FinnHub    │ Alpha       │  NewsAPI    │  中文財經   │
│  實時新聞   │ Vantage     │  新聞源     │  新聞源     │
└─────────────┴─────────────┴─────────────┴─────────────┘
    ↓
新聞處理流水線
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  去重處理   │  時效性     │  緊急程度   │  相關性     │
│            │  評估       │  評估       │  評分       │
└─────────────┴─────────────┴─────────────┴─────────────┘
    ↓
格式化新聞報告
    ↓
LLM分析 (基於提示詞模板)
    ↓
結構化分析報告
```

### 1.2 工具鏈組件詳解

#### 1.2.1 新聞分析師 (NewsAnalyst)

**位置**: `tradingagents/agents/analysts/news_analyst.py`

**核心功能**:
- 智能工具選擇（根據股票類型和運行模式）
- 提示詞模板管理
- LLM調用和結果處理
- 分析報告生成

**工具選擇邏輯**:
```python
# 工具鏈
if is_china:
    tools = [
        toolkit.get_realtime_stock_news,  # 實時新聞（包含東方財富）
        toolkit.get_google_news,         # Google新聞（中文搜索）
        toolkit.get_global_news_openai   # OpenAI全球新聞（作為補充）
    ]

# 非工具鏈
else:
    tools = [
        toolkit.get_realtime_stock_news,  # 實時新聞
        toolkit.get_global_news_openai,
        toolkit.get_google_news
    ]

# 離線模式工具鏈
if not online_tools:
    tools = [
        toolkit.get_realtime_stock_news,  # 嘗試實時新聞
        toolkit.get_finnhub_news,
        toolkit.get_reddit_news,
        toolkit.get_google_news,
    ]
```

#### 1.2.2 實時新聞聚合器 (RealtimeNewsAggregator)

**位置**: `tradingagents/dataflows/realtime_news_utils.py`

**核心功能**:
- 多源新聞聚合
- 新聞去重和排序
- 緊急程度評估
- 相關性評分
- 時效性分析

**數據源優先級**:
1. **FinnHub實時新聞** (最高優先級)
2. **Alpha Vantage新聞**
3. **NewsAPI新聞源**
4. **中文財經新聞源**

**新聞項目數據結構**:
```python
@dataclass
class NewsItem:
    title: str              # 新聞標題
    content: str           # 新聞內容
    source: str            # 新聞來源
    publish_time: datetime # 發布時間
    url: str              # 新聞鏈接
    urgency: str          # 緊急程度 (high, medium, low)
    relevance_score: float # 相關性評分
```

#### 1.2.3 新聞處理流水線

**去重處理**:
- 基於標題相似度的去重算法
- 時間窗口內的重複新聞過濾

**緊急程度評估**:
```python
# 高緊急程度關鍵詞
high_urgency_keywords = [
    "破產", "訴訟", "收購", "合並", "FDA批準", "盈利警告",
    "停牌", "重組", "违規", "調查", "制裁"
]

# 中等緊急程度關鍵詞
medium_urgency_keywords = [
    "財報", "業績", "合作", "新產品", "市場份額",
    "分红", "回購", "增持", "減持"
]
```

**相關性評分算法**:
- 股票代碼匹配度
- 公司名稱匹配度
- 行業關鍵詞匹配度
- 內容相關性分析

## 2. 提示詞系統設計

### 2.1 系統提示詞模板

```python
system_message = """您是一位專業的財經新聞分析師，負責分析最新的市場新聞和事件對股票價格的潛在影響。

您的主要職責包括：
1. 獲取和分析最新的實時新聞（優先15-30分鐘內的新聞）
2. 評估新聞事件的緊急程度和市場影響
3. 識別可能影響股價的關鍵信息
4. 分析新聞的時效性和可靠性
5. 提供基於新聞的交易建議和價格影響評估

重點關註的新聞類型：
- 財報發布和業績指導
- 重大合作和並購消息
- 政策變化和監管動態
- 突發事件和危機管理
- 行業趨勢和技術突破
- 管理層變動和戰略調整

分析要點：
- 新聞的時效性（發布時間距離現在多久）
- 新聞的可信度（來源權威性）
- 市場影響程度（對股價的潛在影響）
- 投資者情緒變化（正面/負面/中性）
- 與歷史類似事件的對比

📊 價格影響分析要求：
- 評估新聞對股價的短期影響（1-3天）
- 分析可能的價格波動幅度（百分比）
- 提供基於新聞的價格調整建議
- 識別關鍵價格支撐位和阻力位
- 評估新聞對長期投資價值的影響
- 不允許回複'無法評估價格影響'或'需要更多信息'

請特別註意：
⚠️ 如果新聞數據存在滞後（超過2小時），請在分析中明確說明時效性限制
✅ 優先分析最新的、高相關性的新聞事件
📊 提供新聞對股價影響的量化評估和具體價格預期
💰 必須包含基於新聞的價格影響分析和調整建議

請撰寫詳細的中文分析報告，並在報告末尾附上Markdown表格總結關鍵發現。"""
```

### 2.2 提示詞設計原則

#### 2.2.1 角色定位
- **專業身份**: 財經新聞分析師
- **核心職責**: 新聞分析和價格影響評估
- **專業要求**: 量化分析和具體建議

#### 2.2.2 任務導向
- **主要任務**: 5個核心職責明確定義
- **關註重點**: 6類重要新聞類型
- **分析維度**: 5個關鍵分析要點

#### 2.2.3 輸出要求
- **強制要求**: 價格影響分析（不允許回避）
- **格式要求**: 中文報告 + Markdown表格
- **品質標準**: 詳細分析 + 量化評估

#### 2.2.4 約束條件
- **時效性約束**: 優先15-30分鐘內新聞
- **可靠性約束**: 評估新聞來源權威性
- **完整性約束**: 必須包含價格影響分析

### 2.3 動態提示詞註入

```python
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "您是一位有用的AI助手，與其他助手協作。"
        " 使用提供的工具來推進回答問題。"
        " 您可以訪問以下工具：{tool_names}。\n{system_message}"
        "供您參考，當前日期是{current_date}。我們正在查看公司{ticker}。請用中文撰寫所有分析內容。",
    ),
    MessagesPlaceholder(variable_name="messages"),
])

# 動態參數註入
prompt = prompt.partial(system_message=system_message)
prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
prompt = prompt.partial(current_date=current_date)
prompt = prompt.partial(ticker=ticker)
```

## 3. 工具鏈執行流程

### 3.1 初始化階段

```python
def create_news_analyst(llm, toolkit):
    @log_analyst_module("news")
    def news_analyst_node(state):
        # 1. 提取狀態信息
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        session_id = state.get("session_id", "未知會話")
        
        # 2. 股票類型識別
        market_info = get_stock_market_info(ticker)
        is_china = market_info['is_china']
        
        # 3. 工具選擇
        tools = select_tools_by_market(is_china, toolkit.config["online_tools"])
        
        # 4. 提示詞構建
        prompt = build_prompt_template(system_message, tools, current_date, ticker)
```

### 3.2 新聞獲取階段

```python
def get_realtime_stock_news(ticker: str, hours_back: int = 6):
    # 1. 多源新聞獲取
    finnhub_news = _get_finnhub_realtime_news(ticker, hours_back)
    av_news = _get_alpha_vantage_news(ticker, hours_back)
    newsapi_news = _get_newsapi_news(ticker, hours_back)
    chinese_news = _get_chinese_finance_news(ticker, hours_back)
    
    # 2. 新聞聚合
    all_news = finnhub_news + av_news + newsapi_news + chinese_news
    
    # 3. 去重和排序
    unique_news = _deduplicate_news(all_news)
    sorted_news = sorted(unique_news, key=lambda x: x.publish_time, reverse=True)
    
    # 4. 格式化報告
    report = format_news_report(sorted_news, ticker)
    
    return report
```

### 3.3 LLM分析階段

```python
def analyze_news_with_llm(llm, prompt, tools, state):
    # 1. 工具綁定
    chain = prompt | llm.bind_tools(tools)
    
    # 2. LLM調用
    result = chain.invoke(state["messages"])
    
    # 3. 工具調用處理
    if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
        # 處理工具調用結果
        tool_results = process_tool_calls(result.tool_calls)
        report = generate_analysis_report(tool_results)
    else:
        # 直接使用LLM生成的內容
        report = result.content
    
    return report
```

### 3.4 報告生成階段

```python
def format_news_report(news_items: List[NewsItem], ticker: str) -> str:
    report = f"# {ticker} 實時新聞分析報告\n\n"
    report += f"📅 **生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"📊 **新聞總數**: {len(news_items)} 條\n\n"
    
    # 緊急新聞優先顯示
    urgent_news = [item for item in news_items if item.urgency == 'high']
    if urgent_news:
        report += "## 🚨 緊急新聞\n\n"
        for item in urgent_news:
            report += format_news_item(item)
    
    # 一般新聞
    normal_news = [item for item in news_items if item.urgency != 'high']
    if normal_news:
        report += "## 📰 最新新聞\n\n"
        for item in normal_news[:10]:  # 限制顯示數量
            report += format_news_item(item)
    
    return report
```

## 4. 關鍵特性和優勢

### 4.1 智能工具選擇
- **股票類型識別**: 自動識別、、美股
- **數據源優化**: 優先中文新聞源，美股優先英文新聞源
- **模式適配**: 在線/離線模式自動切換

### 4.2 多源新聞聚合
- **專業API**: FinnHub、Alpha Vantage提供高品質金融新聞
- **通用API**: NewsAPI提供廣泛新聞覆蓋
- **本地化**: 中文財經新聞源支持分析

### 4.3 智能新聞處理
- **去重算法**: 基於內容相似度的智能去重
- **緊急程度評估**: 關鍵詞匹配 + 內容分析
- **相關性評分**: 多維度相關性計算
- **時效性分析**: 新聞發布時間與當前時間對比

### 4.4 強化提示詞設計
- **角色明確**: 專業財經新聞分析師定位
- **任務具體**: 5大職責 + 6類新聞類型
- **輸出標準**: 強制價格影響分析
- **品質保證**: 詳細分析 + 量化評估

### 4.5 完整的日誌追蹤
- **性能監控**: 每個步驟的耗時統計
- **工具使用**: 工具調用情況記錄
- **數據品質**: 新聞數量和品質統計
- **錯誤處理**: 異常情況的詳細記錄

## 5. 使用示例

### 5.1 基本使用

```python
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.llm_adapters import Chat

# 創建LLM和工具包
llm = Chat
toolkit = Toolkit()

# 創建新聞分析師
news_analyst = create_news_analyst(llm, toolkit)

# 執行分析
state = {
    "trade_date": "2024-01-15",
    "company_of_interest": "AAPL",
    "messages": [],
    "session_id": "test_session"
}

result = news_analyst(state)
print(result["news_report"])
```

### 5.2 自定義配置

```python
# 自定義新聞聚合器
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

aggregator = RealtimeNewsAggregator()

# 自定義緊急程度關鍵詞
aggregator.high_urgency_keywords = ["破產", "收購", "FDA批準"]
aggregator.medium_urgency_keywords = ["財報", "合作", "新產品"]

# 獲取新聞
news_items = aggregator.get_realtime_stock_news("AAPL", hours_back=12)
report = aggregator.format_news_report(news_items, "AAPL")
```

## 6. 配置要求

### 6.1 API密鑰配置

```bash
# .env 文件配置
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWSAPI_KEY=your_newsapi_key
```

### 6.2 依賴包要求

```python
# requirements.txt
requests>=2.28.0
langchain-core>=0.1.0
>=1.9.0  # 用於東方財富新聞
```

## 7. 性能優化

### 7.1 緩存機制
- **新聞緩存**: 避免重複API調用
- **分析緩存**: 相同股票的分析結果緩存
- **工具結果緩存**: 工具調用結果緩存

### 7.2 並發處理
- **多源並發**: 多個新聞源並發獲取
- **異步處理**: 非阻塞的新聞獲取
- **超時控制**: 避免長時間等待

### 7.3 錯誤處理
- **降級策略**: API失敗時的備用方案
- **重試機制**: 網絡錯誤的自動重試
- **異常捕獲**: 完整的異常處理機制

## 8. 擴展性設計

### 8.1 新數據源接入
- **標準接口**: 統一的新聞源接入接口
- **插件化**: 新數據源的插件化集成
- **配置化**: 通過配置文件管理數據源

### 8.2 分析能力擴展
- **情感分析**: 新聞情感傾向分析
- **事件提取**: 關鍵事件的自動提取
- **影響預測**: 基於歷史數據的影響預測

### 8.3 多語言支持
- **中英文**: 中英文新聞的統一處理
- **本地化**: 不同市場的本地化支持
- **翻譯集成**: 自動翻譯功能集成

這個新聞分析工具鏈和提示詞系統為TradingAgentsCN提供了強大的新聞分析能力，能夠實時獲取、處理和分析市場新聞，為投資決策提供重要參考。
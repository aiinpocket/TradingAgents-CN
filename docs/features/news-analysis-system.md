# 

TradingAgentsCN

## 1. 

### 1.1 

```
 (NewsAnalyst)
 ↓
 ()
 ↓

 

 ↓ ↓ ↓
 (RealtimeNewsAggregator)
 ↓

 FinnHub Alpha NewsAPI 
 Vantage 

 ↓

 ↓

 
 

 ↓

 ↓
LLM ()
 ↓

```

### 1.2 

#### 1.2.1 (NewsAnalyst)

****: `tradingagents/agents/analysts/news_analyst.py`

****:
- 
- 
- LLM
- 

****:
```python
# 
if is_china:
 tools = [
 toolkit.get_realtime_stock_news, # 
 toolkit.get_google_news, # Google
 toolkit.get_global_news_openai # OpenAI
 ]

# 
else:
 tools = [
 toolkit.get_realtime_stock_news, # 
 toolkit.get_global_news_openai,
 toolkit.get_google_news
 ]

# 
if not online_tools:
 tools = [
 toolkit.get_realtime_stock_news, # 
 toolkit.get_finnhub_news,
 toolkit.get_google_news,
 ]
```

#### 1.2.2 (RealtimeNewsAggregator)

****: `tradingagents/dataflows/realtime_news_utils.py`

****:
- 
- 
- 
- 
- 

****:
1. **FinnHub** ()
2. **Alpha Vantage**
3. **NewsAPI**
4. ****

****:
```python
@dataclass
class NewsItem:
 title: str # 
 content: str # 
 source: str # 
 publish_time: datetime # 
 url: str # 
 urgency: str # (high, medium, low)
 relevance_score: float # 
```

#### 1.2.3 

****:
- 
- 

****:
```python
# 
high_urgency_keywords = [
 "", "", "", "", "FDA", "",
 "", "", "", "", ""
]

# 
medium_urgency_keywords = [
 "", "", "", "", "",
 "", "", "", ""
]
```

****:
- 
- 
- 
- 

## 2. 

### 2.1 

```python
system_message = """


1. 15-30
2. 
3. 
4. 
5. 


- 
- 
- 
- 
- 
- 


- 
- 
- 
- //
- 

 
- 1-3
- 
- 
- 
- 
- ''''


 2
 
 
 

Markdown"""
```

### 2.2 

#### 2.2.1 
- ****: 
- ****: 
- ****: 

#### 2.2.2 
- ****: 5
- ****: 6
- ****: 5

#### 2.2.3 
- ****: 
- ****: + Markdown
- ****: + 

#### 2.2.4 
- ****: 15-30
- ****: 
- ****: 

### 2.3 

```python
prompt = ChatPromptTemplate.from_messages([
 (
 "system",
 "AI"
 " "
 " {tool_names}\n{system_message}"
 "{current_date}{ticker}",
 ),
 MessagesPlaceholder(variable_name="messages"),
])

# 
prompt = prompt.partial(system_message=system_message)
prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
prompt = prompt.partial(current_date=current_date)
prompt = prompt.partial(ticker=ticker)
```

## 3. 

### 3.1 

```python
def create_news_analyst(llm, toolkit):
 @log_analyst_module("news")
 def news_analyst_node(state):
 # 1. 
 current_date = state["trade_date"]
 ticker = state["company_of_interest"]
 session_id = state.get("session_id", "")
 
 # 2. 
 market_info = get_stock_market_info(ticker)
 is_china = market_info['is_china']
 
 # 3. 
 tools = select_tools_by_market(is_china, toolkit.config["online_tools"])
 
 # 4. 
 prompt = build_prompt_template(system_message, tools, current_date, ticker)
```

### 3.2 

```python
def get_realtime_stock_news(ticker: str, hours_back: int = 6):
 # 1. 
 finnhub_news = _get_finnhub_realtime_news(ticker, hours_back)
 av_news = _get_alpha_vantage_news(ticker, hours_back)
 newsapi_news = _get_newsapi_news(ticker, hours_back)
 chinese_news = _get_chinese_finance_news(ticker, hours_back)
 
 # 2. 
 all_news = finnhub_news + av_news + newsapi_news + chinese_news
 
 # 3. 
 unique_news = _deduplicate_news(all_news)
 sorted_news = sorted(unique_news, key=lambda x: x.publish_time, reverse=True)
 
 # 4. 
 report = format_news_report(sorted_news, ticker)
 
 return report
```

### 3.3 LLM

```python
def analyze_news_with_llm(llm, prompt, tools, state):
 # 1. 
 chain = prompt | llm.bind_tools(tools)
 
 # 2. LLM
 result = chain.invoke(state["messages"])
 
 # 3. 
 if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
 # 
 tool_results = process_tool_calls(result.tool_calls)
 report = generate_analysis_report(tool_results)
 else:
 # LLM
 report = result.content
 
 return report
```

### 3.4 

```python
def format_news_report(news_items: List[NewsItem], ticker: str) -> str:
 report = f"# {ticker} \n\n"
 report += f" ****: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
 report += f" ****: {len(news_items)} \n\n"
 
 # 
 urgent_news = [item for item in news_items if item.urgency == 'high']
 if urgent_news:
 report += "## \n\n"
 for item in urgent_news:
 report += format_news_item(item)
 
 # 
 normal_news = [item for item in news_items if item.urgency != 'high']
 if normal_news:
 report += "## \n\n"
 for item in normal_news[:10]: # 
 report += format_news_item(item)
 
 return report
```

## 4. 

### 4.1 
- ****: 
- ****: 
- ****: /

### 4.2 
- **API**: FinnHubAlpha Vantage
- **API**: NewsAPI
- ****: 

### 4.3 
- ****: 
- ****: + 
- ****: 
- ****: 

### 4.4 
- ****: 
- ****: 5 + 6
- ****: 
- ****: + 

### 4.5 
- ****: 
- ****: 
- ****: 
- ****: 

## 5. 

### 5.1 

```python
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.utils.agent_utils import Toolkit
from langchain_openai import ChatOpenAI

# LLM
llm = ChatOpenAI(model="gpt-4o-mini")
toolkit = Toolkit()

# 
news_analyst = create_news_analyst(llm, toolkit)

# 
state = {
 "trade_date": "2024-01-15",
 "company_of_interest": "AAPL",
 "messages": [],
 "session_id": "test_session"
}

result = news_analyst(state)
print(result["news_report"])
```

### 5.2 

```python
# 
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

aggregator = RealtimeNewsAggregator()

# 
aggregator.high_urgency_keywords = ["", "", "FDA"]
aggregator.medium_urgency_keywords = ["", "", ""]

# 
news_items = aggregator.get_realtime_stock_news("AAPL", hours_back=12)
report = aggregator.format_news_report(news_items, "AAPL")
```

## 6. 

### 6.1 API

```bash
# .env 
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWSAPI_KEY=your_newsapi_key
```

### 6.2 

```python
# requirements.txt
requests>=2.28.0
langchain-core>=0.1.0
>=1.9.0 # 
```

## 7. 

### 7.1 
- ****: API
- ****: 
- ****: 

### 7.2 
- ****: 
- ****: 
- ****: 

### 7.3 
- ****: API
- ****: 
- ****: 

## 8. 

### 8.1 
- ****: 
- ****: 
- ****: 

### 8.2 
- ****: 
- ****: 
- ****: 

### 8.3 
- ****: 
- ****: 
- ****: 

TradingAgentsCN
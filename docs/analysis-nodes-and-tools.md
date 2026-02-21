# TradingAgents 

## 

TradingAgents 

## 

### 
```mermaid
graph TD
 A[] --> B[]
 B --> C[]
 C --> D[]
 D --> E[]
 E --> F[]

 F --> G[]

 G --> H1[]
 G --> H2[]
 G --> H3[]
 G --> H4[]

 H1 --> I[]
 H2 --> I
 H3 --> I
 H4 --> I

 I --> J1[]
 I --> J2[]
 J1 --> K[]
 J2 --> K

 K --> L[]
 L --> M[]

 M --> N1[]
 M --> N2[]
 M --> N3[]

 N1 --> O[]
 N2 --> O
 N3 --> O

 O --> P[]
 P --> Q[]
```

### 
1. **** (1-5): 
2. **** (6): 
3. **** (7-8): 
4. **** (9-11): 
5. **** (12-13): 

## 

### 1. (Analysts)

#### (Market Analyst)
****: 

****:
- (MA, RSI, MACD, )
- 
- 
- 
- 

****:
```python
# 
- get_stock_market_data_unified # ()
- get_YFin_data_online # Yahoo Finance 
- get_stockstats_indicators_report_online # 

# 
- get_YFin_data # Yahoo Finance 
- get_stockstats_indicators_report # 
```

****:
- ****: Yahoo Finance + FinnHub

#### (Fundamentals Analyst)
****: 

****:
- 
- DCF
- (P/E, P/B, EV/EBITDA)
- 
- 

****:
```python
# 
- get_stock_fundamentals_unified # ()

# 
- get_finnhub_company_insider_sentiment # 
- get_finnhub_company_insider_transactions # 
- get_simfin_balance_sheet # 
- get_simfin_cashflow # 
- get_simfin_income_stmt # 
```

****:
- ****: FinnHub + SimFin 

#### (News Analyst)
****: 

****:
- 
- 
- 
- 
- 

****:
```python
# 
- get_realtime_stock_news # 
- get_global_news_openai # (OpenAI)
- get_google_news # Google 

# 
- get_finnhub_news # FinnHub 
```

#### (Social Media Analyst)
****: 

****:
- 
- 
- 
- 
- 

****:
```python
# 
- get_stock_news_openai # (OpenAI)

# 
- get_finnhub_social_sentiment # FinnHub 
```

### 2. (Researchers)

#### (Bull Researcher)
****: 

****:
- 
- 
- 
- 
- 

****: LLM

#### (Bear Researcher)
****: 

****:
- 
- 
- 
- 
- 

****: LLM

### 3. (Managers)

#### (Research Manager)
****: 

****:
- /
- 
- 
- 
- 

****:
```python
# 
- 
- 
- 
- 
- 
```

#### (Risk Manager)
****: 

****:
- 
- 
- 
- 
- 

### 4. (Trading)

#### (Trader)
****: 

****:
- 
- 
- 
- 
- 

****:
```python
# 
{
 "action": "//",
 "confidence": " (1-10)",
 "target_price": "",
 "stop_loss": "",
 "position_size": "",
 "time_horizon": "",
 "reasoning": ""
}
```

### 5. (Risk Management)

#### (Risky Analyst)
****: 
****: 

#### (Safe Analyst)
****: 
****: 

#### (Neutral Analyst)
****: 
****: 

### 6. (Signal Processing)

#### (Signal Processor)
****: 

****:
1. 
2. 
3. 
4. 
5. 

## 

### 

#### 
```python
# 
get_stock_market_data_unified(ticker, start_date, end_date)
get_stock_fundamentals_unified(ticker, start_date, end_date)
```

#### 
| | | | |
|---------|---------|-----------|---------|
| **** | Yahoo + FinnHub | FinnHub + SimFin | FinnHub + Google |

### 

LangGraph

```python
# 
 → → → 
 ↓ ↓ ↓ ↓
 → → → 
```

****:
1. ****: → 
2. ****: → 
3. ****: → 

## LLM

### 

LLMToolNode

#### 1⃣ 
```python
# 
****
get_stock_market_data_unified{company_name}{ticker}

```

#### 2⃣ 
| | | | |
|---------|------|-----------|--------|
| `get_stock_market_data_unified` | **** | (3) | |
| `get_YFin_data_online` | Retrieve stock price data from Yahoo Finance | (3) | |
| `get_stockstats_indicators_report_online` | Retrieve stock stats indicators | (4) | |

#### 3⃣ 
- `unified` = 
- `online` = 
- `indicators` = 

#### 4⃣ 
```python
# - 3
get_stock_market_data_unified(ticker, start_date, end_date)

# - 4indicator
get_stockstats_indicators_report_online(symbol, indicator, curr_date, look_back_days)
```

### LLM

```
1. : ""
2. : 5
3. : """"
4. : unified
5. : unified
6. : get_stock_market_data_unified
```

### 

ToolNode****

```
1: get_stock_market_data_unified ()
2: get_YFin_data_online ()
3: get_stockstats_indicators_report_online ()
4: get_YFin_data ()
5: get_stockstats_indicators_report ()
```

### 

****:
```
[DEBUG] : ['get_stock_market_data_unified']
[] : ['get_stock_market_data_unified']
[] : AAPL
[] : 
[] ...
```

****: LLM15

## 

### 

****LLM

### 

#### 1
```python
# LLM
result = chain.invoke(state["messages"])

if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
 # LLM
 logger.info(f"[] : {tool_calls_info}")
 return {"messages": [result]} # 
```

#### 2
```python
# LangGraph
tool_result = get_stock_fundamentals_unified.invoke(args)
# 
```

#### 3
```python
# 
final_result = llm.invoke(messages_with_tool_data)
return {"fundamentals_report": final_result.content}
```

#### 
```python
else:
 # LLM
 logger.debug(f"[DEBUG] ")

 # 
 unified_tool = find_tool('get_stock_fundamentals_unified')
 combined_data = unified_tool.invoke({
 'ticker': ticker,
 'start_date': start_date,
 'end_date': current_date,
 'curr_date': current_date
 })

 # 
 analysis_prompt = f"{company_name}\n{combined_data}"
 final_result = llm.invoke(analysis_prompt)

 return {"fundamentals_report": final_result.content}
```

### 

**3**:
```
[] fundamentals_analyst - : AAPL
[] : ['get_stock_fundamentals_unified'] # 1
[] : AAPL # 2
[] fundamentals_analyst - - : 45.32s # 3
```

****:
```
[] fundamentals_analyst - : AAPL
[DEBUG] # 1LLM
[DEBUG] get_stock_fundamentals_unified... # 2
[] : AAPL # 3
[] : 1847 # 4
[] fundamentals_analyst - - : 52.18s # 
```

### 

#### 1⃣ LLM
LLM
- **GPT**: 
- **Claude**: 
- **Google Gemini**: 

#### 2⃣ 
LLM""

#### 3⃣ 
LLM""

### 

#### 1⃣ 
```python
# 
" get_stock_fundamentals_unified "
""
""
```

#### 2⃣ 
- 
- 

#### 3⃣ 
- 
- 
- 

## 

### 
```python
# 
selected_analysts = [
 "market", # 
 "fundamentals", # 
 "news", # 
 "social" # 
]
```

### 
```python
# 
research_depth = {
 1: "", # 
 2: "", # 
 3: "" # 
}
```

### 
```python
# 
risk_config = {
 "max_debate_rounds": 2, # 
 "max_risk_discuss_rounds": 1, # 
 "memory_enabled": True, # 
 "online_tools": True # 
}
```

## 

### 
1. ****: 
2. ****: 
3. ****: /
4. ****: 
5. ****: 
6. ****: 

### 
1. ****: 
2. ****: API
3. ****: 
4. ****: 
5. ****: 

## 

### 
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 
graph = TradingAgentsGraph(
 selected_analysts=["market", "fundamentals"],
 config={
 "llm_provider": "google",
 "research_depth": 2,
 "online_tools": True
 }
)

# 
state, decision = graph.propagate("AAPL", "2025-01-17")
print(f": {decision['action']}")
```

### 
```python
# 
quick_analysis = ["market"]

# 
fundamental_analysis = ["fundamentals", "news"]

# ()
complete_analysis = ["market", "fundamentals", "news", "social"]
```

## 

### 
```python
# 
market_data = toolkit.get_stock_market_data_unified.invoke({
 'ticker': 'AAPL',
 'start_date': '2025-01-01',
 'end_date': '2025-01-17'
})

# 
fundamentals = toolkit.get_stock_fundamentals_unified.invoke({
 'ticker': 'AAPL',
 'start_date': '2025-01-01',
 'end_date': '2025-01-17',
 'curr_date': '2025-01-17'
})
```

### 
```
[] market_analyst - : AAPL
[] : ['get_stock_market_data_unified']
[] : AAPL
[] Yahoo Finance
[] market_analyst - - : 41.73s
```

## 

### Q: 
A: LangGraph"→→"

### Q: 
A:
- ****: market
- ****: fundamentals + news
- ****: market + fundamentals + news + social

### Q: 
A: 
- (AAPL, GOOGL) → → Yahoo/FinnHub

### Q: 
A:
1. research_depth (1=, 2=, 3=)
2. 
3. API

### Q: 
A: 
- **action**: //
- **confidence**: (1-10)
- **target_price**: 
- **reasoning**: 

### Q: API
A:
- ****: /
- ****: 
- ****: 
- ****: API KEY

### Q: API
A: 
- ****: 
- **API**: 
- ****: 
- ****: 
- ****: 

### Q: 
A: 
```bash
python test_memory_fallback.py
```


### Q: API
A: 
```bash
python scripts/check_api_config.py
```
API

## 

### 1. 
```python
# 
config = {
 "cache_enabled": True,
 "cache_duration": 3600, # 1
 "force_refresh": False
}
```

### 2. 
```python
# 
parallel_analysts = ["news", "social"] # 
sequential_analysts = ["market", "fundamentals"] # 
```

### 3. 
```python
# 
config = {
 "max_execution_time": 300, # 5
 "tool_timeout": 30, # 30
 "llm_timeout": 60 # LLM60
}
```

## 

### 
```python
import logging

# 
logging.getLogger('agents').setLevel(logging.DEBUG)
logging.getLogger('tools').setLevel(logging.INFO)
```

### 
```python
# 
from web.utils.async_progress_tracker import AsyncProgressTracker

tracker = AsyncProgressTracker(
 analysis_id="analysis_123",
 analysts=["market", "fundamentals"],
 research_depth=2,
 llm_provider="google"
)
```

## 

### 1. 
- ****: 
- ****: 
- ****: 

### 2. 
- ****: WebSocket
- ****: 
- **AI**: AI

### 3. 
- ****: 
- ****: AI
- ****: 

## 

- [](./architecture/system-architecture.md)
- [](./architecture/agent-architecture.md)
- [](./progress-tracking-explanation.md)
- [API](./api/api-reference.md)
- [](./deployment/deployment-guide.md)
- [](./troubleshooting/common-issues.md)

---

*TradingAgents v0.1.7GitHub*

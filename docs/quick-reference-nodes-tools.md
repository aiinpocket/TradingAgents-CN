# TradingAgents 

## 

```
 → → → → → 
 ↓
 ()
 ← get_stock_market_data_unified
 ← get_stock_fundamentals_unified
 ← get_realtime_stock_news
 ← get_stock_news_openai
 ↓

 ←→ 
 ()
 ↓
 ()
 ↓

 ← → 
 ()
 ↓
 → 
```

## 

| | | | |
|---------|---------|---------|---------|
| **** | | | `get_stock_market_data_unified` |
| **** | | | `get_stock_fundamentals_unified` |
| **** | | | `get_realtime_stock_news` |
| **** | | | `get_stock_news_openai` |
| **** | | | LLM + |
| **** | | | LLM + |
| **** | | | LLM + |
| **** | | | LLM + |
| **** | | | LLM |
| **** | | | LLM |
| **** | | | LLM |
| **** | | | LLM + |
| **** | | | |

## 

### 
```python
# ()
get_stock_market_data_unified(ticker, start_date, end_date)
# 
# : Yahoo + FinnHub

# 
get_YFin_data_online(symbol, start_date, end_date) # Yahoo Finance
get_stockstats_indicators_report_online(symbol, period) # 
```

### 
```python
# ()
get_stock_fundamentals_unified(ticker, start_date, end_date, curr_date)
# 
# : FinnHub + SimFin

# 
get_finnhub_company_insider_sentiment(symbol) # 
get_simfin_balance_sheet(ticker, year, period) # 
get_simfin_income_stmt(ticker, year, period) # 
```

### 
```python
# 
get_realtime_stock_news(symbol, days_back) # 
get_global_news_openai(query, max_results) # (OpenAI)
get_google_news(query, lang, country) # Google 

# 
get_finnhub_news(symbol, start_date, end_date) # FinnHub 
```

### 
```python
# 
get_stock_news_openai(symbol, sentiment_focus) # 
get_finnhub_social_sentiment(symbol) # FinnHub 
```

## 

| | | | | |
|---------|---------|-----------|-------------|-----------|
| **** | (AAPL) | Yahoo + FinnHub | FinnHub + SimFin | FinnHub + Google |

## 

### 
```python
# (1-2)
selected_analysts = ["market"]

# (3-5)
selected_analysts = ["market", "fundamentals"]

# (5-10)
selected_analysts = ["market", "fundamentals", "news", "social"]
```

### 
```python
research_depth = 1 # : 
research_depth = 2 # : ()
research_depth = 3 # : 
```

### LLM
```python
llm_provider = "openai" # OpenAI GPT-4 
llm_provider = "anthropic" # Anthropic Claude 
```

## 

LangGraph

```
1 
 ↓ ()
2 
 ↓ ()
3 
 ↓ ()
4 
 ↓ ()
5 
 ↓ ()
6 → 
```

****:
```
[] market_analyst - : AAPL
[] : ['get_stock_market_data_unified']
[] market_analyst - - : 41.73s
```

## 

### 
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

# 
graph = TradingAgentsGraph(
 selected_analysts=["market", "fundamentals"],
 config={"llm_provider": "openai", "research_depth": 2}
)

# 
state, decision = graph.propagate("AAPL", "2025-01-17")
print(f": {decision['action']}, : {decision['confidence']}")
```

### Web
```bash
# Web
python web/run_web.py

# http://localhost:8501
# 1. 
# 2. 
# 3. ""
# 4. 
```

## 

| | | |
|-----|------|---------|
| | / | research_depth |
| | LangGraph | |
| | | |
| API | / | .envAPI |
| | /API | |
| | | UTF-8 |

## 

### 
```
1 → 2 → 3 
```

### 
```
1 LLM → 2 → 3 
 ↓ (LLM)
4 → 5 
```

### LLM
1. **** ()
2. ****
3. ****
4. ****
5. ****

## 

### 
```json
{
 "action": "//",
 "confidence": 8.5,
 "target_price": "195.80",
 "stop_loss": "175.20",
 "position_size": "",
 "time_horizon": "3-6",
 "reasoning": "..."
}
```

### 
```

 
 
 
 
 


 
 
 
 
 
```

---

* | TradingAgents v0.1.7 | *

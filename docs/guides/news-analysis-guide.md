# 

TradingAgentsCN

## 1. 



- ****
- ****
- ****

## 2. 

### 2.1 API

API

```python
# config.py.env
FINNHUB_API_KEY = "your_finnhub_api_key"
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_api_key"
NEWSAPI_API_KEY = "your_newsapi_api_key"
```

API
- FinnHub: https://finnhub.io/
- Alpha Vantage: https://www.alphavantage.co/
- NewsAPI: https://newsapi.org/

### 2.2 

```python
# 
from tradingagents.agents.utils.agent_utils import Toolkit

# 
from langchain_openai import ChatOpenAI
from tradingagents.agents.analysts.news_analyst import create_news_analyst
```

## 3. 

### 3.1 

```python
# 
toolkit = Toolkit()

# 
ticker = "AAPL" # 
curr_date = "2023-07-01" # 
news_report = toolkit.get_realtime_stock_news(ticker, curr_date)

print(news_report)
```


- 
- 
- 
- 
- 
- 

### 3.2 



```python
# 
# 
ticker = "AAPL" # 
news_report = toolkit.get_stock_news_unified(ticker, curr_date)
print(news_report)

# 
tsla_news = toolkit.get_stock_news_unified("TSLA", curr_date)
print(tsla_news)

nvda_news = toolkit.get_stock_news_unified("NVDA", curr_date)
print(nvda_news)
```


- ****FinnhubGoogle News

## 4. 



```python
# LLM
llm = ChatOpenAI() # OpenAI
toolkit = Toolkit()

# 
news_analyst = create_news_analyst(llm, toolkit)

# 
state = {
 "trade_date": "2023-07-01",
 "company_of_interest": "AAPL",
 "messages": []
}

# 
result = news_analyst(state)

# 
print(result["news_report"])
```


- 
- 
- 
- 
- 
- 

## 5. 

```python
# 
global_news = toolkit.get_global_news_openai(curr_date)
print(global_news)
```

## 6. 

### 6.1 



```python
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

# 
aggregator = RealtimeNewsAggregator(
 finnhub_enabled=True,
 alpha_vantage_enabled=True,
 newsapi_enabled=False, # NewsAPI
 chinese_finance_enabled=False # 
)

# 
news_items = aggregator.get_news(ticker, curr_date)

# 
report = aggregator.format_news_report(news_items, ticker, curr_date)
print(report)
```

### 6.2 



```python
from tradingagents.dataflows.realtime_news_utils import RealtimeNewsAggregator

# 
high_urgency_keywords = ["", "", "", "", "FDA", ""]
medium_urgency_keywords = ["", "", "", "", ""]

# 
aggregator = RealtimeNewsAggregator()

# 
aggregator.high_urgency_keywords = high_urgency_keywords
aggregator.medium_urgency_keywords = medium_urgency_keywords

# 
news_items = aggregator.get_news(ticker, curr_date)

# 
report = aggregator.format_news_report(news_items, ticker, curr_date)
print(report)
```

## 7. 

1. **** `get_realtime_stock_news` 

2. **** `get_stock_news_unified` 

3. **** `get_global_news_openai` 

5. **API** FinnHubAlpha VantageNewsAPI API

6. ****

7. ****

## 8. 

### 8.1 API

API

- API
- API
- 

### 8.2 



- 
- 
- 

## 9. 



TradingAgentsCN
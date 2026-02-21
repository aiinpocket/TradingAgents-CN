# 

## 

 TradingAgents 

## 

### 



```python
# 
from tradingagents.utils.tool_logging import log_analyst_module

# 
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_analyst_module("analyst_type")
def analyst_node(state):
 # 
 pass
```

### 

 `AgentState` 

```python
class AgentState:
 company_of_interest: str # 
 trade_date: str # 
 fundamentals_report: str # 
 market_report: str # 
 news_report: str # 
 sentiment_report: str # 
 messages: List # 
```

## 

### 1. (Fundamentals Analyst)

****: `tradingagents/agents/analysts/fundamentals_analyst.py`

****:
- 
- 
- 

****:
- 
- 
- /

****:
```python
def create_fundamentals_analyst(llm, toolkit):
 @log_analyst_module("fundamentals")
 def fundamentals_analyst_node(state):
 ticker = state["company_of_interest"]

 # 
 from tradingagents.utils.stock_utils import get_stock_market_info
 market_info = get_stock_market_info(ticker)

 # 
 company_name = _get_company_name_for_fundamentals(ticker, market_info)

 # 
 if toolkit.config["online_tools"]:
 tools = [toolkit.get_stock_fundamentals_unified]
 else:
 # 
 tools = [...]
```

****:
- ****: FinnHubSimFin

### 2. (Market Analyst)

****: `tradingagents/agents/analysts/market_analyst.py`

****:
- RSIMACD
- 
- 
- 

****:
- 
- 
- 
- 

### 3. (News Analyst)

****: `tradingagents/agents/analysts/news_analyst.py`

****:
- 
- 
- 
- 

****:
- Google News API
- FinnHub
- 
- 

****:
- 
- 
- 

### 4. (Social Media Analyst)

****: `tradingagents/agents/analysts/social_media_analyst.py`

****:
- 
- 
- 
- 

****:
- FinnHub 
- 
- 

## 

### 



```python
# 
tools = [toolkit.get_stock_fundamentals_unified]

# 
# - : Yahoo FinanceFinnHub
```

### /

**** (`online_tools=True`):
- API
- 
- 

**** (`online_tools=False`):
- 
- 
- 

## 

### 

```python
from tradingagents.utils.stock_utils import get_stock_market_info
market_info = get_stock_market_info(ticker)

# 
# - is_us: 
# - market_name: 
# - currency_name: 
# - currency_symbol: 
```

### 

****
- AAPL, TSLA
- (USD)
- FinnHub, Yahoo Finance

## 

### 1. 
```mermaid
graph LR
 A[] --> B[]
 B --> C[]
 C --> D[]
 D --> E[]
```

### 2. 
```mermaid
graph TB
 A[] --> B[]
 A --> C[]
 A --> D[]
 A --> E[]

 B --> F[]
 C --> G[]
 D --> H[]
 E --> I[]
```

### 3. 
```mermaid
graph LR
 A[] --> B[]
 B --> C[]
 C --> D[]
```

## 

### 
```python
# 
selected_analysts = [
 "market", # 
 "social", # 
 "news", # 
 "fundamentals" # 
]
```

### 
```python
toolkit_config = {
 "online_tools": True, # 
 "cache_enabled": True, # 
 "timeout": 30, # API
 "retry_count": 3 # 
}
```

## 

### 
```python
# 
logger = get_logger("default")

# 
logger.debug(f" [DEBUG] ")
logger.info(f" [] : {ticker}")
logger.warning(f" [DEBUG] memoryNone")
```

### 
- 
- API
- 
- 

## 

### 

1. ****
```python
# tradingagents/agents/analysts/custom_analyst.py
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.utils.logging_init import get_logger

def create_custom_analyst(llm, toolkit):
 @log_analyst_module("custom")
 def custom_analyst_node(state):
 # 
 pass
 return custom_analyst_node
```

2. ****
```python
# trading_graph.py
selected_analysts.append("custom")
```

### 

1. ****
2. ****
3. ****

## 

### 1. 
- try-catchAPI
- 
- 

### 2. 
- 
- 
- API

### 3. 
- 
- 
- 

### 4. 
- 
- 
- 

## 

### 

1. **API**
 - 
 - API
 - 

2. ****
 - 
 - 
 - 

3. ****
 - 
 - 
 - API

### 

1. ****
```python
logger.setLevel(logging.DEBUG)
```

2. ****
```python
logger.debug(f": {state}")
```

3. ****
```python
logger.debug(f": {toolkit.config}")
```

TradingAgents

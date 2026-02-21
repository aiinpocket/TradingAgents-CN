# 

## 

 TradingAgents 

## 

### 



```python
# 
from tradingagents.utils.tool_logging import log_risk_module

# 
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_risk_module("risk_type")
def risk_node(state):
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
 trader_recommendation: str # 
 messages: List # 
```

## 

### 1. (Conservative Risk Analyst)

****: `tradingagents/agents/risk_mgmt/conservative_debator.py`

****:
- /
- 
- 
- 

****:
```python
def create_safe_debator(llm):
 @log_risk_module("conservative")
 def safe_node(state):
 # 
 company_name = state["company_of_interest"]
 trader_recommendation = state.get("trader_recommendation", "")
 
 # 
 from tradingagents.utils.stock_utils import get_stock_market_info
 market_info = get_stock_market_info(company_name)
 
 # 
 if market_info.get("is_us"):
 stock_type = ""
 currency_unit = ""
 else:
 stock_type = ""
 currency_unit = ""
 
 # 
 market_report = state.get("market_report", "")
 sentiment_report = state.get("sentiment_report", "")
 news_report = state.get("news_report", "")
 fundamentals_report = state.get("fundamentals_report", "")
 
 # 
 safe_prompt = f"""
 /
 
 : {company_name}
 : {stock_type}
 : {currency_unit}
 
 : {trader_recommendation}
 
 : {market_report}
 : {sentiment_report}
 : {news_report}
 : {fundamentals_report}
 
 
 1. 
 2. 
 3. 
 4. 
 5. 
 """
 
 # LLM
 response = llm.invoke(safe_prompt)
 
 return {"conservative_risk_analysis": response.content}
```

****:
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 1. 

****:
- 
- 
- 
- 

****:
- 
- 
- 
- 

### 2. 

****:
- 
- 
- 
- 

****:
- 
- 
- 
- 

### 3. 

****:
- 
- 
- 
- 

****:
- 
- 
- 
- 

### 4. 

****:
- 
- 
- 
- 

****:
- 
- 
- 
- 

## 

### 

```python
risk_config = {
 "risk_tolerance": "moderate", # 
 "max_portfolio_var": 0.05, # VaR
 "max_single_position": 0.05, # 
 "max_sector_exposure": 0.20, # 
 "correlation_threshold": 0.70, # 
 "rebalance_trigger": 0.05, # 
 "stress_test_frequency": "weekly" # 
}
```

## 

### 

```python
# 
logger.info(f" [] : {company_name}")
logger.info(f" [] : {stock_type}, : {currency_unit}")
logger.debug(f" [] {len(risk_factors)} ")
logger.warning(f" [] : {high_risk_factors}")
logger.info(f" [] : {risk_level}")
```

### 

- 
- 
- 
- 
- 

## 

### 

1. ****
```python
# tradingagents/agents/risk_mgmt/new_risk_analyst.py
from tradingagents.utils.tool_logging import log_risk_module
from tradingagents.utils.logging_init import get_logger

logger = get_logger("default")

def create_new_risk_analyst(llm):
 @log_risk_module("new_risk_type")
 def new_risk_node(state):
 # 
 pass
 
 return new_risk_node
```

2. ****
```python
# 
from tradingagents.agents.risk_mgmt.new_risk_analyst import create_new_risk_analyst

new_risk_analyst = create_new_risk_analyst(llm)
```

## 

### 1. 
- 
- 
- 
- 

### 2. 
- 
- 
- 
- 

### 3. 
- 
- 
- 
- 

### 4. 
- 
- 
- 
- 

## 

### 

1. ****
 - 
 - LLM
 - 
 - 

2. ****
 - 
 - 
 - 
 - 

3. ****
 - 
 - 
 - 
 - 

### 

1. ****
```python
logger.debug(f": ={company_name}, ={stock_type}")
logger.debug(f": {risk_factors}")
logger.debug(f": {risk_assessment}")
```

2. ****
```python
logger.debug(f": ={len(fundamentals_report)}")
logger.debug(f": ={len(market_report)}")
logger.debug(f": ={trader_recommendation[:100]}...")
```

TradingAgents
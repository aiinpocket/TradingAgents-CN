# 

## 

 TradingAgents 

## 

### 



```python
# 
from tradingagents.utils.tool_logging import log_manager_module

# 
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_manager_module("manager_type")
def manager_node(state):
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
 bull_argument: str # 
 bear_argument: str # 
 trader_recommendation: str # 
 risk_analysis: str # 
 messages: List # 
```

## 

### 1. (Research Manager)

****: `tradingagents/agents/managers/research_manager.py`

****:
- 
- 
- 
- 
- 

****:
```python
def create_research_manager(llm):
 @log_manager_module("research_manager")
 def research_manager_node(state):
 # 
 company_name = state["company_of_interest"]
 trade_date = state.get("trade_date", "")

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
 fundamentals_report = state.get("fundamentals_report", "")
 market_report = state.get("market_report", "")
 sentiment_report = state.get("sentiment_report", "")
 news_report = state.get("news_report", "")

 # 
 bull_argument = state.get("bull_argument", "")
 bear_argument = state.get("bear_argument", "")

 # 
 manager_prompt = f"""
 

 : {company_name}
 : {stock_type}
 : {currency_unit}
 : {trade_date}

 === ===
 : {fundamentals_report}
 : {market_report}
 : {sentiment_report}
 : {news_report}

 === ===
 : {bull_argument}
 : {bear_argument}

 
 1. 
 2. 
 3. //
 4. 
 5. 
 6. 

 
 """

 # LLM
 response = llm.invoke(manager_prompt)

 return {"investment_plan": response.content}
```

****:
- ****: 
- ****: 
- ****: 
- ****: 

### 2. (Portfolio Manager)

****: `tradingagents/agents/managers/portfolio_manager.py`

****:
- 
- 
- 
- 

****:
```python
{
 "action": " AAPL 200",
 "target_allocation": "5%",
 "reasoning": "...",
 "risk_assessment": ""
}
```

### 3. (Risk Manager)

****: `tradingagents/agents/managers/risk_manager.py`

****:
- 
- 
- 
- 

****:
```python
{
 "risk_level": "",
 "max_drawdown": "15%",
 "stop_loss": "$145.50",
 "position_size": "3% of portfolio"
}
```

## 

### 

```python
manager_config = {
 "decision_model": "consensus", # 
 "confidence_threshold": 0.7, # 
 "risk_tolerance": "moderate", # 
 "position_sizing_method": "kelly", # 
 "max_position_size": 0.05, # 
 "rebalance_frequency": "weekly", # 
 "performance_review_period": "monthly" # 
}
```

## 

### 

```python
# 
logger.info(f"[] : AAPL")
logger.info(f"[] 4 ")
logger.info(f"[] : 7.5, : 5.2")
logger.info(f"[] : , : 75%")
logger.info(f"[] : 4%, : $185")
logger.info(f"[] ")
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
# tradingagents/agents/managers/new_manager.py
from tradingagents.utils.tool_logging import log_manager_module
from tradingagents.utils.logging_init import get_logger

logger = get_logger("default")

def create_new_manager(llm):
 @log_manager_module("new_manager")
 def new_manager_node(state):
 # 
 pass

 return new_manager_node
```

2. ****
```python
# 
from tradingagents.agents.managers.new_manager import create_new_manager

new_manager = create_new_manager(llm)
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
 - 
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
logger.debug(f": {decision_inputs}")
logger.debug(f": {analysis_results}")
logger.debug(f": {decision_output}")
```

2. ****
```python
logger.debug(f": {information_completeness}")
logger.debug(f": {analysis_depth}")
logger.debug(f": {decision_quality}")
```

TradingAgents

# 

## 

 TradingAgents 

## 

### 



```python
# 
from tradingagents.utils.tool_logging import log_trader_module

# 
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_trader_module("trader")
def trader_node(state):
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
 investment_plan: str # 
 messages: List # 
```

## 

### 

****: `tradingagents/agents/trader/trader.py`

****:
- 
- 
- 
- 
- 

### 

```python
def create_trader(llm):
 @log_trader_module("trader")
 def trader_node(state):
 # 
 company_name = state["company_of_interest"]
 investment_plan = state.get("investment_plan", "")
 
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
 trader_prompt = f"""
 
 
 : {company_name}
 : {stock_type}
 : {currency_unit}
 
 : {investment_plan}
 
 : {market_report}
 : {sentiment_report}
 : {news_report}
 : {fundamentals_report}
 
 
 1. //
 2. {currency_unit}
 3. 0-100%
 4. 1-10
 5. 
 """
 
 # LLM
 response = llm.invoke(trader_prompt)
 
 return {"trader_recommendation": response.content}
```

## 

### 



1. **** (`investment_plan`)
 - 
 - 
 - 

2. **** (`market_report`)
 - 
 - 
 - 

3. **** (`sentiment_report`)
 - 
 - 
 - 

4. **** (`news_report`)
 - 
 - 
 - 

5. **** (`fundamentals_report`)
 - 
 - 
 - 

### 

```python
# 
info_weights = {
 "investment_plan": 0.35, # 
 "fundamentals_report": 0.25, # 
 "market_report": 0.20, # 
 "news_report": 0.15, # 
 "sentiment_report": 0.05 # 
}
```

## 

### 



```python
# 
from tradingagents.utils.stock_utils import get_stock_market_info
market_info = get_stock_market_info(company_name)

# 
if market_info.get("is_us"):
 trading_hours = "09:30-16:00 (EST)"
 price_limit = ""
 settlement = "T+2"
 currency = "(USD)"
```

### 

****:
- 
- 
- 
- 
- 
- 

## 

### 



```python
class TradingRecommendation:
 action: str # (//)
 target_price: float # 
 confidence: float # (0-100%)
 risk_score: int # (1-10)
 reasoning: str # 
 time_horizon: str # 
 stop_loss: float # 
 take_profit: float # 
```

### 



1. ****
 - 
 - 
 - 

2. ****
 - 0-100%
 - 
 - 

3. ****
 - 1-10
 - 110
 - 

4. ****
 - 
 - 
 - 

## 

### 1. 

```mermaid
graph LR
 A[] --> E[]
 B[] --> E
 C[] --> E
 D[&] --> E
 E --> F[]
```

### 2. 

```mermaid
graph TB
 A[] --> B[]
 B --> C[]
 C --> D[]
 D --> E[]
 E --> F[]
```

### 3. 

```mermaid
graph LR
 A[] --> B[]
 B --> C[]
 B --> D[]
 B --> E[]
 C --> F[]
 D --> F
 E --> F
```

## 

### 

1. ****:
 - 
 - 
 - 
 - 

2. ****:
 - 
 - 
 - 
 - 

3. ****:
 - 
 - 
 - 
 - 

4. ****:
 - 
 - 
 - 
 - 

### 

```python
# 
risk_controls = {
 "max_position_size": 0.05, # 
 "stop_loss_ratio": 0.08, # 
 "take_profit_ratio": 0.15, # 
 "max_drawdown": 0.10, # 
 "correlation_limit": 0.70 # 
}
```

## 

### 

1. ****:
 - 
 - 
 - 
 - 

2. ****:
 - 
 - 
 - 
 - 

3. ****:
 - 
 - 
 - VaR
 - 

### 

```python
# 
class TradingPerformance:
 def __init__(self):
 self.trades = []
 self.accuracy_rate = 0.0
 self.total_return = 0.0
 self.max_drawdown = 0.0
 self.sharpe_ratio = 0.0
 
 def update_performance(self, trade_result):
 # 
 pass
 
 def generate_report(self):
 # 
 pass
```

## 

### 

```python
trader_config = {
 "risk_tolerance": "moderate", # 
 "investment_style": "balanced", # 
 "time_horizon": "medium", # 
 "position_sizing": "kelly", # 
 "rebalance_frequency": "weekly" # 
}
```

### 

```python
market_config = {
 "trading_hours": {
 "us": "09:30-16:00"
 },
 "settlement_days": {
 "us": 2
 },
 "commission_rates": {
 "us": 0.0005
 }
}
```

## 

### 

```python
# 
logger.info(f" [] : {company_name}")
logger.info(f" [] : {stock_type}, : {currency_unit}")
logger.debug(f" [] : {investment_plan[:100]}...")
logger.info(f" [] ")
```

### 

```python
# 
decision_log = {
 "timestamp": datetime.now(),
 "ticker": company_name,
 "market_type": stock_type,
 "input_reports": {
 "fundamentals": len(fundamentals_report),
 "market": len(market_report),
 "news": len(news_report),
 "sentiment": len(sentiment_report)
 },
 "decision": {
 "action": action,
 "target_price": target_price,
 "confidence": confidence,
 "risk_score": risk_score
 }
}
```

## 

### 

1. ****
```python
class CustomTradingStrategy:
 def __init__(self, config):
 self.config = config
 
 def generate_recommendation(self, state):
 # 
 pass
 
 def calculate_position_size(self, confidence, risk_score):
 # 
 pass
```

2. ****
```python
# trader.py
strategy_map = {
 "conservative": ConservativeStrategy(),
 "aggressive": AggressiveStrategy(),
 "custom": CustomTradingStrategy()
}

strategy = strategy_map.get(config.get("strategy", "balanced"))
```

### 

1. ****
```python
class RiskModel:
 def calculate_risk_score(self, market_data, fundamentals):
 pass
 
 def estimate_var(self, position, confidence_level):
 pass
 
 def suggest_position_size(self, risk_budget, expected_return):
 pass
```

2. ****
```python
risk_models = {
 "var": VaRRiskModel(),
 "monte_carlo": MonteCarloRiskModel(),
 "factor": FactorRiskModel()
}
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
logger.debug(f": {check_input_completeness(state)}")
logger.debug(f": {market_info}")
logger.debug(f": {info_weights}")
```

2. ****
```python
logger.debug(f": {validate_target_price(target_price)}")
logger.debug(f": {validate_risk_score(risk_score)}")
```

3. ****
```python
import time
start_time = time.time()
# 
end_time = time.time()
logger.debug(f": {end_time - start_time:.2f}")
```

TradingAgents